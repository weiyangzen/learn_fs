# sources/distributed-fs/glusterfs/libglusterfs/src/compat-errno.c

## Purpose
This file provides GlusterFS's errno compatibility translation layer. It maps native platform `errno` values to GlusterFS stable `GF_ERROR_CODE_*` values and back so errors can be serialized, compared, and transported across different operating systems without assuming that numeric errno assignments are identical.

## Important APIs, types, and functions
The public APIs are `gf_errno_to_error(int32_t op_errno)` and `gf_error_to_errno(int32_t error)`. They lazily initialize two static 1024-entry arrays, `gf_errno_to_error_array` and `gf_error_to_errno_array`, guarded only by the integer flag `gf_compat_errno_init_done`. `init_errno_arrays()` first installs identity mappings for `0..GF_ERROR_CODE_UNKNOWN-1`, then calls platform-specific `init_compat_errno_arrays()` implementations selected by `GF_SOLARIS_HOST_OS`, `GF_DARWIN_HOST_OS`, `GF_BSD_HOST_OS`, or `GF_LINUX_HOST_OS`.

## Control flow
Callers pass an errno or portable error code into one of the two conversion functions. Zero is returned immediately. On first nonzero use, arrays are initialized with identity mappings and then adjusted for platforms where errno ordering differs. Inputs inside the portable error-code range are looked up in the appropriate array; out-of-range values are returned unchanged.

## State and persistence behavior
All state is process-local static memory. The translation arrays persist for the lifetime of the process and are never reset. No disk persistence occurs. Initialization is lazy and non-atomic, so concurrent first calls can race while writing the same deterministic table values.

## Dependencies and integration points
The file depends on `glusterfs/compat-errno.h` for `GF_ERROR_CODE_*` constants and platform errno availability. It is used by dictionary serialization, RPC, translator callbacks, and other libglusterfs components that need portable error values in cross-platform messages.

## Risks and edge cases
The lazy initialization flag is not protected by a mutex or atomic primitive. The mappings are deterministic, but data race tooling can report this and weak memory models could observe partially initialized arrays. Array bounds depend on `GF_ERROR_CODE_UNKNOWN` staying below 1024 and native errno constants used as indexes also remaining below 1024. Platform blocks are long hand-maintained tables, so incorrect or missing mappings can silently degrade to identity behavior.

## Test signals
Useful tests should verify round-trip conversions for Linux identity behavior and for representative Solaris, Darwin, and BSD remaps under those build flags. Boundary tests should cover zero, negative values, `GF_ERROR_CODE_UNKNOWN`, and values above the mapping range. Thread sanitizer coverage of concurrent first use would exercise the known lazy-init race.
