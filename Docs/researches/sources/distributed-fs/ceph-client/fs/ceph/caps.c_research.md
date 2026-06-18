# sources/distributed-fs/ceph-client/fs/ceph/caps.c

## Purpose

`caps.c` implements CephFS client capability management. Capabilities are the MDS-issued permissions that let a client cache inode metadata, cache or buffer file data, perform directory operations, write file data to OSDs, and delay metadata flushes. This file tracks capability objects, desired/used/dirty/revoking bitmasks, MDS session ownership, cap import/export during MDS migration, cap flush ordering, capsnap metadata for snapshots, and release encoding for outgoing MDS requests.

It is the synchronization core that makes `addr.c` safe: page-cache reads/writes, mmap faults, inline-data conversion, and fsync all depend on the cap state machine here to decide when data or metadata can be cached, dirtied, flushed, revoked, or waited on.

## Important APIs, Types, and Functions

The public lifecycle APIs include `ceph_caps_init`, `ceph_caps_finalize`, `ceph_adjust_caps_max_min`, `ceph_reserve_caps`, `ceph_unreserve_caps`, `ceph_get_cap`, `ceph_put_cap`, and `ceph_reservation_status`. These manage the MDS client’s slab-backed pool of `struct ceph_cap` objects and enforce total/used/reserved/available invariants.

Per-inode lookup and installation are handled by `__get_cap_for_mds`, `ceph_get_cap_for_mds`, `ceph_add_cap`, `__ceph_remove_cap`, `ceph_remove_cap`, and `__ceph_remove_caps`. Cap objects are indexed in `ci->i_caps` by MDS id and also linked into each session’s LRU/list.

Capability query and desire computation are handled by `__ceph_caps_issued`, `__ceph_caps_issued_other`, `__ceph_caps_issued_mask`, `__ceph_caps_issued_mask_metric`, `__ceph_caps_revoking_other`, `__ceph_caps_used`, `__ceph_caps_file_wanted`, `__ceph_caps_wanted`, and `__ceph_caps_mds_wanted`.

Reference acquisition and release are centered on `try_get_cap_refs`, `ceph_try_get_caps`, `__ceph_get_caps`, `ceph_get_caps`, `ceph_take_cap_refs`, `ceph_get_cap_refs`, `ceph_put_cap_refs`, `ceph_put_cap_refs_async`, and `ceph_put_wrbuffer_cap_refs`. File-open mode accounting is handled by `ceph_get_fmode`, `ceph_put_fmode`, and `__ceph_touch_fmode`.

Dirty metadata and flushing are handled by `__ceph_mark_dirty_caps`, `ceph_alloc_cap_flush`, `ceph_free_cap_flush`, `__mark_caps_flushing`, `try_flush_caps`, `caps_are_flushed`, `ceph_fsync`, `ceph_write_inode`, `ceph_check_caps`, `ceph_flush_dirty_caps`, and the kick helpers `ceph_early_kick_flushing_caps`, `ceph_kick_flushing_caps`, and `ceph_kick_flushing_inode_caps`.

MDS message handling is centered on `encode_cap_msg`, `__prep_cap`, `__send_cap`, `__send_flush_snap`, `ceph_flush_snaps`, `handle_cap_grant`, `handle_cap_flush_ack`, `handle_cap_flushsnap_ack`, `handle_cap_trunc`, `handle_cap_export`, `handle_cap_import`, `parse_fscrypt_fields`, and `ceph_handle_caps`. Release encoding uses `ceph_encode_inode_release` and `ceph_encode_dentry_release`.

## Control Flow

A typical cap starts as a reserved or freshly allocated `struct ceph_cap`, then `ceph_add_cap` attaches it to an inode and MDS session. The function updates snap realm association, records auth-cap ownership, stores issued/wanted/sequence state, checks side effects of newly issued caps, and queues delayed cap checking if issued caps exceed actual wants.

Callers acquire usable cap references through `ceph_try_get_caps` or `ceph_get_caps`. The internal `try_get_cap_refs` checks file-lock error state, pending truncates, currently issued and implemented caps, write max-size limits, pending capsnaps, readonly MDS sessions, shutdown state, and MDS wanted state. On success it increments per-inode reference counters through `ceph_take_cap_refs`; on transient failure the blocking path waits on `ci->i_cap_wq`, biases fmode refs to keep wants alive, requests larger max_size, or renews caps after stale sessions.

When writes or metadata changes dirty inode state, `__ceph_mark_dirty_caps` sets `ci->i_dirty_caps`, installs a preallocated cap-flush object, ensures a head snap context exists, links the inode to the auth session’s dirty list, takes an inode reference for writeback, and queues delayed cap flushing. Later, `ceph_check_caps` compares file-wanted, used, dirty, issued, implemented, revoking, and retain masks. It may invalidate page cache, queue writeback, mark dirty caps flushing, send cap update/flush messages, or delay cap release.

`__prep_cap` is the state transition point before sending a cap message. It applies retained caps, moves implemented caps through revocation state, records wanted caps, captures size, max_size, xattrs, timestamps, mode/uid/gid, inline-data status, fscrypt auth, flags, flush tid, and oldest flush tid. `encode_cap_msg` serializes these fields into the current MDS cap message format, including fscrypt rounded size plus real file size when encryption is enabled.

