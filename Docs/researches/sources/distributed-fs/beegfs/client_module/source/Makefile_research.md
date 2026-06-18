## sources/distributed-fs/beegfs/client_module/source/Makefile

### Purpose
Kernel-build Makefile for the BeeGFS client module source tree. It runs feature detection, sets compiler flags, declares the module object, and lists all C sources compiled into the module.

### Important APIs, Types, and Functions
- `BEEGFS_CLIENT_BUILDDIR` locates the adjacent build directory.
- `BEEGFS_FEATURE_DETECTION` invokes `feature-detect-cacher.sh` and `feature-detect.sh` with kernel build flags.
- Fails the build unless feature detection ends with `--~~success~~--`.
- Adds feature-detection output and `BEEGFS_CFLAGS` to `ccflags-y`.
- Helper variables/functions compute kernel version and conditionally add flags.
- `obj-m += ${TARGET}.o` declares the module.
- `SOURCES` enumerates all C files for networking, messages, filesystem ops, threading, node stores, caches, components, and app/config/logging.
- `${TARGET}-y` maps sources to objects.
- `BEEGFS_NO_RDMA` adds a compile define.
- `OFED_INCLUDE_PATH` adds OFED include paths and compatibility include flags; kernel >= 4.18 gets `HAVE_BITS_H`.

### Control Flow and State
This is evaluated by Kbuild. Feature detection happens at make evaluation time. The object list controls module composition. Optional RDMA/OFED branches adjust compilation based on environment.

### Dependencies and Integration Points
Depends on Linux kernel Kbuild variables, BeeGFS feature-detection scripts, OFED headers when configured, and the full client source tree. Invoked by DKMS, CMake external build, and direct make flows.

### Risks and Edge Cases
Feature-detection output is injected into compiler flags; incorrect shell quoting can break builds, which the header comment says was a known issue. The source list is manual and can omit new files. Kernel-version helper only uses major/patchlevel formatting and may be too coarse for distro backports. OFED compatibility includes can conflict with kernel headers.

### Test Signals
Build matrix tests across supported kernels, with/without RDMA and OFED, are the primary signal. Feature-detect script output should be cached and validated.
