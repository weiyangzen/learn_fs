# sources/distributed-fs/ceph-client/arch/x86/kernel/early_printk.c

## Purpose
Implements legacy `earlyprintk=` consoles for VGA, I/O serial, MMIO serial, PCI serial, Xen HVC, EHCI debug port, and xDBC before regular consoles initialize.

## Important APIs, Types, And Functions
`early_vga_write()` writes text mode VGA memory. `early_serial_putc()` and `early_serial_write()` write UART output through static-call selected I/O or MMIO functions. `early_serial_init()`, `early_mmio_serial_init()`, and `early_pci_serial_init()` parse console options. `early_console_register()` registers the selected boot console. `setup_early_printk()` is the early parameter handler.

## Control Flow
The parser scans the `earlyprintk=` string for known backends and optional `keep`. Serial setup chooses default or requested port/baud, initializes UART registers unless `nocfg`, and updates kexec debug port globals where applicable. PCI serial validates BDF/class unless `force`, enables I/O or memory decode, maps BAR0 if needed, then initializes hardware. VGA uses boot screen geometry and scrolls manually.

## State, Persistence, And Dependencies
State includes current VGA cursor, serial base address, static calls for serial accessors, registered `early_console`, and optional kexec debug port addresses. It depends on early I/O, early ioremap, PCI direct config access, console core, boot params, Xen HVC, and optional USB debug backends.

## Integration Points
Provides early boot diagnostics before full console drivers and can be retained with `keep`. Kexec debug paths reuse discovered serial ports.

## Risks
Incorrect MMIO/PCI addresses can fault or write device memory. Only 32-bit MMIO addresses are supported in `mmio32`. The parser scans substrings incrementally, so option syntax must remain compatible.

## Test Signals
Booting with `earlyprintk=vga`, `serial`, `ttyS`, `mmio32`, and `pciserial` should print early logs, honor baud/nocfg/keep, and avoid duplicate console registration.
