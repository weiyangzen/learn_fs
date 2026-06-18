# sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8195/mt8195-audsys-clkid.h

## Purpose
Defines the MT8195 audiosys gate clock id namespace used by the audsys gate table and by MT8195 audio code that indexes `afe_priv->clk[]`.

## Important APIs, Types, and Functions
The file defines one anonymous enum from `CLK_AUD_AFE` through `CLK_AUD_GASRC19`, ending with `CLK_AUD_NR_CLK`. IDs cover core AFE gates, LRCK counter, SPDIF tuners, APLL tuners, DAC/ADC and hires gates, DMIC clocks, line-in/eARC tuners, I2S/TDM/HDMI/PCM interface clocks, A1/A2/A3/A4 system clocks, memif clocks for DL and UL channels, and GASRC0-19 clocks.

## Control Flow
No runtime logic exists. The enum order is used as a stable index into `aud_clks[]` and lookup arrays.

## State and Persistence
No state is stored here. The ids address persistent clock framework objects registered by `mt8195_audsys_clk_register()` and hardware gate bits in audio top registers.

## Dependencies and Integration Points
Included by `mt8195-audsys-clk.c` and expected to stay consistent with `mt8195-afe-clk.h`/private clock arrays. DAI code refers to higher-level `MT8195_CLK_AUD_*` indexes, while this header supplies the audsys registration id range for those gates.

## Risks
Enum reordering or inserting entries without updating `aud_clks[]` can silently bind a clock name to the wrong id. Missing new hardware gates prevents DAPM or DAI paths from enabling required blocks. The anonymous enum style offers no type safety.

## Test Signals
Build failures catch only gross missing symbols. Runtime tests should check all expected `aud_*` gate names are registered and that ADDA, eTDM, PCM, memif, HDMI/DP, and GASRC consumers can enable their corresponding clocks.
