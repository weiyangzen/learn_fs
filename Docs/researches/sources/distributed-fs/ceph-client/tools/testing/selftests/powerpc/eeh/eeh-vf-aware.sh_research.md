# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/eeh/eeh-vf-aware.sh

## Purpose
Tests EEH behavior for SR-IOV virtual functions whose drivers are EEH-aware.

## Important APIs, Types, and Functions
Sources `eeh-functions.sh`; calls preparation, enables VFs, filters with `eeh_can_recover`, injects with `eeh_one_dev`, and disables VFs afterward.

## Control Flow
The script enables one VF per discovered PF, tests recoverable VFs, logs results, then tears VFs down.

## State and Persistence
Mutates `sriov_numvfs` and EEH state for selected devices.

## Dependencies and Integration Points
Depends on SR-IOV-capable hardware, pseries/platform support, EEH debugfs, and recovery-aware VF drivers.

## Risks and Test Signals
Risks are VF disruption and incomplete cleanup on abrupt exit. Signals are skip when no VFs, fail on unrecovered VF, and cleanup through `eeh_disable_vfs`.
