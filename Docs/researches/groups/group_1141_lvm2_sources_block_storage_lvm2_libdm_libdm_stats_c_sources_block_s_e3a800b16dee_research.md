# Group Research: group_1141_lvm2_sources_block_storage_lvm2_libdm_libdm_stats_c_sources_block_s_e3a800b16dee

Scope: `Docs/research_subset_a.md`; all listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/libdm/libdm-stats.c -->
# File Research: sources/block-storage/lvm2/libdm/libdm-stats.c

## Summary
Implements libdevmapper's userspace interface for device-mapper statistics regions, counters, metrics, histograms, groups, and file-extent mapping. It builds and parses `@stats_*` target messages, maintains cached region/group tables, aggregates counters over regions and groups, formats histogram data, and optionally maps regular-file extents into stats regions via FIEMAP.

## Main Responsibilities
- Creates, binds, lists, populates, clears, deletes, and destroys `struct dm_stats` handles and statistics regions.
- Parses kernel `@stats_list` and `@stats_print` responses into `dm_stats_region`, `dm_stats_group`, `dm_stats_counters`, and `dm_histogram` structures.
- Implements stats walking over areas, regions, and groups using cursor state plus `DM_STATS_WALK_*` flags.
- Computes named counters and derived metrics such as reads/sec, writes/sec, request size, wait time, throughput, service time, and utilization.
- Creates and parses histogram bounds, formats histogram bin strings, and caches aggregate histograms.
- Persists group membership in region `aux_data` as `DMS_GROUP="alias:members"` descriptors.
- Maps file extents to stats regions using `FS_IOC_FIEMAP`, groups those regions, updates mappings, and can spawn `dmfilemapd` when enabled.
- Provides GNU symbol-version compatibility wrappers for older `dm_stats_create_region()` ABIs.

## Key APIs
- Handle/binding: `dm_stats_create()`, `dm_stats_destroy()`, `dm_stats_bind_devno()`, `dm_stats_bind_name()`, `dm_stats_bind_uuid()`, `dm_stats_bind_from_fd()`.
- Region lifecycle: `dm_stats_create_region()`, `dm_stats_delete_region()`, `dm_stats_clear_region()`, `dm_stats_list()`, `dm_stats_populate()`, `dm_stats_print_region()`.
- Walking/introspection: `dm_stats_walk_init()`, `dm_stats_walk_start()`, `dm_stats_walk_next()`, `dm_stats_walk_end()`, `dm_stats_object_type()`.
- Counters/metrics: `dm_stats_get_counter()`, generated `dm_stats_get_*` counter functions, `dm_stats_get_metric()`, generated metric functions, `dm_stats_get_utilization()`.
- Histogram helpers: `dm_histogram_bounds_from_string()`, `dm_histogram_bounds_from_uint64()`, `dm_histogram_to_string()`, `dm_stats_get_histogram()`.
- Groups: `dm_stats_create_group()`, `dm_stats_delete_group()`, `dm_stats_set_alias()`, `dm_stats_get_group_descriptor()`, `dm_stats_get_group_id()`.
- File mappings: `dm_stats_create_regions_from_fd()`, `dm_stats_update_regions_from_fd()`, `dm_stats_start_filemapd()`.

## Important Behavior
`dm_stats_create()` owns three pools: a main region/counter pool, a histogram pool, and a group pool. Region and group tables are pool-allocated arrays indexed by region ID, with holes represented by sentinel IDs. Rebinding a handle clears existing binding, regions, and groups.

Region creation formats `@stats_create` messages with optional range, area step, `precise_timestamps`, histogram bounds, program ID, and escaped aux data. Histogram bounds below millisecond precision automatically force precise timestamps if the driver supports them.

`@stats_list` parsing handles sparse region IDs, extracts program ID and aux data, parses optional `precise_timestamps` and `histogram:` arguments, and converts embedded group descriptors into group table entries while stripping the internal group tag from user-visible aux data.

`@stats_print` parsing reads one row per area, scales millisecond counters to nanoseconds when needed, and parses area histogram counts through a separate histogram pool to avoid interleaving growing objects in the main pool.

The walk engine can visit areas first, then aggregate regions, then groups, depending on flags. Group IDs are encoded in region IDs using `DM_STATS_WALK_GROUP`; current cursors are decoded by accessor functions.

