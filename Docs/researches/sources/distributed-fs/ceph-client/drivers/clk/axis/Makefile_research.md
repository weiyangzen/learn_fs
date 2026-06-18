<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/axis/Makefile -->
# sources/distributed-fs/ceph-client/drivers/clk/axis/Makefile

Purpose: This Makefile connects the Axis ARTPEC-6 clock controller implementation to the kernel build. It builds `clk-artpec6.o` when `CONFIG_MACH_ARTPEC6` is enabled.

Important APIs, types, and functions: There are no C APIs in this file. Its single functional line is `obj-$(CONFIG_MACH_ARTPEC6) += clk-artpec6.o`, under an SPDX header.

Control flow: Kbuild evaluates the configuration symbol and includes the object in the built-in or modular object list according to the symbol value. Because the driver itself uses `builtin_platform_driver()` and `CLK_OF_DECLARE_DRIVER()`, this build inclusion is what makes both early and platform-driver phases available for ARTPEC-6 systems.

State and persistence behavior: The file has no runtime state. Its persistent behavior is build graph selection.

Dependencies and integration points: It depends on `CONFIG_MACH_ARTPEC6`, which is expected to be selected for Axis ARTPEC-6 platforms. The object implements the DT-compatible `"axis,artpec6-clkctrl"` provider.

Risks and test signals: The main risk is build omission: without this line or with a wrong config symbol, ARTPEC-6 DT clock consumers cannot resolve their clocks. Test signals are successful ARTPEC-6 builds, `clk-artpec6.o` present in the link, and runtime registration of the ARTPEC-6 clock provider.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/axis/Makefile -->
