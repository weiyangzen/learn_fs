# sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8188/mt8188-afe-clk.h

Purpose: Declares the MT8188 AFE clock contract shared by the platform and DAI implementations. It defines stable clock IDs, audio PLL IDs, MCLK source selectors, APLL widget names, and the public helper prototypes implemented by `mt8188-afe-clk.c`.

Important APIs and types: The first enum defines `MT8188_CLK_*` IDs for the 26 MHz root, APLL roots, APLL dividers, top muxes, ADSP/audio 26M, AFE gates, DMIC/ADDA/eTDM/PCMIF gates, memif gates, and `MT8188_CLK_NUM`. The second enum defines `MT8188_AUD_PLL1` through `MT8188_AUD_PLL5`. The third enum defines MCLK selectors from 26M through APLL5. Public helpers cover source selection (`mt8188_afe_get_mclk_source_clk_id()`, `mt8188_afe_get_default_mclk_source_by_rate()`), clock registration (`mt8188_afe_init_clock()`), generic clock operations, APLL enable/disable, main AFE clock enable/disable, and register-read/write clock enable/disable.

Control flow and integration: This header is included by all mt8188 audio implementation files that need clocks. The PCM platform calls initialization and runtime-PM helpers. eTDM uses MCLK source, clock parent/rate, and APLL helpers. ADDA, DMIC, and PCMIF rely on clock IDs indirectly through DAPM clock supplies and private clock arrays.

State and persistence: The header itself stores no state, but its enum numeric order is persistent ABI inside this driver set because `mt8188-afe-clk.c` indexes the `aud_clks[]` name table by these values and `mt8188_afe_private->clk` is allocated to `MT8188_CLK_NUM`.

Dependencies: Requires a forward declaration of `struct mtk_base_afe` and references `struct clk` in prototypes without declaring it in this file. In practice, users include Linux clock headers or another header that declares it.

Risks: Enum/name-table drift is the main maintenance risk. `MT8188_CLK_AUD_TOP0_SPDF` exists in the enum but the corresponding `aud_clks[]` entry in the implementation is not populated in the scanned source, while later clock IDs are populated by designated initializers. That is survivable only because designated initializers are used, but any consumer requesting the unpopulated ID would get a NULL clock name. The MCLK enum lists APLL3-5, but implementation helpers reject those selectors.

Test signals: Compile coverage catches missing `struct clk` visibility and prototype mismatches. Probe coverage catches missing clock-name providers for populated IDs. eTDM MCLK tests should confirm 26M/APLL1/APLL2 selector behavior and verify unsupported APLL3-5 paths fail cleanly.
