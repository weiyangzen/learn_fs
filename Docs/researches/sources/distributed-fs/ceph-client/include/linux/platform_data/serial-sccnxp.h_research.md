# sources/distributed-fs/ceph-client/include/linux/platform_data/serial-sccnxp.h

## Purpose
`serial-sccnxp.h` is a Linux kernel serial/UART board-data header. It gives board files, MFD
children, ACPI glue, or platform-device setup code a compact contract for passing the primary type
`struct sccnxp_pdata` into the matching driver at probe time.

## Important APIs, types, and functions
Macros/constants: `_PLATFORM_DATA_SERIAL_SCCNXP_H_`, `SCCNXP_MAX_UARTS`, `LINE_OP0`, `LINE_OP1`,
`LINE_OP2`, `LINE_OP3`, `LINE_OP4`, `LINE_OP5`, `LINE_OP6`, `LINE_OP7`, `LINE_IP0`, `LINE_IP1`,
`LINE_IP2`, `LINE_IP3`, and 11 more. Types: `struct sccnxp_pdata`. Declared or inline functions:
none visible in this header. Important struct details: struct sccnxp_pdata fields include `const u8
reg_shift`, `const u32 mctrl_cfg[SCCNXP_MAX_UARTS]`, `const unsigned int poll_time_us`.

## Control flow
Setup code fills the declared platform-data structure, constants, or callbacks before registering
the platform or auxiliary device. The matching driver reads these values during probe to select
hardware revisions, pins, bus widths, GPIOs, DMA settings, regulator defaults, firmware names, or
callback hooks; later runtime paths use saved copies for interrupt handling, PM, hotplug, media
routing, or register programming. Consumers include `sources/distributed-fs/ceph-
client/arch/mips/sni/a20r.c`, `sources/distributed-fs/ceph-client/drivers/tty/serial/sccnxp.c`.

## State and persistence
The header is declarative and has no persistence by itself. State appears when board code
instantiates the declared structs or constants, when drivers cache the values in their private data,
and when callbacks mutate underlying hardware registers. Values are usually fixed for the lifetime
of the registered device.

## Dependencies and integration points
Direct source-tree consumers found by include search are `sources/distributed-fs/ceph-
client/arch/mips/sni/a20r.c`, `sources/distributed-fs/ceph-client/drivers/tty/serial/sccnxp.c`. It
integrates through `struct platform_device` platform data, board files, MFD child registration, and
legacy non-DT setup paths; many modern systems may replace parts of this contract with Device Tree,
ACPI, or software-node properties.

## Risks and test signals
Risks are mostly contract drift between platform setup and the consuming driver: wrong enum value,
missing callback, invalid GPIO/IRQ/resource, incompatible register-width or bus-mode flag, or
lifetime bugs when platform data points at temporary storage. Test signals include compile coverage
for the owning architecture, probe with representative board data, DT/ACPI fallback comparison where
available, suspend/resume if callbacks are present, and fault injection for missing optional
resources.

## Source-read signal
Read `sources/distributed-fs/ceph-client/include/linux/platform_data/serial-sccnxp.h` completely for this pass (84 lines, 1938 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/linux/platform_data/serial-sccnxp.h_research.md`.
