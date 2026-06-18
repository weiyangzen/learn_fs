# sources/distributed-fs/ceph-client/sound/hda/codecs/side-codecs/tas2781_hda_i2c.c

## Purpose
This is the I2C HDA side-codec driver for TI TAS2563, TAS2770, TAS2781, and TAS5825 amplifier families. It discovers multi-amp I2C resources from ACPI, initializes the TAS firmware library, binds to the HDA component manager, loads RCA/DSP firmware, creates ALSA controls, handles EFI calibration, and manages runtime/system power.

## Important APIs, types, and functions
`struct tas2781_hda_i2c_priv` stores two generic sound controls, a calibration callback, and a chip id enum. ACPI discovery is handled by `tas2781_get_i2c_res()` and `tas2781_read_acpi()`. Playback and controls are handled by `tas2781_hda_playback_hook()`, amp volume callbacks, force-firmware-load callbacks, chip-specific control templates, and DSP/profile control templates. `tas2563_save_calibration()` handles TAS2563-specific EFI variables. Firmware callbacks are `tasdev_fw_ready()` and `tasdevice_dspfw_init()`. Component callbacks are `tas2781_hda_bind()` and `tas2781_hda_unbind()`. Probe/remove/PM are `tas2781_hda_i2c_probe()`, `tas2781_hda_i2c_remove()`, and the TAS2781 PM callbacks.

## Control flow
Probe allocates the HDA wrapper and private state, creates `tasdevice_priv` with `tasdevice_kzalloc()`, identifies the chip by device name, sets chip id/global address/calibration callback, reads ACPI resources into per-amp addresses, optionally reads ASUS speaker-id GPIO, initializes the TAS device library, enables runtime PM, resets devices, and registers a component. Component bind sets the vendor category from HDA subsystem vendor, runtime-resumes the device, fills the component slot, and calls `tascodec_init()` to request RCA firmware. When RCA firmware arrives, the driver parses it, adds the profile control and chip-specific volume/force controls, and for DSP-capable chips parses DSP firmware, adds program/config controls, loads program 0, applies initial profile blocks, and reads calibration.

Playback open runtime-resumes and switches tuning on under `codec_lock`; close switches tuning off and autosuspends. Runtime suspend powers down unused playback state; runtime resume reloads the current program. System resume resets cached per-device book/program/config state, resets hardware, reloads firmware program and initial profile block, and restores tuning if playback was active.

## State and persistence
State is spread across `tas2781_hda`, `tas2781_hda_i2c_priv`, and `tasdevice_priv`: chip id, global I2C address, discovered device addresses/count, speaker id, firmware names/states, current profile/program/config, playback flag, ALSA control pointers, and calibration data. EFI calibration variables are persistent firmware inputs; driver allocations are device-managed.

## Dependencies and integration points
The file depends on ACPI resources/GPIO, EFI, firmware loading, runtime PM, HDA component APIs, HDA codec subsystem ids, ALSA controls/TLVs, and TAS common I2C/firmware libraries. It integrates with `hda_component` via playback hooks and with shared `tas2781_hda.c` for common calibration/control callbacks.

## Risks and edge cases
Device identification relies on exact `dev_name()` patterns for serial-multi-instantiate variants. ACPI resource enumeration skips the global address and caps channel count. ASUS speaker-id GPIO mapping is conditional on subsystem vendor. Some chips lack DSP or calibration, so control creation paths differ by chip id. Firmware callback paths must tolerate parse failure and release firmware. `tas2781_hda_i2c_probe()` calls shared remove on errors after partial setup, so drvdata and component registration order are important.

## Test signals
Test each ACPI id (`INT8866`, `TIAS2781`, `TXNW2770`, `TXNW2781`, `TXNW5825`), multi-device resource enumeration, ASUS speaker-id firmware naming, RCA and DSP firmware load success/failure, chip-specific controls, TAS2563 and TAS2781 calibration paths, playback open/close tuning switches, runtime autosuspend, system resume reload, and component unbind cleanup.
