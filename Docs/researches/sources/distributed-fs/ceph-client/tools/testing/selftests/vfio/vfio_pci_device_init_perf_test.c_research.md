<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/vfio/vfio_pci_device_init_perf_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/vfio/vfio_pci_device_init_perf_test.c

## Purpose
Measures parallel VFIO PCI device initialization latency across one or more BDFs and all IOMMU modes.

## Important APIs, Types, and Functions
thread_main, timespec helpers, fixture with pthread_barrier, TEST_F init.

## Control Flow
Parses multiple BDFs, initializes one shared IOMMU, starts one thread per device behind a barrier, times vfio_pci_device_init per thread, joins, cleans devices, and prints wall/min/max/avg timing.

## State and Persistence
Creates threads, a barrier, one shared IOMMU, and transient VFIO device objects.

## Dependencies and Integration Points
Depends on pthreads, libvfio, multiple prepared devices for useful measurements, and kselftest harness.

## Risks and Edge Cases
This is performance/reporting, not pass/fail threshold; shared IOMMU setup races are intentionally allowed by libvfio container setup.

## Test Signals
Signal is printed timing data with successful device init/cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/vfio/vfio_pci_device_init_perf_test.c -->
