# sources/distributed-fs/ceph-client/sound/soc/intel/boards/sof_ti_common.c

Purpose: Shared helper for Intel SOF boards using Texas Instruments TAS2563 speaker devices.

Important APIs, types, and functions: The file defines a single `Spk` pin switch, speaker widget, and route from `Spk` to codec `OUT`. TAS2563 uses one mounted device to manage multiple physical devices, so the helper exposes one component array entry. `tas2563_init()` adds DAPM widgets, card controls, and routes. `sof_tas2563_dai_link()` patches a generated amp link with the TAS2563 component array and init callback.

Control flow and integration: `sof_rt5682.c` uses this helper when the detected amp type is `CODEC_TAS2563`.

State and persistence: Static DAPM/control/component arrays only. No persistent state.

Dependencies: ASoC DAPM APIs and TI codec ACPI/DAI constants.

Risks: The one-component design relies on the TAS2563 codec driver managing multi-device hardware behind a single component. Test signals include card-control creation and speaker playback on TAS2563 platforms.
