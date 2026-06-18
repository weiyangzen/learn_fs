# sources/distributed-fs/ceph-client/kernel/gcov/gcc_4_7.c

## Purpose
`gcc_4_7.c` implements the compiler-specific gcov backend for GCC 4.7 and newer profiling layouts. It understands GCC-generated `gcov_info`, function metadata, active counter arrays, GCC-version-dependent counter counts and record-size units, and converts live profiling data into gcda format for the generic debugfs exporter.

## Important APIs, types, and functions
Private types are `struct gcov_ctr_info`, `struct gcov_fn_info`, and `struct gcov_info`, matching GCC's generated layout for the compiler version in use. The global list head is `gcov_info_head`. Public helpers include `gcov_info_filename()`, `gcov_info_version()`, `gcov_info_next()`, `gcov_info_link()`, `gcov_info_unlink()`, `gcov_info_within_module()`, `gcov_info_reset()`, `gcov_info_is_compatible()`, `gcov_info_add()`, `gcov_info_dup()`, `gcov_info_free()`, and `convert_to_gcda()`.

## Control flow
Compiler constructor code registers `gcov_info` through the base file, which links objects into the singly linked list here. Reset walks every instrumented function and active counter type, zeroing counter arrays. Duplication deep-copies the object filename, function pointer array, per-function metadata, and active counter value arrays. Addition walks matching functions and active counter types to accumulate counts. `convert_to_gcda()` serializes file header, optional GCC 12+ checksum field, function records, and all active counter records with proper GCC unit sizing.

## State and persistence
Live `gcov_info` objects are compiler-generated static data; only their `next` pointer and counter values change at runtime. Deep copies created for debugfs readers or unload persistence own duplicated filenames, function info, and counter arrays. Compatibility is based on `stamp`, so saved data persists only across reloads with the same compile stamp. No persistent storage is written by this file.

## Dependencies and integration points
This backend is selected by build configuration for GCC coverage and is consumed by `gcc_base.c` and `fs.c` through `gcov.h`. It depends on exact GCC layout compatibility, compiler version macros, kernel allocation helpers, and gcov record constants. `gcov_link[]` provides `.gcno` symlink metadata for the debugfs layer.

## Risks and test signals
Risks include GCC layout drift, incorrect `GCOV_COUNTERS` values for a new compiler, GCC 12 byte-versus-word record-size handling, compatibility based only on `stamp`, active-counter traversal mismatches between source and destination, and large allocations during duplication. Test signals include coverage builds across supported GCC versions, gcda parsing by matching `gcov`, unload/reload accumulation, reset of all active counter kinds, GCC 12+ output checksum field handling, and failure injection in `gcov_info_dup()`.
