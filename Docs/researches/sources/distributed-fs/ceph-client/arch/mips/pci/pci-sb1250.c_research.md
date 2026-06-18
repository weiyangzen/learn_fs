## sources/distributed-fs/ceph-client/arch/mips/pci/pci-sb1250.c

### Purpose
This file provides Broadcom/Sibyte SB1250 PCI/LDT host glue. It maps configuration and I/O spaces, detects whether firmware enabled the PCI/LDT buses, implements config access with device-mode filtering, sets resource limits, registers the controller, and optionally takes over VGA console.

### Important APIs, Types, And Functions
Important state includes `cfg_space`, `sb1250_bus_status`, optional `ldt_eoi_space`, `sb1250_pci_ops`, and `sb1250_controller`. `sb1250_pci_can_access()` filters config cycles by bus status and device mode. `sb1250_pcibios_read()` and `sb1250_pcibios_write()` implement width-aware config operations. `sb1250_pcibios_init()` initializes the platform.

### Control Flow
The initcall sets `PCI_PROBE_ONLY`, minimum I/O/MEM limits, global resource ends, maps 16 MiB config space, checks firmware host/device mode and bridge command bits, maps I/O space with match-bytes policy, optionally maps LDT EOI space if the LDT bridge is enabled, registers the controller, and hands VGA console to `vga_con` when configured.

### State, Persistence, And Dependencies
Persistent effects are KSEG2/KSEG3 mappings, bus status flags, global resource limits, LDT EOI mapping, and registered PCI controller. Dependencies include Sibyte SCD/board register definitions, raw 64-bit reads, console infrastructure, and legacy MIPS PCI.

### Integration Points
Firmware/CFE assigns resources, so Linux claims them only. LDT support and VGA console integration are conditional.

### Risks
Large config/EOI mappings consume kernel virtual memory on 32-bit kernels. Device mode hides most bus-0 devices. If firmware leaves the PCI bridge master bit clear, scanning is skipped. Config write filtering must correctly simulate master aborts.

### Test Signals
Boot with firmware-initialized PCI, verify `PCI_PROBE_ONLY`, config-space all-ones on disallowed accesses, LDT interrupts with EOI mapping, and VGA console takeover when enabled.
