# sources/distributed-fs/ceph-client/drivers/cdx/Kconfig

## Purpose
This Kconfig file introduces `CONFIG_CDX_BUS`, the core Composable DMA Transfer bus support option, and includes the controller subdirectory configuration.

## Important APIs, Types, and Functions
There are no C APIs here. The key symbol is `CDX_BUS`, a boolean option named "CDX Bus driver". It depends on `OF && ARM64 || COMPILE_TEST`, which permits normal device-tree ARM64 builds and broader compile coverage.

## Control Flow
During kernel configuration, enabling `CDX_BUS` makes the bus core buildable and then sources `drivers/cdx/controller/Kconfig` so controller drivers can be selected beneath the bus option.

## State and Persistence Behavior
The selected configuration persists in the kernel `.config`. At runtime, this symbol controls whether the CDX bus core and optional MSI support from the Makefile are compiled into the kernel image.

## Dependencies and Integration Points
The help text describes CDX devices as firmware-discovered, memory-mapped FPGA fabric devices exposed to APUs through a CDX controller. The symbol gates `drivers/cdx/Makefile` and controller options.

## Risks
The dependency expression relies on Kconfig precedence: `(OF && ARM64) || COMPILE_TEST`. Real hardware support requires OF and ARM64 even though compile-test can build elsewhere. Disabling this symbol removes all CDX bus registration and controller integration.

## Test Signals
Configuration tests should verify that `CDX_BUS=y` is selectable on ARM64+OF and under `COMPILE_TEST`, and that selecting it causes `cdx.o` and controller choices to appear in the build.
