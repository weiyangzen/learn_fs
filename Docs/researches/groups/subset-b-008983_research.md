<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/include/verbose.h -->
# Research: sources/storage-engines/wiredtiger/src/include/verbose.h

## Purpose

`verbose.h` defines WiredTiger's internal verbose logging convenience layer. It does not implement message formatting or dispatch itself; instead, it gives hot-path code cheap category/level checks and then calls the cold worker functions declared in `extern.h` and implemented in `src/support/err.c`. The header centralizes the mapping between `WT_VERBOSE_CATEGORY` / `WT_VERBOSE_LEVEL` values and the macros used throughout the storage engine to emit diagnostic messages.

The file also stores generated category string data with `WT_VERBOSE_CATEGORY_STR_INIT`. `src/support/err.c` uses this initializer for `verbose_category_strings[]`, and JSON verbose output includes those strings plus numeric category and level identifiers.

## Important APIs, Types, and Macros

`WT_VERBOSE_MESSAGE_INFO` bundles a log id, category, and level for id-bearing verbose messages. The id-aware macros create this structure on the stack and pass it to `__wt_verbose_worker_id`.

`WT_VERBOSE_MULTI_CATEGORY` stores a pointer to a category array plus its count. `WT_DECL_VERBOSE_MULTI_CATEGORY(items)` builds that structure with `WT_ELEMENTS(items)`, commonly from compound literals such as `((WT_VERBOSE_CATEGORY[]){WT_VERB_RECOVERY, WT_VERB_RTS})`.

`WT_VERBOSE_CATEGORY_STR_INIT` is a generated initializer whose order must match the public `WT_VERBOSE_CATEGORY` enum in `src/include/wiredtiger.h.in`. `__wt_verbose_category_string` returns these names for diagnostics and falls back to `"unknown"` only when the category is outside `WT_VERB_NUM_CATEGORIES`.

`WT_VERBOSE_LEVEL_STR(level, level_str)` maps `WT_VERBOSE_ERROR`, `WT_VERBOSE_WARNING`, `WT_VERBOSE_NOTICE`, `WT_VERBOSE_INFO`, and `WT_VERBOSE_DEBUG_1` through `WT_VERBOSE_DEBUG_5` to string labels used by event formatting.

`WT_SET_VERBOSE_LEVEL`, `WT_VERBOSE_LEVEL_ISSET`, and `WT_VERBOSE_ISSET` read and write `S2C(session)->verbose[category]` via relaxed enum atomics. `WT_VERBOSE_LEVEL_DEFAULT` is `WT_VERBOSE_DEBUG_1`, preserving the historical behavior of older category-only verbose messages. `WT_VERBOSE_CATEGORY_DEFAULT` is `WT_VERB_DEFAULT` and is used by generic error macros in `include/error.h`.

`WT_VERBOSE_SET_AND_SAVE` and `WT_VERBOSE_RESTORE` temporarily override one category's level and restore it from a caller-provided array. `src/support/generation.c` uses this near generation-drain timeouts to turn on extra eviction, reconciliation, and checkpoint logging.

The emission macros are `__wt_verbose_level`, `__wt_verbose_error`, `__wt_verbose_warning`, `__wt_verbose_notice`, `__wt_verbose_info`, `__wt_verbose_debug1`, `__wt_verbose_debug2`, `__wt_verbose_debug3`, and the legacy `__wt_verbose`. The id variants are `__wt_verbose_level_id` and `__wt_verbose_info_id`. The multi-category variants are `__wt_verbose_level_multi_id`, `__wt_verbose_level_multi`, and `__wt_verbose_multi`.

`WT_CONFIG_DEBUG` is a narrow helper that emits a configuration warning when `S2C(session)->debug.flags` contains `WT_CONN_DEBUG_CONFIGURATION`; it routes through the normal verbose warning path for `WT_VERB_CONFIGURATION`.

## Control Flow

The normal control path is: caller invokes a macro with a `WT_SESSION_IMPL *`, category, level, format string, and at least one variadic argument; the macro checks `WT_VERBOSE_LEVEL_ISSET`; only if the configured threshold allows the requested level does it call `__wt_verbose_worker` or `__wt_verbose_worker_id`. The worker functions in `support/err.c` create a `va_list` and call `__eventv`, which adds timestamp, thread id, optional session and dhandle context, category, log id, level, and the formatted message before sending it through the event handler or stderr fallback.

