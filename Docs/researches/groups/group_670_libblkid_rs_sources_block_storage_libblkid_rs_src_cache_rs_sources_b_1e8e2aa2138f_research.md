# Group Research: group_670_libblkid_rs_sources_block_storage_libblkid_rs_src_cache_rs_sources_b_1e8e2aa2138f

Scope: `Docs/research_subset_a.md` includes `sources/block-storage/libblkid-rs`. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/block-storage/libblkid-rs/src/cache.rs -->
# File Research: sources/block-storage/libblkid-rs/src/cache.rs

Purpose: Defines `BlkidCache`, the high-level Rust handle for libblkid cache operations.

Key APIs:
- `get_cache`, `put_cache`, `gc_cache`
- block-device probing: `probe_all`, `probe_all_new`, `probe_all_removable`
- cache lookups: `get_dev`, `get_tag_value`, `get_devname`, `find_dev_with_tag`, `verify`
- cached-device iteration through `BlkidDevIter`

Implementation notes:
- Wraps `libblkid_rs_sys::blkid_cache` plus a boolean tracking whether `blkid_put_cache` has already been called.
- Converts Rust strings/paths into `CString`; non-UTF-8 paths are rejected through `BlkidErr::InvalidConv`.
- Frees strings returned by libblkid with `libc::free`.

Notable risks:
- `put_cache(&mut self)` frees/releases the C cache but does not consume `self`; later method calls can use a stale pointer.
- `Drop` calls raw `free()` when `put_cache` was not called, instead of a libblkid-specific release API. If the cache owns nested allocations, this risks incomplete cleanup.
- `get_dev` wraps the returned pointer without a null check, so a null `blkid_dev` can enter safe Rust as `BlkidDev`.
<!-- END FILE RESEARCH: sources/block-storage/libblkid-rs/src/cache.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/libblkid-rs/src/consts.rs -->
# File Research: sources/block-storage/libblkid-rs/src/consts.rs

Purpose: Defines typed Rust enums and flag-set wrappers for libblkid integer constants.

Key APIs:
- Device cache flags: `BlkidDevFlag`, `BlkidDevFlags`
- Usage flags: `BlkidUsageFlag`, `BlkidUsageFlags`
- Superblock flags: `BlkidSublks`, `BlkidSublksFlags`
- Filter constants: `BlkidFltr`
- Probe return enums: `BlkidProbeRet`, `BlkidSafeprobeRet`, `BlkidFullprobeRet`
- Probe request flags: `BlkidProbreqFlag`, `BlkidProbreqFlags`

Implementation notes:
- Uses `consts_enum_conv!` and `flags!` macros from `macros.rs`.
- Constants are mostly direct casts from `libblkid_rs_sys`.

Notable risks:
- `BlkidSublks::Uuidraw` maps to `BLKID_SUBLKS_UUID`; it likely should map to `BLKID_SUBLKS_UUIDRAW`.
- Flag parsing depends on the `flags!` macro, whose `TryFrom` implementation appears to reject unset bits by trying to convert `0` repeatedly.
- Documentation for `BlkidUsageFlags` says it is a set of `BlkidDevFlag`, but it actually wraps `BlkidUsageFlag`.
<!-- END FILE RESEARCH: sources/block-storage/libblkid-rs/src/consts.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/libblkid-rs/src/deprecated.rs -->
# File Research: sources/block-storage/libblkid-rs/src/deprecated.rs

Purpose: Adds deprecated libblkid filter methods onto `BlkidProbe` behind the crate’s `deprecated` feature.

Key APIs:
- `filter_usage`
- `filter_types`
- `invert_filter`
- `reset_filter`

Implementation notes:
- Mirrors old libblkid APIs and routes errors through `errno!`.
- Converts `&[&str]` into a null-terminated C pointer array for type filters.

Notable risks:
- The string-list conversion is duplicated from newer probe filter methods.
- Any `CString::new` failure is collapsed to `InvalidConv`, losing the original nul-byte location.
- Deprecated methods remain public when the feature is enabled, so behavior should stay aligned with libblkid compatibility expectations.
<!-- END FILE RESEARCH: sources/block-storage/libblkid-rs/src/deprecated.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/libblkid-rs/src/dev.rs -->
# File Research: sources/block-storage/libblkid-rs/src/dev.rs

