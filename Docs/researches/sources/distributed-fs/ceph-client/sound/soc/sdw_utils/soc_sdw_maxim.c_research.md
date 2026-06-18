# sources/distributed-fs/ceph-client/sound/soc/sdw_utils/soc_sdw_maxim.c

Purpose: supports Maxim MAX98363/MAX98373 SoundWire speaker amplifiers in generic ASoC SoundWire machine drivers.

Important APIs and data: `max_98373_dapm_routes[]` connects `Left Spk`/`Right Spk` to backend outputs. `asoc_sdw_maxim_spk_rtd_init()` installs those routes. `max_98373_sdw_ops` wraps common SoundWire stream ops but overrides prepare/hw_free to enable/disable speaker pins. `asoc_sdw_mx8373_sdw_late_probe()` disables speaker pins after boot. `asoc_sdw_maxim_init()` increments amp count, switches on `info->part_id`, and for MAX98373 installs late probe and custom ops.

Control flow and state: prepare calls `asoc_sdw_prepare()` then enables per-prefix speaker pins for playback; hw_free deprepares then disables. Late probe initializes pins disabled. `maxim_part_id` is static but only used during init selection.

Dependencies and integration: tied to Maxim entries in `codec_info_list`; uses ASoC DAPM, SoundWire stream helper wrappers, and card late-probe plumbing.

Risks: helper silently returns 0 from pin toggling even if the last pin operation failed, so hardware pin-state failures may be hidden. Prefix-derived pin names must match DAPM widgets. Unsupported part IDs abort with `-EINVAL`.

Test signals: boot leaves speakers disabled, playback prepare enables the correct left/right pins, hw_free disables them, and MAX98363 keeps default stream ops while MAX98373 uses custom ops.
