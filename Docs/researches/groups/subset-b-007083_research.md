# Research: subset-b-007083

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/cluster/ec/src/ec-galois.c -->
# sources/distributed-fs/glusterfs/xlators/cluster/ec/src/ec-galois.c

## Purpose

`ec-galois.c` implements the finite-field arithmetic support used by GlusterFS EC erasure coding. It builds a `GF(2^8)` context with logarithm and exponent tables, attaches the precomputed byte multiplication operation table from `ec-gf8.h`, and exposes basic field operations for matrix generation and code generation.

This file is deliberately narrow: it does not encode or decode data itself. Instead, it provides reusable field arithmetic to `ec-method.c` and code-building paths such as `ec-code.c` and generated C code helpers. The implementation currently accepts only `bits == 8`, which matches the shipped `ec_gf8_mul` table.

## Important APIs, Types, And Functions

- `ec_gf_prepare(uint32_t bits, uint32_t mod)` is the public constructor. It validates `bits`, defaults `mod` to `0x11d`, allocates the `ec_gf_t`, initializes `log` and `pow` tables, binds `gf->table` to `ec_gf8_mul`, and computes `min_ops`, `max_ops`, and `avg_ops` from the precomputed multiplication recipes.
- `ec_gf_destroy(ec_gf_t *gf)` releases `pow`, `log`, and the `ec_gf_t` allocation. It assumes a valid non-NULL pointer from `ec_gf_prepare`.
- `ec_gf_add(ec_gf_t *gf, uint32_t a, uint32_t b)` implements field addition as XOR. Inputs outside `[0, gf->size)` return `gf->size` as an error sentinel.
- `ec_gf_mul(ec_gf_t *gf, uint32_t a, uint32_t b)` multiplies nonzero operands by adding logarithms and indexing `pow`; zero operands return zero. Out-of-range inputs return the sentinel.
- `ec_gf_div(ec_gf_t *gf, uint32_t a, uint32_t b)` divides by subtracting logarithms via an offset into the duplicated exponent table. Division by zero and out-of-range inputs return the sentinel.
- `ec_gf_exp(ec_gf_t *gf, uint32_t a, uint32_t b)` computes exponentiation with square-and-multiply over `ec_gf_mul`. `0^0` and out-of-range bases return the sentinel.
- Internal helpers `ec_gf_alloc` and `ec_gf_init_tables` encapsulate allocation and table construction. They use Gluster memory APIs (`GF_MALLOC`, `GF_FREE`) and EC error-pointer macros (`EC_ERR`, `EC_IS_ERR`).

The backing type is `struct _ec_gf` in `ec-types.h`: it stores field parameters, operation count statistics, `log`, `pow`, and the `ec_gf_mul_t **table` used by code-generation paths.

## Control Flow

Construction is linear. `ec_gf_prepare` rejects unsupported widths, selects the GF(8) multiplication table, normalizes a zero modulus to `0x11d`, allocates the object and two arrays, calls `ec_gf_init_tables`, and then scans `tbl[i]->ops` until `EC_GF_OP_END` for each nonzero element to collect operation statistics.

`ec_gf_init_tables` seeds `pow[0] = 1`, marks `log[0] = gf->size` as a special non-field logarithm value, and iterates powers of the primitive element by left-shifting the previous power. When the shifted value exceeds the field size, it reduces by XORing the modulus. Each generated value is written twice into `pow`/`log` at the base index and at an offset of `gf->size - 1`, avoiding explicit modulo operations in multiplication/division.

The arithmetic functions are intentionally branch-light and table-driven. Add is XOR, multiply and divide handle zero first, and exponentiation delegates to multiply so input validation and field semantics remain centralized.

## State And Persistence Behavior

State is in-memory only. `ec_gf_prepare` creates an `ec_gf_t` whose lifetime is owned by callers such as the EC method list initialization path in `ec-method.c`. No persistent files, xattrs, dictionaries, or on-disk metadata are changed.

The `log` and `pow` arrays are mutable after allocation but treated as read-only lookup tables once initialized. The `ec_gf8_mul` table is externally provided static data. `min_ops`, `max_ops`, and `avg_ops` are derived diagnostics/cost hints for multiplication recipes, not persistent counters.

## Dependencies And Integration Points

- Includes `ec-mem-types.h` for memory type identifiers, `ec-gf8.h` for the GF(8) multiplication table, and `ec-helpers.h` for EC error-pointer helpers.
- Uses `ec-types.h` indirectly through included headers for `ec_gf_t`, `ec_gf_mul_t`, and `ec_gf_op_t`.
- Integrated by `ec-method.c`, which calls `ec_gf_prepare(EC_GF_BITS, EC_GF_MOD)` and uses `ec_gf_exp`, `ec_gf_div`, and `ec_gf_mul` to build erasure-code matrices. It later calls `ec_gf_destroy`.
- Integrated by code generation paths such as `ec-code.c`, which consult field division/multiplication results and `gf->table` to generate optimized XOR/copy operation sequences.