Counter aggregation is centralized in `dm_stats_get_counter()`: group aggregation iterates all member regions and optionally all areas; region aggregation sums all areas; plain access reads a single area's counters. Derived metrics are calculated from these aggregate counters and the configured sampling interval.

File mapping rejects unsupported cases such as non-regular files, non-device-mapper backing devices, and btrfs physical FIEMAP data. It merges contiguous physical extents, creates one stats region per extent, rolls back newly created regions on partial failure, and can update a previous group by deleting missing extents and creating regions for new extents.

## State and Lifetime
`dm_stats_region` owns malloc-allocated `program_id` and `aux_data`, while counters and histogram bounds are pool-owned. Histograms created for parsed area data and aggregate caches live in `hist_mem`. Group aliases and bitsets are explicitly freed by group destruction.

Pool allocation order matters: region and group destruction walks backward so pool frees can unwind safely. Histogram objects for area counters are freed back to the first histogram in a region.

File mapping uses a temporary `extent_mem` pool so transient FIEMAP extents do not disturb the handle's region-table pool.

## Risks
The API relies heavily on sentinel values, encoded flag bits in IDs, and current-cursor substitution. Callers that pass invalid region IDs or mix group/region flags incorrectly can reach unchecked array indexing in some accessors.

Group metadata is persisted by rewriting aux data on the group leader. Failures during aux-data updates, group deletion, or mapped-file updates can leave kernel-side stats regions partly changed, though rollback paths cover many creation failures.

Parsing is tightly coupled to kernel message formats and fixed 4096-byte row buffers. Any kernel format drift or unexpectedly long string data can cause parse failures.

FIEMAP mapping assumes physical extent data is meaningful and excludes btrfs explicitly; other filesystems with unusual FIEMAP semantics may still produce surprising mappings.
<!-- END FILE RESEARCH: sources/block-storage/lvm2/libdm/libdm-stats.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/libdm/libdm-string.c -->
# File Research: sources/block-storage/lvm2/libdm/libdm-string.c

## Summary
Provides libdm string, formatting, escaping, device-name construction, and size/unit conversion helpers. These routines support command parsing, LVM device-mapper name encoding, safe formatted allocation, and human-readable size rendering.

## Main Responsibilities
- Splits whitespace-delimited strings with `dm_split_words()`.
- Splits hyphen-escaped LVM device names into VG, LV, and layer components.
- Builds escaped device-mapper names and UUIDs.
- Wraps `snprintf`, `vasprintf`, and `asprintf` with libdm allocation and legacy error semantics.
- Escapes/unescapes quotes, colons, and at signs.
- Implements bounded `dm_strncpy()`.
- Converts sector counts to formatted size strings.
- Parses unit suffixes and custom numeric units into byte factors.

## Key APIs
- `dm_split_words()`
- `dm_split_lvm_name()`
- `dm_snprintf()`, `dm_vasprintf()`, `dm_asprintf()`
- `dm_basename()`
- `dm_build_dm_name()`, `dm_build_dm_uuid()`
- `dm_escape_double_quotes()`, `dm_unescape_double_quotes()`
- `dm_unescape_colons_and_at_signs()`
- `dm_strncpy()`
- `dm_size_to_string()`
- `dm_units_to_factor()`

## Important Behavior
LVM name quoting uses doubled hyphens inside components and single hyphens between components. `_unquote()` terminates each component in place and returns the next component start.

`dm_snprintf()` treats truncation as `-1`, normalizing newer `snprintf()` behavior to the older libdm expectation.

`dm_vasprintf()` grows a temporary buffer until `vsnprintf()` fits, then returns the allocated string and reports the length including the terminating null byte.

`dm_size_to_string()` expects input sizes in 512-byte sectors, then formats them using binary, decimal, human-readable, sector, byte, or custom-unit modes. It supports suffix styles selected by `dm_size_suffix_t` and adds `<` for rounded human-readable output where requested.

`dm_units_to_factor()` parses optional leading numeric values, supports binary lowercase units, decimal uppercase units, sectors, bytes, and human-readable modes, and can reject multi-character suffixes in strict mode.

## State and Lifetime
Most returned strings are allocated from a caller-provided `dm_pool`; `dm_vasprintf()` and `dm_asprintf()` allocate with `dm_malloc`. Several unescape helpers mutate caller buffers in place.

