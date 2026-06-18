<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/vfio/scripts/lib.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/vfio/scripts/lib.sh

## Purpose
Shared shell functions for VFIO setup/cleanup scripts.

## Important APIs, Types, and Functions
DEVICES_DIR, write_to, get_driver, bind, unbind, set/get_sriov_numvfs, set/clear_driver_override.

## Control Flow
Wraps sysfs writes with echoed commands and provides small helpers to inspect and mutate PCI driver/SR-IOV state.

## State and Persistence
Uses TMPDIR/vfio-selftests-devices as persistent script state root; writes directly to /sys/bus/pci.

## Dependencies and Integration Points
Depends on bash, readlink, basename, cat, and PCI sysfs.

## Risks and Edge Cases
No error handling beyond shell failures in callers; variables are mostly unquoted.

## Test Signals
Setup/cleanup scripts rely on these helpers for reversible device preparation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/vfio/scripts/lib.sh -->
