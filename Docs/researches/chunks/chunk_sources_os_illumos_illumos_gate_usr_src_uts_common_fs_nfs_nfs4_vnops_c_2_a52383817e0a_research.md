# Chunk Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/nfs/nfs4_vnops.c lines 9831-16006

## Scope

This chunk covers the tail of NFSv4 vnode VM/page-cache handling, page writeback and COMMIT logic, mmap add/delete bookkeeping, pathconf/ACL/share-lock helpers, directory cache update helpers, OPEN_CONFIRM, the main NFSv4 byte-range lock implementation, close-state cleanup, and lock-state reinstitution after lost requests. The source tree `sources/os/illumos/illumos-gate` is included by `Docs/research_subset_a.md`.

The requested range starts inside `nfs4_getapage()`; its function header and initial cache-validation call are just above the chunk boundary.

## APIs and Entry Points

- VM/page-cache vnode operations and helpers: `nfs4_getapage()` tail, `nfs4_readahead()`, `nfs4_putpage()`, `nfs4_putapage()`, `nfs4_sync_putapage()`, `nfs4_pageio()`, `nfs4_sync_pageio()`, and `nfs4_dispose()`.
- mmap operations: `nfs4_map()`, `open_and_get_osp()`, `nfs4_addmap()`, `nfs4_delmap()`, `nfs4_delmap_callback()`, plus delmap-caller list helpers.
- File/attribute operations: `nfs4_space()`, `nfs4_realvp()`, `nfs4_pathconf()`, `nfs4_setsecattr()`, `nfs4_getsecattr()`, and ACL mask/translation helpers.
- Cache/state helpers: `nfs4_update_attrcache()`, `nfs4_update_dircaches()`, `nfs4open_confirm()`, `state_to_cred()`, `nfs4_find_sysid()`, `vtodv()`, and `vtoname()`.
- Locking entry points and internals: `nfs4_frlock()`, `nfs4frlock()`, `nfs4_safelock()`, `nfs4_register_lock_locally()`, `nfs4_lockrelease()`, denial conversion helpers, and lost-lock reinstate helpers.
- Close-state entry points: `nfs4close_notw()`, `nfs4close_all()`, and `nfs4close_one()`.

## Core Control Flow

`nfs4_getapage()` completes page fault/page-in handling by computing block-sized or page-sized reads, queuing readahead when sequential access is detected, calling `pvn_read_kluster()`, issuing `nfs4_bio()` unless the request is known beyond EOF in `segkmap`, and returning pages through `pvn_plist_init()`.

`nfs4_putpage()` and `nfs4_putapage()` coordinate dirty-page writeback with `rp->r_count`, async I/O, and `R4MODINPROGRESS` protection so writes are not lost while `r_size` is unstable. COMMIT paths serialize through `R4COMMIT`, gather committable pages, issue `OP_COMMIT`, and repeat flush/commit when the server write verifier changes.

`nfs4_map()` validates cache/lock safety, creates missing open-stream state for mmap, then maps through `as_map()`. `nfs4_addmap()` updates rnode and open-stream mmap counters. `nfs4_delmap()` installs an address-space callback and returns `EAGAIN` so costly flush/CLOSE work runs without holding `as->a_lock`.

`nfs4_frlock()` validates POSIX locks, flushes pages before non-query operations, serializes against mmap, then delegates protocol work to `nfs4frlock()`. `nfs4frlock()` builds `PUTFH + LOCK/LOCKU/LOCKT` compounds, synchronizes open/lock seqids, handles delegation reopen, recovery, credential retry, denied blocking retries, local lock registration, and lost request preservation.

`nfs4close_one()` handles normal, delmap, force, resend, and after-resend close paths. It decrements open/mmap counters, performs `OPEN_DOWNGRADE` when references remain, skips OTW close for delegation-only or failed-reopen streams, sends final `CLOSE` when needed, and cleans up state references.

## State and Synchronization

- Rnode VM state uses `r_statelock`, `r_count`, `r_cv`, `r_flags`, `r_size`, `r_nextr`, `r_error`, `r_commit`, `r_mapcnt`, `r_inmap`, and `r_indelmap`.
- Commit state uses `R4COMMIT`, `R4COMMITWAIT`, `r_commit.c_cv`, `c_pages`, `c_commbase`, `c_commlen`, and page `p_fsdata` values `C_NOCOMMIT`, `C_DELAYCOMMIT`, and `C_COMMIT`.
- mmap/lock exclusion uses `r_lkserlock`, `r_rwlock`, `VNOCACHE`, remote-lock checks, mandatory-lock checks, and lost-lock conflict checks.
- NFSv4 open state uses open owners/streams, `os_sync_lock`, `os_open_ref_count`, `os_mapcnt`, `os_mmap_read`, `os_mmap_write`, `os_valid`, `os_force_close`, and `os_failed_reopen`.
- Lock state uses local `reclock()` with `LM_SYSID_CLIENT`, lock-owner seqids/stateids, `lo_pending_rqsts`, lost-request queues, and recovery synchronization.

## Dependencies

This chunk depends on illumos vnode, VM, page, segment, address-space callback, DNLC, lock manager, credential, signal, and zone APIs. It also depends on NFSv4 compound RPC operations including `OP_CPUTFH`, `OP_COMMIT`, `OP_OPEN_CONFIRM`, `OP_LOCK`, `OP_LOCKU`, `OP_LOCKT`, `OP_CLOSE`, and `OP_OPEN_DOWNGRADE`, plus recovery, delegation, ACL, and state-owner helpers elsewhere in the NFSv4 client.

## Risks and Edge Cases

- The `R4MODINPROGRESS`/`r_size` handshake prevents dirty-page write loss during extending writes.
- COMMIT must detect write-verifier changes and re-dirty/rewrite pages before acknowledging stability.
- `nfs4_delmap()` relies on callers interpreting `EAGAIN` as callback-driven retry, not ordinary failure.
- mmap and byte-range locks are conservative: mapped files only allow whole-file non-mandatory locks.
- Lost `LOCK`, `LOCKU`, and `CLOSE` requests treat timeout, `EINTR`, and forced unmount as possibly delivered server requests.
- `nfs4_create_getsecattr_return()` contains `if (!orig_mask & VSA_...)` expressions; precedence makes these `(!orig_mask) & ...`, which may not match the intended count-only cleanup checks.
- `nfs4close_one()` cleanup depends on many boolean ownership flags for locks, seqid syncs, stream refs, and start-fop state.

## Cross-Chunk References

- Earlier lines define vnode operation tables, `nfs4_getpage()`, `nfs4_putpages()`, `nfs4_bio()`, open/create/remove/rename paths, delegation helpers, and globals consumed here.
- `nfs4_getapage()` begins before this chunk; this chunk contains most of its body but not the signature setup.
- This chunk calls helpers defined elsewhere, including `nfs4_async_readahead()`, `nfs4_async_putapage()`, `nfs4_async_pageio()`, `nfs4_async_commit()`, `nfs4_rdwrlbn()`, `nfs4_flush_pages()`, `nfs4close_otw()`, and recovery/state-owner helpers.
- Recovery code in other files consumes lost-request records prepared here for `OP_LOCK`, `OP_LOCKU`, `OP_CLOSE`, and `OP_OPEN_DOWNGRADE`.