## Risks
The split and target parsers are intentionally simple and mostly whitespace based; they do not implement shell-like quoting. In-place unquoting requires mutable buffers and can surprise callers using shared string storage.
<!-- END FILE RESEARCH: sources/block-storage/lvm2/libdm/libdm-string.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/libdm/libdm-targets.c -->
# File Research: sources/block-storage/lvm2/libdm/libdm-targets.c

## Summary
Parses status strings returned by multiple device-mapper targets into structured libdm status objects. It covers snapshot, raid, cache, writecache, integrity, thin-pool, thin, and mirror targets.

## Main Responsibilities
- Converts target-specific status text into pool-allocated structs.
- Recognizes target error/fail states where status output is symbolic rather than fully numeric.
- Handles multiple kernel status-format versions for raid, cache, and thin-pool targets.
- Parses device health, sync progress, cache policy arguments, and thin provisioning status flags.

## Key APIs
- `dm_get_status_snapshot()`
- `dm_get_status_raid()`
- `dm_get_status_cache()`
- `dm_get_status_writecache()`
- `dm_get_status_integrity()`
- `parse_thin_pool_status()`
- `dm_get_status_thin_pool()`
- `dm_get_status_thin()`
- `dm_get_status_mirror()`

## Important Behavior
Snapshot status accepts numeric `used/total [metadata]` data plus symbolic states `Invalid`, `Merge failed`, and `Overflow`.

Raid parsing counts space-delimited fields to support old 4-field output, 1.5.0+ 6-field output, and 1.9.0+ 7-field output. It truncates reported device health to the usable device count and includes compatibility adjustments for misleading lowercase `a` raid leg states during resync/recover/idle transitions.

Cache parsing reads fixed numeric fields first, then scans feature flags such as `writethrough`, `writeback`, `passthrough`, `metadata2`, and `no_discard_passdown`. It stores core and policy arguments as argv-style arrays and detects `ro` and `needs_check`.

Thin-pool parsing handles `Error`, `Fail`, transaction ID, metadata/data usage, discard policy, out-of-data/read-only state, `error_if_no_space`, and `needs_check`. Thin device status supports `-`, `Fail`, or mapped/highest sector pairs.

Mirror parsing reads image devices, sync ratio, per-image health chars, log type, optional log devices, and log health. Health chars map to alive, flush/write/sync/read failed, or unclassified states.

## State and Lifetime
All status structs and nested strings/arrays are allocated from the caller's `dm_pool`. On parse failure, the function frees the top-level struct from that pool when possible and returns `0` with `*status = NULL`.

## Risks
The parsers assume single-space field delimiting in helper functions. Several optional-state detections use substring checks, so they depend on kernel status strings remaining unambiguous. Unknown cache features are logged but do not abort parsing.
<!-- END FILE RESEARCH: sources/block-storage/lvm2/libdm/libdm-targets.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/libdm/libdm-timestamp.c -->
# File Research: sources/block-storage/lvm2/libdm/libdm-timestamp.c

## Summary
Implements a small opaque timestamp abstraction for libdm. It can use monotonic `clock_gettime()` when realtime support is configured, or fall back to `gettimeofday()`.

## Main Responsibilities
- Allocates, captures, compares, copies, and frees `struct dm_timestamp`.
- Converts timestamps to nanosecond counters for comparison and delta calculations.
- Hides platform-specific timestamp representation behind one libdm API.

## Key APIs
- `dm_timestamp_alloc()`
- `dm_timestamp_get()`
- `dm_timestamp_compare()`
- `dm_timestamp_delta()`
- `dm_timestamp_copy()`
- `dm_timestamp_destroy()`

## Important Behavior
With `HAVE_REALTIME`, timestamps use `CLOCK_MONOTONIC`, avoiding wall-clock jumps. Without it, the fallback uses `gettimeofday()` and is subject to wall-clock/NTP adjustments.

`dm_timestamp_compare()` returns `-1`, `0`, or `1` by comparing nanosecond totals. `dm_timestamp_delta()` returns the absolute nanosecond difference without preserving ordering.

## State and Lifetime
Timestamps are heap-allocated with `dm_zalloc()` and freed with `dm_free()`. The concrete struct differs by configuration: `timespec` for realtime, `timeval` for fallback.

## Risks
The API does not validate null inputs in compare/delta/copy. Callers must only pass allocated timestamp objects. The fallback mode is not monotonic.
<!-- END FILE RESEARCH: sources/block-storage/lvm2/libdm/libdm-timestamp.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/libdm/make.tmpl.in -->
# File Research: sources/block-storage/lvm2/libdm/make.tmpl.in

