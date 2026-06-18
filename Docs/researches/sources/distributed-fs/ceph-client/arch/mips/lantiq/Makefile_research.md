# sources/distributed-fs/ceph-client/arch/mips/lantiq/Makefile

Purpose: selects core Lantiq platform objects and descends into SoC-family subdirectories.

Important APIs/types/functions: always builds `irq.o`, `clk.o`, and `prom.o`; conditionally builds `early_printk.o`, `xway/`, and `falcon/`.

Control flow: object inclusion follows `CONFIG_EARLY_PRINTK`, `CONFIG_SOC_TYPE_XWAY`, and `CONFIG_SOC_FALCON`.

State and persistence: build-system state only.

Dependencies and integration: ties Kconfig selections to platform initialization, interrupt controller, clock, PROM, and SoC-specific sysctrl/reset code.

Risks: missing directory selection prevents `ltq_soc_detect()` or `ltq_soc_init()` providers from linking.

Test signals: Lantiq allmod/allyes builds and per-SoC defconfig link checks.
