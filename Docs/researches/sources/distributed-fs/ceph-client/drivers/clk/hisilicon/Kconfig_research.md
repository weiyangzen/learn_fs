# sources/distributed-fs/ceph-client/drivers/clk/hisilicon/Kconfig

Purpose: defines HiSilicon clock and reset controller configuration options for multiple SoCs and firmware-mediated stub clocks.

Important APIs/types/functions: options include `COMMON_CLK_HI3516CV300`, `COMMON_CLK_HI3519`, `COMMON_CLK_HI3559A`, `COMMON_CLK_HI3660`, `COMMON_CLK_HI3670`, `COMMON_CLK_HI3798CV200`, `COMMON_CLK_HI6220`, `RESET_HISI`, `STUB_CLK_HI6220`, and `STUB_CLK_HI3660`.

Control flow: SoC clock options depend on `ARCH_HISI || COMPILE_TEST`, many select `RESET_HISI`, and defaults follow `ARCH_HISI`. Stub clock options depend on mailbox support and default to their SoC clock driver.

State and persistence: no runtime state.

Dependencies and integration points: drives the Hisilicon Makefile and reset-controller availability. Stub clock selections integrate clock drivers with mailbox firmware channels.

Risks: some SoC drivers are bool while others are tristate, so link coverage must include both built-in and module paths. Reset support is selected only by CRG-style drivers; Hi3660 does not select `RESET_HISI` here.

Test signals: Kconfig build matrix for each SoC under `COMPILE_TEST`, mailbox-disabled configs for stub clocks, and reset-controller symbol availability for CRG drivers.
