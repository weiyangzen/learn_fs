# sources/distributed-fs/ceph-client/arch/sh/drivers/pci/fixups-titan.c



Source read size: 36 lines, 821 bytes.



Purpose: board-specific SH PCI fixup and IRQ-routing code for `titan` platforms.

Important APIs/types/functions: `pcibios_map_platform_irq()` is the common hook; some boards also override `pci_fixup_pcic()` to program SH7751 PCIC/BSC timing, local address registers, interrupt masks, and config BARs.

Control flow: generic PCI enumeration calls the IRQ mapper for each device slot/pin. Boards with `pci_fixup_pcic()` run during controller initialization to mirror memory-controller settings and set PCI local/memory/I/O windows before bus scan.

State and persistence: IRQ mapping tables, PCIC control registers, memory-controller mirror values, and optional resource/DMA coherent-memory fixups persist after boot.

Dependencies and integration points: selected by the board Kconfig object for `titan`, integrates with `pci-sh4.h`, machine IRQ constants or `evt2irq()`, and the generic SH PCI core.

Risks and test signals: fixed slot/pin tables can return -1 or wrong IRQs; PCIC register magic is board timing-specific; Dreamcast additionally fixes a nonstandard BAR/DMA window. Test PCI interrupt delivery for each slot, boot-time PCIC setup, and resource assignment on the configured board.
