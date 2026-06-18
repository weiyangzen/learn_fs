# sources/distributed-fs/ceph-client/sound/soc/intel/boards/sof_nuvoton_common.h

Purpose: Header for Intel SOF Nuvoton amplifier helpers.

Important APIs, types, and functions: It defines `NAU8318_CODEC_DAI` as `nau8315-hifi`, `NAU8318_DEV0_NAME` from the ACPI HID, and declares `nau8318_set_dai_link()`.

Control flow and integration: Machine drivers include this header and call `nau8318_set_dai_link()` when `snd_soc_acpi_intel_detect_amp_type()` reports NAU8318.

State and persistence: No state. The implementation owns static link component data.

Dependencies: ASoC and Intel ACPI SSP codec identifiers.

Risks: Codec DAI aliasing across NAU8315/NAU8318 names must remain valid. Test signals include build coverage and runtime link binding to the Nuvoton codec component.
