# sources/distributed-fs/ceph-client/arch/mips/pci/pci-ar2315.c

## Purpose
Implements AR2315/AR2316 PCI host controller support for a limited single-board use case, including custom DMA offset translation and interrupt-domain handling.

## Important APIs, Types, And Functions
Defines `struct ar2315_pci_ctrl`, overrides `phys_to_dma` and `dma_to_phys`, installs `ar2315_pci_ops`, and provides `ar2315_pci_probe`, `ar2315_pci_host_setup`, IRQ domain ops, `pcibios_map_irq`, and `pcibios_plat_dev_init`.

## Control Flow
Probe maps controller and external config windows, resets the PCI bus, configures uncached access, delays for hardware stabilization, validates/programs host BARs and command bits, creates an IRQ domain, enables abort/external interrupts, and registers the PCI controller. Config access toggles CFG_SEL, reads the config window, checks abort status, optionally writes masked values, clears aborts, and restores memory access mode. IRQ handling dispatches the first pending bit through the domain.

## State And Persistence
Controller state is in `ar2315_pci_ctrl`; IRQ mappings persist in the irq domain. DMA translation uses a fixed 0x20000000 offset for PCI devices. Hardware reset, BAR, interrupt, and uncached config registers persist until reset.

## Dependencies And Integration Points
Depends on platform resources named `ar2315-pci-ctrl` and `ar2315-pci-ext`, IRQ domain APIs, MIPS physical access behavior, and PCI controller registration.

## Risks And Edge Cases
Global `phys_to_dma`/`dma_to_phys` overrides affect DMA translation on this build. Only devices up to slot 18 are accepted, and host slot 3 is hidden. CFG_SEL toggling must be restored after every access. IRQ handler handles one pending bit per parent interrupt.

## Test Signals
Fonera/AR2315 boot with USB EHCI device, DMA address tests, config abort probes, and external interrupt delivery are the main signals.