Level comparisons rely on the enum ordering from `wiredtiger.h.in`: `WT_VERBOSE_ERROR` is the most severe and has the lowest numeric value, while `WT_VERBOSE_DEBUG_5` is the most verbose. The predicate `(requested_level <= configured_level)` means a category configured at `NOTICE` receives error, warning, and notice messages, while a category configured at `DEBUG_2` also receives default/debug1 and debug2 messages.

Multi-category macros iterate categories in caller-provided order. `__wt_verbose_level_multi` and `__wt_verbose_multi` emit once for the first category whose configured level satisfies the request, then break. The id-bearing multi macro calls `__wt_verbose_level_id` for each category, so it may emit more than one message if multiple categories are enabled.

`__wt_verbose_level_multi` and `__wt_verbose_multi` first copy the `multi_category` expression into a local variable. The file comments call out why: callers may pass a ternary expression returning different category sets, and evaluating it repeatedly could select inconsistent sets.

## State and Persistence Behavior

This header creates no durable storage. Runtime verbose state lives in `WT_CONNECTION_IMPL.verbose[WT_VERB_NUM_CATEGORIES]`, declared in `include/connection.h`. `__wt_verbose_config` in `conn/conn_api.c` populates that array from the `verbose=[...]` connection configuration. If `all` is not present, unspecified categories default to `WT_VERBOSE_NOTICE`; if a category is present without a numeric value, it uses `WT_VERBOSE_LEVEL_DEFAULT`.

Verbose settings are process-local connection state and can be adjusted during connection setup and reconfiguration. The save/restore macros mutate the same array temporarily; callers must provide a correctly sized `WT_VERBOSE_LEVEL verbose_orig_level[WT_VERB_NUM_CATEGORIES]` and restore every category they saved.

Event messages themselves are not persisted by this header. They are passed to the configured event handler, JSON output path, stderr fallback, or error-log infrastructure depending on `support/err.c` and connection settings.

## Dependencies and Integration Points

The header depends on core WiredTiger typedefs and enums being available first: `WT_VERBOSE_CATEGORY`, `WT_VERBOSE_LEVEL`, `WT_SESSION_IMPL`, `WT_CONNECTION_IMPL`, `WT_VERBOSE_MESSAGE_INFO`, and `WT_VERBOSE_MULTI_CATEGORY` are tied together through `wt_internal.h`, `wiredtiger.h.in`, and `connection.h`.

It integrates with `conn/conn_api.c` for verbose category names accepted in configuration. The config name table must stay consistent with `WT_VERBOSE_CATEGORY` and `WT_VERBOSE_CATEGORY_STR_INIT`.

It integrates with `support/err.c`, which owns `verbose_category_strings[]`, `__eventv`, `__wt_verbose_worker`, `__wt_verbose_worker_id`, and `__wt_verbose_category_string`.

It is used broadly by subsystems such as block manager, checkpoint, compaction, eviction, layered/disaggregated storage, recovery, rollback-to-stable, transaction, and version reporting. `btree/bt_handle.c` uses `WT_VERB_VERSION` to dump btree version information, while connection open emits the WiredTiger version string through the same category.

## Risks and Edge Cases

The generated string initializer is order-sensitive. Adding, removing, or reordering `WT_VERBOSE_CATEGORY` values without regenerating/updating `WT_VERBOSE_CATEGORY_STR_INIT` and the configuration mapping in `conn_api.c` can produce misleading category names or broken configuration behavior.

The variadic macros require at least one argument after the format string. The header explicitly documents that it does not use a non-portable empty `__VA_ARGS__` comma elision trick. Callers that only need a literal message usually pass `"%s", "message"`.

The macros assume `session` is valid for the pre-check because `WT_VERBOSE_LEVEL_ISSET` immediately evaluates `S2C(session)`. The worker can handle a null session, but the macro gate generally cannot.

Relaxed atomic access is appropriate for diagnostic thresholds but does not provide sequencing beyond atomicity. Code must not rely on verbose-level changes as synchronization for other state.

