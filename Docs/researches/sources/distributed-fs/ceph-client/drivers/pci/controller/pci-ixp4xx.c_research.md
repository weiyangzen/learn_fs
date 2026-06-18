# sources/distributed-fs/ceph-client/drivers/pci/controller/pci-ixp4xx.c

## Purpose
`pci-ixp4xx.c` is the PCI host controller driver for Intel IXP42x/IXP43x ARM SoCs. It turns the SoC PCI controller into a Linux `pci_host_bridge`, implements indirect PCI config cycles, configures AHB-to-PCI and PCI-to-AHB address windows, applies IXP42x config-read errata handling, and installs ARM abort handling for PCI master aborts. The source explicitly notes unverified I/O-space access and DMA support as TODO areas.

## Important APIs, types, and functions
`struct ixp4xx_pci` stores the device, MMIO base, `errata_hammer`, and host/option mode. `ixp4xx_readl()` and `ixp4xx_writel()` deliberately use `__raw_readl()`/`__raw_writel()` because the IXP4xx peripheral bus changes byte ordering based on CPU endian mode, while PCI device accesses remain little-endian.

Config access is split between non-posted indirect PCI cycles and CRP local controller config cycles. `ixp4xx_pci_read_indirect()` and `ixp4xx_pci_write_indirect()` program `NP_AD`, `NP_CBE`, and data registers, then call `ixp4xx_pci_check_master_abort()` to clear and report `IXP4XX_PCI_ISR_PFE`. `ixp4xx_config_addr()` builds Type 0 or Type 1 config addresses for the root bus and subordinate buses. `ixp4xx_pci_read_config()` and `ixp4xx_pci_write_config()` implement the `pci_ops` callbacks with byte-lane-enable calculation and value shifting. `ixp4xx_crp_write_config()` writes controller-local config fields such as BARs and command bits; `ixp4xx_crp_read_config()` is available under `CONFIG_ARM` for abort status handling.

Window setup lives in `ixp4xx_pci_parse_map_ranges()` and `ixp4xx_pci_parse_map_dma_ranges()`. Both consume `pci_host_bridge` windows populated from firmware and require 64 MiB ranges for memory and DMA windows. `ixp4xx_pci_addr_to_64mconf()` converts a base address into four 16 MiB byte fields for controller registers.

## Control flow
`ixp4xx_pci_probe()` allocates a host bridge with private state, selects the `ixp4xx_pci_ops`, detects the IXP42x errata quirk from the OF compatible string, maps the controller registers, reads the controller mode from `IXP4XX_PCI_CSR`, and, on ARM, installs an imprecise external abort handler with `hook_fault_code()`.

Probe then parses and programs memory, I/O, and DMA ranges. In host mode it writes local PCI BAR0-3 to consecutive 16 MiB windows starting at `__pa(PAGE_OFFSET)`, BAR4 to the following CSR/prefetch window, BAR5 to an I/O window at `0xfffffc00`, and the retry/transfer-ready timeout register. It clears PCI error interrupts, writes the CSR initialize-complete and byte-swapping bits, enables PCI memory/master in the local command register, and finally calls `pci_host_probe()`.

## State and persistence behavior
Runtime state is minimal and device-managed: private state, MMIO base, mode flags, and controller registers. The driver writes persistent hardware state for BARs, address windows, interrupt status, endian swap behavior, and PCI command bits, but it maintains no disk state and provides no remove path. The ARM abort handler uses the file-scope `ixp4xx_pci_abort_singleton`, which effectively assumes a single active controller instance.

## Dependencies and integration points
The driver depends on OF platform matching, generic PCI host bridge setup, firmware-provided PCI ranges/dma-ranges, ARM fault handling, IXP4xx controller register semantics, and Linux PCI config access conventions. It integrates with the PCI core only through `pci_host_probe()` and the custom `pci_ops`; there is no MSI, IRQ-domain, runtime PM, or reset-controller integration in this file.

## Risks and edge cases
The biggest hardware risks are endian handling, strict 64 MiB memory/DMA range requirements, and the IXP42x read errata path that repeatedly hammers the config register and assumes reads have no side effects. The abort handler singleton and builtin-only design make removal or multiple-controller scenarios unsafe. Missing `dma-ranges` only logs an error in the parser but still returns success, so firmware omissions may lead to partially configured hardware. The TODOs around I/O-space access and DMA support are explicit test gaps.

## Test signals
Validation should include OF probing for both `intel,ixp42x-pci` and `intel,ixp43x-pci`, config-space reads/writes on root and subordinate buses, master-abort behavior for absent devices, endian-mode tests on big-endian and little-endian ARM builds, 64 MiB range rejection, host-mode BAR programming, I/O-space exercises, DMA-capable endpoint traffic, and ARM imprecise abort recovery.
