## sources/distributed-fs/ceph-client/arch/mips/pci/pci-tx4927.c

### Purpose
This file contains Toshiba TX4927 PCI clock reporting, optional 66 MHz setup, and PCI error IRQ registration helpers used by TXx9 board code.

### Important APIs, Types, And Functions
`tx4927_report_pciclk()` logs whether PCI66 is asserted and computes internal PCI clock from CPU clock and divider mode, or reports external clock. `tx4927_pciclk66_setup()` asserts M66EN and adjusts divider mode to double the clock when possible. `tx4927_setup_pcierr_irq()` registers `tx4927_pcierr_interrupt` for the TX4927 PCIERR IRQ.

### Control Flow
Board setup calls these helpers before or during PCI controller initialization. Clock setup reads `ccfg`/`pcfg`, selects a supported divider, writes changed config with `tx4927_ccfg_change()`, and returns the computed clock or `-1` for external clock.

### State, Persistence, And Dependencies
Persistent effects are TX4927 CCFG divider and PCI66 bits plus an installed PCI error interrupt handler. Dependencies include `tx4927_ccfgptr`, `txx9_cpu_clock`, TX4927 bit definitions, and the shared TX4927 PCI error handler.

### Integration Points
This is not a standalone controller driver; platform board files call it when wiring TX4927 PCI.

### Risks
Wrong divider selection can overclock PCI. Error IRQ registration failure is only a warning. External-clock mode leaves frequency unknown to callers except via `-1`.

### Test Signals
Check boot clock logs, measured PCI clock against divider settings, M66EN assertion, and PCIERR interrupt delivery on forced controller errors.
