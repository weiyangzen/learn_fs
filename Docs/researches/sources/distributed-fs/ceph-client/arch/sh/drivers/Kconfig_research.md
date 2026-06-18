# sources/distributed-fs/ceph-client/arch/sh/drivers/Kconfig



Source read size: 20 lines, 583 bytes.



Purpose: SH-specific driver Kconfig aggregation for DMA, companion chips, heartbeat LEDs, and push-switch framework.

Important APIs/types/functions: sources `arch/sh/drivers/dma/Kconfig` and `arch/sh/cchips/Kconfig`; defines `HEARTBEAT` and `PUSH_SWITCH`.

Control flow: selected symbols determine whether SH-specific platform drivers and legacy DMA support are compiled.

State and persistence: build-time configuration only.

Dependencies and integration points: feeds `arch/sh/drivers/Makefile`, board platform devices, and optional modules.

Risks and test signals: selecting old SH drivers without matching board platform data gives dead devices or build-only coverage. Test defconfigs using heartbeat and push-switch.
