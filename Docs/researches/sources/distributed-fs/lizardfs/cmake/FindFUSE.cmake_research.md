# sources/distributed-fs/lizardfs/cmake/FindFUSE.cmake

## Purpose
This find module locates FUSE 2.x libraries and headers, with separate handling for Apple/pkg-config and non-Apple layouts.

## Important APIs, Types, and Functions
It sets `FUSE_LIBRARY`, `FUSE_LIBRARY_DIR`, `FUSE_INCLUDE_DIR`, `FUSE_CFLAGS`, `FUSE_CFLAGS_OTHER`, and `FUSE_VERSION_STRING` when possible. On Apple it uses `pkg_check_modules(PC_FUSE fuse)` and searches for `fuse.h`. Elsewhere it finds `libfuse` and `fuse/fuse.h`, then reads `fuse_common.h` for major/minor versions.

## Control Flow and State
The module's control path depends on `APPLE`. Version extraction only occurs when an include directory is discovered. `find_package_handle_standard_args` enforces library and include presence for `FUSE_FOUND`.

## Dependencies and Integration Points
`Libraries.cmake` requires FUSE or FUSE3 for non-MinGW builds, and top-level `CMakeLists.txt` adds `src/mount/fuse` when either is found. Link directories include `${FUSE_LIBRARY_DIR}`.

## Risks and Edge Cases
Header layout assumptions differ between platforms. On non-Apple, the module rewrites `FUSE_INCLUDE_DIR` to append `/fuse`, which consumers must expect. pkg-config is required on Apple. No imported target is created.

## Test Signals
Configure reports FUSE discovery. Missing both FUSE and FUSE3 is fatal on non-MinGW. FUSE mount target compile/link success validates include and library variables.
