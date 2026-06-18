<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap1/mcbsp.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap1/mcbsp.c

## Purpose
Registers OMAP1 McBSP audio/serial port platform devices with fixed memory, IRQ, DMA resources and OMAP1-specific DSP clock request/free operations.

## Important APIs, Types, and Functions
Defines OMAP1 `omap_mcbsp_ops` with `.request`/`.free`, resource tables for 15xx and 16xx, `omap_mcbsp_register_board_cfg()`, and `arch_initcall` `omap1_mcbsp_init()`.

## Control Flow
Initialization exits on non-OMAP1, selects 15xx or 16xx resource tables, allocates a platform-device pointer array, creates `omap-mcbsp` devices, adds resources, sets register width/step, attaches platform data, and registers each device. McBSP1/3 request paths enable `api_ck` and `dsp_ck` on first use and release them on last free.

## State and Persistence Behavior
Persistent state includes `dsp_use`, cached `api_clk`/`dsp_clk`, and the allocated `omap_mcbsp_devices` array. Hardware state includes DSP reset-control bits and enabled clocks for DSP public peripherals.

## Dependencies and Integration Points
Depends on clock framework names `api_ck`/`dsp_ck`, IRQ macros, DMA request numbers, `asoc-ti-mcbsp` platform data, and CPU revision predicates.

## Risks
Clock get failures are tolerated but can leave DSP public McBSP access broken. `dsp_use` is not protected by a lock and assumes serialized McBSP request/free paths. Resource tables must match SoC variant exactly.

## Test Signals
Probe ASoC McBSP on OMAP15xx and OMAP16xx, exercise McBSP1/2/3 playback/capture, and verify clock enable counts return to zero after close. Resource validation should check IRQ/DMA names `rx` and `tx`.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap1/mcbsp.c -->
