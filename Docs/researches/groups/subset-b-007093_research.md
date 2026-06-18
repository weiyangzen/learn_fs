# Research: subset-b-007093

Grouped research for GlusterFS posix-locks files under `sources/distributed-fs/glusterfs/xlators/features/locks/src`. Each section is wrapped for reconciliation into the source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/locks/src/common.c -->
# sources/distributed-fs/glusterfs/xlators/features/locks/src/common.c

## Purpose

`common.c` implements the shared mechanics behind the locks translator: per-inode lock state creation, byte-range POSIX lock insertion/merging, blocked-lock granting, lock tracing, mandatory-lock enforcement lookup, client/request local cleanup, and coordination between inode-removal operations and inodelks. It is the core state machine for fcntl-style locks and a utility layer consumed by `entrylk.c`, `inodelk.c`, and the rest of the posix-locks xlator.

## Important APIs, types, and functions

- `get_domain()` returns or creates a `pl_dom_list_t` within a `pl_inode_t`; domains partition entrylk and inodelk lists by volume/domain name.
- `pl_inode_get()` attaches a `pl_inode_t` to an inode context, initializes all lock lists, mutex/condition state, GFID, and mandatory-lock flags, and optionally fetches mandatory-lock xattr state.
- `new_posix_lock()`, `__delete_lock()`, `__destroy_lock()`, `posix_lock_to_flock()`, `locks_overlap()`, and `same_owner()` are the basic byte-range lock lifecycle and comparison helpers.
- `pl_setlk()` is the main byte-range set/unlock path. It checks client connectivity, handles pre-lock unlocks for blocking upgrades/downgrades, grants or blocks the request, queues when metalock is active, then wakes blocked locks and blocked I/O.
- `pl_getlk()` returns the first conflicting granted byte-range lock, or rewrites the request to `F_UNLCK` when none exists.
- `grant_blocked_locks()` and `__grant_blocked_locks()` scan blocked byte-range locks, re-check grantability, merge granted locks into `ext_list`, and unwind the saved frames outside the inode mutex.
- `pl_lock_preempt()` forcefully removes conflicting byte-range locks and blocked I/O for a requesting owner, unwinding displaced operations with `EBUSY`.
- `pl_is_mandatory_locking_enabled()`, `pl_fetch_mlock_info_from_disk()`, and `pl_update_refkeeper()` bridge in-memory lock state to mandatory-lock policy and inode lifetime management.
- `pl_inode_remove_prepare()`, `pl_inode_remove_complete()`, `pl_inode_remove_cbk()`, `pl_inode_remove_unlocked()`, and `pl_inode_remove_inodelk()` coordinate unlink/rmdir/rename-style removal with outstanding inodelks.

## Control flow

The byte-range lock path begins with `new_posix_lock()` copying the requested `gf_flock`, client, fd, lk-owner, and flags into a heap object. `pl_setlk()` then takes `pl_inode->mutex`, rejects disconnected clients for blocking non-unlock requests, optionally sends a synthetic pre-lock unlock when a blocking lock conflicts, and calls `__is_lock_grantable()`. Grantable locks are inserted through `__insert_and_merge()`, which recursively merges same-owner same-type ranges or subtracts same-owner different-type/unlock ranges. Non-grantable blocking requests are marked `blocked`, left on `ext_list`, and unwound only when later granted. Nonblocking conflicts return would-block.

Blocked lock handling is split deliberately: while holding `pl_inode->mutex`, `__grant_blocked_locks()` moves candidate blocked locks to a temporary list and reinserts grantable ones; after unlocking, `grant_blocked_locks()` unwinds saved call frames. This avoids stack unwinds and callbacks while holding the inode lock. `pl_send_prelock_unlock()` follows the same pattern after injecting an `F_UNLCK` lock.

The remove coordination path resolves an inode from a `loc_t`, records `pl_inode->inode`, checks all inodelk domains for owners from other clients, and either marks the inode locked for removal or queues a stub in `pl_inode->waiting`. Completion decrements `remove_running`, clears `is_locked` when appropriate, grants blocked inodelks, sends contention notifications, and releases inode refs.

## State and persistence behavior

