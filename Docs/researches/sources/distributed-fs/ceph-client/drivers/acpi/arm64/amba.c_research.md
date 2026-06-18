# sources/distributed-fs/ceph-client/drivers/acpi/arm64/amba.c

## Purpose
Creates AMBA bus devices from selected ACPI-described ARM peripherals.

## Important APIs, Types, And Functions
Registers an ACPI scan handler matching `ARMH0061` and `ARMH0330`. Main functions are `acpi_amba_init()`, `amba_register_dummy_clk()`, and `amba_handler_attach()`.

## Control Flow
Initialization registers a fixed dummy `apb_pclk` and adds the ACPI scan handler. Attach skips ACPI nodes that already have a physical device, allocates an AMBA device, extracts the first memory resource and up to `AMBA_NR_IRQS` IRQs, assigns an ACPI fwnode, optionally attaches the parent's physical device, and calls `amba_device_add()`.

## State And Persistence
Created AMBA devices persist in the device model. The dummy clock is global clock state.

## Dependencies And Integration Points
Integrates ACPI scan, AMBA bus, resource parsing, clkdev, fwnode, and parent device linkage.

## Risks
Risks include missing memory resources, duplicate physical-node creation, dummy clock registration failures not being checked, and resource parsing changes affecting AMBA probing.

## Test Signals
Test matching HIDs, resource extraction, parent device assignment, already-bound ACPI nodes, AMBA add failure cleanup, and driver binding for PL061 and DMA-330.
