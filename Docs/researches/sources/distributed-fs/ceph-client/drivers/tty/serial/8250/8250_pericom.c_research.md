<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/8250/8250_pericom.c -->
# sources/distributed-fs/ceph-client/drivers/tty/serial/8250/8250_pericom.c

## Purpose

`sources/distributed-fs/ceph-client/drivers/tty/serial/8250/8250_pericom.c` is a dedicated PCI driver for Pericom PI7C9X795 UARTs and many ACCES I/O products based on that family. These devices are blacklisted from the generic 8250 PCI driver so this driver can provide Pericom-specific port counting, register spacing, and baud divisor behavior. The source was read as a complete 214-line file for this report.

## Important APIs, Types, and Functions

The local state type is `struct pericom8250`, storing the BAR mapping pointer, number of registered ports, and flexible array of 8250 line numbers. `pericom_do_set_divisor()` is the key custom UART callback; it searches supported sample-clock ratios and writes divisor latch plus a sample-clock register to approximate the requested baud within a 2 percent tolerance. `pericom8250_probe()` and `pericom8250_remove()` implement device lifecycle. `pericom8250_pci_ids[]` lists Pericom and ACCES I/O PCI device IDs, and `pericom8250_pci_driver` registers the PCI driver.

## Control Flow

Probe enables the PCI device, estimates the maximum number of ports from BAR0 length divided by eight, computes requested port count from vendor/device encoding, allocates `pericom8250`, maps BAR0 with `pcim_iomap()`, and initializes a template `uart_8250_port`. The template uses port IO, a 14.7456 MHz effective clock (`921600 * 16`), skip-test/autoconf/share-IRQ flags, the PCI IRQ, and the custom divisor setter. It then iterates over ports while respecting the BAR-derived maximum. Pericom 7954-style quad devices use an offset jump for logical port 3 (`0x38` instead of `3 * 8`); others use eight-byte spacing. Each port is registered with `serial8250_register_8250_port()`. Remove unregisters every successfully registered line.

## State and Persistence Behavior

Runtime state is limited to the devm-managed `pericom8250` object, the managed BAR mapping, and registered 8250 line numbers. Divisor programming persists in UART registers until changed by termios, reset, or removal. The driver does not implement suspend/resume or explicit PCI error recovery; it relies on PCI core and 8250 core behavior available for simple devices.

## Dependencies and Integration Points

The driver depends on PCI probe/remove, managed resource allocation, BAR mapping, 8250 internals, `serial8250_register_8250_port()`, `serial8250_unregister_port()`, and divisor latch helpers. It integrates with the generic PCI driver through the generic driver's blacklist entries for Pericom and ACCES I/O vendors.

## Risks and Edge Cases

Port count decoding is compact but hardware-specific: Pericom uses low device-id bits, while ACCES I/O derives count from bits 5:3. Bad IDs or unexpected encodings can produce the wrong `nr`. The divisor search silently returns without programming if no ratio is within tolerance, leaving prior UART settings intact. The driver uses `pdev->irq` directly rather than allocating vectors, so interrupt setup depends on PCI core defaults. Quad offset handling is special-cased by port count and index, which must match the hardware layout.

## Test Signals

Validation should include Pericom 1/2/4/8-port devices, ACCES I/O 2/4/8-port products, the quad port-3 offset jump, baud accuracy across common and high rates, remove after partial registration, BAR length limiting, and confirmation that the generic 8250 PCI driver does not bind the same IDs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/8250/8250_pericom.c -->
