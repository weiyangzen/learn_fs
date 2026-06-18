# sources/distributed-fs/ceph-client/drivers/spi/spi-intel-platform.c

## Purpose

`spi-intel-platform.c` is the platform-device front-end for the Intel PCH/PCU SPI flash controller. It supports non-PCI enumeration paths by receiving `struct intel_spi_boardinfo` as platform data, mapping the MMIO resource, and delegating controller initialization to the shared Intel SPI core.

## Important APIs, Types, and Functions

The only functional entry point is `intel_spi_platform_probe()`. It retrieves platform data, maps resource 0 with `devm_platform_ioremap_resource()`, and calls `intel_spi_probe()`. The platform driver exposes `intel_spi_groups` through its driver `dev_groups` and declares the `platform:intel-spi` alias.

## Control Flow

When a platform device named `intel-spi` probes, the front-end validates that platform data exists, maps MMIO, and invokes the common core. The core then configures sequencers, registers spi-mem operations, and creates SPI NOR child devices.

## State and Persistence Behavior

This wrapper owns no independent state. All persistent state and flash side effects are handled by `spi-intel.c`; platform data remains owned by the enumerating platform code.

## Dependencies and Integration Points

It depends on platform devices, `spi-intel.h`, and boardinfo supplied by x86 platform code. It is an integration shim for systems where the SPI controller is described by platform resources instead of a PCI function.

## Risks and Edge Cases

Missing platform data returns `-EINVAL`; incorrect boardinfo type will make the core use wrong register offsets or sequencer capabilities. Resource mapping errors are propagated directly. There is no front-end write-protect callback unless boardinfo supplies one.

## Test Signals

Test probe with valid and missing platform data, invalid MMIO resource, each supported boardinfo type supplied by platform code, sysfs group presence, and common-core SPI NOR discovery through the platform path.
