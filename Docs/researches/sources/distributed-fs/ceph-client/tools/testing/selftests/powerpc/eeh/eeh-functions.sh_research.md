# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/eeh/eeh-functions.sh

## Purpose
Shared shell library for EEH support detection, PE state checks, device break/recovery, and SR-IOV VF setup/cleanup.

## Important APIs, Types, and Functions
Defines `log`, `pe_ok`, `eeh_supported`, `eeh_test_prep`, `eeh_can_break`, `eeh_one_dev`, `eeh_has_driver`, `eeh_can_recover`, `eeh_find_all_pfs`, `eeh_enable_vfs`, and `eeh_disable_vfs`.

## Control Flow
Helpers check `/proc/powerpc/eeh`, verify debugfs controls, raise max freeze count, reject bridges/ahci/bad PE state, inject EEH errors, poll recovery up to `EEH_MAX_WAIT`, discover SR-IOV PFs, enable one VF per PF, and disable VFs afterward.

## State and Persistence
State is hardware/sysfs/debugfs state: EEH freeze counters, PE isolation/recovery state, and `sriov_numvfs` changes. No ordinary files are persisted.

## Dependencies and Integration Points
Depends on PCI sysfs, PowerPC EEH debugfs files, pseries RTAS indicators for SR-IOV, shell utilities, and kselftest skip code 4.

## Risks and Test Signals
Risks are substantial because it intentionally breaks PCI devices. The helper mitigates by skipping bridges, ahci, unsupported recovery, and bad initial PE states; failures are recovery timeout, missing controls, or unsafe device rejection.