Purpose: Wraps cached libblkid device handles and device iteration.

Key APIs:
- `BlkidDev::devname`
- `BlkidDev::devsize`
- `BlkidDev::tag_iter`
- `BlkidDev::has_tag`
- `BlkidDevIter::search`
- `Iterator for BlkidDevIter`

Implementation notes:
- `BlkidDev` is a non-owning wrapper around `blkid_dev`.
- `devsize` opens the device path and passes its file descriptor to `blkid_get_dev_size`.
- `BlkidDevIter` owns the C iterator and ends it in `Drop`.

Notable risks:
- `BlkidDev::new` accepts null pointers from callers; methods assume valid C handles.
- `Iterator::next` treats any negative return as end-of-iteration, so libblkid errors cannot be distinguished from normal completion.
- `devsize` depends on opening the device path, so cached devices that no longer exist or require privileges return I/O errors.
<!-- END FILE RESEARCH: sources/block-storage/libblkid-rs/src/dev.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/libblkid-rs/src/devno.rs -->
# File Research: sources/block-storage/libblkid-rs/src/devno.rs

Purpose: Provides a Rust newtype for device numbers and conversions between device numbers, major/minor values, device names, and whole-disk devices.

Key APIs:
- `from_device_numbers`
- `major`
- `minor`
- `to_devname`
- `to_wholedisk`

Implementation notes:
- Uses platform-specific `maj_t` and `min_t` aliases.
- Frees the string returned by `blkid_devno_to_devname`.

Notable risks:
- `to_wholedisk` converts the entire 4096-byte buffer with `std::str::from_utf8`, preserving trailing NUL bytes. It should read only up to the first NUL.
- No `ty` module is defined for Android because the cfgs cover Linux and non-Linux/non-Android Unix only.
- `to_wholedisk` uses a fixed buffer size matching the crate docs, but truncation behavior depends on libblkid.
<!-- END FILE RESEARCH: sources/block-storage/libblkid-rs/src/devno.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/libblkid-rs/src/encode.rs -->
# File Research: sources/block-storage/libblkid-rs/src/encode.rs

Purpose: Exposes libblkid string encoding helpers.

Key APIs:
- `encode_string`
- `safe_string`

Implementation notes:
- Shared helper allocates a buffer, calls the supplied C encoder, truncates at the first NUL, and converts to Rust `String`.
- Includes unit tests for basic escaping and whitespace replacement.

Notable risks:
- Buffer size is `string.len() * 4`; a fully escaped string may need an extra byte for the terminating NUL.
- Empty input creates a zero-length output buffer, which may fail even if libblkid would otherwise encode an empty string.
- Any nonzero C return is reported as `InvalidConv`.
<!-- END FILE RESEARCH: sources/block-storage/libblkid-rs/src/encode.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/libblkid-rs/src/err.rs -->
# File Research: sources/block-storage/libblkid-rs/src/err.rs

Purpose: Defines the crate-wide error type and `Result` alias.

Key APIs:
- `pub type Result<T> = std::result::Result<T, BlkidErr>`
- `BlkidErr` variants for FFI conversion, I/O, UTF-8, UUID, libblkid codes, and generic messages.

Implementation notes:
- `from_err!` generates `From` conversions for common standard-library errors.
- Implements `Display` and `std::error::Error`.

Notable risks:
- `uuid::Error` and `std::ffi::IntoStringError` are represented but do not have generated `From` implementations.
- `LibErr(0)` is used by `errno_ptr!` for null pointers, even though zero is not an actual negative libblkid error code.
- `PositiveReturnCode` assumes APIs wrapped by `errno!` should only return `0` or negative values.
<!-- END FILE RESEARCH: sources/block-storage/libblkid-rs/src/err.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/libblkid-rs/src/lib.rs -->
# File Research: sources/block-storage/libblkid-rs/src/lib.rs

Purpose: Crate root for the Rust libblkid binding.

