# sources/distributed-fs/ceph-client/drivers/firmware/arm_scmi/vendors/imx/Kconfig

Purpose: This Kconfig file defines NXP i.MX vendor SCMI protocol extension drivers for BBM, CPU, LMM, and MISC protocols.

Important APIs/types/functions: `IMX_SCMI_BBM_EXT` enables RTC/button BBM support. `IMX_SCMI_CPU_EXT` enables i.MX CPU protocol operations and depends on `IMX_SCMI_CPU_DRV`. `IMX_SCMI_LMM_EXT` enables Logical Machine Manager operations and depends on `IMX_SCMI_LMM_DRV`. `IMX_SCMI_MISC_EXT` enables miscellaneous controls and depends on `IMX_SCMI_MISC_DRV`. All depend on `ARM_SCMI_PROTOCOL` or compile-test with OF and default to `y` on `ARCH_MXC`.

Control flow: Config selections determine whether corresponding vendor protocol modules are built from the Makefile. The dependencies on external i.MX consumer drivers prevent protocol extensions from being built unless consumers are available, except BBM.

State and persistence: Build configuration only.

Dependencies and integration points: Integrates NXP vendor protocol implementations with the SCMI framework and i.MX architecture defaults. The module names are `imx-sm-bbm`, `imx-sm-cpu`, `imx-sm-lmm`, and `imx-sm-misc`.

Risks and edge cases: Default `y` on `ARCH_MXC` can compile vendor protocol code into kernels with matching architecture. Compile-test coverage depends on OF. Consumer-driver dependency symbols must remain synchronized with public `linux/scmi_imx_protocol.h` users.

Test signals: Build i.MX configs with each extension built-in/module/disabled, compile-test non-i.MX OF builds, and verify modules register vendor SCMI protocol aliases.