The durable state is mostly external to this file: lock state is in memory on `pl_inode_t` and domain lists; mandatory-lock enforcement can be recovered from disk via `GF_ENFORCE_MANDATORY_LOCK` xattr. `pl_inode_get()` sets `check_mlock_info` so the xattr is fetched lazily when mandatory locking is active and a `pl_local_t` with fd/loc is available. `refkeeper` holds an inode ref while byte-range locks exist, preventing pruning. Lists on `pl_inode_t` include `ext_list` for byte-range locks, `dom_list` for per-domain entry/inode locks, `rw_list` for blocked I/O, `metalk_list` and `queued_locks` for metalock behavior, and `waiting` for removal stubs.

Timing fields (`blkd_time`, `granted_time`) are assigned at insertion for dump/debug behavior. The code relies on list membership to encode lock state: granted byte-range locks have `blocked == 0` on `ext_list`; blocked byte-range locks have `blocked == 1` on the same list.

## Dependencies and integration points

This file depends on Gluster core objects (`xlator_t`, `inode_t`, `fd_t`, `call_frame_t`, `loc_t`, `dict_t`, `client_t`), list helpers, memory accounting, inode context APIs, logging/tracing APIs, syncop xattr APIs, and lk-owner helpers. It calls into other lock modules via declarations such as `do_blocked_rw()`, `pl_metalock_is_active()`, `__pl_queue_lock()`, `__grant_blocked_inode_locks()`, `unwind_granted_inodes()`, and contention notification helpers. `PL_STACK_UNWIND_AND_FREE` from `common.h` is used to unwind lock calls while cleaning `pl_local_t`.

## Risks and edge cases

- Lock splitting and merging in `__insert_and_merge()` assumes `subtract_locks()` receives contained ranges; unexpected geometry asserts and logs an error.
- The file stores fd identity as a cast integer (`fd_to_fdnum()`), so correctness depends on not treating it as a durable descriptor value.
- `pl_setlk()` unlocks `pl_inode->mutex` early in the disconnected-client branch, making lock/unlock structure fragile if future edits add cleanup before `out`.
- Mandatory-lock xattr fetch is synchronous and uses negative `op_ret` as errno-like data; incorrect syncop return handling would affect enforcement decisions.
- Remove coordination keeps `pl_inode->mutex` locked across a `-1` return from `pl_inode_remove_prepare()` by contract, so callers must always complete via `pl_inode_remove_complete()`.
- Recursive lock merging is concise but difficult to audit for all overlapping same-owner transitions, especially with `F_UNLCK` cleanup.

## Test signals

Useful tests include same-owner range merge/split/unlock cases, conflicting owner read/write matrices, blocking `F_SETLKW` grant after unlock, metalock queue behavior, disconnected-client blocking lock rejection, mandatory-lock xattr recovery with fd and loc paths, inode refkeeper transitions when lock lists become empty/non-empty, and remove-vs-inodelk sequencing where removal waits on external owners but same-client/internal locks proceed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/locks/src/common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/locks/src/common.h -->
# sources/distributed-fs/glusterfs/xlators/features/locks/src/common.h

## Purpose

`common.h` exposes the shared interface for the posix-locks translator. It defines lock dump format strings, the common unwind-and-cleanup macro, byte-range lock return codes, and prototypes for byte-range locking, inode/entry domain locking, tracing, mandatory-lock helpers, reserve-lock helpers, and inode-removal coordination.

## Important APIs, types, and functions

