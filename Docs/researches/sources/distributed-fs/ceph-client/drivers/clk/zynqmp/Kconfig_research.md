# sources/distributed-fs/ceph-client/drivers/clk/zynqmp/Kconfig

Purpose: declares the `COMMON_CLK_ZYNQMP` configuration symbol for Xilinx ZynqMP UltraScale+ clock controller support.

Important APIs/types/functions: this is Kconfig metadata, not C code. The symbol is a boolean prompt that depends on `ZYNQMP_FIRMWARE || COMPILE_TEST` and defaults to `ZYNQMP_FIRMWARE`.

Control flow: during kernel configuration, enabling this option makes ZynqMP firmware-backed clock support selectable when the PMU firmware interface is present or compile testing is requested.

State and persistence: no runtime state; the selected symbol becomes part of the kernel configuration and influences compilation.

Dependencies and integration points: integrates with platform firmware support through `ZYNQMP_FIRMWARE`; paired with the local Makefile and the CCF drivers in this directory.

Risks: the local Makefile builds objects using `CONFIG_ARCH_ZYNQMP`, not `CONFIG_COMMON_CLK_ZYNQMP`, so configuration wiring should be reviewed if clocks are expected under compile-test-only builds.

Test signals: `menuconfig` visibility, `allyesconfig`/`COMPILE_TEST` builds, and ZynqMP platform builds confirming the clock controller object set is included.
