# sources/distributed-fs/ceph-client/drivers/clk/mstar/Kconfig

Purpose: declares configuration symbols for MStar/SigmaStar MSC313 clock drivers.

Important APIs/types: `MSTAR_MSC313_CPUPLL` controls the CPU PLL driver. `MSTAR_MSC313_MPLL` controls the MPLL/divider block and selects `REGMAP_MMIO`.

Control flow: Kconfig symbols are boolean, default to `ARCH_MSTARV7`, and allow `COMPILE_TEST` builds. The MPLL symbol ensures regmap-mmio support is present.

State and persistence: build-time only; it affects which object files are compiled into the kernel.

Dependencies and integration: tied to the mstar Makefile and platform drivers with `builtin_platform_driver`.

Risks: both drivers are bool-only and not modular. Missing `REGMAP_MMIO` selection for CPUPLL is fine because it uses raw MMIO, but any future refactor must revisit dependencies.

Test signals: `ARCH_MSTARV7` defconfig inclusion, `COMPILE_TEST` allmod/allnoconfig builds, and verifying selected objects in the build log.