- Dump format macros (`RANGE_FMT`, `ENTRY_FMT`, `DUMP_*`, `ENTRY_*`, `RANGE_*`) standardize statedump/log rendering for granted and blocked locks.
- `PL_STACK_UNWIND_AND_FREE()` unwinds a strict fop and then releases all resources held by `pl_local_t`, including inodelk domain-count data, two locs, fd, inode, xdata, and the local object.
- `enum { PL_LOCK_GRANTED, PL_LOCK_WOULD_BLOCK, PL_LOCK_QUEUED }` describes `pl_setlk()` results.
- Prototypes expose byte-range lock lifecycle (`new_posix_lock`, `pl_getlk`, `pl_setlk`, `pl_lock_preempt`, `grant_blocked_locks`, `posix_lock_to_flock`, `locks_overlap`, `same_owner`, `__delete_lock`, `__destroy_lock`).
- Domain and inode helpers (`get_domain`, `pl_inode_get`, `pl_update_refkeeper`) are shared by entrylk, inodelk, and other lock families.
- Inodelk/entrylk grant, cleanup, count, and contention APIs are declared for cross-file use.
- Tracing helpers (`pl_trace_*`, `entrylk_trace_*`, `pl_print_*`) centralize request/response/block logging.
- Mandatory and removal helpers (`pl_is_mandatory_locking_enabled`, `pl_inode_remove_*`) define the cross-module removal protocol.

## Control flow

The header itself has no runtime control flow, but it defines cleanup control through `PL_STACK_UNWIND_AND_FREE()`: callers must detach `frame->local`, unwind, then release every referenced member. The prototypes reveal the module boundaries: common byte-range code calls out to inodelk/entrylk grant functions, while inodelk/entrylk call back into common for domains, tracing, owner validation, local cleanup, and removal synchronization.

## State and persistence behavior

The macro encodes ownership transfer of `pl_local_t` fields after a fop unwinds. It clears pointers after unref/wipe to avoid accidental reuse during cleanup. No persistent state is declared here, but APIs include mandatory-lock enforcement and count functions that observe in-memory `pl_inode_t` state and xattr-backed policy.

## Dependencies and integration points

This header depends on lock types from `locks.h`, Gluster fop stack APIs, loc/fd/inode/dict reference APIs, and lk-owner/flock types. It is included by core implementation files such as `common.c`, `entrylk.c`, and `inodelk.c`, making it the contract layer for lock operations across the xlator.

## Risks and edge cases

- `PL_STACK_UNWIND_AND_FREE()` is a large macro with side effects and assumes `frame` and local fields are valid in a narrow ownership context.
- Several double declarations appear (`__pl_inodelk_unref` is listed twice), which is harmless in C but signals interface sprawl.
- Functions with `__` prefixes are exposed across files, so internal locking assumptions are not enforced by the type system.
- Dump format macros require caller-supplied arguments to match exactly; mismatches would be compile-time warnings only when format checking sees through macro expansion.

## Test signals

Compilation with strict warnings is important for prototype drift and format mismatches. Runtime tests should exercise `PL_STACK_UNWIND_AND_FREE()` paths for successful, failed, and blocked lock unwinds to detect leaked loc/fd/inode/dict references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/locks/src/common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/locks/src/entrylk.c -->
# sources/distributed-fs/glusterfs/xlators/features/locks/src/entrylk.c

## Purpose

`entrylk.c` implements Gluster entry locks: locks on names inside a directory, including a `NULL` basename that represents the whole directory. It handles granted and blocked entry locks per domain, starvation avoidance, stale-lock revocation, contention upcalls, client cleanup, and the `entrylk`/`fentrylk` xlator entry points.

## Important APIs, types, and functions

- `new_entrylk_lock()` creates a `pl_entry_lock_t` from a frame, basename, type, domain, and optional connection id.
- `names_conflict()`, `names_equal()`, `__same_entrylk_owner()`, and `__conflicting_entrylks()` define entry lock compatibility. A `NULL` basename conflicts with every name; same `(client, lk_owner)` is allowed to conflict.
- `__entrylk_prune_stale()` revokes stale or overly blocked entry locks using `clrlk_clear_entrylk()`.
- `entrylk_contention_notify_check()` and `entrylk_contention_notify()` throttle and emit `GF_UPCALL_ENTRYLK_CONTENTION` notifications.
- `__lock_entrylk()` grants or blocks a request and includes starvation prevention by respecting already-blocked conflicting locks unless the owner already has a lock.
- `__unlock_entrylk()` removes the matching granted lock.
- `grant_blocked_entry_locks()` and `__grant_blocked_entry_locks()` retry blocked entry locks and unwind newly granted frames.
- `pl_common_entrylk()` is the common entry point for both path-based `pl_entrylk()` and fd-based `pl_fentrylk()`.
- `pl_entrylk_client_cleanup()` releases all entry locks associated with a disconnected client context.
- `get_entrylk_count()` and `__get_entrylk_count()` count granted plus blocked entry locks.

