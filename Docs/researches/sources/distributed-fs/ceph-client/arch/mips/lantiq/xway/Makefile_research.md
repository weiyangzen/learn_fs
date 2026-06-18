# sources/distributed-fs/ceph-client/arch/mips/lantiq/xway/Makefile

Purpose: builds XWAY-family platform support.

Important APIs/types/functions: includes `prom.o`, `sysctrl.o`, `clk.o`, `dma.o`, `gptu.o`, `dcdc.o`, and `vmmc.o`.

Control flow: unconditional within the XWAY subdirectory selected by the parent Makefile.

State and persistence: build-system only.

Dependencies and integration: supplies SoC detection, clocks, PMU/sysctrl, DMA, timers, regulator log probe, and VMMC memory reservation.

Risks: broad unconditional object inclusion means DT compatibility and initcall ordering must keep unused devices harmless.

Test signals: XWAY defconfig link and boot tests across Danube/AR9/VR9/AR10/GRX390 variants.
