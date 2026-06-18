<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/common/soc-acpi-intel-adl-match.c -->
# sources/distributed-fs/ceph-client/sound/soc/intel/common/soc-acpi-intel-adl-match.c

## Purpose
Alder Lake ACPI machine-match tables for Intel ASoC/SOF platforms, covering SSP/I2S codec combinations and a broad set of SoundWire link-address topologies.

## APIs, Types, and Functions
Exports `snd_soc_acpi_intel_adl_machines[]` and `snd_soc_acpi_intel_adl_sdw_machines[]`. The file defines codec lists for ES83x6, MAX98357A, RT5682/RT5682S, RT1019P, and LT6911 HDMI, plus SoundWire endpoint/address/link descriptors for RT711/RT711-SDCA, RT1308, RT1316, RT714, CS42L43, CS35L56, MAX98373, and RT5682 combinations.

## Control Flow, State, and Persistence
There is no executable runtime state. Match ordering and `.id`/`.comp_ids`/`.machine_quirk` entries select machine drivers and topology names for boards with codecs on SSP buses. SoundWire entries use `.link_mask` and `.links` to require specific active links and endpoint groupings; selected entries bind to `sof_sdw` with explicit `sof-adl-*.tplg` files.

## Dependencies and Integration
Depends on ASoC ACPI match headers and SSP common topology suffix support. The arrays are consumed by Intel SOF/SST platform code during ACPI enumeration; SoundWire descriptors feed the SOF SoundWire machine driver.

## Risks and Test Signals
Risks include overlapping codec IDs where array order changes board selection, incorrect link masks for ADL/ADL-P variants, topology filename drift, and endpoint group-position mistakes for aggregated amplifiers. Test signals are ACPI matching on ADL boards, SOF topology load for each listed codec combination, SoundWire device enumeration matching expected links, and audio playback/capture on SSP and SoundWire designs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/common/soc-acpi-intel-adl-match.c -->
