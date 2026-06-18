<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/max98373-sdw.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/max98373-sdw.c

## Purpose

This file is the SoundWire bus front-end for the MAX98373 smart amplifier. It combines a SoundWire-aware regmap, SoundWire slave properties, runtime and system PM, stream port setup, and SoundWire DAI callbacks with the common MAX98373 ASoC component exported by `max98373.c`.

## Important APIs, types, and functions

The key entry points are `max98373_sdw_probe()`, `max98373_init()`, `max98373_read_prop()`, `max98373_update_status()`, `max98373_bus_config()`, `max98373_sdw_dai_hw_params()`, `max98373_pcm_hw_free()`, `max98373_sdw_set_tdm_slot()`, `max98373_suspend()`, and `max98373_resume()`. The driver registers one DAI, `max98373-aif1`, with playback and capture support at 8 kHz through 96 kHz using 32-bit samples. `max98373_sdw_regmap` uses 32-bit register addresses, 8-bit values, single register SoundWire transfers, RBTREE cache, and readable/volatile callbacks that include SoundWire SCP/DP windows and amplifier registers.

## Control flow

Probe initializes the SoundWire regmap, allocates `struct max98373_priv`, puts the regmap into cache-only mode until enumeration, reads slot/reset properties through the common `max98373_slot_config()`, registers the common SoundWire component, and enables autosuspend. `read_prop` advertises source port 3 for IV feedback capture and sink port 1 for playback, with simple channel-prepare state machines. When the SoundWire core reports `SDW_SLAVE_ATTACHED`, `update_status` calls `max98373_io_init()`, which leaves cache-only mode, optionally bypasses cache for first hardware init, resumes runtime PM, performs software reset, programs SoundWire mode, ADC/IV defaults, LR mix, DC blockers, TX source and Hi-Z slots, optional interleave, speaker enable, BDE, and limiter. Bus reconfiguration derives the SoundWire clock selector from `curr_dr_freq / 2` and programs `MAX98373_R2036_SOUNDWIRE_CTRL`.

The DAI `hw_params` path obtains the SoundWire stream runtime from ALSA DAI DMA data, converts PCM params to SoundWire stream/port configs, chooses port 1 for playback and port 3 for capture, optionally overrides playback channel count/mask from TDM slot settings, then calls `sdw_stream_add_slave()`. It validates up to 16 channels, maps 16/24/32-bit widths to PCM channel-size fields, and maps rates from 8 kHz to 96 kHz into `MAX98373_R2028_PCM_SR_SETUP_2` for both speaker and IV ADC rate fields. `hw_free` removes the SoundWire slave from the stream. `set_stream` and `shutdown` attach and clear the SoundWire stream pointer through DAI DMA data.

## State and persistence behavior

Persistent driver state lives in `struct max98373_priv`: SoundWire slave pointer, regmap, slot selections, TDM flags, cache array, `hw_init`, `first_hw_init`, playback slot count, and RX mask. Suspend snapshots the small feedback-cache register list before forcing cache-only mode. Resume waits for SoundWire reattachment when `slave->unattach_request` is set, clears cache-only, and syncs cached writes. Hardware init is deliberately deferred until SoundWire enumeration to avoid ASoC PM races before the device is attached.

## Dependencies and integration points

This file depends on Linux SoundWire (`sdw_slave`, `sdw_stream_add_slave`, `snd_sdw_params_to_config`), ALSA SoC DAI/component registration, runtime PM, regmap, firmware node properties handled in `max98373.c`, and common MAX98373 register definitions. It integrates with ACPI ID `MX98373`, OF compatible `maxim,max98373`, and SoundWire device ID vendor `0x019F`/part `0x8373`.

## Risks and test signals

Risks include failed or late SoundWire reattachment during resume, clock selector fallback silently using 12.288 MHz on unsupported bus clocks, cache coherence around first hardware init and reset, and TDM playback masks that are accepted without validating slot count against actual stream channels. Test signals include successful SoundWire attach logs, no `Initialization not complete` timeout on suspend/resume, correct DP1 playback and DP3 IV capture stream setup, register cache sync after runtime suspend, and working 8/16/44.1/48/96 kHz streams with and without TDM slot configuration.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/max98373-sdw.c -->
