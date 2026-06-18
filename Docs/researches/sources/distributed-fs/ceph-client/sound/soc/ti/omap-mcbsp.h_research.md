<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/ti/omap-mcbsp.h -->
# sources/distributed-fs/ceph-client/sound/soc/ti/omap-mcbsp.h

## Purpose
Public McBSP ASoC header for machine drivers. It exposes clock-source IDs, divider IDs, and the sidetone control-registration helper without leaking private register definitions.

## APIs, Types, and Functions
Defines `enum omap_mcbsp_clksrg_clk` with internal FCLK, external CLKS, internal ICLK, external CLKX, and external CLKR sources. Defines `enum omap_mcbsp_div` with `OMAP_MCBSP_CLKGDV`. Declares `omap_mcbsp_st_add_controls(struct snd_soc_pcm_runtime *rtd, int port_id)`.

## Control Flow, State, and Persistence
No runtime state is stored here. The constants are passed by board drivers into `snd_soc_dai_set_sysclk()` and `snd_soc_dai_set_clkdiv()`; the sidetone helper adds controls to an existing DAI at runtime.

## Dependencies and Integration
Includes `sound/dmaengine_pcm.h` for ASoC/DMA-related types and is included by OMAP machine drivers such as N810, Pandora, OSK, RX51, and TWL4030 boards.

## Risks and Test Signals
Risks are ABI drift between enum values and `omap-mcbsp.c`, plus machine drivers calling `set_sysclk` before `set_fmt` in cases documented as order-sensitive. Test signals are build coverage of all machine drivers, clock/divider calls accepted by McBSP, and RX51 sidetone controls appearing for port 2.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/ti/omap-mcbsp.h -->
