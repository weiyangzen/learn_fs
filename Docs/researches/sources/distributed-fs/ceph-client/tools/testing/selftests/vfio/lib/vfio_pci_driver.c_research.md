<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/vfio/lib/vfio_pci_driver.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/vfio/lib/vfio_pci_driver.c

## Purpose
Implements generic dispatch and state validation for selected VFIO PCI driver backend operations.

## Important APIs, Types, and Functions
driver_ops array, vfio_pci_driver_probe/init/remove/memcpy_start/memcpy_wait/memcpy/send_msi, vfio_check_driver_op.

## Control Flow
Probes available x86 backends, stores the matching ops, asserts correct initialized/memcpy_in_progress state before each operation, delegates to backend hooks, and updates progress flags.

## State and Persistence
State is embedded in device->driver and tracks ops selection plus lifecycle/progress booleans.

## Dependencies and Integration Points
Depends on DSA/IOAT ops on x86 and libvfio assertions.

## Risks and Edge Cases
If multiple probes match, the last match wins; no backend on non-x86 means driver operation tests must skip/fail appropriately.

## Test Signals
Driver tests exercise init/remove, memcpy paths, MSI, and mixed-device behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/vfio/lib/vfio_pci_driver.c -->
