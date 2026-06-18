# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/eeh/eeh-basic.sh

## Purpose
Runs basic EEH injection/recovery against PCI devices that are safe and recoverable.

## Important APIs, Types, and Functions
Sources `eeh-functions.sh`; uses `eeh_test_prep`, iterates `/sys/bus/pci/devices`, checks `eeh_can_break`, `eeh_can_recover`, and calls `eeh_one_dev`.

## Control Flow
After preparation, each eligible non-bridge/non-excluded PCI function is broken through debugfs, checked, waited for recovery, and logged.

## State and Persistence
Mutates hardware error state through EEH debugfs and may temporarily disrupt PCI devices. No files are intended to persist beyond sysfs/debugfs writes.

## Dependencies and Integration Points
Depends on PowerPC EEH support, mounted debugfs, PCI sysfs, and recovery-capable drivers.

## Risks and Test Signals
Risk is device disruption, especially drivers without recovery. Skip/fail/pass signals come from helper return codes and recovery timeout.
