# sources/distributed-fs/ceph-client/sound/soc/sdw_utils/soc_sdw_rt_dmic.c

Purpose: updates card component metadata for Realtek SoundWire DMIC endpoints, with special handling for RT1320/RT1321 SDCA SmartMic counts.

Important API: `asoc_sdw_rt_dmic_rtd_init()` derives a user-space microphone name from `component->name_prefix`, translating `rt714` to `rt715-sdca` for compatibility. If the component device is an RT1320/RT1321 SoundWire slave, it iterates all card components, counts same-part peripherals that expose an SDCA SmartMic function, and appends `cfg-mics:<count>` to `card->components`.

Control flow and state: runtime init builds a devm string, optionally scans card components and SDCA function tables, then appends either `mic:<name>` or `mic:<name> cfg-mics:<n>`. Persistent state is only `card->components`.

Dependencies and integration: used by multiple Realtek DMIC DAI entries in `codec_info_list`; depends on SoundWire slave helpers and `sdca_function.h` type constants.

Risks: correctness depends on codec drivers registering SDCA function data before this callback. The component iterator reuses the `component` variable, so later code must not assume it still points to the original. User-space UCM naming compatibility is encoded in string special cases.

Test signals: card components contain expected mic names, RT1320/RT1321 cards include accurate `cfg-mics`, and SDCA SmartMic devices are discovered from `sdca_data.function[]`.
