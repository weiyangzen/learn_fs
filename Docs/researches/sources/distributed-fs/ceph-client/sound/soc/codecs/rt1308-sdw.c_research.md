# sources/distributed-fs/ceph-client/sound/soc/codecs/rt1308-sdw.c

## Purpose
SoundWire ASoC component driver for the Realtek RT1308 speaker amplifier. It exposes one playback DAI over SoundWire DP1, configures SDW slave properties, initializes the vendor register space when the slave attaches, applies optional BQ parameters from firmware properties, and wires amplifier power sequencing into DAPM.

## APIs, Types, and Functions
Key entry points are the `sdw_driver` callbacks `rt1308_sdw_probe()`, `rt1308_update_status()`, `rt1308_read_prop()`, `rt1308_bus_config()`, suspend/resume, and the ASoC DAI ops `rt1308_sdw_hw_params()`, `rt1308_sdw_pcm_hw_free()`, `rt1308_set_sdw_stream()`, `rt1308_sdw_shutdown()`, and `rt1308_sdw_set_tdm_slot()`. `rt1308_io_init()` performs first-attach hardware programming, `rt1308_clock_config()` maps bus clock rates to chip clock codes, `rt1308_apply_bq_params()` writes property-supplied filter triplets, and `rt1308_classd_event()` controls class-D power status and efuse calibration reads. The file uses `struct rt1308_sdw_priv` from the header for regmap, SoundWire slave, bus params, initialization flags, TDM slot state, hardware version, and BQ data.

## Control Flow
Probe creates an SDW regmap and calls `rt1308_sdw_init()`, which allocates private state, sets regcache cache-only, registers the component/DAI, and enables autosuspended runtime PM while leaving the device inactive until enumeration. `read_prop` advertises paging, invalid-initial-parity quirk, sink port 1, and port prep timeouts. On SDW attach, `update_status` calls `io_init`; that enables regmap I/O, marks runtime PM active on first initialization, resets the SDW register window, reads the hardware version, writes a vendor preset sequence, applies BQ parameters, and marks `hw_init`/`first_hw_init`. Bus reconfiguration stores `sdw_bus_params` and programs the clock code from half the current data-rate frequency. Playback hw_params converts ALSA params into SoundWire stream and port config, forces DP1 RX, applies any TDM slot mask override, and adds the slave to the stream; hw_free removes it.

## State and Persistence
Persistent driver state is only in memory and hardware registers: `hw_init`, `first_hw_init`, `rx_mask`, `slots`, `hw_ver`, cached regmap state, and optional `bq_params`. Hardware settings survive only while the device remains powered or hibernated; resume synchronizes the 0xc000-0xcfff region after reattachment. The hibernation flag at 0xcf01 lets later initialization skip the blind preset when the device already retained state.

## Dependencies and Integration
Depends on ALSA SoC component/DAI/DAPM APIs, SoundWire slave and stream helpers, runtime PM, regmap SDW transport, and RT1308 register definitions from `rt1308.h` plus defaults/private state from `rt1308-sdw.h`. It integrates with machine drivers through DAI name `rt1308-aif`, stream `DP1 Playback`, optional `set_tdm_slot`, and `realtek,bq-params*` device properties.

## Risks and Test Signals
Risks include invalid BQ property lengths because `rt1308_apply_bq_params()` steps by three without validating divisibility, unsupported SoundWire clock frequencies returning `-EINVAL`, playback-only stream support despite generic DAI callbacks, and resume races around `unattach_request`/initialization completion. Test signals include SDW enumeration with device id 0x025d:0x1308, 48 kHz playback on DP1, valid and invalid TDM masks, bus clock rate changes, runtime suspend/resume with regcache sync, DAPM class-D transitions, and BQ property application.
