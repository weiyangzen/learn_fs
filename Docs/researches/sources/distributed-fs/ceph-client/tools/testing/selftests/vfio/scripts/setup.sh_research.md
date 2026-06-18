<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/vfio/scripts/setup.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/vfio/scripts/setup.sh

## Purpose
Prepares PCI devices for VFIO selftests by disabling VFs, unbinding current drivers, setting vfio-pci override, and binding vfio-pci.

## Important APIs, Types, and Functions
main, get_sriov_numvfs, set_sriov_numvfs, get_driver, unbind, set_driver_override, bind.

## Control Flow
For each BDF, verifies sysfs device exists, records original SR-IOV VF count and driver, disables VFs, unbinds original driver, sets driver_override to vfio-pci, binds vfio-pci, and writes marker files for cleanup.

## State and Persistence
Persists original state under TMPDIR/vfio-selftests-devices/BDF and mutates PCI sysfs binding and sriov_numvfs.

## Dependencies and Integration Points
Depends on bash, root privileges, vfio-pci driver, PCI sysfs, and lib.sh.

## Risks and Edge Cases
Interruption can leave devices bound to vfio-pci until cleanup.sh runs; already-setup BDF exits early.

## Test Signals
Successful setup creates marker files consumed by run.sh and cleanup.sh.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/vfio/scripts/setup.sh -->
