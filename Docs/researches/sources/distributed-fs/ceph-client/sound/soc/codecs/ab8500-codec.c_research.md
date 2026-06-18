# sources/distributed-fs/ceph-client/sound/soc/codecs/ab8500-codec.c

## Purpose
ASoC component driver for the ST-Ericsson AB8500 PMIC audio codec. It exposes the AB8500 audio register bank through a custom regmap, declares a large DAPM graph for analog/digital microphone, headset, earpiece, lineout, handsfree, vibrator, sidetone, ANC, and TDM paths, and registers two DAIs for playback and capture on the IF0 digital interface.

## Important APIs, Types, and Functions
The private `struct ab8500_codec_drvdata` stores the audio regmap, a control mutex, and sidetone FIR state. `ab8500_codec_read_reg()` and `ab8500_codec_write_reg()` bridge regmap operations to `abx500_get_register_interruptible()` and `abx500_set_register_interruptible()` on the `AB8500_AUDIO` bank. `sid_status_control_get()` and `sid_status_control_put()` implement a user control for applying the sidetone FIR sequence. `ab8500_audio_setup_mics()`, `ab8500_audio_set_ear_cmv()`, and `ab8500_audio_init_audioblock()` perform probe-time PMIC/audio setup. DAI operations are `ab8500_codec_set_dai_fmt()` and `ab8500_codec_set_dai_tdm_slot()`. The platform probe allocates state, initializes regmap, and calls `devm_snd_soc_register_component()`.

## Control Flow
Platform probe creates driver data and the regmap, then ASoC component probe parses device-tree microphone and earpiece properties, adds microphone bias routes, configures microphone mode bits, initializes the audio block through sysctrl, writes hardware default overrides, disables the ANC configure input pin, and initializes the control mutex. Runtime DAI setup first validates provider/consumer mode and clock gating, then programs IF0 format, polarity, bit delay, word length, slot count, and TDM DA/AD slot mapping. Sidetone application checks the hardware busy bit, writes zeroed FIR coefficients across the sidetone address space, toggles the FIR set bit, and marks the in-memory state configured.

## State and Persistence
Persistent state is hardware register state plus `sid_status` in driver memory. The regmap has custom read/write callbacks but no cache policy in this file, so hardware access depends on AB8500 MFD calls. Device-tree choices for mic bias, mic type, and earpiece common-mode voltage are applied at probe and not reread. The sidetone state is protected by `ctrl_lock`.

## Dependencies and Integration Points
This file depends on AB8500 MFD/sysctrl APIs, ASoC component/DAI/DAPM APIs, device tree, and the local `ab8500-codec.h` register map. Machine drivers interact through DAI format and TDM slot callbacks plus ASoC controls and routes. Board data is expressed through `stericsson,*` device-tree properties and AB8500 platform devices.

## Risks
The DAPM/control surface is broad and register-bit dense, so bitfield mismatches can silently route or power the wrong path. TDM slot handling only accepts masks within 8 bits and only maps 0, 1, 2, or 8 active slots; other valid-looking masks fail. `ffs()`/`fls()` values are one-based, so slot math must stay aligned with AB8500 register encoding. The sidetone write path zeros coefficients rather than loading user-provided values and returns `-EIO` for unsupported enum writes. Device-tree property spelling includes `stericsson,earpeice-cmv`, which may be externally depended upon despite the typo.

## Test Signals
Useful tests are component probe on AB8500 hardware or emulated regmap callbacks, DAPM route enumeration, ALSA control read/write for sidetone and gains, DAI format matrix tests for I2S/DSP_A/DSP_B plus inversion/provider modes, TDM slot tests for 2/4/8/16 total slots and invalid masks, and boot logs for AB8500 MFD/sysctrl failures.