## Summary
Autoconf-generated make template shared by libdm/LVM2 subdirectories. It defines toolchain variables, install paths, warning flags, recursive targets, object/dependency rules, static/shared library rules, symbol export generation, cleaning, and optional analysis helpers.

## Main Responsibilities
- Imports configured tools, flags, libraries, prefixes, install directories, and feature settings.
- Establishes silent/verbose build behavior through `V`, `Q`, and `SHOW`.
- Sets compiler warnings, hardening flags, PIC/PIE options, debug flags, and include paths.
- Defines common recursive targets for subdirectories.
- Builds objects, dependency files, gettext template files, static libraries, and shared libraries.
- Installs shared libraries and plugins with compatibility symlinks.
- Generates linker version scripts from exported-symbol lists and optionally exported headers.
- Supports `cflow`, `cppcheck`, `gcc -fanalyzer`, gettext `.mo`, clean, and distclean targets.

## Key Targets and Variables
- Build flow: `all`, `$(SUBDIRS)`, `$(TARGETS)`, `$(LIB_STATIC)`, `$(LIB_SHARED).$(LIB_VERSION)`.
- Recursive helpers: `SIMPLE_RECURSIVE_TARGETS`, `SIMPLE_RECURSIVE_RULE`.
- Install: `install`, `install_device_mapper`, `install_lib_shared`, `install_dm_plugin`, `install_lvm2_plugin`.
- Analysis: `cflow`, `cppcheck`, `gccanalyze`.
- Cleanup: `cleandir`, `clean`, `distclean`.
- Symbol export: `.exported_symbols_generated`, `.export.sym`.
- Dependency inclusion gated by `@USE_TRACKING@`.

## Important Behavior
`CC` can be overridden by the environment, but the built-in default `cc` is replaced by the configured compiler. `CFLAGS` are protected against recursively re-adding `-fPIC`.

Shared library builds branch on `LIB_SUFFIX` for ELF `.so` versus Darwin `.dylib`. Static libraries are rebuilt with `ar rsv` after removing the old archive.

Full RELRO, `now`, `--as-needed`, and PIE flags are conditionally appended based on configure results and static/shared link mode.

Symbol script generation either builds a simple `Base` version or stitches together `.exported_symbols.*` files in version order, while checking that generated symbols match versioned symbol lists.

## State and Lifetime
This is a template consumed by configure to produce concrete Makefiles. Most values are `@...@` substitutions, and generated dependency files are optionally included for normal build goals.

## Risks
Global flags and include paths affect all subdirectories using the template. Symbol-list mismatches intentionally fail the build. The Makefile embeds platform-specific branches and old compiler warning switches that depend on configure checks.
<!-- END FILE RESEARCH: sources/block-storage/lvm2/libdm/make.tmpl.in -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/libdm/misc/dm-ioctl.h -->
# File Research: sources/block-storage/lvm2/libdm/misc/dm-ioctl.h

## Summary
Defines the userspace-visible device-mapper ioctl ABI version 4 structures, command numbers, ioctl macros, constants, and flags. It mirrors the kernel device-mapper ioctl interface used by libdm.

## Main Contents
- Device-mapper naming limits and directory/control-node constants.
- `struct dm_ioctl`, the header for all ioctl payloads.
- Table/status payload structs: `dm_target_spec`, `dm_target_deps`, `dm_name_list`, `dm_target_versions`, `dm_target_msg`.
- Command enum values from `DM_VERSION_CMD` through `DM_GET_TARGET_VERSION_CMD`.
- `_IOWR` ioctl definitions such as `DM_DEV_CREATE`, `DM_TABLE_LOAD`, and `DM_TARGET_MSG`.
- ABI version constants: `DM_VERSION_MAJOR 4`, `DM_VERSION_MINOR 45`, `DM_VERSION_PATCHLEVEL 0`.
- Device/table/status flags including read-only, suspend, buffer-full, uevent, secure-data, deferred-remove, internal-suspend, and IMA measurement flags.

## Important Behavior
Every ioctl uses one contiguous memory buffer beginning with `struct dm_ioctl`. `data_size` is total buffer size and `data_start` points to payload offset.

`dm_ioctl.version` is in/out and recognized commands fill it even on command failure. Device lookup can use UUID instead of name if UUID is provided.

