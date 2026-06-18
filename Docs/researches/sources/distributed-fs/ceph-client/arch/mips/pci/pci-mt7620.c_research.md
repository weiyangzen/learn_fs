## sources/distributed-fs/ceph-client/arch/mips/pci/pci-mt7620.c

### Purpose
This file implements PCIe host support for Ralink/MediaTek MT7620A, MT7628AN, and MT7688 SoCs. It programs PCIe PHY sequences, resets and clocks the controller, checks link presence, implements config-space ops, maps interrupts, and registers the host controller.

### Important APIs, Types, And Functions
Global mappings include `bridge_base`, `pcie_base`, and reset control `rstpcie0`. Helpers `bridge_w32/r32/m32`, `pcie_w32/r32/m32`, `pcie_phyctrl_set()`, `wait_pciephy_busy()`, and `pcie_phy()` abstract register access. `pci_config_read()` and `pci_config_write()` implement `mt7620_pci_ops`. Hardware setup is split between `mt7620_pci_hw_init()` and `mt7628_pci_hw_init()`. `mt7620_pci_probe()`, `pcibios_map_irq()`, and `pcibios_plat_dev_init()` are the platform-facing hooks.

### Control Flow
Probe obtains reset control and maps bridge/PCIe resources, broadens global resource limits, resets the controller, enables clock, asserts PERST, selects a SoC-specific PHY init path, waits, deasserts PERST, and checks `PCIE_LINK_UP_ST`. If no card is present, it disables reset/clock/PHY. With a link, it programs MEM/IO bases, BAR0, class, interrupts, SDK-derived config tweaks, loads OF ranges, and registers the controller. IRQ mapping treats bus 1 slot 0 as the endpoint and bus 0 slot 0 as the root complex.

### State, Persistence, And Dependencies
State is SoC sysc clock/reset bits, PCIe PHY registers, root-complex config registers, global I/O mapping, and registered PCI controller resources. Dependencies include Ralink register helpers, reset framework, OF PCI ranges, delays, and `ralink_soc` identification.

### Integration Points
The driver matches `"mediatek,mt7620-pci"` DT nodes and relies on Ralink SoC initialization to set `ralink_soc`. It plugs into legacy MIPS PCI enumeration and common `pcibios_map_irq()`.

### Risks
Several failures return `-1` rather than standard errno. `pci_config_read/write()` do not reject invalid sizes explicitly. SDK "voodoo" PHY/config sequences are board-sensitive. No-card detection disables the controller, so marginal links can prevent enumeration.

### Test Signals
Boot with MT7620A and MT7628/MT7688 hardware, verify link-up and no-card paths, config access to bus 1 slot 0, assigned IRQ 4, OF resource ranges, and endpoint DMA/interrupt functionality.
