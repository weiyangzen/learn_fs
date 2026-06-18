# sources/distributed-fs/ceph-client/sound/soc/amd/acp/acp-sdw-sof-mach.c

## Purpose
`acp-sdw-sof-mach.c` is the SOF-backed AMD SoundWire machine driver. It builds SoundWire and optional DMIC backend links for `amd_sof_sdw` ACPI machine entries and registers an ASoC card that uses SOF platform components.

## Important APIs, Types, and Functions
Main functions mirror the legacy driver: `mc_probe()`, `mc_remove()`, `sof_card_dai_links_create()`, `create_sdw_dailinks()`, `create_sdw_dailink()`, `create_dmic_dailinks()`, `log_quirks()`, and `sof_sdw_quirk_cb()`. It uses `platform_component[]`, `sdw_ops`, `asoc_sdw_*` utility functions, `struct amd_mc_ctx`, and SoundWire codec info lists.

## Control Flow
Probe allocates contexts, stores ACP revision, initializes the card, applies DMI/module quirks, resets codec amp counters, then creates DAI links. Endpoint parsing determines SoundWire backend count and auxiliary devices. For each stream direction with devices, it maps ACP revision/link/backend to a CPU pin ID, builds a stream name, allocates CPU/codec/ch-map arrays, calls `asoc_sdw_init_dai_link()` with `no_pcm` set for SOF backend links, marks links nonatomic, and runs endpoint-specific init. Optional DMIC is created when a quirk or `mach_params->dmic_num` requests it, using CPU `acp-sof-dmic` and the SOF platform component.

## State and Persistence
Quirk state is module-global and load-time overrideable. Card and DAI-link state is devm-managed per platform device. SOF topology and firmware filenames are supplied by the ACPI match table, not persisted here.

## Dependencies and Integration Points
It depends on SOF platform component naming, SoundWire utility parsing/init helpers, ACP CPU pin mapping helpers, `snd_soc_pm_ops`, and ACPI match tables exporting `amd_sof_sdw` entries. It imports `SND_SOC_SDW_UTILS` and `SND_SOC_AMD_SDW_MACH`.

## Risks
The same SoundWire endpoint parsing/count synchronization risks apply as in the legacy driver. The static SOF platform component name may need overriding by platform data in broader SOF code; if mismatched, card registration or PCM routing fails. DMIC `no_pcm` differs from legacy and must match topology expectations.

## Test Signals
Validate ACP63/ACP70 SOF SoundWire cards, SOF topology loading, RT711 jack detect quirk, optional DMIC from quirk and `dmic_num`, DAI link names and pin numbers, suspend/resume through `snd_soc_pm_ops`, and cleanup on card registration failure.