`dm_target_spec.next` has different offset semantics for table load versus status retrieval, and parameter strings immediately follow the struct with alignment padding before the next target.

`dm_name_list` includes optional event number, flags, and UUID storage after the null-terminated name, aligned to an 8-byte boundary.

## State and Lifetime
This header is ABI, not implementation. Consumers allocate and populate buffers according to these layouts before issuing ioctls to the device-mapper control node.

## Risks
Layout and command-number stability are critical; changes must match kernel `dm-ioctl.c`. Flexible array members use legacy zero-length arrays in several structs, so callers must compute buffer sizes carefully.
<!-- END FILE RESEARCH: sources/block-storage/lvm2/libdm/misc/dm-ioctl.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/libdm/misc/dm-log-userspace.h -->
# File Research: sources/block-storage/lvm2/libdm/misc/dm-log-userspace.h

## Summary
Defines the protocol between the kernel device-mapper userspace dirty-log module and a userspace log daemon. It documents netlink connector setup, request types, payload direction, payload formats, versioning, and the shared request structure.

## Main Contents
- Request type constants `DM_ULOG_CTR` through `DM_ULOG_IS_REMOTE_RECOVERING`.
- Request mask helper `DM_ULOG_REQUEST_TYPE()`.
- Protocol version `DM_ULOG_REQUEST_VERSION 2`.
- `struct dm_ulog_request`, containing log identifiers, version, error, sequence, request type, data size, and flexible payload.

## Important Behavior
The kernel sends `struct dm_ulog_request` plus optional payload to userspace. Userspace processes the dirty-log operation and returns the same request structure with `error`, `data_size`, and any kernel-bound payload filled in.

The `uuid` and `luid` identify a specific mirror log instance. The UUID is required for cluster-aware log communication, while the LUID differentiates live/inactive tables that may share a UUID.

Constructor requests may return a backing device name for `dm_get_device()`. Version 2 records that `DM_ULOG_CTR` can return this string.

Several request types carry arrays or small structs in `data`, including mark/clear region arrays, resync-work results, and remote-recovering status.

## State and Lifetime
This header only defines the wire format and constants. The request payload is variable length and interpreted according to `request_type` after masking with `DM_ULOG_REQUEST_MASK`.

## Risks
The protocol requires strict agreement between kernel and userspace on payload size, endianness, and struct layout. The 8-bit request mask reserves upper bits for future use, so consumers should always decode with `DM_ULOG_REQUEST_TYPE()`.
<!-- END FILE RESEARCH: sources/block-storage/lvm2/libdm/misc/dm-log-userspace.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/libdm/misc/dm-logging.h -->
# File Research: sources/block-storage/lvm2/libdm/misc/dm-logging.h

## Summary
Provides libdm logging macro glue that routes source-file and line-number-aware messages through the exported `dm_log_with_errno` callback and then includes the broader LVM logging interface.

## Main Contents
- Declares `extern dm_log_with_errno_fn dm_log_with_errno`.
- Defines `LOG_MESG()`, `LOG_LINE()`, `LOG_LINE_WITH_ERRNO()`, and `LOG_LINE_WITH_CLASS()`.
- Includes `lib/log/log.h` after macro setup.

## Important Behavior
Logging macros capture `__FILE__` and `__LINE__` and pass either errno-like values or debug classes through the same callback signature.

## State and Lifetime
The actual logging function pointer is defined elsewhere. This header establishes the macro contract used by libdm source files.

## Risks
Every log call depends on `dm_log_with_errno` being initialized consistently by the library/application. Macro varargs are compiler-extension style.
<!-- END FILE RESEARCH: sources/block-storage/lvm2/libdm/misc/dm-logging.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/libdm/misc/dmlib.h -->
# File Research: sources/block-storage/lvm2/libdm/misc/dmlib.h

## Summary
Primary internal include for libdm source files. It defines symbol-version export macros, documents their use, includes public libdevmapper and utility headers, connects logging, and pulls in `unistd.h`.

## Main Contents
- `DM_EXPORT_NEW_SYMBOL(rettype, func, ver)`
- `DM_EXPORT_SYMBOL(func, ver)`
- `DM_EXPORT_SYMBOL_BASE(func)`
- GNU symbol-version implementations using either `__attribute__((__symver__))` or `.symver` assembly.
- Non-GNU fallback macros that compile without symbol versioning.
- Includes `libdm/libdevmapper.h`, `libdm/dm-tools/util.h`, and `libdm/misc/dm-logging.h`.

