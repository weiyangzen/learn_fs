<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/avs/boards/Kconfig -->
# sources/distributed-fs/ceph-client/sound/soc/intel/avs/boards/Kconfig

Purpose: Kconfig menu for Intel AVS ASoC machine drivers. It exposes per-board tristate options and the compatibility option for obsolete card names.

Important APIs, types, and functions: no C APIs are defined. Symbols include `SND_SOC_INTEL_AVS_CARDNAME_OBSOLETE` and `SND_SOC_INTEL_AVS_MACH_*` entries for DA7219, DMIC, ES8336, HDAudio, I2S test, MAX98927/MAX98357A/MAX98373, NAU8825, PCM3168A, PROBE, RT274/RT286/RT298/RT5514/RT5640/RT5663/RT5682, and SSM4567.

Control flow: each machine driver is selectable only when `SND_SOC_INTEL_AVS` is enabled. I2C-based codecs depend on `I2C` and `MFD_INTEL_LPSS || COMPILE_TEST`; codec symbols are selected so the matching codec driver is available. Debug probe support depends on `DEBUG_FS` and selects `SND_HWDEP`.

State and persistence: configuration choices persist in the built kernel/module set. `SND_SOC_INTEL_AVS_CARDNAME_OBSOLETE` influences runtime behavior through the global `obsolete_card_names` module parameter default in `board_selection.c`.

Dependencies and integration points: integrates kernel build selection with `boards/Makefile` object names and with platform devices created by `board_selection.c`. The selected codec symbols must match codec component names hard-coded in the board source files.

Risks: missing a machine config causes board platform devices to have no binding driver even if ACPI detects the endpoint. `select` pulls codecs but dependency coverage is still board-specific; unusual test builds rely on `COMPILE_TEST`. Obsolete card naming helps userspace UCM compatibility but risks diverging from new long names.

Test signals: `scripts/config` or `.config` contains expected `SND_SOC_INTEL_AVS_MACH_*` values, `modinfo` shows generated modules, and a detected endpoint binds to a matching platform driver instead of remaining unbound.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/avs/boards/Kconfig -->
