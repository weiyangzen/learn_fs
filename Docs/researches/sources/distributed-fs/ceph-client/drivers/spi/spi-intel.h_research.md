# sources/distributed-fs/ceph-client/drivers/spi/spi-intel.h

## Purpose

`spi-intel.h` is the private interface between the Intel SPI flash core and its PCI/platform front-ends. It keeps the front-ends small by exposing the shared probe function and sysfs attribute groups while importing the boardinfo type definition used to describe controller variants and write-protect callbacks.

## Important APIs, Types, and Functions

The header includes `linux/platform_data/x86/spi-intel.h`, declares `extern const struct attribute_group *intel_spi_groups[]`, and declares `int intel_spi_probe(struct device *dev, void __iomem *base, const struct intel_spi_boardinfo *info)`.

## Control Flow

PCI and platform wrappers include this header, map their MMIO resources, prepare or retrieve `struct intel_spi_boardinfo`, and call `intel_spi_probe()`. They also reference `intel_spi_groups` in their driver definitions so sysfs attributes exported by the core are attached to front-end devices.

## State and Persistence Behavior

The header defines no state. It exposes hooks through which front-ends hand persistent MMIO mappings and boardinfo into the core. Any flash or BIOS-lock side effects happen inside `spi-intel.c`.

## Dependencies and Integration Points

It depends on Linux device/MMIO types through including C files and on the x86 Intel SPI platform-data header. It integrates the core with PCI and platform modules without exposing internal `struct intel_spi`.

## Risks and Edge Cases

The ABI between wrappers and core is intentionally narrow; incorrect boardinfo passed through this function can still select wrong register offsets. Header changes can break both wrappers and any other in-tree user of `intel_spi_probe()` or `intel_spi_groups`.

## Test Signals

Build tests should compile both PCI and platform wrappers with this header. Link tests should verify `intel_spi_probe` and `intel_spi_groups` exports resolve when modules are built separately.
