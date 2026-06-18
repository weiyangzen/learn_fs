# sources/distributed-fs/ceph-client/sound/soc/codecs/rt1316-sdw.c

## Purpose
SoundWire SDCA ASoC driver for the RT1316 smart amplifier. It provides stereo playback on DP1, IV-sense capture on DP2, SDCA power and function-unit controls, vendor blind initialization, optional BQ parameter loading, and runtime-PM-aware SoundWire attach/resume handling.

## APIs, Types, and Functions
Important callbacks are `rt1316_sdw_probe()`, `rt1316_sdw_init()`, `rt1316_read_prop()`, `rt1316_update_status()`, `rt1316_io_init()`, PM suspend/resume, component probe, and DAI ops `rt1316_sdw_hw_params()`, `rt1316_sdw_pcm_hw_free()`, `rt1316_set_sdw_stream()`, and `rt1316_sdw_shutdown()`. DAPM event helpers `rt1316_classd_event()` and `rt1316_pde24_event()` drive SDCA PDE power states. Controls cover RX channel clustering, XU24 bypass, IV tags, IV mixer switches, and DAC output-volume update mode.

## Control Flow
Probe creates an SDW regmap and registers the component while regcache is cache-only. `read_prop` advertises paging, parity quirk, source port 2, sink port 1, and full data-port properties. When the slave reports attached, `io_init` enables regmap I/O, sets runtime PM active on the first attach, writes a software reset and the blind-write preset, then marks initialization complete. Component probe reads optional `realtek,bq-params*` properties and, if hardware was already initialized, resumes runtime PM and applies those register triplets. `hw_params` converts ALSA params to SoundWire stream config, maps playback to DP1 and capture to DP2, and adds the slave. DAPM class-D and PDE24 widgets switch SDCA PDE entities between PS0 and PS3.

## State and Persistence
State is held in `struct rt1316_sdw_priv`: component, regmap, slave, bus params, `hw_init`, `first_hw_init`, and BQ parameter storage. Regcache tracks SDCA and vendor registers across suspend; resume waits for initialization completion if the slave detached, clears `unattach_request`, and syncs the regmap. No persistent storage is used.

## Dependencies and Integration
Depends on SoundWire SDCA register macros, regmap SDW, runtime PM, ALSA SoC DAPM/DAI helpers, and header constants from `rt1316-sdw.h`. The driver binds SDW id 0x025d:0x1316 class 0x3, registers DAI `rt1316-aif`, and exposes `DP1 Playback` plus `DP2 Capture`.

## Risks and Test Signals
Risks include BQ property count not being checked for multiples of three, fixed 48 kHz rate advertisement, no explicit bus_config clock handling, and resume requiring timely SoundWire initialization. Test signals include SDW enumeration, playback and IV capture at 48 kHz with 16/20/24-bit formats, DP1/DP2 stream add/remove, DAPM PDE transitions, XU24 bypass and IV controls, runtime suspend/resume, and property-driven BQ writes.
