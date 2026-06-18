# sources/distributed-fs/ceph-client/sound/soc/codecs/tas2783-sdw.c

## Purpose
This file implements the SoundWire/SDCA ASoC driver for the TAS2783 smart amplifier. It registers a SoundWire slave driver, builds an SDCA-aware regmap, downloads required firmware after the slave attaches, applies UEFI-stored calibration when available, and exposes playback/capture routing plus volume controls for a single smart-amplifier function.

## APIs, Types, and Functions
Core structures include `struct tas2783_prv`, `struct tas_fw_hdr`, `struct tas_fw_file`, and `struct calibration_data`. Key functions are `tas_sdw_probe()`, `tas_sdw_remove()`, `tas_update_status()`, `tas_io_init()`, `tas2783_fw_ready()`, `tas_sdw_hw_params()`, `tas_sdw_pcm_hw_free()`, `tas_port_prep()`, `tas2783_sdca_dev_suspend()`, and `tas2783_sdca_dev_resume()`. Regmap support is defined by `tas_regmap`, `tas2783_sdca_mbq_size()`, `tas2783_readable_register()`, and `tas2783_volatile_register()`. The ASoC component exposes `Amp Volume` and `Speaker Volume` controls, FU21/FU23 DAPM mute events, and DAI ops for SoundWire stream attachment.

## Control Flow
SoundWire probe reads slave properties, allocates private state, optionally parses SDCA function descriptors looking for `SDCA_FUNCTION_TYPE_SMART_AMP`, initializes an MBQ SoundWire regmap in cache-only mode, and registers the ASoC component with runtime PM. When SoundWire reports `SDW_SLAVE_ATTACHED`, `tas_update_status()` syncs cached state and runs `tas_io_init()`. Initialization resets the device, generates a firmware filename from PCI subsystem/link/unique ID or `tas2783-link-uid.bin`, requests firmware asynchronously, waits up to three seconds, then writes SDCA function defaults or a static init sequence. PCM `hw_params` requires successful firmware download, clears a latch bit, powers PDE23 on with retries, maps ALSA params to SoundWire stream/port configuration, and attaches port 1 for playback or port 2 for capture. `hw_free` removes the slave stream and powers the entity off.

## State and Persistence
Persistent runtime state includes `hw_init`, `status`, firmware download completion/success flags, calibration buffer/read size, waitqueue, pde/calibration mutexes, the SDCA parsed function data, and cached regmap values. Calibration is read from UEFI variables `SmartAmpCalibrationData` or `CALI_DATA` under a TAS2783 GUID, validated by magic number, speaker count, calculated size, timestamp, and CRC32, then applied only to the entry matching the SoundWire unique ID. Suspend switches regmap to cache-only; resume waits for reattachment if needed and syncs the cache.

## Dependencies and Integration
Depends on Linux SoundWire core, SDCA helpers, SDCA regmap MBQ support, ASoC, runtime PM, firmware loader, EFI variable services, CRC32, unaligned access helpers, and optional PCI ancestry for firmware naming. It imports `SND_SOC_SDCA` and optionally registers a misc utility interface through `tas25xx_register_misc()` when enabled in the header.

## Risks and Test Signals
Risks include firmware being mandatory for playback, fixed firmware wait timeout, SDCA descriptor fallback divergence from descriptor-derived initialization, UEFI calibration endian/alignment assumptions via `u32 *` casts, unique-ID mismatches silently leaving defaults, and power-state races around SoundWire attach/resume. Test signals include attach/detach cycles, timeout and bad-firmware paths, SDCA-function and static-init paths, CRC-failing and matching UEFI calibration data, playback/capture port numbering, runtime/system suspend with unattach requests, and explicit port prepare behavior for `simple_ch_prep_sm`.
