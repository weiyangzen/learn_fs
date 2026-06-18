# sources/distributed-fs/ceph-client/drivers/clk/zynqmp/Makefile

Purpose: lists the object files that implement the ZynqMP clock controller.

Important APIs/types/functions: this build file adds `pll.o`, `clk-gate-zynqmp.o`, `divider.o`, `clk-mux-zynqmp.o`, and `clkc.o` when `CONFIG_ARCH_ZYNQMP` is enabled.

Control flow: Kbuild consumes the `obj-$(CONFIG_ARCH_ZYNQMP)` assignment and links the complete clock implementation into the kernel for ZynqMP architecture builds.

State and persistence: no runtime state; it persists build graph membership only.

Dependencies and integration points: integrates with arch selection and the C files that export `zynqmp_clk_register_*()` helpers and the platform driver.

Risks: it does not reference `CONFIG_COMMON_CLK_ZYNQMP`, so the Kconfig symbol in the same directory may not be the direct build switch. Any future object added to the directory must be included here or it will silently not build.

Test signals: `make drivers/clk/zynqmp/`, ZynqMP defconfig builds, and compile-test matrix checks for missing object references.
