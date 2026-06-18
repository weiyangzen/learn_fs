# sources/distributed-fs/glusterfs/xlators/cluster/ec/src/ec-generic.c

## Purpose

`ec-generic.c` implements GlusterFS EC translator adapters for generic non-data-write FOPs: `flush`, `fsync`, `fsyncdir`, `lookup`, `statfs`, `xattrop`, `fxattrop`, and `ipc`. Each operation follows the EC framework pattern: validate and allocate an `ec_fop_data_t`, copy or reference request arguments, dispatch the request to selected child xlators with `STACK_WIND_COOKIE`, combine child callbacks into a quorum answer, rebuild EC-specific metadata where necessary, report to the upper callback, and unlock or finish.

This file is not the EC data encoder/decoder. It is the glue that makes normal filesystem operations work across EC bricks while preserving EC version/size metadata, lock discipline, and answer consistency.

## Important APIs, Functions, And Operation Groups

### Shared FOP Framework

All public entry points allocate request state with `ec_fop_data_allocate` from `ec-data.c`, passing a FOP id, target mask, minimum/flags, a wind function, a manager state-machine function, callback union, and user data. Request state holds copied `loc_t`, referenced `fd_t`, `dict_t`, callback data, and locks. On setup failure the public entry point invokes the caller callback immediately with `-1` and the local error; otherwise it calls `ec_manager(fop, error)`.

Callbacks allocate an `ec_cbk_data_t` with `ec_cbk_data_allocate`, fill the operation-specific result fields, reference dictionaries/inodes/fds as needed, call `ec_combine`, then call `ec_complete(fop)`.

Manager functions switch on `EC_STATE_*` values. Positive states handle normal progress, negative states handle error unwinding. Locking operations reuse the common sequence `LOCK -> DISPATCH -> DELAYED_START/PREPARE_ANSWER -> REPORT -> LOCK_REUSE -> UNLOCK -> END`.

### `flush`

- `ec_flush` validates the fd using `ec_validate_fd`, allocates `GF_FOP_FLUSH`, marks `use_fd`, references `fd` and `xdata`, and starts the manager.
- `ec_validate_fd` compares `fd_ctx->bad_version` against `inode_ctx->bad_version` under fd and inode locks. If the fd saw an older bad version than the inode, the operation fails with `EBADF`.
- `ec_manager_flush` prepares a full-range fd lock, flushes pending EC size/version metadata with `ec_flush_size_version`, dispatches to all selected children, prepares a simple answer, reports `fop->cbks.flush`, then reuses/unlocks.
- `ec_flush_cbk` combines op return/error and optional xdata.

### `fsync`

- `ec_fsync` mirrors `flush` but stores the `datasync` flag in `fop->int32`.
- `ec_combine_fsync` requires pre/post `iatt` answers to combine with `ec_iatt_combine`; mismatches are logged as notice and rejected for that answer set.
- `ec_manager_fsync` locks with `EC_QUERY_INFO`, flushes EC size/version, dispatches, prepares an answer, rebuilds two iatt structures with `ec_iatt_rebuild`, and replaces reported sizes with the authoritative inode size from `ec_get_inode_size`.
- Reports through `fop->cbks.fsync` with pre/post attributes.

### `fsyncdir`

- `ec_fsyncdir` stores `datasync`, references an fd and xdata, and uses a full-range fd lock.
- `ec_manager_fsyncdir` has the same metadata-flush and dispatch shape as `flush`, but calls the directory fsync child FOP and reports through `fop->cbks.fsyncdir`.
- It does not rebuild iatt data because the callback carries only xdata.

### `lookup`

- `ec_lookup` allocates `GF_FOP_LOOKUP` with `EC_FLAG_LOCK_SHARED`, copies the input `loc`, and copies xdata with `dict_copy_with_ref` so it can safely remove content keys and add EC metadata probes.
- `ec_manager_lookup` ensures request xdata exists, removes `GF_CONTENT_KEY` from caller xdata, and asks children for `EC_XATTR_SIZE`, `EC_XATTR_VERSION`, and `EC_XATTR_DIRTY`.
- `ec_lookup_cbk` references the returned inode, copies object and parent iatts, references xdata, extracts/removes dirty xattr data, and combines answers using `ec_combine_lookup`.
- `ec_lookup_rebuild` removes EC version from returned xdata, updates the loc/inode relationship with `ec_loc_update`, reads cached inode version/size from `ec_inode_t`, removes EC size from xdata for regular files, stores raw fragment size in `cbk->size`, and reports the cached full logical size when available.
- Lookup intentionally runs without an EC lock. If no answer met the usual minimum but callback data exists, the manager chooses the first callback as the next-best answer before `ec_fop_prepare_answer`.

