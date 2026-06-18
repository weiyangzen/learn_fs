# sources/distributed-fs/ceph-client/sound/hda/codecs/side-codecs/tas2781_hda.c

## Purpose
This file is the shared HDA support library for Texas Instruments TAS2781-family side-codec drivers. It provides EFI calibration import, common remove behavior, and ALSA control callbacks for profile/program/config selections used by both I2C and SPI transport drivers.

## Important APIs, types, and functions
It exports `tasdev_fct_efi_guid[]`, `tas2781_save_calibration()`, `tas2781_hda_remove()`, and the control callbacks `tasdevice_info_profile()`, `tasdevice_info_programs()`, `tasdevice_info_config()`, `tasdevice_get_profile_id()`, `tasdevice_set_profile_id()`, `tasdevice_program_get()`, `tasdevice_program_put()`, `tasdevice_config_get()`, and `tasdevice_config_put()`. Internal helpers `cali_cnv()` and `tas2781_apply_calib()` validate and convert EFI calibration blobs into the format expected by the TAS firmware library.

## Control flow
`tas2781_save_calibration()` checks EFI runtime support, selects a vendor GUID from the HDA category, probes two possible EFI variable names, allocates a buffer sized for the reported variable or minimum device count, reads calibration data, and calls `tas2781_apply_calib()`. Calibration apply supports older V1 and newer TAS2781 V2/V3 blob layouts, verifies CRC32, optionally extracts register addresses from a special node, converts per-device values to big-endian algorithm format, and sets total data size. Remove unregisters the component, disables runtime PM, and calls `tasdevice_remove()`. Control callbacks expose integer ranges and clamp/set current ids under `codec_lock` for mutable values.

## State and persistence
Calibration data is stored in `tasdevice_priv->cali_data` using device-managed allocation. Current profile/program/config state is stored in `tasdevice_priv` fields (`rcabin.profile_cfg_id`, `cur_prog`, `cur_conf`). EFI variables are persistent platform firmware state, but this driver only reads them.

## Dependencies and integration points
It depends on EFI runtime services, CRC32, Linux firmware/component/PM APIs, ALSA SoC control types, `sound/tas2781.h`, and the TAS2781 firmware library structures. I2C/SPI drivers call these exports when firmware parsing is complete and when HDA controls are created.

## Risks and edge cases
Malformed EFI calibration data disables calibration by setting `total_sz` to zero, allowing DSP defaults to continue. CRC layout assumptions are critical, especially for V2/V3 node counts and register-address nodes. `tas2781_hda_remove()` assumes drvdata and `tas_hda->priv` are valid and that component removal is safe for the supplied ops. Control info callbacks assume firmware/config data has already been parsed.

## Test signals
Test EFI missing/unsupported paths, both EFI variable names, V1 and V2/V3 CRC success/failure, multiple amp counts, category GUID selection for Dell/HP/Lenovo, control clamping/change return values, and remove after successful and partially failed probe.