Save/restore is fragile if used with a partially initialized `verbose_orig_level` array or if error paths skip restore. That can leave extra diagnostic output enabled for a category longer than intended.

`WT_VERBOSE_LEVEL_STR` has no default case. Unknown level values leave the output string as `""`, so validation in `__wt_verbose_config` and direct macro callers are important.

The id multi-category macro can emit duplicate messages across categories, unlike the non-id multi macros that stop after the first enabled category. Callers need to choose the variant based on whether repeated category-tagged events are desirable.

## Test Signals

Python verbose tests such as `test/suite/test_verbose02.py` and `test/suite/test_verbose04.py` exercise category coverage and expected default `WT_VERBOSE_DEBUG_1` behavior. These are good regression signals when changing category lists, defaults, or config parsing.

Compile tests should catch missing enum labels used in `WT_VERBOSE_LEVEL_STR` and mismatches in category names if generated code is refreshed. Runtime tests should verify `verbose=[all:N]`, category-specific overrides, boolean category entries, invalid negative/string levels, and JSON output fields for category, category id, log id, and verbose level.

Call-site tests around generation-drain timeout logging can validate `WT_VERBOSE_SET_AND_SAVE` / `WT_VERBOSE_RESTORE` behavior by ensuring temporary debug categories are enabled only for the diagnostic window and are restored afterward.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/include/verbose.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/include/verify_build.h -->
# Research: sources/storage-engines/wiredtiger/src/include/verify_build.h

## Purpose

`verify_build.h` is a compile-time contract header. It stops the build when the compiler, platform ABI, or struct definitions no longer satisfy layout assumptions that WiredTiger depends on for public/private object aliasing, block metadata encoding, cache-line padding, update-record layout, and fixed-size file offsets.

The file has no runtime functions. Its entire behavioral surface is `static_assert` plus the `WT_VERIFY_OPAQUE_POINTER` macro used near API entry points to prove that internal structures begin with their public `iface` field.

## Important APIs, Types, and Macros

`WT_VERIFY_OPAQUE_POINTER(type)` expands to a `static_assert(offsetof(type, iface) == 0, ...)`. WiredTiger exposes public handles as opaque pointers whose first field is the public interface object. Internal code casts between public and private types, so `iface` must be the first member.

The fixed-size assertions check `sizeof(WT_BLOCK_DESC) == WT_BLOCK_DESC_SIZE` and `sizeof(WT_REF) == WT_REF_SIZE`. Those constants encode expected packed layout for storage-engine metadata and btree reference structures.

The `WT_BLOCK_DISAGG` assertions pin offsets for the shared prefix with `WT_BLOCK`: `name`, `objectid`, `ref`, `q`, and `hashq`. The comment explains that both structures can be inserted into `conn->blockhash` / `conn->blockqh` and traversed as `WT_BLOCK *`, so prefix aliasing must remain exact.

The `WT_UPDATE` checks assert that the whole update structure aligns to an 8-byte boundary, that its variable-length `data` field starts at `WT_UPDATE_SIZE`, and that `WT_UPDATE_SIZE_NOVALUE` currently equals `sizeof(WT_UPDATE)` with no extra difference from `WT_UPDATE_SIZE`.

`WT_PADDING_CHECK(s)` asserts either the structure is no larger than one cache line or its size is a multiple of `WT_CACHE_LINE_ALIGNMENT`. It is applied to `WT_TXN_SHARED`, making cache-line padding a build-time invariant.

The platform assertions require `sizeof(size_t) >= 8`, `sizeof(wt_off_t) == 8`, and `sizeof(time_t) <= sizeof(uint64_t)`.

## Control Flow

This header runs at compile time. Including it after the relevant type definitions causes the compiler to evaluate all `static_assert` expressions. Success produces no code. Failure aborts compilation with the specific assertion message.

`WT_VERIFY_OPAQUE_POINTER` is a macro rather than a global assertion because it is invoked at relevant API implementation points, for example connection open, session API code, log cursor code, and cursor implementations. These invocations localize the guarantee to the internal handle type being exposed through a public interface.

## State and Persistence Behavior