## Control flow

`pl_entrylk()` and `pl_fentrylk()` both call `pl_common_entrylk()` with either `loc->inode` or `fd->inode`. The common path extracts `"connection-id"` from xdata, gets the `pl_inode_t`, gets or creates the domain, traces the request, allocates a request lock, and takes an early inode ref to keep `pinode` alive across concurrent disconnect cleanup.

For `ENTRYLK_LOCK` and `ENTRYLK_LOCK_NB`, the code locks the client context and inode, calls `__lock_entrylk()`, records successful or blocking lock ownership in `ctx->entrylk_lockers`, and either unwinds immediately or leaves the frame saved on a blocked lock. For `ENTRYLK_UNLOCK`, it removes the matching lock, drops client-list membership and references, releases the extra inode ref, then tries to grant blocked locks.

`__lock_entrylk()` first rejects conflicts with granted locks. If no granted conflict exists, it still blocks behind conflicting already-blocked locks to avoid starvation, except when the same owner already has a lock and needs nested progress. Granted locks receive an additional ref and are added to `dom->entrylk_list`; blocked locks are queued on `dom->blocked_entrylks`.

Client cleanup walks `ctx->entrylk_lockers`, separates granted locks from blocked-only locks, unwinds blocked frames with `EAGAIN`, grants newly unblocked waiters, unreferences lock objects, and releases inode refs.

## State and persistence behavior

Entry lock state is in-memory only and lives in `pl_dom_list_t` lists: `entrylk_list` for granted locks and `blocked_entrylks` for blocked requests. Each lock also has `client_list` membership in the owning `pl_ctx_t`, refcounting, optional `connection_id`, timing fields, and `contention_time`. `pinode->inode` is held while granted or blocking state needs to survive client cleanup races. Stale-lock revocation does not persist state; it clears in-memory locks through the clear-lock path and logs counts.

## Dependencies and integration points

The file depends on `locks.h` structures, `common.h` domain/tracing/owner helpers, `clear.h` clear-lock APIs, Gluster list/logging/upcall utilities, client contexts from `pl_ctx_get()`, and xlator stack unwind APIs. It emits `GF_UPCALL_ENTRYLK_CONTENTION` through `this->notify`. It uses `pl_does_monkey_want_stuck_lock()` for optional test/fault behavior configured in private state.

## Risks and edge cases

- `__blocked_entrylk_conflict()` returns the requested `lock` instead of the conflicting blocked lock; callers only test non-NULL, so behavior is fine but the API is misleading.
- Correctness relies on lock objects being on up to three lists (`domain_list`, `blocked_locks`, `client_list`) with refcounts matching each state transition.
- `NULL` basename means whole-directory lock, so trace and log paths must tolerate null strings.
- Client cleanup handles races where a lock is both granted and still on a granted-list handoff via `blocked_locks`; this is subtle and easy to break.
- Starvation prevention intentionally blocks otherwise grantable locks, which can surprise tests that only model granted-lock conflicts.

## Test signals

Tests should cover exact-name locks, whole-directory `NULL` locks, same-owner nested locks, nonblocking conflict returning `EAGAIN`, blocking conflict later granted on unlock, cleanup of granted and blocked locks during disconnect, contention upcall throttling, stale revocation by age and max-blocked threshold, and `check_entrylk_on_basename()` behavior across domains.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/locks/src/entrylk.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/locks/src/inodelk.c -->
# sources/distributed-fs/glusterfs/xlators/features/locks/src/inodelk.c

## Purpose

`inodelk.c` implements Gluster inode locks: domain-scoped byte-range locks on an inode used by internal/distributed operations rather than ordinary POSIX fcntl locking. It handles conflict detection, blocking, starvation avoidance, stale-lock revocation, contention upcalls, synchronization with inode removal, client cleanup, and the `inodelk`/`finodelk` xlator entry points.

## Important APIs, types, and functions

