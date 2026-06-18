# sources/distributed-fs/ceph-client/arch/sh/drivers/pci/pci-sh7780.c



Source read size: 407 lines, 11184 bytes.



Purpose: low-level PCI host controller initialization and error handling for SH7763/SH7780/SH7781/SH7785 PCIC.

Important APIs/types/functions: `sh7780_pci_init()`, `sh7780_pci_setup_irqs()`, `sh7780_pci_err_irq()`, `sh7780_pci_serr_irq()`, `sh7780_pci66_init()`, `sh7780_pci_controller`, error descriptor tables, and PCIC memory-window registers.

Control flow: enables PCIC register access, resets controller, validates Renesas ID, maps low memory through LAR/LSR windows, requests SERR/ERR IRQs, disables cache snoop windows for noncoherent DMA, programs PCI memory and I/O BAR windows, enables command bits, registers the controller, and optionally enables 66 MHz mode if all devices support it.

State and persistence: controller reset/config registers, memory/I/O windows, error IRQ timers, registered host bridge, and PCI status bits persist.

Dependencies and integration points: depends on SH4 PCI ops, generic PCI error helpers, memory_start/end, CPU 29-bit mode, `evt2irq`, and board IRQ fixups.

Risks and test signals: memory-size rounding and 29-bit resource pruning affect DMA visibility; IRQ backoff must not hide persistent errors; 66 MHz mode requires all devices capable. Test PCI enumeration, error IRQ injection, 33/66 MHz negotiation, large memory, and 29-bit mode.