### `statfs`

- `ec_statfs` allocates `GF_FOP_STATFS`, copies a loc, references xdata, dispatches to children, and combines `struct statvfs` with `ec_statvfs_combine`.
- `ec_manager_statfs` scales `f_blocks`, `f_bfree`, and `f_bavail` by `ec->fragments` unless xdata contains `"quota-deem-statfs"` set true. This maps per-fragment brick capacity to logical EC volume capacity while allowing quota code to opt out.
- Reports through `fop->cbks.statfs`.

### `xattrop` And `fxattrop`

- `ec_xattrop` handles loc-based xattrop and `ec_fxattrop` handles fd-based xattrop. Both store `gf_xattrop_flags_t` in `fop->xattrop_flags`, reference the xattr dict and xdata, and share `ec_manager_xattrop`.
- The wind functions call child `xattrop` or `fxattrop` with the stored flags and dictionary.
- `ec_xattrop_cbk` references the returned xattr dict, inspects `EC_XATTR_VERSION` for the self-heal bit, sets `fop->healing` for the child index under `fop->lock`, removes `EC_XATTR_DIRTY`, and records whether dirty bits were already set in the `ec_lock_link_t` stored in `fop->data`.
- `ec_combine_xattrop` requires dictionaries to compare equal with `ec_dict_compare`; the manager also calls `ec_dict_combine(cbk, EC_COMBINE_DICT)` before reporting.
- Lock preparation targets inode or fd with `EC_UPDATE_META` over the full range.

### `ipc`

- `ec_ipc` stores the integer operation in `fop->int32`, references xdata if present, dispatches to children, combines simple xdata callbacks, and reports through `fop->cbks.ipc`.
- It has no EC lock phase and ends after reporting.

## Control Flow

The dominant flow is:

1. Public FOP entry validates `this`, `frame`, and `this->private`; some fd operations call `ec_validate_fd`.
2. It allocates `ec_fop_data_t`, stores all request inputs by copy or reference, and starts `ec_manager`.
3. The manager prepares locks or request xdata, then calls `ec_dispatch_all`.
4. Each selected child receives a `STACK_WIND_COOKIE` with the child index as cookie.
5. Child callbacks allocate callback state, fill operation-specific fields, combine results, and mark the FOP complete.
6. The manager prepares the answer, rebuilds EC-specific metadata when necessary, calls the upper callback, and either ends or unlocks.

Error flow uses negative state values. Managers assert `fop->error != 0`, report `-1` with that error through the appropriate callback if present, then unwind lock reuse/unlock for locking operations. Unknown states log `EC_MSG_UNHANDLED_STATE` and end.

## State And Persistence Behavior

Most state is transient request state in `ec_fop_data_t` and callback state in `ec_cbk_data_t`. The file references and mutates several EC metadata channels:

- `ec_validate_fd` reads `ec_fd_t.bad_version` and `ec_inode_t.bad_version` under locks to reject stale/bad file descriptors.
- `flush`, `fsync`, and `fsyncdir` call `ec_flush_size_version`, which pushes pending EC size/version metadata before child dispatch.
- `lookup` requests EC xattrs, removes internal EC xattrs from returned dictionaries, and updates loc/inode context through `ec_loc_update`. For regular files it converts fragment-reported size to cached full logical size when inode context has it.
- `xattrop`/`fxattrop` operate directly on xattr dictionaries and track dirty/version/self-heal bits. The manager uses `EC_UPDATE_META` locks because these operations update EC metadata.
- `statfs` rewrites returned logical capacity values in memory before reporting.

