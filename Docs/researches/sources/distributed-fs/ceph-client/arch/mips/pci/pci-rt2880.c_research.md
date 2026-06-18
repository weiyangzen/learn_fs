## sources/distributed-fs/ceph-client/arch/mips/pci/pci-rt2880.c

### Purpose
This file implements PCI host support for Ralink RT288x SoCs. It maps controller registers, implements config-space read/write, configures bridge windows and IDs, maps the single external PCI IRQ, and registers the controller from a platform driver.

### Important APIs, Types, And Functions
The file uses `rt2880_pci_base`, register access helpers, `rt2880_pci_get_cfgaddr()`, `rt2880_pci_config_read()`, `rt2880_pci_config_write()`, `rt2880_pci_read_u32()`, and `rt2880_pci_write_u32()`. `rt2880_pci_ops` and `rt2880_pci_controller` describe controller operations/resources. `rt288x_pci_probe()` performs setup. `pcibios_map_irq()` and `pcibios_plat_dev_init()` provide platform hooks.

### Control Flow
Probe maps controller and I/O space, installs the I/O port base, sets global I/O resource limits, initializes bridge config, arbitration, BAR0, memory and I/O bases, IDs/class/subsystem IDs, interrupt mask, root BAR0, records the OF node, and registers the controller. During device enable, `pcibios_plat_dev_init()` lazily initializes slot 0 BAR0 and command bits once because generic PCI does not do it for this platform.

### State, Persistence, And Dependencies
State is in MMIO registers, `rt2880_pci_controller.io_map_base`, global I/O port base, and a static `slot0_init` guard. Dependencies include Ralink RT288x register constants, OF platform matching, and legacy MIPS PCI.

### Integration Points
The driver matches `"ralink,rt288x-pci"`. It cooperates with Ralink SoC init and uses `RT288X_CPU_IRQ_PCI` for slot 0x11 devices.

### Risks
Unknown slots call `BUG()`, making unexpected hardware fatal. `ioremap()` failures are not checked. Slot 0 special initialization is deferred until another device is enabled, which is fragile if enumeration order changes.

### Test Signals
Boot with RT288x PCI endpoints, verify root BAR0 programming, IRQ assignment for slot 0x11, correct config access widths, and no crash when only expected slots exist.
