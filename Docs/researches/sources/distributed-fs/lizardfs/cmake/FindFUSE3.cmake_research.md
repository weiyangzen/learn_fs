# sources/distributed-fs/lizardfs/cmake/FindFUSE3.cmake

## Purpose
This find module locates FUSE 3 libraries and headers.

## Important APIs, Types, and Functions
It sets `FUSE3_LIBRARY`, `FUSE3_INCLUDE_DIR`, `FUSE3_VERSION_STRING`, and `FUSE3_FOUND`. It finds `libfuse3`, searches for `fuse3/fuse.h`, appends `/fuse3` to the include directory, reads `fuse_common.h`, extracts major/minor version macros, and uses `find_package_handle_standard_args`.

## Control Flow and State
The module is linear and only computes version information when the include directory is present. It does not configure compile definitions directly; callers consume the found variables.

## Dependencies and Integration Points
`Libraries.cmake` runs this alongside FUSE 2 discovery. Top-level build logic includes the FUSE mount implementation when either FUSE family is found.

## Risks and Edge Cases
The include path rewrite must match consumers' include style. Version parsing assumes upstream macro format. There is no pkg-config fallback, which may matter on systems where FUSE3 is installed in nonstandard locations.

## Test Signals
Configure-time `FUSE3_FOUND` and mount target compilation are the practical signals. Missing both FUSE modules is fatal outside MinGW.
