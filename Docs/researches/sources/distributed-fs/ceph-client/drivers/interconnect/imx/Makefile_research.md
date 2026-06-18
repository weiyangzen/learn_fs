# sources/distributed-fs/ceph-client/drivers/interconnect/imx/Makefile

Purpose: build map for i.MX interconnect helper and SoC topology modules.

Important APIs/types/functions: composite objects map `imx.o`, `imx8mm.o`, `imx8mq.o`, `imx8mn.o`, and `imx8mp.o` to module names ending in `-interconnect`.

Control flow: `obj-$(CONFIG_INTERCONNECT_IMX*)` lines compile the common helper and selected SoC drivers.

State and persistence: no runtime state; affects kernel build products and module names.

Dependencies/integration: consumes symbols from `imx/Kconfig`.

Risks and test signals: verify each Kconfig symbol produces the expected object/module and that module builds resolve helper exports. Spacing is inconsistent but not functionally relevant.
