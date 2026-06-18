# sources/distributed-fs/ceph-client/drivers/hsi/controllers/Kconfig

## Purpose
Defines the HSI controller submenu and the `OMAP_SSI` build option for the legacy OMAP Synchronous Serial Interface hardware driver.

## Important APIs, Types, and Functions
This is Kconfig metadata rather than C code. `config OMAP_SSI` is a tristate option titled "OMAP SSI hardware driver".

## Control Flow
The option is visible under the HSI controllers comment. It can be built in, modular, or disabled when its dependencies are satisfied.

## State and Persistence
No runtime state. The selected Kconfig value persists in the kernel build configuration and controls whether `omap_ssi.o` is built.

## Dependencies and Integration Points
Requires `HSI`, `OF`, `COMMON_CLK`, and either `ARCH_OMAP3` or `COMPILE_TEST`. It integrates with the local controller Makefile, which maps `CONFIG_OMAP_SSI` to the OMAP SSI object.

## Risks and Test Signals
Risk is mostly dependency coverage: the driver assumes device-tree data, common clock support, and OMAP-compatible resources. Build testing should cover both `ARCH_OMAP3` and `COMPILE_TEST`, including module and built-in configurations.