## Important Behavior
New default-version symbols get `@@DM_<ver>`, older compatibility symbols get `@DM_<ver>`, and base symbols can be bound to `@Base`. Compatibility implementations must use suffixed function names such as `_v1_02_104`.

When `GNU_SYMVER` is unavailable, version macros reduce to normal function definitions or empty declarations, preserving source compatibility without versioned exports.

## State and Lifetime
No runtime state. This header is intended to be included first by every library source file so symbol/export and logging definitions are consistently available.

## Risks
Symbol-version declarations require exact function prototypes and names. Incorrect use can create ABI breaks or missing exported versions, especially when adding backward-compatible implementations.
<!-- END FILE RESEARCH: sources/block-storage/lvm2/libdm/misc/dmlib.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/libdm/misc/kdev_t.h -->
# File Research: sources/block-storage/lvm2/libdm/misc/kdev_t.h

## Summary
Defines Linux kernel-style `dev_t` major/minor encoding and decoding macros for libdm.

## Main Contents
- `MAJOR(dev)`
- `MINOR(dev)`
- `MKDEV(ma, mi)`

## Important Behavior
The macros implement the split Linux device-number layout where major occupies bits derived from `0xfff00`, and minor combines low 8 bits with high minor bits shifted from bit 12.

## State and Lifetime
Pure preprocessor helper header with no runtime state.

## Risks
These macros intentionally shadow common system macros and assume Linux-style `dev_t` layout. Including order matters where system headers also define `major`, `minor`, or related helpers.
<!-- END FILE RESEARCH: sources/block-storage/lvm2/libdm/misc/kdev_t.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/libdm/mm/dbg_malloc.c -->
# File Research: sources/block-storage/lvm2/libdm/mm/dbg_malloc.c

## Summary
Implements libdm heap allocation wrappers with optional debug-memory tracking. In debug mode it records allocation metadata, guard bytes, leak reports, and bounds checks; in normal mode it delegates to libc allocation functions with a large-allocation guard.

## Main Responsibilities
- Provides malloc, zalloc, aligned malloc, strdup, realloc, free, memory dump, and bounds-check wrappers.
- Tracks debug allocations in a doubly linked list of `memblock` headers.
- Stomps allocated and freed memory with recognizable byte patterns in debug mode.
- Adds far-end guard bytes and validates them on free and explicit bounds checks.
- Integrates with Valgrind pool macros when `VALGRIND_POOL` is enabled.

## Key APIs
- Low-level helpers: `dm_malloc_aux()`, `dm_malloc_aux_debug()`, `dm_zalloc_aux()`, `dm_zalloc_aux_debug()`, `dm_realloc_aux()`, `dm_free_aux()`, `dm_strdup_aux()`.
- Debug reporting: `dm_dump_memory_debug()`, `dm_bounds_check_debug()`.
- Public wrapper layer: `dm_malloc_wrapper()`, `dm_malloc_aligned_wrapper()`, `dm_zalloc_wrapper()`, `dm_strdup_wrapper()`, `dm_free_wrapper()`, `dm_realloc_wrapper()`, `dm_dump_memory_wrapper()`, `dm_bounds_check_wrapper()`.

## Important Behavior
Allocations larger than 50,000,000 bytes are rejected as likely metadata corruption. Debug allocations reserve space for a `memblock` header and trailing guard bytes whose value is based on the allocation ID.

`dm_free_aux()` asserts that the pointer matches the block's magic pointer, verifies trailing guard bytes, checks for double free by ID, unlinks the block, overwrites freed memory with `0xad/0xde`, and frees the full block.

`dm_realloc_aux()` allocates a new debug block, copies the smaller of old and new sizes, then frees the old block.

Normal aligned allocation uses `posix_memalign()`, defaulting to page alignment when alignment is zero. Under `DEBUG_MEM`, aligned allocation is not truly aligned and falls back to debug malloc.

## State and Lifetime
Debug mode keeps global `_head`, `_tail`, and `_mem_stats` state for all active allocations. Normal mode has no tracking state.

## Risks
The debug allocator uses assertions for corruption detection, so failures abort the process. It is not visibly synchronized, so debug allocation tracking is not thread-safe. Normal `dm_strdup_wrapper()` calls libc `strdup()` directly and inherits its null-input behavior.
<!-- END FILE RESEARCH: sources/block-storage/lvm2/libdm/mm/dbg_malloc.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/libdm/mm/pool-debug.c -->
# File Research: sources/block-storage/lvm2/libdm/mm/pool-debug.c

