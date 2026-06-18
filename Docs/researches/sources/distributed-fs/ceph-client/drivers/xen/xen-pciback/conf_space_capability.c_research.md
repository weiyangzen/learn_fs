# sources/distributed-fs/ceph-client/drivers/xen/xen-pciback/conf_space_capability.c

## Purpose
`conf_space_capability.c` registers virtual overlays for selected PCI capability-list entries so a pciback guest can inspect capabilities while unsafe writes are blocked or constrained.

## Important APIs, types, and functions
The key type is `struct xen_pcibk_config_capability`, stored in a global capability list. Public functions are `xen_pcibk_config_capability_init` and `xen_pcibk_config_capability_add_fields`. Capability handlers cover VPD, PM, MSI, and MSI-X. Important callbacks include `vpd_address_write`, `pm_caps_read`, `pm_ctrl_write`, `pm_ctrl_init`, `msi_field_init`, `msix_field_init`, and `msi_msix_flags_write`.

## Control flow
Initialization registers supported capabilities. Per-device setup scans for each capability using `pci_find_capability`, adds the common capability header overlay at the discovered offset, then adds capability-specific fields. PM init disables PME, PM writes allow only safe bits and delegate state transitions to `pci_set_power_state`. MSI/MSI-X writes are rejected unless permissive mode or device `allow_interrupt_control` permits them, and they prevent enabling conflicting interrupt modes.

## State and persistence
State includes the global list of supported capability descriptors and per-device config field entries. Field init for MSI/MSI-X returns static configuration descriptors; PM init may change hardware PME state. Persistent storage is not used.

## Dependencies and integration points
It depends on Linux PCI capability definitions and helpers, pciback device policy flags, and the config-field dispatcher. It integrates with pciback's virtual config-space initialization.

## Risks and test signals
Risks include exposing unsafe capability writes, interrupt-mode conflicts, permissive bypass behavior, PM state transition failures, VPD write restrictions, and duplicate capability field offsets. Test signals include guests enabling/disabling MSI and MSI-X, INTx/MSI exclusivity cases, PM state changes, VPD reads/writes, permissive and allow-interrupt-control toggles, and devices with absent or malformed capabilities.
