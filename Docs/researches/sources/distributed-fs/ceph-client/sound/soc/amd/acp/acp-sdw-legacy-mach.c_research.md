# sources/distributed-fs/ceph-client/sound/soc/amd/acp/acp-sdw-legacy-mach.c

## Purpose
`acp-sdw-legacy-mach.c` is the generic non-SOF AMD SoundWire machine driver. It parses ACPI SoundWire endpoint descriptions, applies DMI/module quirks, creates backend DAI links for SoundWire devices and optional ACP DMIC, and registers the ASoC card named `amd-soundwire`.

## Important APIs, Types, and Functions
Main functions are `mc_probe()`, `mc_remove()`, `soc_card_dai_links_create()`, `create_sdw_dailinks()`, `create_sdw_dailink()`, `create_dmic_dailinks()`, `log_quirks()`, and `soc_sdw_quirk_cb()`. It uses `struct asoc_sdw_mc_private`, `struct amd_mc_ctx`, `struct asoc_sdw_dailink`, `struct asoc_sdw_endpoint`, and SoundWire utility callbacks in `sdw_ops`.

## Control Flow
Probe allocates AMD and generic SoundWire machine contexts, records ACP revision from `mach_params.subsystem_rev`, sets card metadata, copies PCI SSID when present, applies DMI quirks and optional `quirk=` override, resets codec amp counters, and calls `soc_card_dai_links_create()`. That function counts and parses SoundWire endpoints, determines whether an ACP DMIC link is required, allocates codec-conf/aux/dai-link arrays, creates one or more SoundWire links with CPU pin IDs derived from ACP revision and link/backend ID, then optionally creates a PDM DMIC link. Finally, probe builds a component string with amp and mic counts and registers the card.

## State and Persistence
Quirk state is module-global (`soc_sdw_quirk`) but can be overridden at load time. Card, context, DAI links, codec confs, and aux devices are devm-managed for the platform device. No persistent storage is used.

## Dependencies and Integration Points
The driver depends on SoundWire ASoC utilities, codec information lists, ACPI mach tables, DMI, `get_acp63_cpu_pin_id()`/`get_acp70_cpu_pin_id()`, ACP PDM platform names, and `snd_soc_pm_ops`. It binds platform ID `amd_sdw` from ACP63/ACP70 ACPI match tables.

## Risks
The CPU pin mapping expression must identify the correct SoundWire link; wrong link/backend mapping yields unusable DAIs. The code assumes parsed endpoint counts and allocated config counts stay synchronized and warns if iterators do not land at expected ends. Global quirk state can affect multiple probes. Internal DMIC can be ignored by utility context, reducing available capture unexpectedly.

## Test Signals
Validate systems with RT722-only, RT711/RT1316/RT714, Cirrus, Realtek, and TAS combinations; DMI quirks for ACP DMIC and codec speaker; module quirk override; generated DAI link names such as `SDW0-PIN*-PLAYBACK`; jack/speaker/DMIC operation; and clean `asoc_sdw_mc_dailink_exit_loop()` on remove/register failure.