## Summary
Debug implementation of libdm memory pools. It allocates every pool block separately, tracks per-pool allocation statistics, supports growable temporary objects, and favors correctness checks over allocation efficiency.

## Main Responsibilities
- Creates and destroys `dm_pool` objects.
- Allocates, frees, and empties pool blocks.
- Implements grow/end/abandon object construction.
- Tracks debug statistics for bytes, blocks, maximums, and serial numbers.
- Adds pools to the global pool list for leak checking.

## Key APIs Implemented
- `dm_pool_create()`
- `dm_pool_destroy()`
- `dm_pool_alloc()`
- `dm_pool_alloc_aligned()`
- `dm_pool_empty()`
- `dm_pool_free()`
- `dm_pool_begin_object()`
- `dm_pool_grow_object()`
- `dm_pool_end_object()`
- `dm_pool_abandon_object()`

## Important Behavior
Each allocation creates a `struct block` with separate `data`, then appends it to the pool's block list. `dm_pool_free()` finds the block whose `data` matches the pointer and frees that block plus all later blocks, matching stack-like pool semantics.

Object construction repeatedly allocates a larger temporary block, copies the previous object content, frees the previous temporary block, and appends the final object as a normal pool block at `dm_pool_end_object()`.

Alignment is effectively ignored except for an assertion that requested alignment does not exceed default double alignment.

## State and Lifetime
`struct dm_pool` stores block list pointers, current object state, debug stats, lock state, and global-list linkage. Blocks are freed in list order starting from the selected free point.

## Risks
`dm_pool_abandon_object()` frees only the `struct block` header and not `p->object->data`, which is notable in this debug implementation. Alignment support is incomplete by design. Locking/protection CRC helpers are stubs or warnings in this variant.
<!-- END FILE RESEARCH: sources/block-storage/lvm2/libdm/mm/pool-debug.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/libdm/mm/pool-fast.c -->
# File Research: sources/block-storage/lvm2/libdm/mm/pool-fast.c

## Summary
Fast implementation of libdm memory pools. It allocates chunks, bumps a cursor for pool allocations, supports stack-style rewind, one spare chunk, growable objects, optional Valgrind annotations, and optional mprotect-based pool locking support.

## Main Responsibilities
- Creates pools with chunk sizes rounded up to a power of two.
- Allocates aligned memory by bumping the current chunk pointer.
- Rewinds/free chunks back to a pointer.
- Constructs variable-length objects within pool chunks, moving to larger chunks when necessary.
- Computes a checksum over allocated pool memory when lock checking is enabled.
- Protects chunks with `mprotect()` when `DEBUG_ENFORCE_POOL_LOCKING` is configured.

## Key APIs Implemented
- `dm_pool_create()`
- `dm_pool_destroy()`
- `dm_pool_alloc()`
- `dm_pool_alloc_aligned()`
- `dm_pool_empty()`
- `dm_pool_free()`
- `dm_pool_begin_object()`
- `dm_pool_grow_object()`
- `dm_pool_end_object()`
- `dm_pool_abandon_object()`

## Important Behavior
The current chunk is a LIFO stack. If the current chunk lacks room, `_new_chunk()` either reuses the one-entry `spare_chunk` or allocates a new chunk and links it as the current head.

`dm_pool_free()` searches for the chunk containing `ptr`, sets that chunk's begin pointer to `ptr`, moves newer chunks through the spare slot/free path, and makes the containing chunk current.

`dm_pool_begin_object()` reserves object state at the current aligned begin pointer. `dm_pool_grow_object()` appends bytes to the in-progress object and moves the object into a new chunk if the current one lacks space. `dm_pool_end_object()` advances the chunk begin by `object_len` and returns the object's starting pointer.

Valgrind hooks mark pool memory no-access when free/reserved and undefined when handed to callers.

## State and Lifetime
`struct dm_pool` stores the current chunk, one spare chunk, name, chunk size, in-progress object length/alignment, lock flag, and CRC. Pools are linked into the global `_dm_pools` list under `_dm_pools_mutex`.

