# sources/distributed-fs/ceph-client/include/linux/pm-trace.h

## Purpose
the suspend/resume trace helper interface. It records device fingerprints across failed suspend
cycles so the next boot can identify the last device reached.

## Important APIs, types, and functions
Macros/constants: `PM_TRACE_H`, `TRACE_DEVICE`, `TRACE_RESUME`, `TRACE_SUSPEND`. Types: none visible
in this header. Declared or inline functions: `set_trace_device`, `generate_pm_trace`,
`show_trace_dev_match`, `pm_trace_rtc_valid`, `pm_trace_is_enabled`.

## Control flow
Setup code fills the declared platform-data structure, constants, or callbacks before registering
the platform or auxiliary device. The matching driver reads these values during probe to select
hardware revisions, pins, bus widths, GPIOs, DMA settings, regulator defaults, firmware names, or
callback hooks; later runtime paths use saved copies for interrupt handling, PM, hotplug, media
routing, or register programming. Consumers include `sources/distributed-fs/ceph-
client/kernel/power/main.c`, `sources/distributed-fs/ceph-client/include/linux/mc146818rtc.h`,
`sources/distributed-fs/ceph-client/drivers/base/power/main.c`, `sources/distributed-fs/ceph-
client/drivers/base/power/trace.c`.

## State and persistence
The header is declarative and has no persistence by itself. State appears when board code
instantiates the declared structs or constants, when drivers cache the values in their private data,
and when callbacks mutate underlying hardware registers. Values are usually fixed for the lifetime
of the registered device.

## Dependencies and integration points
It includes `linux/types.h`, `asm/pm-trace.h`. Direct source-tree consumers found by include search
are `sources/distributed-fs/ceph-client/kernel/power/main.c`, `sources/distributed-fs/ceph-
client/include/linux/mc146818rtc.h`, `sources/distributed-fs/ceph-client/drivers/base/power/main.c`,
`sources/distributed-fs/ceph-client/drivers/base/power/trace.c`. It integrates with the driver core,
bus types, PM domains, wakeup-source code, runtime PM, suspend/hibernate sequencing, and
architecture/platform suspend backends.

## Risks and test signals
Risks are mostly contract drift between platform setup and the consuming driver: wrong enum value,
missing callback, invalid GPIO/IRQ/resource, incompatible register-width or bus-mode flag, or
lifetime bugs when platform data points at temporary storage. Test signals include compile coverage
for the owning architecture, probe with representative board data, DT/ACPI fallback comparison where
available, suspend/resume if callbacks are present, and fault injection for missing optional
resources.

## Source-read signal
Read `sources/distributed-fs/ceph-client/include/linux/pm-trace.h` completely for this pass (43 lines, 940 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/linux/pm-trace.h_research.md`.
