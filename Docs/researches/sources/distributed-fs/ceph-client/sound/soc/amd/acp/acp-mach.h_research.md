# sources/distributed-fs/ceph-client/sound/soc/amd/acp/acp-mach.h

## Purpose
`acp-mach.h` declares the common machine-driver contract used by AMD ACP legacy, SOF, ES83xx, and shared machine files. It centralizes endpoint IDs, codec IDs, quirk bits, per-card driver data, optional machine callbacks, and the exported DAI-link creation APIs.

## Important APIs, Types, and Functions
Key definitions are `enum be_id`, `enum cpu_endpoints`, `enum codec_endpoints`, `struct acp_mach_ops`, and `struct acp_card_drvdata`. The header declares `acp_sofdsp_dai_links_create()`, `acp_legacy_dai_links_create()`, and `acp_quirk_table`. Inline helpers `acp_ops_probe()`, `acp_ops_configure_link()`, `acp_ops_configure_widgets()`, `acp_ops_suspend_pre()`, and `acp_ops_resume_post()` dispatch optional board-specific callbacks.

## Control Flow
Machine drivers store an `acp_card_drvdata` pointer in `card->drvdata`. Shared creation code reads endpoint and codec IDs to generate DAI links. Specialized drivers, especially ES83xx, install callbacks in `acp_mach_ops`; the inline wrappers call those callbacks only if present and otherwise return a nonzero default value.

## State and Persistence
The header owns no runtime state. It defines the card-lifetime state held in `acp_card_drvdata`: CPU and codec endpoint IDs, DAI format, ACP revision, clock handles, ACPI machine pointer, private machine data, and flags for SoC MCLK and TDM mode.

## Dependencies and Integration Points
It includes ALSA core, jack, PCM params, DAPM, input, module, ASoC, and `acp_common.h`. It is included by SOF/legacy machine drivers, ACP platform files, and ES83xx support. The enum values must match the assumptions in `acp-mach-common.c` and board data tables.

## Risks
The default inline return value is `1`, not `0`, so callers must treat a missing optional callback carefully. Endpoint and codec enum changes are ABI-like within this driver family; mismatches can produce wrong DAI links. `acp_get_drvdata()` assumes `card->drvdata` has the expected type.

## Test Signals
Build coverage should catch missing prototypes and enum users. Runtime smoke tests should verify that board IDs using each endpoint/codec combination still produce the expected DAI links and that optional ES83xx ops are invoked only for ES83xx cards.
