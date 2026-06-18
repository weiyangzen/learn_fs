# sources/distributed-fs/ceph-client/drivers/pci/controller/pci-versatile.c

## Purpose
`pci-versatile.c` is the ARM Versatile PCI host bridge driver. It maps Versatile PCI controller registers and config windows, finds the FPGA PCI core's own slot, hides that slot from normal enumeration, sets inbound SDRAM mappings, and registers a basic PCI host bridge.

## Important APIs, Types, And Functions
Global MMIO pointers `versatile_pci_base` and `versatile_cfg_base[]` back the controller and type/config spaces. `versatile_map_bus()` returns config-space addresses unless the target slot is in `pci_slot_ignore`. `pci_versatile_ops` uses `pci_generic_config_read32` and `pci_generic_config_write`. `versatile_pci_probe()` maps resources, programs outbound memory maps from host bridge windows, discovers the local PCI core, enables memory/master/invalidate on it, writes BAR0-2 to SDRAM, sets a QEMU compatibility signal, and calls `pci_host_probe()`.

## Control Flow, State, And Persistence
Boot parameter `pci_slot_ignore=` updates the global ignore bitmap before probing. Probe scans 32 slots through config base 0 for fixed device/class IDs, then adds the discovered local slot to the ignore bitmap and writes `PCI_SELFID`. All config accesses use config base 1 with bus/devfn/offset addressing. Runtime state is global and process-lifetime only; hardware mappings are programmed once at probe and there are no suspend/resume paths.

## Dependencies, Integration Points, Risks, And Test Signals
The driver integrates with OF platform matching `"arm,versatile-pci"`, generic PCI host bridge allocation, host bridge window parsing, ARM `PAGE_OFFSET` physical mapping, PCI reassignment flags, and QEMU's historic IRQ mapping compatibility behavior. Risks include single-controller global state, dependency on local PCI core discovery, and SDRAM identity-style inbound mapping assumptions. Test for PCI core slot detection, hidden self device, working reassigned resources, correct IRQ behavior on QEMU/hardware, and functional config reads for non-ignored slots.
