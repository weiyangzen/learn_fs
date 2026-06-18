<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/pcie/aspm.c -->
# sources/distributed-fs/ceph-client/drivers/pci/pcie/aspm.c

## Purpose
`aspm.c` manages PCIe Active State Power Management, Clock Power Management, LTR, and L1 PM substates. It provides always-built save/restore helpers for LTR and L1SS, and under `CONFIG_PCIEASPM` maintains link-state topology, computes supported/capable/default/disabled states, applies global and per-link policies, and exposes sysfs/module controls.

## Important APIs, Types, and Functions
Key always-available functions are `pci_save_ltr_state()`, `pci_restore_ltr_state()`, `pci_configure_aspm_l1ss()`, `pci_save_aspm_l1ss_state()`, and `pci_restore_aspm_l1ss_state()`. With ASPM enabled, `struct pcie_link_state` tracks upstream/downstream devices, root/parent relation, ASPM bitmasks, and Clock PM state. Exported/public functions include `pcie_aspm_init_link_state()`, `pcie_aspm_exit_link_state()`, `pcie_aspm_pm_state_change()`, `pcie_aspm_powersave_config_link()`, `pci_configure_ltr()`, `pci_bridge_reconfigure_ltr()`, `pci_disable_link_state()`, `pci_disable_link_state_locked()`, `pci_enable_link_state()`, `pci_enable_link_state_locked()`, `pcie_aspm_enabled()`, `pcie_no_aspm()`, and `pcie_aspm_support_enabled()`.

## Control Flow and State
Enumeration configures LTR path support, creates link state for downstream ports, validates subordinate devices, optionally configures common clock and retrains, computes L0s/L1/L1SS support from both link partners, applies latency constraints from endpoints, initializes Clock PM, and configures the path according to policy. Runtime policy changes and per-device enable/disable requests take `pci_bus_sem` and `aspm_lock`, update default/disable masks, and write LNKCTL/L1SS registers in spec-defined order. L1SS restore disables ASPM and L1.2 before programming timing fields, then re-enables saved bits.

## Dependencies and Integration Points
ASPM depends on PCI config helpers, OF defaults, PM state, PCI core saved capability buffers, link retraining, and sysfs/module parameter infrastructure. Endpoint drivers call link-state APIs to disable problematic states; controller and VMD paths call locked variants. It updates saved PCIe capability state so suspend/resume restores the most recent kernel-managed link settings.

## Risks and Test Signals
Risks include enabling low-power states without full LTR path support, incorrect L1SS ordering, common-clock retrain failures, stale link state after hot-remove, policy changes racing hotplug, and devices whose advertised latency is wrong. Tests should cover boot parameters `pcie_aspm=off/force`, module policy writes, per-link sysfs attributes, hotplug removal, suspend/resume with L1.2, endpoint drivers disabling states, OF default behavior, and link retraining failure rollback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/pcie/aspm.c -->
