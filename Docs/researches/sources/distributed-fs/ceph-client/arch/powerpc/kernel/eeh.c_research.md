<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/eeh.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/kernel/eeh.c

## Purpose
`eeh.c` is the core Enhanced Error Handling implementation for PowerPC PCI. It detects frozen PCI processing elements after all-ones MMIO reads, logs platform error detail, manages global EEH state, exposes reset/control APIs, supports pass-through ownership, and provides proc/debugfs diagnostics.

## Important APIs, Types, And Functions
Important globals are exported `eeh_subsystem_flags`, `eeh_max_freezes`, `eeh_debugfs_no_recover`, `eeh_ops`, `confirm_error_lock`, and `eeh_stats`. Key functions include `eeh_setup()`, `eeh_show_enabled()`, `eeh_slot_error_detail()`, `eeh_dev_check_failure()`, exported `eeh_check_failure()`, `eeh_pci_enable()`, `pcibios_set_pcie_reset_state()`, `eeh_pe_reset_full()`, `eeh_save_bars()`, `eeh_init()`, `eeh_probe_device()`, `eeh_remove_device()`, exported `eeh_unfreeze_pe()`, `eeh_dev_open()`, `eeh_dev_release()`, `eeh_iommu_group_to_pe()`, `eeh_pe_set_option()`, `eeh_pe_get_state()`, `eeh_pe_reset()`, `eeh_pe_configure()`, and `eeh_pe_inject_err()`.

## Control Flow
MMIO failure detection resolves the token to a physical address, looks up an `eeh_dev` in the address cache, checks PHB failure first, skips passed-through PEs, serializes duplicate reports, queries platform state, escalates to frozen parents when needed, marks the PE isolated, and queues an async recovery event. Reset APIs freeze or thaw MMIO/DMA, block config access during reset, restore BARs/config, and clear PE state. Probe/remove bind or unbind PCI devices to `eeh_dev`, sysfs, and address-cache state. Debugfs can enable/disable EEH, force recovery, trigger checks, inject MMIO errors, and report whether a driver supports recovery.

## State And Persistence
State is in-memory: global flags/statistics, PE state bits, per-device saved config space, address-cache entries, pass-through counters, and debugfs/procfs settings. No state persists across reboot.

## Dependencies And Integration Points
It integrates with platform `struct eeh_ops`, PCI hotplug, IOMMU groups, RTAS/OPAL logging through platform callbacks, debugfs/procfs, PCI device notifiers, reboot notifiers, the EEH event thread, and the address cache.

## Risks
The detection path can run in interrupt context, so locking and allocation assumptions are sensitive. Duplicate all-ones reads can form loops, mitigated by `EEH_MAX_FAILS` logging. Config-space blocked PEs must avoid normal PCI access or can fence a PHB. Pass-through PEs must not be thawed unexpectedly.

## Test Signals
Test signals include EEH injection through debugfs, all-ones MMIO detection, proc stats increments, successful temporary and permanent error logs, pass-through open/release behavior, PHB fenced event handling, reset API behavior, and hotplug add/remove races.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/eeh.c -->
