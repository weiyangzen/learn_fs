# sources/distributed-fs/lizardfs/cmake/Libraries.cmake

## Purpose
This module discovers external libraries, tools, and optional bundled components used by the LizardFS build.

## Important APIs, Types, and Functions
It conditionally finds GTest for tests, requires `fmt`, `spdlog`, sockets, threads, and FUSE/FUSE3 on non-MinGW, detects `rt`, tcmalloc, jemalloc, `a2x`, zlib, systemd via pkg-config, Boost, Thrift, Polonaise, crcutil, Judy, PAM, Berkeley DB, ISA-L, and optional NFS-Ganesha/ntirpc downloads.

## Control Flow and State
The module is configure-time dependency orchestration. It sets feature macros and variables such as `LIZARDFS_HAVE_ZLIB_H`, `LIZARDFS_HAVE_SYSTEMD_SD_DAEMON_H`, `HAVE_CRCUTIL`, `CRCUTIL_LIBRARIES`, `CRCUTIL_INCLUDE_DIRS`, `LIZARDFS_HAVE_JUDY`, and `LIZARDFS_HAVE_PAM`. It fatals when mutually exclusive allocators are both enabled, when required fmt/spdlog/socket/thread/FUSE dependencies are missing, or when request-specific dependencies are unavailable elsewhere.

## Dependencies and Integration Points
Top-level `CMakeLists.txt` includes this before adding subdirectories. It integrates with local find modules, `DownloadExternal`, pkg-config, Boost CMake files, and external bundled `crcutil`. Variables feed `config.h.in`, link libraries, include directories, and optional subdirectory behavior.

## Risks and Edge Cases
Dependency policy is mixed: some missing packages are fatal, others only log optional support. FUSE is mandatory on non-MinGW even if a build might not need the mount client. Bundled crcutil is enabled on little-endian systems when system libcrcutil is absent. Optional NFS-Ganesha triggers network downloads into the source tree. Allocator options are manually exclusive.

## Test Signals
Configure logs are detailed signals. Build success of subsystem targets validates include/link propagation. Enabling tests validates GTest; enabling docs validates `a2x`; enabling NFS-Ganesha validates download and external build paths.
