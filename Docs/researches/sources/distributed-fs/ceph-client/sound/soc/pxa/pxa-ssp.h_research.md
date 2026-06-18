# sources/distributed-fs/ceph-client/sound/soc/pxa/pxa-ssp.h

Purpose: declares PXA SSP clock source and divider constants used by machine drivers and the SSP DAI.

Important APIs/types/functions: defines `PXA_SSP_CLK_PLL`, `PXA_SSP_CLK_EXT`, `PXA_SSP_CLK_NET`, `PXA_SSP_CLK_AUDIO`, `PXA_SSP_CLK_NET_PLL`, divider IDs `PXA_SSP_AUDIO_DIV_ACDS`, `PXA_SSP_AUDIO_DIV_SCDB`, `PXA_SSP_DIV_SCR`, audio divider values, network divider values, and `PXA_SSP_PLL_OUT`.

Control flow: no executable flow; values are passed to DAI clock APIs.

State and persistence: no mutable state.

Dependencies and integration: consumed by `pxa-ssp.c` and board/machine code that configures SSP clocks.

Risks: constants are ABI-like for machine drivers; changing values would silently alter clock selection. Some constants are historical and not all are consumed in the current driver.

Test signals: compile coverage of users and clock configuration tests for each clock source path.
