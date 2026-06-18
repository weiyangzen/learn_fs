# sources/distributed-fs/ceph-client/drivers/interconnect/imx/Kconfig

Purpose: Kconfig definitions for NXP i.MX interconnect support.

Important APIs/types/functions: defines `INTERCONNECT_IMX` plus per-SoC `INTERCONNECT_IMX8MM`, `INTERCONNECT_IMX8MN`, `INTERCONNECT_IMX8MQ`, and `INTERCONNECT_IMX8MP`.

Control flow: the generic symbol depends on `ARCH_MXC || COMPILE_TEST`; each SoC symbol depends on the generic helper. Selection controls whether the common helper and topology platform modules are built.

State and persistence: persistent kernel `.config` state determines built-in/module availability.

Dependencies/integration: paired with `imx/Makefile` and platform drivers that call `imx_icc_register()`.

Risks and test signals: build-test all symbols as built-in and modules, including COMPILE_TEST. Per-SoC entries have no help text, so usability depends on symbol names.