Flush acknowledgements reverse the dirty/flushing state. `handle_cap_flush_ack` removes acknowledged cap-flush records up to the acknowledged tid, clears `i_flushing_caps`, removes the inode from flushing lists when clean, wakes inode and MDS waiters, and drops the inode reference taken when the inode became dirty. Snapshot flush acknowledgements go through `handle_cap_flushsnap_ack`, remove matching `ceph_cap_snap` records by `follows` and tid, drop snap contexts, and wake waiters.

`ceph_handle_caps` is the message dispatcher. It decodes versioned MDS cap messages, including snap trace, peer migration fields, inline data, epoch barrier, pool namespace, btime/change_attr, dirstats, and fscrypt fields. It finds the inode, locks the session, dispatches import/export/grant/revoke/flush-ack/trunc operations, updates snap realms on import, and sends cap releases if the MDS references an inode/cap the client no longer has.

Import/export handle MDS authority migration. `handle_cap_export` moves or creates placeholder caps for the target session and transfers auth ownership and flushing-list membership if needed. `handle_cap_import` installs the imported auth cap, removes the peer export cap when appropriate, and then lets `handle_cap_grant` apply the imported grant and wake waiters.

`ceph_fsync` first waits for file data writeback, then for full fsync flushes dirty caps and unsafe MDS requests, and waits for non-file-write metadata caps to be acknowledged. `ceph_write_inode` either flushes caps synchronously for sync writeback or queues immediate cap checking for asynchronous writeback.

## State and Persistence Behavior

Core state lives in `ceph_inode_info`: cap rb-tree, auth cap pointer, dirty/flushing cap masks, cap flush list, delayed cap list membership, cap snap list, wanted max size, requested max size, reported size, head snap context, read-cache generation, file-mode refcounts, cap refs (`i_rd_ref`, `i_rdcache_ref`, `i_wr_ref`, `i_wb_ref`, `i_wrbuffer_ref`, `i_fx_ref`, `i_pin_ref`), inline and fscrypt metadata, xattr blobs, layout, and error flags.

MDS-client/session state includes cap object accounting, session cap lists, delayed release lists, dirty/flushing lists, global cap flush list, last flush tid, wait queues, metrics, and session generation/ttl. Cap flush tids provide ordering for waiters and reconnect replay.

Persistence occurs by sending cap messages to the MDS. Dirty metadata is not durable until the MDS acknowledges cap flushes or unsafe requests complete. Fscrypt auth context and real encrypted file size are included in cap messages; file data itself persists through OSD writes in `addr.c`, while caps record metadata such as size, times, xattrs, mode, uid/gid, inline state, and change attribute.

## Dependencies and Integration Points

This file depends on MDS sessions and requests, messenger sends, snap realm management, xattr/security helpers, fscrypt definitions, fscache invalidation, page-cache invalidation, writeback, file locks, and OSD epoch barriers. It integrates with `addr.c` through cap acquisition/release, dirty cap marking, wrbuffer refs, writeback queueing, mmap page-mkwrite, and fsync/write_inode paths. It integrates with directory/dentry code through dentry lease and inode release encoding, complete-directory invalidation, async dirops, and unlink cap dropping.

## Risks and Edge Cases

The highest-risk area is concurrent cap state transitions under multiple locks (`i_ceph_lock`, session mutex, session cap lock, MDS client mutex, snap rwsem, cap dirty lock, and cap delay lock). Deadlocks are avoided by carefully dropping locks before message sends, target-session opens, or blocking waits. Incorrect ordering can strand dirty caps, lose revocation acks, or race MDS migration.

Dirty/flushing accounting is fragile. Losing a `ceph_cap_flush`, failing to propagate `wake` to earlier flush records, or mishandling `i_head_snapc` can hang fsync or leak inode refs. Revocation while writeback or invalidation is in progress is another risk; code queues writeback/invalidate rather than acknowledging too early. Fscrypt fields add risk because encrypted inodes report rounded cap-message size plus a separate real file size. MDS import/export messages can arrive out of order, so sequence and migrate-sequence comparisons are critical.

Shutdown, reconnect, and blocklist paths intentionally drop dirty state and set mapping/filelock errors. These paths trade data availability for unmount/recovery progress and need focused fault-injection coverage.

## Test Signals

Important tests include cap grant/revoke under buffered reads and writes, mmap writers during revocation, fsync waiting for dirty metadata, snapshot creation with dirty data and capsnaps, MDS failover/reconnect with flushing caps, cap import/export during active writeback, encrypted file size/fscrypt-auth propagation, directory complete-cache invalidation on FILE_SHARED changes, file-lock error behavior after cap purge, unlink/drop-cap release encoding, and memory-pressure cap trimming.

Useful runtime signals are balanced cap object counters, no stuck entries in dirty/flushing lists after flush acks, `ci->i_cap_wq` wakeups for waiters, cap hit/miss metrics, bounded delayed-cap queue progress, correct `oldest_flush_tid` propagation, and successful `file_write_and_wait_range` plus metadata flush completion for fsync.
