<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/common/soc-acpi-intel-rpl-match.c -->
# sources/distributed-fs/ceph-client/sound/soc/intel/common/soc-acpi-intel-rpl-match.c

## Purpose
Raptor Lake ACPI match tables for SSP codec boards and SoundWire RT711/RT1316/RT1318/RT714/CS42L43 topologies.

## APIs, Types, and Functions
Exports `snd_soc_acpi_intel_rpl_machines[]` and `snd_soc_acpi_intel_rpl_sdw_machines[]`. Defines endpoint/address/link descriptors for RT711, RT711-SDCA, RT1316, RT1318, RT714, CS42L43, and CRB/RVP layouts, plus codec lists for RT5682, ES83x6, MAX98357A, and LT6911 HDMI.

## Control Flow, State, and Persistence
Static SSP entries select RPL machine drivers and topology names, using companion-codec quirks or topology suffix masks for RT5682/ES8336/generic codec designs. SoundWire entries use link masks and descriptor arrays to choose `sof_sdw` topology files for 4-link, 3-link, 2-link, and link-specific CRB/RVP designs. No mutable state is stored.

## Dependencies and Integration
Depends on ASoC ACPI matching and SSP common helpers. Consumed by RPL SOF platform selection and SoundWire machine driver setup.

## Risks and Test Signals
Risks include link-mask overlap with ADL-derived topologies, incorrect topology selection for RT1316 versus RT1318 amplifier generations, generic RT5682 fallback ordering, and HDMI topology naming differences. Test signals are RPL SSP and SoundWire machine selection, topology load for each listed `.sof_tplg_filename`, and validation of headset, speaker aggregation, DMIC, and HDMI paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/common/soc-acpi-intel-rpl-match.c -->