- `new_inode_lock()` creates `pl_inode_lock_t` requests from a `gf_flock`, frame/client identity, domain, and optional connection id.
- `inodelk_overlap()`, `inodelk_type_conflict()`, `same_inodelk_owner()`, `inodelk_conflict()`, and `inodelks_equal()` define compatibility and unlock matching.
- `__inodelk_prune_stale()` revokes stale or over-blocked locks through `clrlk_clear_inodelk()`.
- `inodelk_contention_notify_check()` and `inodelk_contention_notify()` throttle and send `GF_UPCALL_INODELK_CONTENTION`.
- `__lock_inodelk()` checks removal gating via `pl_inode_remove_inodelk()`, granted-lock conflicts, blocked-lock starvation, and finally inserts into granted or blocked lists.
- `__inode_unlock_lock()` removes an exactly matching same-owner granted inodelk.
- `__grant_blocked_inode_locks()`, `grant_blocked_inode_locks()`, and `unwind_granted_inodes()` retry blocked locks and unwind saved frames.
- `pl_inode_setlk()` is the core set/unlock routine for inodelks.
- `pl_common_inodelk()` validates input, performs special domain conversion for metadata ranges, allocates the request, dispatches `F_SETLK`/`F_SETLKW`, and unwinds.
- `pl_inodelk_client_cleanup()` releases all inodelks associated with a client context.
- `get_inodelk_count()` and `__get_inodelk_count()` count granted and blocked locks, optionally by domain.

## Control flow

`pl_inodelk()` and `pl_finodelk()` pass path-based or fd-based inodes into `pl_common_inodelk()`. The common path validates the frame/inode/flock, rejects negative ranges, maps the special metadata range to a `:metadata` domain when needed, traces the request, obtains the client context and `pl_inode_t`, creates the domain, and allocates a request lock.

Only `F_SETLK` and `F_SETLKW` are supported; `F_GETLK` returns `ENOTSUP`. `F_SETLKW` sets `can_block`. `pl_inode_setlk()` takes an early inode ref, optionally prunes stale locks or performs monkey unlock behavior, prepares contention notification state, and locks the client context plus inode. Non-unlock requests go through `__lock_inodelk()` and are either granted, blocked, or failed. Unlock requests require exact same range and owner, remove the granted lock, wake remove waiters, and then grant blocked inodelks after dropping the mutex.

Blocked-grant flow splices the domain's blocked list to a local list under lock, retries each request through `__lock_inodelk()`, and puts requests that are no longer `-EAGAIN` on a granted handoff list. `unwind_granted_inodes()` performs stack unwinds outside the initial grant loop and then unreferences the lock objects under the inode mutex.

## State and persistence behavior

Inodelk state is in-memory per `pl_dom_list_t`: `inodelk_list` for granted locks and `blocked_inodelks` for blocked locks. Each lock also records range, type, owner, client, pid, domain, user flock, saved frame, connection id, client-list membership, refcount, timing fields, contention timestamp, and retry status. The file does not persist lock state; it integrates with clear-lock code for revocation and with `pl_inode_remove_*` state from `common.c` to gate regular-operation locks while remove operations are active.

The special range `(l_start == LLONG_MAX - 1 && l_len == 0)` changes the lock domain to `volume:metadata`, keeping metadata locks distinct without changing the range representation.

## Dependencies and integration points

The file uses Gluster core types, list/logging/upcall utilities, `clear.h`, `common.h`, and `locks.h`. It works with `pl_ctx_t` client cleanup lists, `pl_inode_remove_inodelk()` and `pl_inode_remove_wake()` from `common.c`, and `this->notify()` for contention upcalls. It shares tracing with byte-range locks via `pl_trace_in/out/block()` and `pl_print_inodelk()`.

## Risks and edge cases

- Inodelk unlock requires exact range equality, unlike POSIX byte-range partial unlock semantics; callers must know this contract.
- `pl_inode_setlk()` has intricate refcount decisions around blocking, nonblocking failure, unlock, and client-list insertion.
- Removal gating depends on client pid conventions: negative pid internal locks bypass synchronization.
- Starvation avoidance can block otherwise grantable locks when a conflicting blocked lock exists, except for owners already holding locks.
- Domain string conversion allocates a new `:metadata` string for special ranges; leaks or double-frees would affect uncommon metadata-lock paths.
- The local `res1` variable in `pl_common_inodelk()` is freed but never assigned in the observed code, suggesting leftover interface churn.

