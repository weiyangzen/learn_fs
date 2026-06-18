# sources/distributed-fs/ceph-client/include/soc/nuvoton/clock-npcm8xx.h

Purpose: defines the auxiliary-bus wrapper used to share NPCM8xx clock-controller register base state with auxiliary child devices.

Important APIs/types/functions: provides `struct npcm_clock_adev` with `void __iomem *base` and embedded `struct auxiliary_device adev`, plus `to_npcm_clock_adev()` using `container_of()`.

Control flow: no runtime flow beyond the inline cast helper. The primary clock driver creates or passes auxiliary devices; reset or other child drivers recover the containing object with the helper.

State and persistence: the persistent state is the MMIO base pointer and auxiliary-device lifetime. The header does not allocate, free, or modify hardware state.

Dependencies and integration: depends on `linux/auxiliary_bus.h` and `linux/container_of.h`. It is included by `drivers/clk/clk-npcm8xx.c` and `drivers/reset/reset-npcm.c`.

Risks: container casts require that the supplied auxiliary device is embedded in `struct npcm_clock_adev`. A wrong object type corrupts memory access. Test signals include NPCM8xx clock/reset probe, auxiliary-device binding, and reset register operations.
