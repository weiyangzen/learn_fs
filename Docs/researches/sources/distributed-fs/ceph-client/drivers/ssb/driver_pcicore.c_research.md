# sources/distributed-fs/ceph-client/drivers/ssb/driver_pcicore.c

## Purpose
PCI/PCIe core support for SSB, including optional MIPS host-mode external PCI controller setup, client-mode PCI/PCIe workarounds, MDIO/SerDes programming, and interrupt-vector enablement for SSB devices behind PCI hosts.

## Important APIs, Types, and Functions
Public functions are `ssb_pcicore_init`, `ssb_pcicore_dev_irqvecs_enable`, and, in hostmode builds, `ssb_pcicore_plat_dev_init` and `ssb_pcicore_pcibios_map_irq`. Hostmode internals implement PCI config-space ops through `get_cfgspace_addr`, `ssb_extpci_read_config`, `ssb_extpci_write_config`, and `ssb_pcicore_init_hostmode`. Workarounds include SPROM core-index fix, PCI/PCIe setup, SerDes polarity, and MDIO read/write.

## Control Flow
`ssb_pcicore_init` enables the core, detects host mode on supported BCM47xx/BCM53xx SoCs without `NOPCI`, and either initializes external PCI host mode or client mode. Host mode resets the external bus, configures SSB-to-PCI windows, waits for devices, enables bridge memory/mastering/interrupts, maps I/O, and registers a PCI controller. Client mode fixes SPROM core index for PCI-hosted SSB, disables PCI interrupts, and applies PCIe SerDes workarounds. IRQ-vector enabling routes device interrupts through PCI config mask or SSB INTVEC depending on core revision/type, then runs setup workarounds once.

## State and Persistence
State includes `pc->hostmode`, `pc->cardbusmode`, `pc->setup_done`, global `extpci_core`, global config lock, and hardware bridge/window/MDIO/TMSLOW/SPROM registers. Hostmode registers a global PCI controller.

## Dependencies and Integration Points
Depends on SSB core accessors, Linux PCI subsystem, MIPS `get_dbe` bus probing, embedded GPIO for CardBus reset, `ssb_mips_irq`, and `ssb_commit_settings`.

## Risks
Host mode is MIPS-specific and only supports one external PCI core through global `extpci_core`. Config-space access remaps physical addresses per access and relies on bus exception probing. Timing delays after reset are hardware-critical. Workarounds are revision-specific and incomplete for some TODO cases such as ASPM and power thresholds.

## Test Signals
Client mode should enable IRQ routing and apply PCI/PCIe workarounds once. Host mode should enumerate external PCI devices without machine checks, assign IRQs, set bridge latency/BAR controls, and survive CardBus reset paths. MDIO transactions should complete within retry bounds.
