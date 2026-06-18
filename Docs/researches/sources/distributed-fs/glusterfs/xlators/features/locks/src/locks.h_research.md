# sources/distributed-fs/glusterfs/xlators/features/locks/src/locks.h

## Purpose

`locks.h` is the primary data-model header for the Gluster posix-locks translator. It defines mandatory-locking modes, byte-range lock records, inode-lock records, entry-lock records, per-domain containers, per-inode aggregate state, metalock state, translator-private configuration, per-call local state, fd and client contexts, and public cleanup/context APIs.

## Important APIs, types, and functions

- `mlk_mode_t` enumerates mandatory-locking policy: none, file-based, forced, and optimal.
- `posix_lock_t` represents fcntl byte-range locks with range, type, flags, user flock, fd identity, saved frame, blocked/granted timestamps, client identity, migrated `client_uid`, lk-owner, pid, and blocking flag.
- `pl_inode_lock_t` represents domain-scoped inodelks with granted/blocked/contend list links, refcount, range/type, domain, user flock, owning `pl_inode_t`, frame, timing, contention time, owner identity, connection id, client-list link, and grant retry status.
- `pl_entry_lock_t` represents directory-entry locks with domain/blocked/contend/client links, refcount, frame/xlator, parent `pl_inode_t`, domain, basename, timing, contention time, owner identity, connection id, and entry lock type.
- `pl_dom_list_t` groups entry and inode locks by domain and links back to a `pl_inode_t`.
- `pl_inode_t` aggregates all lock state for an inode: mutex, domain list, byte-range list, blocked I/O, reserve locks, metalocks, queued locks, removal waiters, mandatory-lock flags, inode refs, GFID, migration marker, fop wind count tracking, and remove-operation gating.
- `pl_meta_lock_t` models metadata locks associated with both an inode and client context.
- `posix_locks_private_t` stores xlator configuration such as brick name, revocation thresholds, contention notification delay, mandatory mode, tracing, monkey unlocking, revocation scope, contention notification enablement, and default mlock enforcement.
- `pl_local_t`, `pl_fdctx_t`, `pl_ctx_t`, and `multi_dom_lk_data` provide per-call, per-fd, per-client, and multi-domain helper state.
- `pl_ctx_get()`, `pl_inodelk_client_cleanup()`, and `pl_entrylk_client_cleanup()` are the exposed context/cleanup APIs.

## Control flow

The header does not execute logic, but its list topology defines the translator's control flow. Requests become lock objects that move between granted and blocked lists on `pl_inode_t` or `pl_dom_list_t`. Blocking operations retain `call_frame_t *frame` until a grant or cleanup path unwinds. Client cleanup walks `pl_ctx_t` lists, while per-inode logic walks `pl_inode_t` and per-domain lists. Removal gating uses `remove_running`, `is_locked`, and `waiting` to pause compatible inodelk attempts until file removal sequencing is safe.

## State and persistence behavior

All structures are in-memory. Some fields mirror persistent or externally recoverable state: `pl_inode_t::gfid` identifies the inode, `mlock_enforced` can be backed by a disk xattr, and `posix_lock_t::client_uid` is designed to survive lock migration better than a raw `client_t *`. Timestamps support statedumps, debugging, revocation, and contention notification throttling. Refcount fields on entry/inode locks and inode references on `pl_inode_t` protect objects across asynchronous blocked-lock unwinds and disconnect cleanup.

## Dependencies and integration points

The header includes Gluster errno/stub support and `locks-mem-types.h`. It relies on core Gluster types for lists, inodes, fds, frames, locs, dicts, xlators, flocks, lock owners, clients, UUIDs, and booleans. All lock implementation files depend on these structure definitions, and other xlator code can call the public cleanup functions during client disconnect.

## Risks and edge cases

- Many structs contain multiple independent list heads; a lock object's state is encoded by list membership, which is powerful but easy to corrupt.
- Raw pointers to clients, frames, inodes, fd objects, and strings require strict lifetime rules outside the header.
- `const char *domain/volume` fields usually point to domain-owned strings, so freeing or replacing a domain string would invalidate locks.
- `pl_inode_t` combines several lock families in one mutex, reducing races but increasing contention and making lock-order discipline important with `pl_ctx_t::lock`.
- `posix_lock_t::client_uid` exists because raw client identity can change during rebalance; any migration path that misses this field can break cleanup.

## Test signals

ABI/build tests should catch structure/prototype drift. Behavioral tests should stress list membership transitions, client disconnect cleanup, migration cleanup by `client_uid`, mandatory-lock flags, metalock queueing, remove waiters, and high-concurrency lock/unlock paths to expose refcount or lock-order issues.