There is no runtime state, persistent state, or emitted data. The header protects the representation of structures that are persisted or shared elsewhere. `WT_BLOCK_DESC` relates to block metadata, `WT_UPDATE` contains inline variable-length update data, `WT_REF` participates in btree state, and `wt_off_t` controls on-disk addressability. If these layouts drift, persisted data interpretation or pointer casting could become unsafe; the header prevents that at build time.

## Dependencies and Integration Points

The header depends on `assert.h` for `static_assert` availability and on prior declarations of all checked WiredTiger types and constants: `WT_BLOCK_DESC`, `WT_BLOCK_DESC_SIZE`, `WT_REF`, `WT_REF_SIZE`, `WT_BLOCK_DISAGG`, `WT_BLOCK`, `WT_UPDATE`, `WT_UPDATE_SIZE`, `WT_UPDATE_SIZE_NOVALUE`, `WT_TXN_SHARED`, `WT_CACHE_LINE_ALIGNMENT`, `wt_off_t`, and alignment helpers such as `WT_ALIGN`.

It integrates with the public API object model. `WT_VERIFY_OPAQUE_POINTER` is used by internal implementations for `WT_CONNECTION_IMPL`, `WT_SESSION_IMPL`, and cursor subclasses such as backup, config, dump, file, layered, log, stat, table, data-source, and prepared-discovery cursors.

It also integrates with disaggregated storage through the `WT_BLOCK_DISAGG` / `WT_BLOCK` shared-prefix assertions. These checks document and enforce a deliberate aliasing relationship used by connection block hash and queue traversal code.

## Risks and Edge Cases

The assertions are intentionally strict. A legitimate struct layout change requires updating the corresponding size constants, offset assertions, and any code that serializes or aliases the structure. Treating a compile failure here as a nuisance would risk silent corruption or invalid pointer casts.

The `WT_BLOCK_DISAGG` prefix contract is especially sensitive because C permits the code to compile if fields drift, but traversal through `WT_BLOCK *` would read the wrong fields. These assertions are the main guard against that class of bug.

The `WT_UPDATE` checks encode assumptions about trailing padding and variable-length-array placement. Adding fields near `data`, changing timestamp types, or changing alignment rules can require a coordinated update to size macros and allocation logic.

Platform support is intentionally narrowed. Builds with 32-bit `size_t`, 4-byte file offsets, or unexpectedly large/non-integral `time_t` fail at compile time rather than producing a binary with untested address-cookie or time conversion behavior.

`WT_PADDING_CHECK` only checks size divisibility, not field-level false sharing. It is a coarse build signal; reviewers still need to inspect concurrent fields when changing shared structures.

## Test Signals

The primary test signal is compilation across supported compilers and build variants. Any failure in this file should be investigated as an ABI/layout change rather than bypassed.

Additional targeted signals include compiling with disaggregated storage enabled after edits to `WT_BLOCK` or `WT_BLOCK_DISAGG`, building cursor/API files after adding an `iface`-backed internal type, and running format or recovery tests after touching `WT_BLOCK_DESC`, `WT_REF`, `WT_UPDATE`, or `wt_off_t` definitions.

Static analysis or small compile-only tests can also verify that each internal public-handle type invokes `WT_VERIFY_OPAQUE_POINTER`, but the current repository mainly enforces this by explicit macro calls in the implementations.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/include/verify_build.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/include/version.h -->
# Research: sources/storage-engines/wiredtiger/src/include/version.h

## Purpose

`version.h` defines WiredTiger's compact internal version value and inline comparison helpers. The same representation is used for general WiredTiger release/compatibility versions and, through `WT_BTREE_VERSION`, for btree source-file version ranges.

The header gives callers a consistent way to represent absent versions, partially specified major/minor versions, and full major/minor/patch versions without repeating comparison logic.

## Important APIs, Types, and Functions

`struct __wt_version` contains `uint16_t major`, `uint16_t minor`, and `uint16_t patch`. `wt_internal.h` typedefs this as `WT_VERSION`.

`typedef WT_VERSION WT_BTREE_VERSION` aliases the same structure for btree version numbers, avoiding confusion at call sites that compare file format ranges instead of WiredTiger release versions.

`WT_NO_VALUE` is `UINT16_MAX`. `WT_NO_VERSION` is a compound literal with all three fields set to `WT_NO_VALUE`.

