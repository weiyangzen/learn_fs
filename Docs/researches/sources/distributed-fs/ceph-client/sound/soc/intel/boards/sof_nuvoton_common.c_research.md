# sources/distributed-fs/ceph-client/sound/soc/intel/boards/sof_nuvoton_common.c

Purpose: Shared helper for Intel SOF boards using a Nuvoton NAU8318 speaker amplifier.

Important APIs, types, and functions: The file defines one speaker pin control, one `Spk` widget, a route from `Spk` to codec `Speaker`, and a component array for `NAU8318_DEV0_NAME`/`NAU8318_CODEC_DAI`. `nau8318_init()` adds DAPM widgets, card controls, and routes with error reporting. `nau8318_set_dai_link()` patches a generated amp DAI link with the NAU8318 component array and init callback.

Control flow and integration: A machine driver such as `sof_nau8825.c` selects this helper based on detected amp type after common board-link generation.

State and persistence: Static component and DAPM tables only. No persistent state.

Dependencies: ASoC DAPM/card-control APIs and SOF/Nuvoton header constants.

Risks: The header uses `nau8315-hifi` as the codec DAI for NAU8318, so codec-driver naming must remain compatible. Test signals include successful DAPM route/control creation and speaker playback on NAU8318 boards.
