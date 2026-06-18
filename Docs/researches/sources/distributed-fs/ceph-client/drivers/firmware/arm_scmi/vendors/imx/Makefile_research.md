# sources/distributed-fs/ceph-client/drivers/firmware/arm_scmi/vendors/imx/Makefile

Purpose: This Makefile maps NXP i.MX SCMI vendor protocol Kconfig symbols to their module objects.

Important APIs/types/functions: It builds `imx-sm-bbm.o`, `imx-sm-cpu.o`, `imx-sm-lmm.o`, and `imx-sm-misc.o` based on `CONFIG_IMX_SCMI_BBM_EXT`, `CONFIG_IMX_SCMI_CPU_EXT`, `CONFIG_IMX_SCMI_LMM_EXT`, and `CONFIG_IMX_SCMI_MISC_EXT`.

Control flow: Standard `obj-$(CONFIG_...)` inclusion controls which protocol extension objects are linked.

State and persistence: Build metadata only.

Dependencies and integration points: It pairs with the i.MX vendor Kconfig and module aliases in each C file.

Risks and edge cases: Object names must match the module names described in Kconfig and the source files. No ordering constraints are expressed.

Test signals: Build each extension as built-in and module and verify expected objects/modules are emitted.
