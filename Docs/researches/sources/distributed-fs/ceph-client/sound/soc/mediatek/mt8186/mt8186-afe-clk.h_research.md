# sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8186/mt8186-afe-clk.h

## Purpose

This header defines the MT8186 AFE clock IDs, APLL names, and clock-control APIs used by MT8186 DAI and platform-driver code.

## Important APIs, Types, and Data

`PERI_BUS_DCM_CTRL` gives the infracfg offset used during runtime resume. `APLL1_W_NAME` and `APLL2_W_NAME` are string labels used in DAPM routes. The APLL enum identifies `MT8186_APLL1` and `MT8186_APLL2`. The large clock enum indexes `afe_priv->clk` and includes audsys gates, infra clocks, top muxes, APLL roots, I2S/TDM master-clock selectors, APLL divider clocks, and `CLK_CLK26M`.

The exported prototypes include core clock init, CG enable/disable, runtime clock enable/disable, APLL enable/disable helpers, APLL selection helpers, audio internal bus parent selection, and MCLK enable/disable.

## Control Flow and State

The header holds no state. Its enum ordering is state-critical because implementation tables in `mt8186-afe-clk.c` use these values as array indexes. `CLK_NUM` sizes the private clock-handle array.

## Dependencies and Integration Points

It forward-declares `struct mtk_base_afe` and is included by AFE PCM, ADDA, and other DAI files that need to control clocks. The enum must stay aligned with `aud_clks[CLK_NUM]` and with clock IDs expected by the local audsys gate provider.

## Risks

Changing enum order breaks all array-indexed clock lookup. Adding a clock without extending `aud_clks[]` or the DT clock graph can cause null clock pointers or missing gate registration. The comment that MCK helpers will be replaced by CCF indicates a transitional API with higher maintenance risk.

## Test Signals

Build failures catch missing declarations, but runtime probe and DAPM clock-supply activation are the meaningful tests. Inspect logs for every clock name being acquired and test MCLK users after any enum/table change.
