## sources/distributed-fs/ceph-client/arch/mips/pci/pci-tx4938.c

### Purpose
This file provides TX4938 PCI clock and error-IRQ helpers plus PCI1 Ethernet slot IRQ mapping. It is board-support glue consumed by TXx9 platform setup.

### Important APIs, Types, And Functions
`tx4938_report_pciclk()` reports PCIC clock from divider mode. `tx4938_report_pci1clk()` reports PCIC1 clock from GBUS clock and divider. `tx4938_pciclk66_setup()` asserts PCI66 and selects a faster supported divider. `tx4938_pcic1_map_irq()` maps PCIC1 slots 31/30 to ETH0/ETH1 IRQs when selected in `pcfg`. `tx4938_setup_pcierr_irq()` installs the shared PCI error handler.

### Control Flow
Board setup invokes reporting/setup helpers. The PCI1 IRQ mapper first checks that the device belongs to `tx4938_pcic1ptr`, then maps specific IDSEL-derived slots if Ethernet functions are selected, returns zero for unmapped PCIC1 slots, and `-1` for other controllers.

### State, Persistence, And Dependencies
State changes are CCFG divider/PCI66 bits and registered error IRQ. Dependencies include TX4938 CCFG/PCFG registers, TX4927 controller helpers, TXx9 clock globals, and interrupt constants.

### Integration Points
It layers TX4938-specific policy over generic TX4927 PCI controller code and board-level mapping.

### Risks
Clock setup may not reflect board signal integrity. Returning zero versus `-1` from `tx4938_pcic1_map_irq()` has distinct meanings and callers must preserve that distinction. PCI error IRQ failure is nonfatal.

### Test Signals
Validate clock logs, PCI66 divider writes, ETH0/ETH1 IRQ mapping for PCIC1 slots, and PCIERR interrupt handling.
