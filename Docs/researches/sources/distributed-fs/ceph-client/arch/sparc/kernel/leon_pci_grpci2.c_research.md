# sources/distributed-fs/ceph-client/arch/sparc/kernel/leon_pci_grpci2.c

Purpose: Implements the GRPCI2 LEON PCI host bridge driver with wider bus support, configurable target BARs, optional reset, IRQ mode handling, error/DMA interrupt demuxing, and config-space access.

Important APIs/types/functions: `struct grpci2_regs` maps control/status, DMA, BAR, AHB-master map, and optional trace registers. `struct grpci2_barcfg` describes OF-configured target BAR mapping. `struct grpci2_priv` embeds `leon_pci_info`, IRQ mode/mask/reset settings, PCI ID, virtual IRQs, windows, and six target BAR configs. `grpci2_cfg_r{8,16,32}()` and `grpci2_cfg_w{8,16,32}()` select the bus in `ctrl`, clear config status, access config space, and wait for `STS_CFGERRVALID`. `grpci2_hw_init()`, `grpci2_pci_flow_irq()`, `grpci2_err_interrupt()`, and `grpci2_of_probe()` drive bridge setup.

Control flow: Probe maps registers, checks host/master capability, parses `barcfg`, `irq_mask`, and `reset` properties, maps PCI windows, claims resources, initializes hardware, configures IRQ routing based on `irq_mode`, registers error handling, enables error/system interrupts, and hands off to `leon_pci_init()`.

State and persistence: Persistent runtime state is the single global `grpci2priv`, bridge control/status register programming, AHB-to-PCI map entries, target BAR registers, virtual IRQs, and registered PCI devices. OF properties persist as boot-time policy only.

Dependencies and integration points: It integrates OF platform data, LEON IRQ update helpers, generic PCI host ops, LEON bypass stores/loads, `of_ioremap()`, and common LEON PCI enumeration.

Risks and test signals: The config-access wait loops have no timeout, so stuck hardware can hang the kernel. The `irq_mask` parse path appears to assign `do_reset` instead of `irq_mask`, making that property suspicious. Tests should cover all IRQ modes, reset/no-reset boots, custom target BARs, config errors for absent devices, DMA/error IRQ routing, resource conflict cleanup, and bus numbers up to 255.
