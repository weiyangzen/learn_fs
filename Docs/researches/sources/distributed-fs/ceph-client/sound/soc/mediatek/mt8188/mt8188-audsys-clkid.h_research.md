# sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8188/mt8188-audsys-clkid.h

Purpose: Defines the local audio subsystem gate-clock IDs consumed by `mt8188-audsys-clk.c`. The enum indexes the `aud_clks[CLK_AUD_NR_CLK]` gate descriptor array and names the gate set for AFE core, tuners, ADDA, DMIC, eTDM, PCMIF, memifs, and GASRC clocks.

Important definitions: IDs include core and tuner gates (`CLK_AUD_AFE`, `CLK_AUD_APLL1_TUNER`, `CLK_AUD_APLL2_TUNER`), ADDA gates (`CLK_AUD_DAC`, `CLK_AUD_ADC`, hires variants), DMIC gates, line-in/eARC tuner gates, eTDM/PCMIF related gates (`CLK_AUD_I2SIN`, `CLK_AUD_TDM_IN`, `CLK_AUD_I2S_OUT`, `CLK_AUD_TDM_OUT`, `CLK_AUD_HDMI_OUT`, `CLK_AUD_PCMIF`), memory interface gates for UL/DL memifs, GASRC gates, and `CLK_AUD_NR_CLK`.

Control flow and integration: `mt8188-audsys-clk.c` uses these values as designated indexes into the gate descriptor array. `CLK_AUD_NR_CLK` controls allocation size and unregister loop bounds. The higher-level `MT8188_CLK_AUD_*` IDs in `mt8188-afe-clk.h` are separate but must map by clock name to these registered gates.

State and persistence: The enum itself stores no runtime state, but its numeric order is a persistent internal ABI for the descriptor table and cleanup arrays.

Dependencies: Independent header with only include guards. It is included by the audsys clock registration implementation.

Risks: Reordering or inserting IDs without matching `aud_clks[]` descriptors can register gates under wrong indexes or leave NULL lookup slots. Because the descriptor table uses designated initializers in this tree, omissions become missing clocks rather than positional misregistration, but cleanup still iterates to `CLK_AUD_NR_CLK`.

Test signals: Build validates enum names used by `mt8188-audsys-clk.c`. Runtime probe plus clock lookup tests validate every descriptor name has a usable gate. DAPM path testing validates the subset needed by active audio routes.
