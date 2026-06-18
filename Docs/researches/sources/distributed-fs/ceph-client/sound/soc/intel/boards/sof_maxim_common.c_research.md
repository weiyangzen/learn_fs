# sources/distributed-fs/ceph-client/sound/soc/intel/boards/sof_maxim_common.c

Purpose: Shared helpers for Intel SOF boards using Maxim speaker amplifiers: MAX98373, MAX98390, MAX98357A, and MAX98360A.

Important APIs, types, and functions: `get_num_codecs()` counts ACPI devices by HID. MAX98373 support adds left/right speaker widgets/routes, reads `maxim,vmon-slot-no` and `maxim,imon-slot-no` properties to create TX masks, validates TDM slot usage from `sof_dai_get_tdm_slots()`, and enables/disables DAPM speaker pins in `max_98373_trigger()`. MAX98390 support handles two or four amps, woofer/tweeter widgets, fixed four-slot TDM masks, and CML-specific codec prefix ordering. MAX98357A/MAX98360A helpers attach a single simple amplifier component with common DAPM speaker controls.

Control flow and integration: Board drivers call `max_98373_dai_link()`, `max_98390_dai_link()`, `max_98357a_dai_link()`, or `max_98360a_dai_link()` to patch an amp link. Card-level codec prefix helpers are called separately for multi-amp devices.

State and persistence: Static component and codec_conf arrays encode ACPI component names and prefixes. Runtime state is limited to DAPM pin changes and ACPI property reads.

Dependencies: ASoC DAPM/DAI APIs, SOF topology helpers for TDM slots, ACPI device enumeration/properties, Intel SoC quirks for CML detection.

Risks: Unsupported amp counts are logged and can leave incomplete link config. TX masks must not overlap and must fit topology TDM slots. DAPM trigger logic assumes component name prefixes match pin names. Test signals include two-amp/four-amp card prefix layout, TDM mask validation, IV-sense capture, speaker pin enable behavior, and simple amplifier playback.
