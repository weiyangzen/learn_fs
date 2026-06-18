<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/vfio/scripts/cleanup.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/vfio/scripts/cleanup.sh

## Purpose
Restores PCI devices modified by VFIO selftest setup back to their prior drivers/SR-IOV state.

## Important APIs, Types, and Functions
cleanup_devices, main, unbind, clear_driver_override, bind, set_sriov_numvfs from lib.sh.

## Control Flow
For each recorded BDF, unbinds vfio-pci if setup bound it, clears driver_override, rebinds the saved original driver, restores sriov_numvfs, and removes the device record directory; with no args, cleans every recorded device.

## State and Persistence
Reads and deletes state under TMPDIR/vfio-selftests-devices; mutates sysfs driver binding and SR-IOV settings.

## Dependencies and Integration Points
Depends on bash, lib.sh, sysfs PCI driver files, and setup.sh-created marker files.

## Risks and Edge Cases
Unquoted paths/variables assume simple BDF names; rebinding the old driver may fail if hardware state changed.

## Test Signals
Successful cleanup removes the devices directory and restores previous bindings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/vfio/scripts/cleanup.sh -->