`__wt_version_cmp(WT_VERSION v, WT_VERSION other)` returns `1`, `0`, or `-1` like `strcmp`. If either input has `patch == WT_NO_VALUE`, the function sets both local patch fields to `0`, making patch optional for comparisons. Major and minor are compared first, then patch if both patches are defined.

`__wt_version_defined(WT_VERSION v)` returns true when major and minor are not `WT_NO_VALUE`. Patch is intentionally not required.

`__wt_version_eq`, `__wt_version_gt`, `__wt_version_gte`, `__wt_version_lt`, and `__wt_version_lte` are small inline wrappers over `__wt_version_cmp`.

## Control Flow

All functions are `static WT_INLINE` and operate on pass-by-value structures, so they have no side effects. Comparison first normalizes missing patch values locally, checks full equality, then performs ordered major/minor/patch greater-than checks. If no greater-than branch matches and equality was false, the result is less-than.

The wrapper predicates do not duplicate ordering logic. They interpret the tri-state comparison result, which keeps optional-patch behavior consistent across equality and range checks.

## State and Persistence Behavior

This header does not maintain state. It defines value semantics for version fields stored elsewhere.

Connection compatibility code initializes `max_compat`, `min_compat`, and `new_compat` to `WT_NO_VERSION`, parses configuration into major/minor fields, stores the current compatibility in `conn->compat_version`, and persists/reloads compatibility through metadata/turtle paths. `conn->recovery_version` is also initialized to `WT_NO_VERSION` during open before turtle validation populates it.

Metadata and checkpoint code use the same value semantics when reading persisted version strings. `meta_turtle.c` reads `major`, `minor`, and `patch` from the turtle file, compares the result with `WT_MIN_STARTUP_VERSION`, and stores it as the recovery version. `meta_ckpt.c` reads btree major/minor versions from checkpoint metadata and checks them against `WT_BTREE_VERSION_MIN` and `WT_BTREE_VERSION_MAX`.

## Dependencies and Integration Points

The header depends on fixed-width integer types, `bool`, `UINT16_MAX`, and `WT_INLINE` being available from the surrounding WiredTiger include stack.

It integrates with connection configuration in `conn/conn_reconfig.c`, where `__wti_conn_compat_config` uses `__wt_version_defined`, `__wt_version_eq`, `__wt_version_lt`, and `__wt_version_gt` to enforce compatibility release, required minimum, and required maximum constraints.

It integrates with startup validation in `conn/conn_api.c` and `meta/meta_turtle.c`, where saved turtle versions are validated before modifying an existing database home.

It integrates with btree/checkpoint metadata via `WT_BTREE_VERSION` and the min/max btree version constants used by checkpoint validation.

## Risks and Edge Cases

`WT_NO_VALUE` is a sentinel inside a `uint16_t` field. Versions cannot use `65535` as a meaningful major, minor, or patch value without colliding with the undefined marker.

Missing patch values are ignored symmetrically. Comparing `1.2.NO_VALUE` to `1.2.9` returns equal because both patch fields are normalized to zero when either patch is missing. This is deliberate for callers that only know major/minor, but it can surprise code that expects a missing patch to be lower or higher than a concrete patch.

`__wt_version_defined` only checks major and minor. A value with major/minor set and patch omitted is a valid defined version, while a value with only patch set is undefined even if `patch != WT_NO_VALUE`.

The comparison helpers do not validate ranges beyond the sentinel rule. Parsing code must still reject invalid textual formats and ensure values fit in `uint16_t`.

Because `WT_NO_VERSION` is a compound literal macro, it is convenient for assignment and initialization in C code but should not be treated as a stable object address.

## Test Signals

Unit or compile-level tests should cover comparison matrices around major, minor, and patch ordering; equality when either patch is `WT_NO_VALUE`; and `__wt_version_defined` for full, major/minor-only, and sentinel values.

Integration tests should exercise compatibility configuration on open and reconfigure, especially `require_min`, `require_max`, unchanged compatibility reconfiguration, and saved metadata compatibility checks. Startup/recovery tests should cover turtle versions below `WT_MIN_STARTUP_VERSION` and btree checkpoint versions outside the supported min/max range.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/include/version.h -->
