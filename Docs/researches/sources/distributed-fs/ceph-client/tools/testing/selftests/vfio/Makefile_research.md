<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/vfio/Makefile -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/vfio/Makefile

## Purpose
Builds VFIO selftests and the libvfio support library on supported architectures.

## Important APIs, Types, and Functions
ARCH gate, TEST_GEN_PROGS, TEST_FILES scripts, lib/libvfio.mk, object link rule.

## Control Flow
Skips program generation on unsupported architectures; otherwise declares DMA mapping, iommufd, PCI device, driver, and perf tests, installs setup/run/cleanup scripts, compiles each test object with LIBVFIO_O, and tracks dependency files.

## State and Persistence
No runtime state; build outputs and dep files are cleaned via EXTRA_CLEAN.

## Dependencies and Integration Points
Depends on kselftest lib.mk, kernel headers, pthread, and libvfio.mk.

## Risks and Edge Cases
Only aarch64/arm64/x86_64 are enabled; Makefile references tests outside this work item too.

## Test Signals
Successful build of listed TEST_GEN_PROGS and scripts copied as TEST_FILES.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/vfio/Makefile -->
