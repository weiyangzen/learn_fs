# sources/distributed-fs/ceph-client/drivers/irqchip/irqchip.c

## Purpose
Provides the common irqchip initialization entry points. It invokes linker-table based OF irqchip initialization and ACPI irqchip table probing, and exports the helper used by platform irqchip drivers to defer until their parent domains exist.

## Important APIs, Types, And Functions
`irqchip_init()` calls `of_irq_init(__irqchip_of_table)` and `acpi_probe_device_table(irqchip)`. `platform_irqchip_probe()` retrieves the matched probe callback, finds the OF parent, defers when the parent domain is not ready, and invokes the platform irqchip probe with the parent node.

## Control Flow
Early boot calls `irqchip_init()` to initialize statically declared irqchips. Platform irqchip drivers using `IRQCHIP_PLATFORM_DRIVER` later call `platform_irqchip_probe()` through their probe path. The helper normalizes a self-parent node to `NULL`, checks parent domain readiness, and returns `-EPROBE_DEFER` when ordering is not yet satisfied.

## State And Persistence
The file owns no mutable runtime state except the linker-table sentinel symbol. It coordinates initialization rather than representing hardware.

## Dependencies And Integration Points
Depends on OF irq initialization, ACPI probing, platform devices, match data carrying `platform_irq_probe_t`, and the special `__irqchip_of_table` linker section.

## Risks
Missing match data returns `-EINVAL`, so platform irqchip declarations must provide probe callbacks. Parent-domain checks use `DOMAIN_BUS_ANY`; specialized domains may still require additional checks in the driver. Incorrect handling of self-parent nodes could cause false defers.

## Test Signals
Boot systems with OF-only, ACPI-only, and platform irqchip drivers, verify parent-probe deferral ordering, and test platform irqchip nodes whose parent is not yet registered.