## Risks
Pool frees are stack-style; freeing an old pointer discards all allocations made after it. Pointer containment checks are strict and log internal errors when the pointer is not in any chunk. The CRC implementation is a lightweight checksum, not a cryptographic integrity check.
<!-- END FILE RESEARCH: sources/block-storage/lvm2/libdm/mm/pool-fast.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/libdm/mm/pool.c -->
# File Research: sources/block-storage/lvm2/libdm/mm/pool.c

## Summary
Top-level memory-pool module that defines global pool tracking, selects debug or fast pool implementation, adds convenience allocation helpers, checks unreleased pools, and implements pool lock/unlock wrappers.

## Main Responsibilities
- Owns the global `_dm_pools` list and `_dm_pools_mutex`.
- Includes `pool-debug.c` when `DEBUG_POOL` is set, otherwise `pool-fast.c`.
- Provides `dm_pool_strdup()`, `dm_pool_strndup()`, and `dm_pool_zalloc()`.
- Reports unreleased memory pools with `dm_pools_check_leaks()`.
- Exposes `dm_pool_locked()`, `dm_pool_lock()`, and `dm_pool_unlock()`.
- Defines page-alignment helpers for `DEBUG_ENFORCE_POOL_LOCKING`.

## Key APIs
- `dm_pool_strdup()`
- `dm_pool_strndup()`
- `dm_pool_zalloc()`
- `dm_pools_check_leaks()`
- `dm_pool_locked()`
- `dm_pool_lock()`
- `dm_pool_unlock()`

## Important Behavior
`DEBUG_POOL` and `DEBUG_ENFORCE_POOL_LOCKING` are mutually exclusive. `DEBUG_ENFORCE_POOL_LOCKING` uses page-aligned chunks and `mprotect()` in the fast implementation to catch writes to locked pools.

`dm_pool_lock()` optionally records a pool checksum, protects memory read-only, marks the pool locked, and logs debug memory state. `dm_pool_unlock()` restores write protection and optionally compares the checksum.

`dm_pools_check_leaks()` reports all pools still present in `_dm_pools`; debug builds include tracked byte counts, while fast builds report pool pointers and names.

## State and Lifetime
The file-level pool list is static and shared by whichever implementation is included. Pools add/remove themselves in implementation-specific create/destroy paths.

## Risks
The implementation is assembled by textual inclusion of either `pool-debug.c` or `pool-fast.c`, so static helper names and globals are shared in one translation unit. Locking support depends on implementation-specific `_pool_crc()` and `_pool_protect()` behavior.
<!-- END FILE RESEARCH: sources/block-storage/lvm2/libdm/mm/pool.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/libdm/raid/raid_parser.c -->
# File Research: sources/block-storage/lvm2/libdm/raid/raid_parser.c

## Summary
Reads and optionally clears failed-device bitmaps in dm-raid metadata superblocks stored on RAID metadata volumes. It understands the original and v1.9.0-extended dm-raid superblock layout enough to count or clear failed-device flags.

## Main Responsibilities
- Defines the relevant on-disk dm-raid superblock fields and constants.
- Detects whether extended v1.9.0 failed-device bitmap fields are present.
- Counts set bits in failed-device fields.
- Opens a metadata volume with direct I/O, reads the first 4 KiB, validates the dm-raid magic, and optionally writes a cleared superblock back.

## Key APIs
- `dm_raid_count_failed_devices()`
- `dm_raid_clear_failed_devices()`

## Important Behavior
The superblock magic is `"DmRd"` and compatible feature flag `FEATURE_FLAG_SUPPORTS_V190` indicates that extended fields are present. `_get_sb_size()` uses that flag to choose either the pre-extension size or the full struct size.

Counting starts with the legacy `failed_devices` field. For extended superblocks, it iterates `extended_failed_devices` and keeps the maximum hweight observed rather than summing all words.

Clearing zeroes `failed_devices`, all extended failed-device words when present, and all bytes after the meaningful superblock size in the 4 KiB I/O buffer before writing.

## State and Lifetime
Each operation allocates a 4 KiB aligned buffer with `posix_memalign()`, opens the metadata path with `O_EXCL | O_DIRECT` and either read-only or read-write mode, then closes and frees everything before returning.

## Risks
The source comments call out endianness uncertainty around magic validation. The copied superblock layout is intentionally trimmed and may drift from kernel `drivers/md/dm-raid.c`. Clearing writes the first 4 KiB of the metadata device and should only be used on the intended rmeta volume.
<!-- END FILE RESEARCH: sources/block-storage/lvm2/libdm/raid/raid_parser.c -->