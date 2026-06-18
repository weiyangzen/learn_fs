# sources/distributed-fs/ceph-client/drivers/pci/controller/pci-rcar-gen2.c

## Purpose
`pci-rcar-gen2.c` supports the internal PCI bus on Renesas R-Car Gen2 and related RZ/N1 SoCs. The controller is used for built-in PCI USB host blocks rather than a general external PCIe hierarchy. It allocates a PCI host bridge, maps controller registers, configures AHB-to-PCI and PCI-to-AHB windows, enables PCI interrupts, optionally installs a debug error IRQ handler, and exposes limited config-space access for the host bridge and built-in devices.

## Important APIs, types, and functions
`struct rcar_pci` stores the device, register base, memory resource for the built-in device window, config resource, and IRQ. `rcar_pci_cfg_base()` implements config mapping for `pci_generic_config_read/write`: it rejects non-root buses, nonzero functions, slots above 2, and host-bridge config offsets at or above 0x40, then programs `RCAR_AHBPCI_WIN1_CTR_REG` for host or device config access and returns the appropriate MMIO offset.

`rcar_pci_setup()` performs the main hardware initialization. It selects a PCI-AHB window from `dma-ranges` or defaults to a 1 GiB window at `0x40000000`, enables runtime PM, reads the unit revision, asserts and deasserts USB/PLL reset bits, configures the window size, programs AHB master/slave mode, enables the PCI arbiter, sets PCI-AHB and AHB-PCI mappings, writes BAR0/BAR1 for the bridge communication area and PCI-AHB window, enables PCI command bits, and enables INT A/B/PME. With `CONFIG_PCI_DEBUG`, `rcar_pci_setup_errirq()` requests a shared error IRQ and unmasks controller error bits handled by `rcar_pci_err_irq()`.

## Control flow
`rcar_pci_probe()` allocates a host bridge and private state, maps the first MMIO resource as controller/config registers, obtains a second MMIO resource for the device memory area, validates that the second resource starts on a 64 KiB boundary, fetches the platform IRQ, installs `rcar_pci_ops`, sets `PCI_REASSIGN_ALL_BUS`, calls `rcar_pci_setup()`, and finally invokes `pci_host_probe()`. The builtin platform driver matches several Renesas compatible strings and suppresses bind attributes.

## State and persistence behavior
The driver stores only the mapped register base, resource copies, and IRQ in memory. Hardware state is programmed in controller registers for resets, bridge windows, arbiter, AHB bus mode, BARs, command bits, and interrupt enables. Runtime PM is enabled and acquired during setup, but there is no matching remove/suspend/resume logic in this file. No disk state is persisted.

## Dependencies and integration points
The driver depends on OF platform resources, generic PCI host bridge probing, runtime PM, generic PCI config accessors, resource lists for `dma_ranges`, and the Renesas AHB-PCI bridge register layout. It integrates with the PCI core through a simple `pci_ops` map function and `pci_host_probe()`, and with the IRQ subsystem only for optional debug error reporting.

## Risks and edge cases
The config mapper intentionally exposes only root bus slots 0-2 and function 0, so any unexpected topology is invisible. The host bridge only exposes config registers below 0x40. Unknown DMA window sizes silently default to 256 MiB after warning, which may mask firmware mistakes. `pm_runtime_get_sync()` is not checked for failure and has no visible balanced put in this driver. The second MMIO resource must be 64 KiB aligned; otherwise probe fails. Error IRQ coverage exists only with `CONFIG_PCI_DEBUG`.

## Test signals
Good tests include probing each compatible SoC, config-space reads for slots 0-2 and rejection of unsupported buses/functions/offsets, DMA window sizes of 256 MiB/512 MiB/1 GiB/2 GiB plus unknown-size fallback, reset sequencing, BAR/window programming, PCI reassignment behavior, built-in OHCI/EHCI enumeration, INT A/B/PME delivery, optional debug error IRQ handling, and runtime-PM behavior during probe.