## Test signals

Tests should exercise read/read sharing, write conflicts, same-owner overlap, exact unlock matching, nonblocking and blocking conflict results, grant-after-unlock, blocked-lock starvation ordering, special metadata domain conversion, remove-operation gating and wakeups, client cleanup of granted and blocked locks, stale revocation thresholds, max-blocked revocation, contention upcall throttling, and unsupported `F_GETLK`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/locks/src/inodelk.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/locks/src/locks-mem-types.h -->
# sources/distributed-fs/glusterfs/xlators/features/locks/src/locks-mem-types.h

## Purpose

`locks-mem-types.h` defines the memory-accounting type identifiers used by the posix-locks translator when allocating its private structures through Gluster's `GF_MALLOC`/`GF_CALLOC` wrappers.

## Important APIs, types, and functions

The only exported type is `enum gf_locks_mem_types_`, starting at `gf_common_mt_end + 1` and assigning identifiers for:

- `pl_dom_list_t`
- `pl_inode_t`
- `posix_lock_t`
- `pl_entry_lock_t`
- `pl_inode_lock_t`
- `pl_rw_req_t`
- `posix_locks_private_t`
- `pl_fdctx_t`
- `pl_meta_lock_t`
- `gf_locks_mt_end`

## Control flow

There is no runtime control flow. The enum values are consumed by allocation calls throughout the lock translator to classify memory usage.

## State and persistence behavior

The file contributes no runtime state and no persistence. It affects diagnostics, memory accounting, and leak attribution for lock-related allocations.

## Dependencies and integration points

It includes `<glusterfs/mem-types.h>` for `gf_common_mt_end` and is included by `locks.h`, which makes these identifiers available to all lock implementation files. Adding a new allocated lock structure should add a corresponding enum value before `gf_locks_mt_end`.

## Risks and edge cases

Enum ordering matters for Gluster memory accounting. Reordering existing values can make diagnostics harder to compare across versions; new values should be appended before the end marker. The guard name is generic enough for this module but must remain consistent with `locks.h`.

## Test signals

Build tests catch missing enum names when allocation sites use them. Runtime memory-accounting or leak tests should show allocations under the expected posix-locks categories.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/locks/src/locks-mem-types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/locks/src/locks.h -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/locks/src/locks.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/locks/src/pl-messages.h -->
# sources/distributed-fs/glusterfs/xlators/features/locks/src/pl-messages.h

## Purpose

`pl-messages.h` defines component message identifiers for the posix-locks translator. These IDs are used with Gluster's structured logging/message-id system and must remain stable over time.

## Important APIs, types, and functions

The file includes `<glusterfs/glfs-message-id.h>` and invokes:

`GLFS_MSGID(PL, PL_MSG_LOCK_NUMBER, PL_MSG_INODELK_CONTENTION_FAILED, PL_MSG_ENTRYLK_CONTENTION_FAILED);`

This declares the PL component's message-id symbols for lock numbering and contention-notification failures.

## Control flow

There is no runtime control flow. The macro expands at compile time into message-id definitions consumed by logging call sites.

## State and persistence behavior

There is no runtime state. The stability of these identifiers is externally significant because logs, diagnostics, and downstream tooling may rely on message IDs remaining unique and non-reused.

## Dependencies and integration points

The header depends on Gluster's global message-id infrastructure and is included by `entrylk.c`; related inodelk/entrylk contention paths can use the declared IDs for structured messages. The comments define the maintenance contract: append new IDs, do not delete or reuse old ones, and ensure the component name matches `glfs-message-id.h`.

## Risks and edge cases

Removing or reordering IDs can cause log compatibility problems. Adding IDs under the wrong component name can collide with global message-id allocation. The current file only defines a small set, so future logging additions should append rather than repurpose.

## Test signals

Build tests catch undefined message IDs or component mismatches. Log/diagnostic tests can verify contention failure paths emit the intended PL message identifiers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/locks/src/pl-messages.h -->
