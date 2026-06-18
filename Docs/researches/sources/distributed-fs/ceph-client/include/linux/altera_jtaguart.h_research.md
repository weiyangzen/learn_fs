<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/altera_jtaguart.h -->
# sources/distributed-fs/ceph-client/include/linux/altera_jtaguart.h

## Purpose
`altera_jtaguart.h` declares platform data for the Altera JTAG UART driver.

## Important APIs, types, and functions
It defines legacy character major/minor numbers and `struct altera_jtaguart_platform_uart`, which carries the physical base address and IRQ number.

## Control flow
Platform setup code supplies the struct to the driver, which maps registers and registers the UART using the provided interrupt.

## State and persistence behavior
No runtime state is stored in the header. The platform data is static boot/probe configuration.

## Dependencies and integration points
It integrates board/platform description with the Altera JTAG UART serial driver.

## Risks and test signals
Risks include wrong physical base, wrong IRQ, and stale major/minor assumptions. Test signals include driver probe, console/tty I/O, interrupt receive tests, and platform-data validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/altera_jtaguart.h -->
