# sources/distributed-fs/ceph-client/arch/arm/mach-mvebu/Makefile

Purpose: Build glue for MVEBU platform objects.

Important APIs/types/functions: Links shared system-controller/soc-id, V7 board/coherency/PMSU/CPU reset/SMP/PM objects, and SoC-specific Dove/Kirkwood files according to config.

Control flow: No runtime flow.

State and persistence: No runtime state.

Dependencies and integration points: Depends on MVEBU Kconfig symbols and PM/SMP options.

Risks: Object gating controls critical boot paths; missing coherency/PMSU objects breaks SMP or suspend on Armada.

Test signals: Compile each MVEBU SoC config with SMP/PM combinations.
