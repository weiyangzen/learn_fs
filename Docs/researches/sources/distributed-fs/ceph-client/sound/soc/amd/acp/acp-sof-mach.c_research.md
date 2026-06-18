# sources/distributed-fs/ceph-client/sound/soc/amd/acp/acp-sof-mach.c

## Purpose
`acp-sof-mach.c` is the machine-driver entry point for non-SoundWire AMD ACP SOF boards. It maps platform device IDs to predefined `acp_card_drvdata` topologies, applies DMI TDM quirks, delegates DAI-link creation to the shared machine layer, and registers the ASoC card.

## Important APIs, Types, and Functions
Static topology records include `sof_rt5682_rt1019_data`, `sof_rt5682_max_data`, `sof_rt5682s_rt1019_data`, `sof_rt5682s_max_data`, `sof_nau8825_data`, `sof_rt5682s_hs_rt1019_data`, and `sof_nau8821_max98388_data`. The main function is `acp_sof_probe()`, and `board_ids[]` maps platform names to those records.

## Control Flow
Probe requires a platform ID entry, allocates `snd_soc_card`, assigns card name and driver data from the ID table, applies the `QUIRK_TDM_MODE_ENABLE` DMI quirk by setting `tdm_mode`, stores ACP revision from ACPI mach params, calls `acp_sofdsp_dai_links_create()`, and registers the card with device-managed ASoC registration.

## State and Persistence
The topology records are static module data and are mutated for fields such as `tdm_mode` and `acp_rev`; this persists for the module lifetime. Card allocations are devm-managed. No persistent storage exists.

## Dependencies and Integration Points
It depends on `acp-mach-common.c` for all link/widget/codec setup, `snd_soc_acpi_mach` platform data for ACP revision, `acp_quirk_table`, and platform IDs created by ACPI machine selection.

## Risks
Static `acp_card_drvdata` mutation can carry state across multiple probes of the same board ID. Missing or wrong platform data can dereference invalid `mach` fields. Any new board must express its complete endpoint/codec topology in the static table or shared link creation will produce incomplete cards.

## Test Signals
Test all `board_ids` names, TDM quirk systems, SOF headset/speaker/DMIC operation, card registration failures with missing codecs, and repeated probe/remove if supported by the platform-device lifecycle.
