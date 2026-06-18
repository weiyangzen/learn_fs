# sources/distributed-fs/ceph-client/drivers/pci/hotplug/cpcihp_zt5550.c

## Purpose
Implements the Intel/Ziatech ZT5550 CompactPCI host-controller glue for the generic CompactPCI hotplug core. It probes the Ziatech controller PCI function, maps its MMIO registers, exposes ENUM# status and optional IRQ handling through `struct cpci_hp_controller_ops`, registers the CompactPCI bus segment, and starts/stops the shared `cpci_hotplug` machinery.

## Important APIs, Types, and Functions
Module parameters are `debug` and `poll`; `poll` suppresses IRQ ops and forces ENUM# polling. The key statics are `zt5550_hpc_ops`, `zt5550_hpc`, `bus0_dev`, `bus0`, `hc_dev`, `hc_registers`, and CSR pointers such as `csr_int_status` and `csr_int_mask`. Important routines are `zt5550_hc_config()`, `zt5550_hc_cleanup()`, `zt5550_hc_query_enum()`, `zt5550_hc_check_irq()`, `zt5550_hc_enable_irq()`, `zt5550_hc_disable_irq()`, `zt5550_hc_init_one()`, `zt5550_hc_remove_one()`, `zt5550_init()`, and `zt5550_exit()`. The PCI driver matches `PCI_VENDOR_ID_ZIATECH` and `PCI_DEVICE_ID_ZIATECH_5550_HC`.

## Control Flow
Module init reserves the legacy ENUM port and registers `zt5550_hc_driver`. Probe enables the HC PCI device, reserves and maps BAR 1, computes direct and indexed CSR pointers, masks indexed host/fault/serial interrupts and direct timer/ENUM interrupts, fills `zt5550_hpc` with query and optional IRQ callbacks, registers the controller with `cpci_hp_register_controller()`, finds the first DEC 21154 bridge as the CompactPCI bus, registers slots `0x0a` through `0x0f` with `cpci_hp_register_bus()`, then starts the generic core with `cpci_hp_start()`. Remove reverses this order by stopping the core, unregistering the bus/controller, and unmapping/disabling the HC.

## State and Persistence Behavior
State is module-global and in-memory only. The driver assumes a single HC chip: a second probe fails while `hc_dev` is set. The controller MMIO mapping and CSR pointer aliases persist from probe until remove. ENUM# is read from I/O port `0xe1` on every query. Interrupt enablement is persisted in the hardware direct interrupt mask register but no durable storage is used.

## Dependencies and Integration Points
Depends on Linux PCI, I/O port reservation, MMIO mapping, interrupt flags, and the generic `cpci_hotplug` controller/bus APIs. It relies on a DEC 21154 bridge being discoverable and on ZT5550-specific register definitions from `cpcihp_zt5550.h`. Its IRQ callbacks are consumed by the CompactPCI core, which owns the actual slot processing.

## Risks
The single-controller assumption and "first DEC 21154" bus discovery are hardware-topology specific. Cleanup does not clear `hc_dev`, so rebind behavior depends on module lifetime and PCI driver expectations. Direct pointer arithmetic on `void __iomem *` and hard-coded BAR/port/register choices are architecture and device specific. Interrupt handling treats any nonzero `CSR_INTSTAT` as this device's shared IRQ claim.

## Test Signals
Useful signals include successful module load with ENUM port reservation, probe of the ZT5550 PCI ID, BAR 1 reservation/ioremap, correct interrupt mask writes, controller registration, DEC 21154 subordinate bus discovery, cPCI slots `0x0a`-`0x0f` appearing in the hotplug core, IRQ mode versus `poll=1`, ENUM# event detection, remove/unload without leaked regions, and failure injection for missing bridge, duplicate HC, and registration errors.
