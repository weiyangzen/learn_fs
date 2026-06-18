# sources/distributed-fs/ceph-client/sound/soc/amd/acp/soc_amd_sdw_common.h

## Purpose
`soc_amd_sdw_common.h` defines shared constants and context for AMD ACP SoundWire machine drivers.

## Important APIs, Types, and Functions
Key definitions include max link/group constants, ACP revision IDs for SoundWire matching, quirk bits `SOC_JACK_JDSRC()`, `ASOC_SDW_FOUR_SPK`, `ASOC_SDW_ACP_DMIC`, and `ASOC_SDW_CODEC_SPKR`, SoundWire link IDs, ACP63/ACP70 CPU pin IDs, `ACP_DMIC_BE_ID`, `struct amd_mc_ctx`, and prototypes for `get_acp63_cpu_pin_id()` and `get_acp70_cpu_pin_id()`.

## Control Flow
There is no executable flow. Legacy and SOF SoundWire machine drivers use these constants while parsing ACPI SoundWire endpoints and creating DAI links.

## State and Persistence
The header owns no state. `struct amd_mc_ctx` defines per-card context fields for ACP revision and maximum SoundWire links.

## Dependencies and Integration Points
It includes Linux bits/types, ASoC, and SoundWire utility headers. It is included by SoundWire machine-common, legacy machine, and SOF machine files.

## Risks
Quirk bit allocation and CPU pin values are shared contracts; changes must stay synchronized with machine drivers, codec utility expectations, and CPU DAI naming. Duplicated ACP revision constants overlap with `acp_common.h` and must remain consistent.

## Test Signals
Build SoundWire drivers and validate generated DAI names/pin IDs for ACP63 and ACP70-class hardware, plus DMI quirk behavior for jack source, codec speakers, and ACP DMIC.
