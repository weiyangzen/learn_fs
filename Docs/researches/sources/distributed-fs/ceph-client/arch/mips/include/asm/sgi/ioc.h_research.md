# sources/distributed-fs/ceph-client/arch/mips/include/asm/sgi/ioc.h

## sources/distributed-fs/ceph-client/arch/mips/include/asm/sgi/ioc.h

### Purpose
`sgi/ioc.h` defines SGI I/O Controller and INT2/INT3 register maps for UARTs, keyboard/mouse, parallel-port integration, interrupt masks/status, timer, panel controls, system ID, DMA selection, reset/write controls, and external I/O status.

### Important APIs, Types, And Functions
Types include `struct sgioc_uart_regs`, `struct sgioc_keyb_regs`, `struct sgint_regs`, and `struct sgioc_regs`. Important macros include `SGINT_ISTAT*`, `SGINT_TCWORD_*`, `SGINT_TIMER_CLOCK`, `SGINT_TCSAMP_COUNTER`, `SGIOC_PANEL_*`, `SGIOC_SYSID_*`, `SGIOC_DMASEL_*`, `SGIOC_RESET_*`, `SGIOC_WRITE_*`, `EXTIO_*`, globals `sgi_ioc_reset`, `sgi_ioc_write`, `sgioc`, and `sgint`.

### Control Flow
Platform and drivers read 8-bit registers aligned on 32-bit boundaries, update software shadows for write-only reset/write registers, program 8254 timer control/count registers, and enable/disable interrupt sources through mask registers.

### State, Persistence, Dependencies, And Integration
State is IOC/INT MMIO, software copies of write-only registers, timer counters, panel/system ID latches, and global controller pointers. Dependencies include Linux types and `pi1.h`. Integration covers serial, keyboard/mouse, parallel port, front panel, timer calibration, interrupt controller, power/AC-fail events, and FullHouse external I/O.

### Risks
The file warns that registers are 8-bit and 32-bit aligned; word access can break hardware behavior. Write-only software shadows must stay synchronized. Timer frequency and mask polarity assumptions affect clock and IRQ delivery.

### Test Signals
Boot SGI IOC platforms, test serial/kbd/mouse/panel/timer interrupts, verify 8-bit accessors, compare software shadow values after reset/write changes, and test FullHouse `extio` status decoding.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/sgi/ioc.h -->
