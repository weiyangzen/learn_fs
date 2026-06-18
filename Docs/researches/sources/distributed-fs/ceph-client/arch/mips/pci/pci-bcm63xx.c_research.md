## sources/distributed-fs/ceph-client/arch/mips/pci/pci-bcm63xx.c

### Purpose
This file initializes Broadcom BCM63xx PCI or PCIe host support during early MIPS boot. It exposes the `bcm63xx_pci_enabled` runtime gate, builds `pci_controller` instances for conventional PCI, optional CardBus, and PCIe, programs host bridge address windows, resets PCIe SERDES/core blocks, and registers the selected controller with the MIPS PCI core.

### Important APIs, Types, And Functions
Key state includes `bcm63xx_controller`, optional `bcm63xx_cb_controller`, `bcm63xx_pcie_controller`, `pci_iospace_start`, and the private `pcie_clk`. `bcm63xx_int_cfg_readl()` and `bcm63xx_int_cfg_writel()` perform host bridge internal config cycles through MPI config registers. `bcm63xx_register_pci()` configures legacy PCI/CardBus windows and bus-mastering BARs. `bcm63xx_register_pcie()` enables the PCIe clock, resets the link, programs bridge options, and registers PCIe resources. `bcm63xx_pci_init()` dispatches by CPU ID.

### Control Flow
The `arch_initcall()` first checks `bcm63xx_pci_enabled`; disabled boards return `-ENODEV`. BCM6328/6362 use PCIe setup, while BCM3368/6348/6358/6368 use legacy PCI. Legacy PCI maps four bytes of I/O space for configuration cycles, sets local-to-PCI memory and I/O windows, configures CardBus IDSEL if enabled, programs PCI-to-local RAM remaps for DMA, clears host retry limits, enables memory/master bits, enables prefetching, and registers controllers. PCIe enables clocks, resets core and external reset lines with delays, configures bridge endian/BE handling, interrupt masks, class code, BAR0 remap, and registers the PCIe controller.

### State, Persistence, And Dependencies
All state is boot-time MMIO configuration plus static resources. Dependencies are BCM63xx CPU ID/revision helpers, MPI/MISC/PCMCIA/PCIe register accessors, reset control, clock framework, PCI controller registration, and constants from `pci-bcm63xx.h`. Persistent effects are hardware windows, reserved PCI I/O memory, and registered PCI buses.

### Integration Points
The file integrates BCM63xx board NVRAM policy through `bcm63xx_pci_enabled`, ops from `ops-bcm63xx.c`, optional CardBus support, and generic MIPS `register_pci_controller()`. Device enumeration, resource assignment, and IRQ mapping are handled by the common PCI layer and platform fixups after registration.

### Risks
The legacy path notes a real SMP hazard: config cycles temporarily remap the first four bytes of I/O space, so concurrent I/O can collide. Memory-size and old BCM6348 revision handling can restrict DMA. PCIe assumes clock and reset names are present. Wrong resource constants or CardBus IDSEL overlap can make devices invisible or corrupt config cycles.

### Test Signals
Useful signals are boot logs showing selected PCI/PCIe path, successful config-space reads, correct resource windows, working DMA from PCI devices, CardBus enumeration when configured, and absence of master/target aborts under concurrent I/O stress.
