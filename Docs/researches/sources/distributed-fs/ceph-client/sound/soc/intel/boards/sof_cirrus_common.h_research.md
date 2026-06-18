# sources/distributed-fs/ceph-client/sound/soc/intel/boards/sof_cirrus_common.h

Purpose: Header for Intel SOF Cirrus Logic amplifier helpers.

Important APIs, types, and functions: It defines CS35L41 DAI and component-name constants, including `CS35L41_CODEC_DAI` and ACPI-derived `CS35L41_DEV0_NAME` through `CS35L41_DEV3_NAME`. It declares `cs35l41_set_dai_link()` for patching a speaker amplifier DAI link and `cs35l41_set_codec_conf()` for assigning card-level codec prefixes.

Control flow and integration: Machine drivers such as `sof_ssp_amp.c` include this header after `sof_board_helpers` creates an amp link. The helper implementation then fills the generated link with the correct codec component array, init callback, and stream ops.

State and persistence: No state is defined here; the implementation owns static arrays.

Dependencies: ASoC and Intel ACPI SSP codec identifiers.

Risks: Header constants must stay aligned with codec-driver DAI names and ACPI HID definitions. Test signals are compile/link namespace coverage and successful card creation on two-amp and four-amp Cirrus systems.
