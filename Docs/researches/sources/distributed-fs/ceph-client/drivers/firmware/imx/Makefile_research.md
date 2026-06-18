# sources/distributed-fs/ceph-client/drivers/firmware/imx/Makefile

Purpose: Maps i.MX firmware Kconfig symbols to objects.

Important APIs/types/functions: Builds `imx-dsp.o`, legacy SCU components (`imx-scu.o misc.o imx-scu-irq.o rm.o imx-scu-soc.o`), and SCMI wrappers (`sm-cpu.o`, `sm-misc.o`, `sm-lmm.o`).

Control flow: No runtime flow. Kbuild includes objects according to selected config symbols.

State and persistence behavior: No state. Object grouping controls which exported symbols and initcalls are present.

Dependencies and integration points: Integrates with i.MX Kconfig. The SCU group is built as one logical feature because helper files depend on the core `imx_scu_call_rpc()` implementation.

Risks and test signals: The SCMI object lines use `obj-${CONFIG_...}` syntax, which should be checked against standard Kbuild expectations (`obj-$(CONFIG_...)`). Test signals include building each SCMI symbol as module/built-in and confirming expected objects are linked.
