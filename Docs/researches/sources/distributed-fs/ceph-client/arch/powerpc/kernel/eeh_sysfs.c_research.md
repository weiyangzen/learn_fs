<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/eeh_sysfs.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/kernel/eeh_sysfs.c

## Purpose
`eeh_sysfs.c` exposes per-PCI-device EEH attributes through sysfs. It lets users inspect EEH mode, PE config address, platform and kernel PE state, manually unfreeze an isolated PE, and optionally notify resume for selected SR-IOV pSeries devices.

## Important APIs, Types, And Functions
Macro `EEH_SHOW_ATTR` creates read-only `eeh_mode` and `eeh_pe_config_addr`. Functions implement `eeh_pe_state_show()`, `eeh_pe_state_store()`, optional `eeh_notify_resume_show/store/add/remove()`, `eeh_sysfs_add_device()`, and `eeh_sysfs_remove_device()`.

## Control Flow
Add skips when EEH is disabled or attributes were already added, then creates mode, config address, PE state, and optional notify-resume files. `eeh_pe_state_show()` returns platform `get_state` and kernel PE state bits. Store ignores non-isolated PEs, otherwise unfreezes the PE and clears isolated state. Notify-resume files are added only for pSeries Open SR-IOV physical-function-related nodes and call `eeh_ops->notify_resume()`.

## State And Persistence
Sysfs files reflect runtime `eeh_dev` and `eeh_pe` state. `EEH_DEV_SYSFS` tracks file creation. Writes can mutate PE isolation state but are not persistent across reboot.

## Dependencies And Integration Points
It integrates with PCI device sysfs, EEH core state APIs, OF node properties, SR-IOV/pSeries platform behavior, and `eeh_probe_device()`/`eeh_remove_device()`.

## Risks
Manual unfreeze can interfere with recovery if used at the wrong time. Removal must tolerate already-removed parent kobjects. Optional notify-resume depends on platform callbacks and specific OF properties.

## Test Signals
Signals include sysfs attribute creation/removal during PCI probe/hotplug, correct state formatting, successful manual unfreeze of isolated PEs, no stale files after device removal, and notify-resume behavior on Open SR-IOV PFs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/eeh_sysfs.c -->
