# sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8365/mt8365-dai-adda.c

## Purpose
Internal analog AD/DA backend DAI implementation for MT8365. It programs ADDA downlink/uplink source blocks, shared ADDA AFE-on state, DAC/ADC clock gates, I2S output coupling for playback, and DAPM routes for internal DAC playback, internal ADC capture, and hostless FM-to-ADDA paths.

## APIs, Types, and Functions
Public functions are `mt8365_dai_enable_adda_on()`, `mt8365_dai_disable_adda_on()`, and `mt8365_dai_adda_register()`. Internal stream helpers include `mt8365_dai_set_adda_out()`, `mt8365_dai_set_adda_in()`, `mt8365_dai_set_adda_out_enable()`, `mt8365_dai_set_adda_in_enable()`, `mt8365_dai_int_adda_startup()`, `mt8365_dai_int_adda_shutdown()`, and `mt8365_dai_int_adda_prepare()`. The file defines the `"INT ADDA"` DAI driver, DAI ops, DAPM mixers `ADDA_DL_CH1/CH2`, virtual switch `INT ADDA O03_O04`, and routes connecting O03/O04, `AIN Mux`, `Hostless FM DL`, and the ADDA streams.

## Control Flow, State, and Persistence
Startup enables the main AFE clock and gates DAC plus pre-distortion clocks for playback or ADC clock for capture. Prepare is idempotent per stream via `be_data[].prepared[]`; playback programs downlink rate/voice mode, pre-distortion and SDM defaults, configures I2S output by rate/bit width, then enables ADDA downlink and I2S output. Capture programs the uplink sampling rate, selects internal ADC, enables UL source, asserts ADDA AFE-on, and enables `AFE_AUD_PAD_TOP` FIFO bits. Shutdown disables the prepared direction, clears I2S/ADDA enables, disables stream-specific clock gates, and disables the main clock. Shared ADDA AFE-on is tracked by a file-scope `adda_afe_on_ref_cnt` protected by `afe_ctrl_lock`.

## Dependencies and Integration
Depends on regmap, ALSA PCM params, MT8365 clock/common headers, and MediaTek `mtk-dai-adda-common.h` for rate transforms. It is registered by `mt8365-afe-pcm.c` and shares ADDA AFE-on state with the DMIC DAI, which calls `mt8365_dai_enable_adda_on()` and `mt8365_dai_disable_adda_on()` for the DMIC clock divider. Playback also depends on I2S helpers declared in `mt8365-afe-common.h`.

## Risks and Test Signals
The file-scope `adda_afe_on_ref_cnt` is global rather than per device, which is risky if multiple MT8365 AFE instances ever exist. Many `regmap_update_bits()` and I2S helper return paths are either ignored or only partly propagated. Disable paths use bitwise negated values under masks, relying on regmap masking semantics. Hardware sequencing includes required delays only on uplink disable, so playback pop/click behavior depends on register defaults and external analog paths. Test signals are internal DAC playback at 8/16/44.1/48 kHz, internal ADC capture at 16/32/48 kHz, simultaneous DMIC/ADDA refcount balance, DAPM route activation for `AIN Mux` and hostless FM, clean shutdown with no ADDA underflow warnings, and audio quality checks for the programmed -0.3 dB downlink gain and SDM defaults.
