# sources/distributed-fs/glusterfs/xlators/features/quota/src/quota.h

## Purpose
`quota.h` is the shared interface and state definition header for the quota xlator, quota enforcer client, and quotad aggregator. It defines quota-specific keys/macros, inode/local/private state structs, callback types, and the cross-file functions used to validate, check, log, and initialize quota enforcement.

## Important APIs and Types
- Macros: `DIRTY`, `SIZE`, `CONTRIBUTION`, `VAL_LENGTH`, `READDIR_BUF`, `WIND_IF_QUOTAOFF`, `QUOTA_WIND_FOR_INTERNAL_FOP`, `DID_REACH_LIMIT`, safe lock increment/decrement helpers, allocation/unwind helpers, and quota xattr key builders.
- `quota_dentry_t` stores a parent GFID and basename for a file/link path.
- `quota_inode_ctx_t` caches size limits, object limits, file/dir counts, `iatt`, parent dentry list, validation/log timestamps, ancestry state, and lock.
- `quota_local_t` carries per-FOP state: locs, deltas, object delta, pending stub, async link count, validation callback/xdata, ancestry callback, common ancestor, result status, and parent frame linkage.
- `quota_priv_t` carries translator options, RPC program/client/service references, inode table, volume UUID, connection status primitives, and validation count.
- Function declarations expose `quota_enforcer_lookup/init()`, `quota_log_usage()`, `quota_build_ancestry()`, `quota_get_limit_dir()`, `quota_check_limit()`, `do_quota_check_limit()`, `quota_fill_inodectx()`, and size/object limit helpers.

## Control Flow
This header does not execute code directly, but its macros shape control flow throughout `quota.c`: quota-off tail-winds, internal-FOP bypass, strict unwind cleanup, tail-wind cleanup, and allocation failure jumps. Its callback typedefs allow asynchronous ancestry and validation code to resume original FOP stubs.

## State and Persistence
The structs define runtime state only. Persistent quota data is referenced through xattr key macros and lower-layer dictionaries, while this header describes the in-memory cache and request-local mirrors of that data.

## Dependencies and Integration Points
It includes GlusterFS call-stub, compatibility, logging, dict, event, RPC client, glusterfs3 protocol, quota-common-utils, and quota messages headers. It is included by all quota and quotad implementation files, so structure changes have broad ABI and compile impact inside this translator.

## Risks
- `quota_local_t` ownership is subtle because frames, copied frames, parent frames, and stubs share/check state via `par_frame` and `link_count`.
- Macros hide cleanup and stack unwinding behavior; misuse can leak locals or unwind with stale frame state.
- New fields in `quota_inode_ctx_t` require lock discipline and `quota_forget()` cleanup updates.

## Test Signals
Build coverage catches declaration drift. Runtime tests should stress frame-local cleanup on all failure labels, inode context creation/deletion, multi-parent hardlink paths, and reconfigure/fini paths that touch `quota_priv_t`.
