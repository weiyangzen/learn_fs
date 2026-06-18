# sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8192/mt8192-dai-tdm.c

This file implements the MT8192 TDM/HDMI playback backend DAI, including HDMI channel mux controls, TDM format/rate/channel programming, MCLK/BCLK DAPM supplies, GPIO selection, and private clock state.

`struct mtk_afe_tdm_priv` stores DAI id, BCK id/rate, output mode, BCK/LRCK inversion, MCLK id/multiple/rate, and selected APLL. Helper functions map PCM format to TDM word length, channel BCK width, LRCK width, channel count encoding, and channels per serial data line. `mt8192_dai_tdm_register()` installs the single `TDM` playback DAI, widgets, routes, and private state.

DAPM supplies sequence APLL, TDM MCK, TDM BCK, and TDM enable. MCK/BCK events call `mt8192_mck_enable()` and `mt8192_mck_disable()`, and the TDM enable event toggles TDM GPIO state. `set_sysclk()` validates output-clock direction and exact APLL divisibility. `set_fmt()` stores I2S/DSP_A/DSP_B mode and inversion. `hw_params()` derives default MCLK as `rate * 512` when needed, computes BCK, warns on clock incompatibility, writes `AFE_TDM_CON1` and `AFE_TDM_CON2`, and updates HDMI channel count.

State is devm-owned `tdm_priv` plus AFE TDM registers, HDMI connection registers, top clock dividers, and pinctrl state. `mclk_rate` is reset on MCLK power-down, so the next hw_params recomputes default MCLK unless `set_sysclk()` runs again. Risks include warning rather than failing when BCK cannot be generated and the single-instance assumption in `get_tdm_id_by_name()`. Test signals include I2S/DSP_A/DSP_B formats, inversion modes, 2/4/6/8-channel playback, explicit/default MCLK, both APLL families, and DAPM power sequencing.
