# sources/distributed-fs/ceph-client/sound/soc/amd/acp/acp-legacy-mach.c

## Purpose
`acp-legacy-mach.c` is the generic legacy AMD ACP machine driver. It maps platform device IDs to codec/CPU/DMIC topology data, invokes shared machine construction helpers, applies ES83xx-specific ops when needed, handles suspend/resume hooks, and registers dynamically created ASoC cards.

## Important APIs, Types, And Functions
Important static card-data templates include `rt5682_rt1019_data`, `rt5682s_max_data`, `rt5682s_rt1019_data`, `es83xx_rn_data`, `max_nau8825_data`, `rt5682s_rt1019_rmb_data`, and `acp_dmic_data`. Key functions are `acp_asoc_init_ops()`, `acp_asoc_suspend_pre()`, `acp_asoc_resume_post()`, and `acp_asoc_probe()`. `board_ids` maps platform names to templates.

## Control Flow
Probe requires a matching platform ID, allocates an `snd_soc_card`, attaches the template as driver data, stores the `snd_soc_acpi_mach`, initializes codec-specific ops for ES83xx, configures widgets, calls shared probe hooks, records ACP revision from either PDM platform data or ACPI machine params, applies DMI TDM mode quirks, creates DAI links with `acp_legacy_dai_links_create()`, and registers the card. Suspend/resume wrappers normalize a shared helper return value of 1 into success.

## State And Persistence
Card state persists in the devm-allocated `snd_soc_card` and shared `acp_card_drvdata` templates. The templates include CPU IDs, codec IDs, DMIC IDs, SoC MCLK/TDM flags, ACP revision, and ACPI machine pointer. Because templates are static and modified at probe time, they behave as module-global state.

## Dependencies And Integration Points
The driver depends on `acp-mach-common` helpers, ES83xx support under `acp3x-es83xx`, ASoC ACPI machine data, DMI quirks, platform devices created by `acp_machine_select()`, and namespace `SND_SOC_AMD_MACH`.

## Risks And Edge Cases
Static template mutation is not multi-instance friendly. Missing `id_entry` fails probe. If widget/probe/link creation helpers fail, the card is not registered. TDM mode quirks overwrite the template flag globally. The special `acp-pdm-mach` path interprets platform data as an `int` revision.

## Test Signals
Test each `board_ids` platform name, ES83xx ops initialization, PDM-only machine path, DMI TDM quirk application, generated DAI link contents, suspend/resume helper return normalization, registration failure paths, and multiple probe attempts for shared template side effects.
