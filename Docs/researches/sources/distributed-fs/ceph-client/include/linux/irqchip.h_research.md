# sources/distributed-fs/ceph-client/include/linux/irqchip.h

## Purpose
`irqchip.h` provides declaration macros and probe glue for interrupt-controller drivers discovered by Device Tree, ACPI MADT subtables, or platform driver matching.

## Important APIs, types, and functions
It defines `platform_irq_probe_t`, typecheck sentinels, `IRQCHIP_DECLARE`, `platform_irqchip_probe`, `IRQCHIP_PLATFORM_DRIVER_BEGIN`, `IRQCHIP_MATCH`, `IRQCHIP_PLATFORM_DRIVER_END`, `IRQCHIP_ACPI_DECLARE`, and `irqchip_init`.

## Control flow
Built-in irqchip drivers declare compatible strings and init/probe callbacks. Early DT init uses `OF_DECLARE_2`; platform-driver macros build a suppressed-bind-attrs platform driver; ACPI declarations register MADT subtable probes. `irqchip_init` is compiled out when irqchip support is disabled.

## State and persistence
The header creates static match/probe metadata through macros. Runtime state is owned by individual irqchip drivers.

## Dependencies and integration points
It integrates with ACPI, OF, platform devices, module tables, built-in platform drivers, and core irqchip initialization.

## Risks and test signals
Risks include wrong callback signature, duplicate declaration names, missing module match tables, and platform probe disabled by config. Tests should compile DT/ACPI/platform irqchip variants and boot-probe controllers from each discovery path.
