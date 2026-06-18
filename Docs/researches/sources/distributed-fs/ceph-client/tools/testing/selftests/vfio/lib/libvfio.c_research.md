<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/vfio/lib/libvfio.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/vfio/lib/libvfio.c

## Purpose
Implements shared libvfio utilities for BDF parsing/selection and aligned virtual-address reservation.

## Important APIs, Types, and Functions
is_bdf, get_bdfs_cmdline, get_bdf_env, vfio_selftests_get_bdfs/get_bdf, mmap_reserve.

## Control Flow
Parses trailing BDF argv entries or VFIO_SELFTESTS_BDF, skips with instructions if absent, and reserves an overlarge PROT_NONE mapping trimmed so returned address satisfies vaddr % align == offset.

## State and Persistence
BDF env pointer is stored static; mmap_reserve returns a reserved mapping caller must later map/unmap.

## Dependencies and Integration Points
Depends on mmap/munmap, ALIGN macro, kselftest skip code, and libvfio assertions.

## Risks and Edge Cases
BDF parser allows fixed hex widths and mutates argc; mmap_reserve pointer arithmetic assumes GNU C void* arithmetic.

## Test Signals
All VFIO tests use BDF selection; BAR misalignment test uses mmap_reserve.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/vfio/lib/libvfio.c -->
