<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-pxa/pxa-dt.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-pxa/pxa-dt.c

Purpose: device-tree machine descriptors for PXA25x, PXA27x, and PXA3xx.

Important objects: `DT_MACHINE_START(PXA25X_DT)`, `DT_MACHINE_START(PXA27X_DT)`, and `DT_MACHINE_START(PXA_DT)` set map IO, restart, and compatible strings (`marvell,pxa250`, `marvell,pxa270`, `marvell,pxa300`, `marvell,pxa310`, `marvell,pxa320`).

Control flow: when a matching root compatible is present, ARM machine selection uses these descriptors. Interrupt and timer init are supplied by irqchip/DT timer infrastructure rather than explicit legacy fields here.

State and persistence: no runtime state beyond selected machine descriptor.

Dependencies and integration: depends on SoC-specific `*_map_io()` and common `pxa_restart()`. Enabled by Kconfig DT machine symbols.

Risks and test signals: compatible strings must match DTS files; missing init fields rely on OF subsystems. Test DT boot for each compatible with timer, IRQ, GPIO, and restart.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-pxa/pxa-dt.c -->