## Risks And Edge Cases

- Only 8-bit fields are supported. Any future width requires both table data and constructor logic updates; passing another width returns an `EC_ERR(EINVAL)` pointer.
- Error signaling for arithmetic uses `gf->size`, not an errno. Callers must treat any result equal to `gf->size` as invalid because valid values are `0..gf->size - 1`.
- `ec_gf_destroy` does not tolerate NULL defensively. Calling it with NULL would pass NULL into field dereferences before freeing.
- The duplicated table allocation uses `gf->size * 2 - 1` entries. This matches the maximum index used by `log[a] + log[b]` and division offsets, but any table-construction change must preserve that invariant.
- `ec_gf_init_tables` assumes the modulus is suitable for the chosen field. The default is valid for GF(256); arbitrary nonzero `mod` values are not validated for irreducibility.
- `gf->avg_ops /= gf->size` divides by 256 while summing only nonzero elements. This is a cost statistic, not correctness-sensitive, but consumers should not interpret it as the average over only nonzero multipliers.

## Test Signals

Useful tests should assert: unsupported `bits` returns an EC error pointer; default modulus produces a 256-element field; addition is XOR; multiplication/division round trips for all nonzero operands; division by zero and out-of-range operands return `gf->size`; `ec_gf_exp(gf, a, 0) == 1` for valid nonzero `a`; `ec_gf_exp(gf, 0, 0)` returns the sentinel; and constructor/destructor run cleanly under leak/error-injection tests for allocation failures.

Integration tests should cover EC matrix generation in `ec-method.c`, because incorrect table generation can surface as bad reconstruction coefficients rather than local crashes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/cluster/ec/src/ec-galois.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/cluster/ec/src/ec-galois.h -->
# sources/distributed-fs/glusterfs/xlators/cluster/ec/src/ec-galois.h

## Purpose

`ec-galois.h` is the public header for GlusterFS EC finite-field arithmetic. It declares the constructor/destructor for an `ec_gf_t` field context and the basic operations needed by EC matrix and code generation.

The header intentionally exposes only functions, not the layout of `ec_gf_t`; the concrete struct is defined in `ec-types.h`. That keeps callers dependent on the field API while allowing implementation details such as log/pow tables and multiplication recipe tables to live elsewhere.

## Important APIs And Types

- Includes `<inttypes.h>` for fixed-width integer declarations.
- Includes `ec-types.h`, which forward declares `ec_gf_t` and defines the backing finite-field structs later in that header.
- Declares `ec_gf_prepare(uint32_t bits, uint32_t mod)` to allocate and initialize a field context.
- Declares `ec_gf_destroy(ec_gf_t *gf)` to release the context.
- Declares `ec_gf_add`, `ec_gf_mul`, `ec_gf_div`, and `ec_gf_exp` for arithmetic on field elements represented as `uint32_t`.

## Control Flow And Integration

The header has no executable control flow beyond include guards. Its function declarations are implemented in `ec-galois.c` and consumed by EC method/code-generation files. The major call chain is EC initialization in `ec-method.c`, which prepares a GF context, builds matrices with exponent/division/multiplication, and destroys the context when the method list is torn down.

Callers receive arithmetic results directly as integer field elements. The implementation uses `gf->size` as an invalid-result sentinel, so callers that perform division, exponentiation, or custom input handling should check for values outside the valid byte range.

## State And Persistence Behavior

This header owns no state and persists nothing. Its API implies in-memory ownership: callers that successfully obtain an `ec_gf_t *` from `ec_gf_prepare` must later call `ec_gf_destroy`.

## Dependencies

The header depends on `ec-types.h` for the `ec_gf_t` type and on standard fixed-width integer types. It is included by EC arithmetic users such as `ec-method.c` and by any component that needs finite-field operations independent of raw FOP dispatch.

## Risks And Edge Cases

- The API does not document error-pointer returns or the arithmetic sentinel, but the implementation uses both. Callers need implementation knowledge or surrounding EC conventions to handle errors safely.
- `ec_gf_destroy` takes a raw pointer and does not advertise NULL safety.
- Element values are `uint32_t` even though the supported implementation is GF(256). Passing values outside the field range is possible and must be handled by the implementation.
- The header does not expose supported field widths; as of the paired implementation, only `bits == 8` is accepted.

## Test Signals

Header-level verification is mostly compile/link coverage: files including this header should compile without needing the internals of `struct _ec_gf`; implementation tests should verify constructor error returns, arithmetic correctness, and destructor ownership. API users should have tests that reject or handle sentinel arithmetic results rather than accidentally treating `256` as a valid byte coefficient.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/cluster/ec/src/ec-galois.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/cluster/ec/src/ec-generic.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/cluster/ec/src/ec-generic.c -->
