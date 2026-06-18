# sources/distributed-fs/ceph-client/sound/soc/codecs/rt1318-sdw.c

## Purpose
SoundWire SDCA ASoC driver for RT1318. It initializes the amplifier over SDW, exposes DP1 playback and DP2 feedback capture, sets SDCA sample-frequency controls for supported rates, and manages class-D power through an SDCA PDE.

## APIs, Types, and Functions
Core functions are `rt1318_sdw_probe()`, `rt1318_sdw_init()`, `rt1318_read_prop()`, `rt1318_update_status()`, `rt1318_io_init()`, suspend/resume, component probe, and DAI ops `rt1318_sdw_hw_params()`, `rt1318_sdw_pcm_hw_free()`, `rt1318_set_sdw_stream()`, and shutdown. `rt1318_classd_event()` writes PDE23 requested power state. Register support is provided by `rt1318_reg_defaults[]`, `rt1318_blind_write[]`, readable/volatile filters, and controls/widgets/routes for RX channel selection, DAC mute, class-D output, and feedback capture.

## Control Flow
Probe initializes a 32-bit-address/8-bit-value SDW regmap, allocates private state, starts cache-only mode, registers the component and one DAI, then enables runtime PM without marking the slave active. `read_prop` declares source port 2 and sink port 1 as full data ports. On attach, `io_init` disables cache-only mode, marks runtime PM active on first attach, applies the blind-write sequence, and marks `first_hw_init`/`hw_init`. `hw_params` builds SDW stream and port config manually, maps playback to RX DP1 and capture to TX DP2, derives a channel mask from ALSA channel count, adds the slave, maps 16/32/44.1/48/96/192 kHz to SDCA sample-frequency indexes, and writes the CS21 sample-rate control.

## State and Persistence
State is `struct rt1318_sdw_priv`: component, regmap, SDW slave, bus params, and initialization flags. Regcache preserves control values across PM transitions; resume waits for SoundWire reinitialization when necessary and syncs all cached registers. The blind-write hardware state is reapplied only when SDCA function status and attach flow require initialization.

## Dependencies and Integration
Depends on SoundWire, SDCA control macros, regmap, runtime PM, and ALSA SoC DAI/DAPM. It binds SDW id 0x025d:0x1318 class 0x3, DAI `rt1318-aif`, streams `DP1 Playback` and `DP2 Capture`, and constants from `rt1318-sdw.h`.

## Risks and Test Signals
Risks include returning `-EINVAL` after `sdw_stream_add_slave()` if an unsupported rate is detected, which can leave cleanup dependent on upper-layer hw_free, no TDM slot customization, and no DMI/firmware use despite included headers. Test signals include supported-rate playback/capture, unsupported rate rejection, SDCA sample-frequency register writes, DP1/DP2 stream removal on hw_free, DAPM class-D PS0/PS3 transitions, runtime resume after detach, and regmap volatile-range correctness for calibration/status registers.
