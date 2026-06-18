<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/8250/8250_pcilib.c -->
# sources/distributed-fs/ceph-client/drivers/tty/serial/8250/8250_pcilib.c

## Purpose

`sources/distributed-fs/ceph-client/drivers/tty/serial/8250/8250_pcilib.c` is the small shared PCI helper library for 8250 PCI serial drivers. It centralizes the common conversion from PCI BAR resources into `uart_8250_port` IO/MMIO fields and provides a common warning/error path for systems built without IO-port support. The source was read as a complete 49-line file for this report.

## Important APIs, Types, and Functions

The exported functions are `serial_8250_warn_need_ioport()` and `serial8250_pci_setup_port()`, both exported with `EXPORT_SYMBOL_NS_GPL(..., "SERIAL_8250_PCI")`. `serial_8250_warn_need_ioport()` logs that a serial port is unsupported because IO resources are unavailable and returns `-ENXIO`. `serial8250_pci_setup_port()` fills `port->port.iotype`, `iobase`, `mapbase`, `membase`, and `regshift` from a selected PCI BAR, offset, and optional mapped MMIO base.

## Control Flow

`serial8250_pci_setup_port()` first rejects BAR indexes beyond `PCI_STD_NUM_BARS`. If the BAR is memory-backed, it marks the UART as `UPIO_MEM`, clears `iobase`, records the physical map base as `pci_resource_start() + offset`, sets `membase` to the caller-provided mapping plus offset, and preserves the requested register shift. If the BAR is not memory-backed and `CONFIG_HAS_IOPORT` is enabled, it marks the UART as `UPIO_PORT`, computes `iobase` from the BAR start plus offset, clears MMIO fields, and forces `regshift` to zero. If IO ports are unavailable, it delegates to `serial_8250_warn_need_ioport()`.

## State and Persistence Behavior

This file owns no long-lived state. Its only state mutation is caller-provided `uart_8250_port` initialization. MMIO mapping lifetime remains owned by the caller, which is why the function accepts `void __iomem *iomem` rather than mapping resources itself.

## Dependencies and Integration Points

It depends on PCI resource APIs, IORESOURCE flags, the 8250 internal `struct uart_8250_port` definition, and kernel module export namespaces. It is used by the generic PCI driver and dedicated PCI sibling drivers such as Microchip PCI1XXXX to keep BAR setup behavior consistent.

## Risks and Edge Cases

The helper assumes that memory BAR callers pass a valid mapping covering `offset`; it does not check resource length or null `iomem` before doing pointer arithmetic. IO BAR setup ignores the requested `regshift` by design, which is correct for standard port IO but wrong if a caller expected shifted port IO. A non-memory BAR on no-IO-port architectures fails with `-ENXIO`, so callers must propagate that rather than trying to register a partial port.

## Test Signals

Test signals include compile/link coverage of `SERIAL_8250_PCI` namespace users, probe of MMIO and port-IO PCI UARTs, no-IOPORT builds where IO BAR devices fail cleanly with the warning, invalid BAR index rejection, and successful tty registration using the fields populated by this helper.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/8250/8250_pcilib.c -->
