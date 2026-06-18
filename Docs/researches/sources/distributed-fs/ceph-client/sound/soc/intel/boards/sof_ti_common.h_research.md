# sources/distributed-fs/ceph-client/sound/soc/intel/boards/sof_ti_common.h

Purpose: Header for Intel SOF Texas Instruments amplifier helpers.

Important APIs, types, and functions: It defines `TAS2563_CODEC_DAI`, `TAS2563_DEV0_NAME`, and declares `sof_tas2563_dai_link()`.

Control flow and integration: Machine drivers include this header and call the helper when ACPI codec detection reports `CODEC_TAS2563`.

State and persistence: No state is declared.

Dependencies: ASoC and Intel ACPI SSP codec identifiers.

Risks: The DAI/component names must remain aligned with the TI codec driver and firmware. Test signals are compile coverage and successful link binding on TAS2563 systems.