Key APIs:
- Public re-exports for cache, constants, device wrappers, device numbers, encoding, errors, partitions, probes, tags, topology, utilities, version helpers, `Uuid`, and `blkid_loff_t`.

Implementation notes:
- Enforces `#![deny(missing_docs)]`.
- Keeps most implementation modules private while exposing selected public types and functions.
- Enables deprecated probe methods only behind the `deprecated` feature.

Notable risks:
- The public API is intentionally close to libblkid, so unsafe C ownership/lifetime rules leak into wrapper design.
- The crate-level docs mention modified behavior for `blkid_get_dev_size`, but the implementation exposes `BlkidDev::devsize` rather than a direct `&Path` function.
<!-- END FILE RESEARCH: sources/block-storage/libblkid-rs/src/lib.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/libblkid-rs/src/macros.rs -->
# File Research: sources/block-storage/libblkid-rs/src/macros.rs

Purpose: Provides internal macros for C string conversion, errno handling, pointer handling, enum conversion, and flag-set construction.

Key macros:
- `str_ptr_to_owned!`
- `str_ptr_with_size_to_owned!`
- `errno!`
- `errno_ptr!`
- `option_ptr!`
- `errno_with_ret!`
- `consts_enum_conv!`
- `flags!`

Implementation notes:
- `errno!` treats `0` as success, negatives as `LibErr`, and positives as `PositiveReturnCode`.
- `errno_ptr!` maps null pointers to `LibErr(0)`.
- `consts_enum_conv!` creates enum-to-integer and integer-to-enum conversions.
- `flags!` stores flag members in a `HashSet`.

Notable risks:
- `flags!::TryFrom` iterates over every bit and tries to convert `(1 << i) & v`; unset bits become `0`, which usually causes `InvalidConv`.
- `str_ptr_with_size_to_owned!` requires a NUL-terminated byte slice of exactly `size`; it is fragile if libblkid reports sizes excluding the terminator.
- Generated enums implement `Into` rather than `From`, which is less idiomatic and prevents blanket conversion ergonomics.
<!-- END FILE RESEARCH: sources/block-storage/libblkid-rs/src/macros.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/libblkid-rs/src/partition.rs -->
# File Research: sources/block-storage/libblkid-rs/src/partition.rs

Purpose: Wraps partition tables, partitions, and partition lists returned from probing.

Key APIs:
- `BlkidParttable`: `get_type`, `get_id`, `get_offset`, `get_parent`
- `BlkidPartition`: `get_table`, `get_name`, `get_uuid`, `get_partno`, `get_start`, `get_size`, `get_type`, `get_type_string`, `get_flags`, partition kind checks
- `BlkidPartlist`: count/table lookup and partition lookup by index, part number, or device number

Implementation notes:
- Uses `PhantomData` to tie handles to a probe/list lifetime at the type level.
- Converts partition UUID strings into `uuid::Uuid`.
- Sector and byte units use wrapper types from `utils.rs`.

Notable risks:
- Pointer wrappers are non-owning and assume libblkid keeps backing memory valid.
- `get_uuid` assumes returned UUID strings parse as canonical UUIDs.
- Several read-only `BlkidPartlist` methods take `&mut self`, which is stricter than necessary.
<!-- END FILE RESEARCH: sources/block-storage/libblkid-rs/src/partition.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/libblkid-rs/src/probe.rs -->
# File Research: sources/block-storage/libblkid-rs/src/probe.rs

Purpose: Implements the main probing interface over libblkid probe handles.

Key APIs:
- Probe creation and lifecycle: `new`, `new_from_filename`, `reset`, `reset_buffers`
- Device binding and metadata: `set_device`, `get_devno`, `get_wholedisk_devno`, `get_size`, `get_offset`, `get_sector_size`, `get_fd`
- Superblock, topology, and partition probing controls
- Probe execution: `do_probe`, `do_safeprobe`, `do_fullprobe`, `do_wipe`, `step_back`
- Value access: `numof_values`, `get_value`, `lookup_value`, `has_value`
- Global helpers: `is_known_fs_type`, `get_superblock_name`, `is_known_partition_type`, `get_partition_name`

