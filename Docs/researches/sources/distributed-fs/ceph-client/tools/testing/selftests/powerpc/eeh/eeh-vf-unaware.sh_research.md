# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/eeh/eeh-vf-unaware.sh

## Purpose
Tests EEH handling for SR-IOV VFs without driver recovery callbacks or awareness.

## Important APIs, Types, and Functions
Sources `eeh-functions.sh`; prepares EEH, enables VFs, selects cases based on recovery capability, invokes EEH injection, then disables VFs.

## Control Flow
Flow mirrors the VF-aware test but targets devices expected to exercise remove/reprobe or non-aware recovery paths.

## State and Persistence
Mutates VF enablement and EEH/debugfs device state.

## Dependencies and Integration Points
Depends on SR-IOV PF discovery, PCI sysfs, EEH debugfs, and helper filtering.

## Risks and Test Signals
Risks include device removal/reprobe side effects and cleanup failure. Test signal is whether the platform recovers or skips unsuitable VFs.
