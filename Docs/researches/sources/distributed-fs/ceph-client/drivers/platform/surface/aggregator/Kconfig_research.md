# sources/distributed-fs/ceph-client/drivers/platform/surface/aggregator/Kconfig

## Purpose

This Kconfig file defines the Surface System Aggregator Module core, optional SSAM client bus, and optional error-injection support. It controls the SAM-over-SSH controller driver and the kernel interface used by Surface client drivers.

## Important APIs, Types, And Functions

`menuconfig SURFACE_AGGREGATOR` is a tristate requiring `SERIAL_DEV_BUS`, `ACPI`, and `!RISCV`, and selecting `CRC_ITU_T`. `CONFIG_SURFACE_AGGREGATOR_BUS` is a boolean extension that defaults to yes and provides a dedicated SSAM bus/device type. `CONFIG_SURFACE_AGGREGATOR_ERROR_INJECTION` depends on `FUNCTION_ERROR_INJECTION` and enables transport/communication failure injection hooks.

## Control Flow

There is no runtime control flow. These symbols select whether `surface_aggregator.o` is built, whether `bus.o` is linked into it, and whether error-injection sites are compiled in related request/packet layers.

## State And Persistence

The state is build configuration only. It determines whether the controller exists, whether SSAM client devices can bind through a bus, and whether test-only failure injection is available.

## Dependencies And Integration Points

The core integrates with serdev, ACPI, CRC-ITU-T, Surface Aggregator clients, and the parent Surface platform Kconfig. The bus option is a dependency for registry, hub, tablet-switch, and other SSAM device drivers.

## Risks

The `ACPI && !RISCV` dependency constrains the core even though `core.c` has OF fallback paths for some setup values. Disabling `SURFACE_AGGREGATOR_BUS` keeps the core available but removes bus-based clients, which can surprise configurations that select higher-level functionality. Error injection must remain development-only.

## Test Signals

Configuration tests should cover core built-in, core as module, bus enabled/disabled, and compile-test where supported. Runtime tests are serdev probe, firmware version query, and SSAM client-driver binding through the bus when enabled.
