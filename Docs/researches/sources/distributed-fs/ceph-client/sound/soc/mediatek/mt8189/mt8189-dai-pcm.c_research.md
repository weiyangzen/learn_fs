# sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8189/mt8189-dai-pcm.c

## Purpose

`mt8189-dai-pcm.c` implements the MT8189 PCM0 backend DAI. Despite the file banner saying I2S control, the implementation programs `AFE_PCM0_INTF_CON0/CON1`, exposes a single symmetric playback/capture PCM DAI, and provides DAPM mixers/routes for PCM0 playback and capture through the AFE interconnect.

## Important APIs, Types, And Data

The exported hook is `mt8189_dai_pcm_register()`, which adds `mtk_dai_pcm_driver[]`, `mtk_dai_pcm_widgets[]`, and `mtk_dai_pcm_routes[]` to `afe->sub_dais`. The DAI array contains one DAI named `PCM 0` with id `MT8189_DAI_PCM_0`, 1-2 channel playback and capture, 8/16/32/48 kHz rates, S16/S24/S32 formats, and symmetric rate/sample-bits constraints.

The file defines PCM register-value enums for left-channel repeat, VBT 16 kHz mode, modem selection, sync type, BT mode, AFIFO/ASRC source, master/slave clocking, word length, PCM mode, format, BCLK inversion, enable, and 1x enable domain. `pcm_rate_transform()` maps ALSA rates to `MTK_AFE_PCM_RATE_*`; `pcm_1x_rate_transform()` maps the same rates to PCM 1x relatch encodings.

DAPM widgets include three playback mixers (`PCM_0_PB_CH1`, `PCM_0_PB_CH2`, `PCM_0_PB_CH4`), a `PCM_0_EN` supply on `AFE_PCM0_INTF_CON0`, a `PCM0_CG` clock gate on `AUDIO_TOP_CON0`, and external input/output pins. Mixers route ADDA UL, DL2, DL_24CH, I2SIN1, and DL0 sources into PCM0 playback channels.

## Control Flow

`mtk_dai_pcm_hw_params()` reads the sample rate, converts both main and 1x encodings, and checks whether the playback or capture DAPM widgets are already active. If either side is active, it returns without reprogramming registers, preserving symmetric full-duplex operation while the other direction is running. For `MT8189_DAI_PCM_0`, it builds `pcm_con0` as non-inverted BCLK, no left-channel repeat, VBT disabled, one-BCK sync, AFIFO bypass mode, master mode, rate-selected PCM mode, and I2S frame format. It builds `pcm_con1` as internal modem, dual-mic TX mode, 26 MHz hopping domain, and the selected 1x rate. It updates `AFE_PCM0_INTF_CON0` while preserving the enable bit and writes masked `AFE_PCM0_INTF_CON1`.

## State And Persistence

The PCM DAI itself has no private allocation. Its state is the hardware registers and DAPM widget active flags. Because hw_params skips programming when playback or capture is already active, the first stream to configure PCM0 determines the shared hardware configuration until both directions go inactive. Register state is preserved by the main AFE regmap/cache and runtime PM handling.

## Dependencies And Integration Points

The file depends on `mt8189-afe-common.h` for PCM register fields, `mt8189-interconnection.h` for input port bit positions, and ASoC DAPM/PCM helpers. The machine driver defines a `PCM_0_BE` link with I2S-style DAI format, playback-only BE settings, and a startup op that restricts rate to 48 kHz. Other DAI files and the memif route table reference the `PCM 0 Capture` and `PCM 0 Playback` widgets.

## Risks

The hw_params active-widget guard prevents conflicting reconfiguration but also silently accepts a second stream whose requested params may differ; symmetric DAI constraints mitigate this, but route-level tests should still cover duplex use. Unsupported rates fall back to 48 kHz with a warning rather than failing. The `regmap_update_bits()` mask for `AFE_PCM0_INTF_CON0` uses `~PCM0_EN_MASK_SFT`, so correctness depends on `PCM0_EN_MASK_SFT` being an actual mask value, not just a shifted-bit macro name. The file banner is misleading, which can confuse maintainers searching for PCM-specific code.

## Test Signals

Run PCM0 playback and capture at the supported rates, then duplex/open-order tests to ensure the active-widget guard preserves the first configuration and ALSA constraints prevent incompatible params. Regmap tracing should confirm PCM0 enable is not clobbered by hw_params. DAPM should show `PCM0_CG` and `PCM_0_EN` active for both playback and capture paths.
