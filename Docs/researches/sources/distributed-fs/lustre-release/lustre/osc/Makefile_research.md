# sources/distributed-fs/lustre-release/lustre/osc/Makefile

## Purpose

This `Makefile` defines the Lustre OSC kernel module build composition. It adds `osc.o` to the module list and enumerates the object files linked into the Object Storage Client module. It also enables GCOV instrumentation for this subdirectory when `CONFIG_GCOV_PROFILE_LUSTRE` is set.

## Important APIs, Types, and Functions

There are no C APIs in this file. The important build variables are:

- `obj-m += osc.o`, which tells kbuild to build the OSC as a loadable module object.
- `osc-objs := ...`, which composes `osc.o` from request, lproc, device, object, page, lock, IO, quota, and cache implementation objects.
- `GCOV_PROFILE := y`, enabled conditionally for Lustre coverage builds.

## Control Flow

Kbuild reads the file while descending into `lustre/osc`. When building modules, it links `osc_request.o`, `lproc_osc.o`, `osc_dev.o`, `osc_object.o`, `osc_page.o`, `osc_lock.o`, `osc_io.o`, `osc_quota.o`, and `osc_cache.o` into `osc.o`. If the Lustre GCOV option is active, kbuild compiles this directory with coverage instrumentation.

## State and Persistence Behavior

The file has no runtime state. Its persistent effect is the module link contract: all listed objects become one OSC module. Adding, removing, or reordering object entries changes which OSC code is linked and can expose missing symbols or initialization-order assumptions at module load.

## Dependencies and Integration Points

It depends on Linux kernel kbuild semantics for `obj-m`, `<module>-objs`, and `GCOV_PROFILE`. It integrates with the rest of the Lustre build system and ensures `lproc_osc.c` is included in the OSC module along with the request, cache, IO, lock, and quota layers.

## Risks and Edge Cases

- A new OSC source file must be added here or it will compile nowhere in module builds.
- Removing `lproc_osc.o` would drop tunable/debugfs/sysfs registration code from the module.
- GCOV coverage depends on the conditional matching the top-level Lustre configuration; incorrect scoping can over-instrument or miss OSC files.

## Test Signals

Build tests should verify `osc.ko` links with all expected objects, `modpost` reports no missing OSC symbols, coverage builds produce GCOV data for OSC files when configured, and non-coverage builds leave `GCOV_PROFILE` unset.
