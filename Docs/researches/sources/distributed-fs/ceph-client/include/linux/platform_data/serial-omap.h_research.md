# sources/distributed-fs/ceph-client/include/linux/platform_data/serial-omap.h

## Purpose
`serial-omap.h` is a Linux kernel serial/UART board-data header. It gives board files, MFD children,
ACPI glue, or platform-device setup code a compact contract for passing the primary type `struct
omap_uart_port_info` into the matching driver at probe time.

## Important APIs, types, and functions
Macros/constants: `__OMAP_SERIAL_H__`, `OMAP_SERIAL_DRIVER_NAME`, `OMAP_SERIAL_NAME`. Types: `struct
omap_uart_port_info`. Declared or inline functions: `int`, `void`. Important struct details: struct
omap_uart_port_info fields include `bool dma_enabled`, `unsigned int uartclk`, `upf_t flags`,
`unsigned int dma_rx_buf_size`, `unsigned int dma_rx_timeout`, `unsigned int autosuspend_timeout`,
`unsigned int dma_rx_poll_rate`, `int (*get_context_loss_count)(struct device *)`.

## Control flow
Setup code fills the declared platform-data structure, constants, or callbacks before registering
the platform or auxiliary device. The matching driver reads these values during probe to select
hardware revisions, pins, bus widths, GPIOs, DMA settings, regulator defaults, firmware names, or
callback hooks; later runtime paths use saved copies for interrupt handling, PM, hotplug, media
routing, or register programming. Consumers include `sources/distributed-fs/ceph-
client/drivers/tty/serial/omap-serial.c`.

## State and persistence
The header is declarative and has no persistence by itself. State appears when board code
instantiates the declared structs or constants, when drivers cache the values in their private data,
and when callbacks mutate underlying hardware registers. Values are usually fixed for the lifetime
of the registered device.

## Dependencies and integration points
It includes `linux/serial_core.h`, `linux/device.h`, `linux/pm_qos.h`. Direct source-tree consumers
found by include search are `sources/distributed-fs/ceph-client/drivers/tty/serial/omap-serial.c`.
It integrates through `struct platform_device` platform data, board files, MFD child registration,
and legacy non-DT setup paths; many modern systems may replace parts of this contract with Device
Tree, ACPI, or software-node properties.

## Risks and test signals
Risks are mostly contract drift between platform setup and the consuming driver: wrong enum value,
missing callback, invalid GPIO/IRQ/resource, incompatible register-width or bus-mode flag, or
lifetime bugs when platform data points at temporary storage. Test signals include compile coverage
for the owning architecture, probe with representative board data, DT/ACPI fallback comparison where
available, suspend/resume if callbacks are present, and fault injection for missing optional
resources.

## Source-read signal
Read `sources/distributed-fs/ceph-client/include/linux/platform_data/serial-omap.h` completely for this pass (42 lines, 1024 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/linux/platform_data/serial-omap.h_research.md`.