Persistent effects happen indirectly through child FOPs and EC helper functions. This file itself persists no standalone data, but it is on the path for metadata writes and xattr updates that affect EC consistency and self-heal decisions.

## Dependencies And Integration Points

- Includes platform endian headers because `ec_xattrop_cbk` decodes big-endian EC version values with `be64toh`.
- Includes `ec.h`, `ec-messages.h`, `ec-helpers.h`, `ec-common.h`, `ec-combine.h`, and `ec-fops.h`.
- Public functions are declared in `ec-fops.h` and invoked from the translator FOP table in `ec.c` through default callbacks.
- Depends on EC core helpers: `ec_manager`, `ec_dispatch_all`, `ec_complete`, `ec_combine`, `ec_fop_prepare_answer`, `ec_lock_prepare_fd`, `ec_lock_prepare_inode`, `ec_lock`, `ec_unlock`, `ec_lock_reuse`, `ec_iatt_combine`, `ec_iatt_rebuild`, `ec_dict_*`, `ec_get_inode_size`, `ec_loc_update`, and `ec_flush_size_version`.
- Integrates with Gluster core types and lifetimes: `call_frame_t`, `xlator_t`, `fd_t`, `inode_t`, `loc_t`, `dict_t`, `struct iatt`, `struct statvfs`, `STACK_WIND_COOKIE`, `dict_ref`, `dict_unref`, `fd_ref`, and `inode_ref`.
- Uses message IDs such as `EC_MSG_DICT_REF_FAIL`, `EC_MSG_FD_BAD`, `EC_MSG_IATT_MISMATCH`, `EC_MSG_LOOKUP_REQ_PREP_FAIL`, and `EC_MSG_UNHANDLED_STATE` for structured logging.

## Risks And Edge Cases

- Several failure paths allocate `fop` and then `goto out` after partial setup. Correct cleanup depends on `ec_manager(fop, error)` and common fop destruction handling; regressions in manager cleanup would leak referenced fd/dict/loc state.
- `ec_ipc` and `ec_ipc_cbk` reference xdata without checking `dict_ref` failure, unlike most other FOPs. If `dict_ref` can fail in practice, this path may report with missing xdata rather than a local ENOMEM.
- `ec_xattrop_cbk` uses `dict_ref(xattr)` when `op_ret >= 0` without checking `xattr` for NULL. It assumes successful child xattrop returns a dictionary.
- Lookup runs unlocked and has explicit tolerance for mixed-generation answers. This is necessary for concurrency, but risks reporting a best-effort answer when children disagree below normal minimums.
- `statfs` capacity multiplication by `ec->fragments` can overflow fields in `struct statvfs` if child values are already near their maximum.
- The xattrop self-heal bit test depends on xattr length being at least one `uint64_t`; the code reads `version[0]` only, so malformed but sufficiently long dictionaries influence `fop->healing`.
- All manager default cases end the FOP after logging. Missing a new state in one manager can fail an operation rather than falling through safely.
- The fd bad-version check uses two separate locks for fd and inode contexts. It compares stable snapshots but does not hold both locks simultaneously, so callers rely on monotonic bad_version semantics.

## Test Signals

High-value tests include:

- Unit or translator tests for stale fd rejection: when inode `bad_version` exceeds fd `bad_version`, `flush` and `fsync` return `EBADF` without dispatching.
- Flush/fsync/fsyncdir tests confirming `ec_flush_size_version` is called before child dispatch and that lock/unlock happens on both success and error states.
- Fsync tests with mismatching iatts across children to verify answer rejection/logging, and successful iatt rebuild to full logical size.
- Lookup tests verifying request xdata asks for EC size/version/dirty, strips `GF_CONTENT_KEY`, removes internal EC xattrs from responses, updates inode/loc context, and reports full file size for regular files when cached.
- Statfs tests for both default scaling by `ec->fragments` and quota `"quota-deem-statfs"` opt-out behavior.
- Xattrop/fxattrop tests covering dictionary mismatch, dirty bit extraction, self-heal bit detection, loc and fd variants, and metadata lock selection.
- Error-injection tests for `dict_ref`, `dict_new`, `dict_set_uint64`, `fd_ref`, `inode_ref`, and `loc_copy` failures so immediate callback error reporting and cleanup are verified.
