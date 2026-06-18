<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/ti/omap-mcbsp-priv.h -->
# sources/distributed-fs/ceph-client/sound/soc/ti/omap-mcbsp-priv.h

## Purpose
Private register, bitfield, cached-MMIO, and state header for the OMAP McBSP ASoC DAI driver and sidetone support.

## APIs, Types, and Functions
Defines McBSP register indices, bit macros for SPCR/PCR/RCR/XCR/SRGR/MCR/CCR/SYSCON/IRQ registers, DMA operating mode constants, clock-source constants, `struct omap_mcbsp_reg_cfg`, forward declaration of sidetone data, and central `struct omap_mcbsp`. Inline helpers `omap_mcbsp_write()` and `omap_mcbsp_read()` update both hardware and a u16/u32 register cache, with macros for cached and uncached access. It declares sidetone init/start/stop.

## Control Flow, State, and Persistence
The header itself does not execute runtime control flow, but it defines the persistent McBSP state shared by controller and sidetone code: device/clock/MMIO, IRQs, active/configured/free flags, platform data, register cache pointer, DMA data, FIFO thresholds, format, input frequency, latency, word length, clock divider, and PM QoS request.

## Dependencies and Integration
Depends on `linux/platform_data/asoc-ti-mcbsp.h` for SoC quirks and callbacks. Used by `omap-mcbsp.c` and `omap-mcbsp-st.c`; the public machine-driver boundary is kept in `omap-mcbsp.h`.

## Risks and Test Signals
Risks include cache coherency assumptions for write-only or status bits, u16/u32 register-size branching, direct casts into `reg_cache`, SoC revision differences hidden behind `has_ccr`/`has_wakeup`, and `mcbsp_omap1()` compile-time behavior. Test signals are register programming on OMAP1/2/3/4 variants, cached interrupt-clear behavior, sidetone register access, and FIFO threshold/CCR paths on hardware with and without those blocks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/ti/omap-mcbsp-priv.h -->
