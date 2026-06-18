<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/vfio/lib/libvfio.mk -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/vfio/lib/libvfio.mk

## Purpose
Build fragment for libvfio object files and include paths.

## Important APIs, Types, and Functions
LIBVFIO_C, LIBVFIO_O, LIBVFIO_OUTPUT, object pattern rule, ARCH conditional x86 drivers.

## Control Flow
Includes subarch detection, lists common library C files, adds IOAT/DSA drivers for x86, creates output directories, adds lib include path, and compiles sources to OUTPUT/libvfio objects.

## State and Persistence
No runtime state; build state is object/dependency output under OUTPUT.

## Dependencies and Integration Points
Depends on top_srcdir scripts/subarch.include and kernel selftest make variables.

## Risks and Edge Cases
$(shell mkdir -p ...) runs at parse time; non-x86 builds omit device drivers so probing can find no backend.

## Test Signals
Successful link of VFIO tests against LIBVFIO_O.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/vfio/lib/libvfio.mk -->
