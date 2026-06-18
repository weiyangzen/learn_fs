# sources/distributed-fs/ceph-client/drivers/clk/mmp/Kconfig

Purpose: This Kconfig fragment declares the Marvell MMP/PXA1908 common clock driver option.

Important APIs, types, and functions: It defines `COMMON_CLK_PXA1908`, a boolean "Clock driver for Marvell PXA1908" that depends on `ARCH_MMP || COMPILE_TEST`, depends on OF, defaults to `y` for `ARCH_MMP && ARM64`, and selects `AUXILIARY_BUS`.

Control flow: There is no runtime flow. The symbol controls whether PXA1908-specific clock objects are included by the MMP clock Makefile.

State and persistence behavior: This is build configuration state only.

Dependencies and integration points: It integrates with architecture selection, OF availability, and the MMP Makefile entries for PXA1908 APBC/APBCP/MPMU/APMU clocks.

Risks and edge cases: COMPILE_TEST builds require all auxiliary bus and OF dependencies to be available outside native platforms. Default-y behavior only applies to ARM64 MMP builds. Test signals include PXA1908 defconfig, COMPILE_TEST builds, and ensuring the selected object set links with common MMP clock helpers.