Implementation notes:
- Owns `blkid_probe` and frees it in `Drop`.
- Builds null-terminated C string arrays for type filters.
- Returns borrowed partition/topology structures from libblkid probe state.

Notable risks:
- `get_superblock_name` ignores `get_name` and `get_flags` on return; if either was requested as false, it can still dereference null or convert unrequested flags.
- `get_value` formats `num_values - 1`; when there are zero values this can underflow.
- `get_topology` returns `BlkidTopology` without a lifetime tying it to the probe, allowing a topology handle to outlive the C backing state.
- `has_value` treats any nonzero C return as true, so negative error returns would be hidden if libblkid uses them there.
<!-- END FILE RESEARCH: sources/block-storage/libblkid-rs/src/probe.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/libblkid-rs/src/tag.rs -->
# File Research: sources/block-storage/libblkid-rs/src/tag.rs

Purpose: Implements tag iteration for devices and parsing of tag strings.

Key APIs:
- `BlkidTagIter`
- `parse_tag_string`

Implementation notes:
- `BlkidTagIter` owns the C iterator and ends it in `Drop`.
- Iterator items are `(String, String)` pairs.
- `parse_tag_string` calls libblkid to split a tag string into type and value.

Notable risks:
- `parse_tag_string` does not free `type_` and `value` returned through output pointers, which likely leaks libblkid-allocated strings.
- Iterator UTF-8 conversion failures are converted to `None`, making invalid data indistinguishable from end-of-iteration.
- `Iterator::next` asserts non-null pointers after a nonnegative return.
<!-- END FILE RESEARCH: sources/block-storage/libblkid-rs/src/tag.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/libblkid-rs/src/topology.rs -->
# File Research: sources/block-storage/libblkid-rs/src/topology.rs

Purpose: Wraps libblkid topology information for a probed device.

Key APIs:
- `get_alignment_offset`
- `get_minimum_io_size`
- `get_optimal_io_size`
- `get_logical_sector_size`
- `get_physical_sector_size`

Implementation notes:
- Thin read-only wrapper around `blkid_topology`.
- No ownership release is implemented, implying the probe owns the topology memory.

Notable risks:
- The type has no lifetime parameter tying it to `BlkidProbe`, even though `probe.rs` documents that topology state is overwritten by later probe calls.
- Methods assume the inner pointer remains valid.
<!-- END FILE RESEARCH: sources/block-storage/libblkid-rs/src/topology.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/libblkid-rs/src/utils.rs -->
# File Research: sources/block-storage/libblkid-rs/src/utils.rs

Purpose: Provides unit wrappers and convenience helpers for libblkid evaluation and uevent operations.

Key APIs:
- `BlkidSectors`
- `BlkidBytes`
- `send_uevent`
- `evaluate_tag`
- `evaluate_spec`

Implementation notes:
- Uses a fixed sector size of 512 for sector/byte conversion.
- `evaluate` shares implementation for parsed tag lookup and unparsed spec lookup.
- Frees strings allocated by `blkid_evaluate_tag` and `blkid_evaluate_spec`.

Notable risks:
- `send_uevent` uses `Path::display().to_string()`, which can be lossy for non-UTF-8 paths.
- `BlkidSectors::bytes` can overflow the underlying signed offset type for very large values.
- `BlkidBytes::sectors` rejects byte counts not divisible by 512, matching the wrapper’s fixed-sector abstraction.
<!-- END FILE RESEARCH: sources/block-storage/libblkid-rs/src/utils.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/libblkid-rs/src/version.rs -->
# File Research: sources/block-storage/libblkid-rs/src/version.rs

Purpose: Exposes libblkid version parsing and runtime library version lookup.

Key APIs:
- `parse_version_string`
- `get_library_version`

Implementation notes:
- Converts input version strings to `CString`.
- Reads version and release-date pointers returned by `blkid_get_library_version`.

Notable risks:
- `get_library_version` does not null-check returned version/date pointers before calling `CStr::from_ptr`.
- `parse_version_string` returns the raw integer result and does not classify invalid or sentinel values.
<!-- END FILE RESEARCH: sources/block-storage/libblkid-rs/src/version.rs -->