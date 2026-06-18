<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/common/soc-acpi-intel-cml-match.c -->
# sources/distributed-fs/ceph-client/sound/soc/intel/common/soc-acpi-intel-cml-match.c

## Purpose
Comet Lake ACPI match tables for SSP/I2S codec boards and SoundWire RT700/RT711/RT1308/RT1316/RT714 topologies.

## APIs, Types, and Functions
Exports `snd_soc_acpi_intel_cml_machines[]` and `snd_soc_acpi_intel_cml_sdw_machines[]`. Defines codec lists for ES83x6, RT1011, RT1015, MAX98357A, and MAX98390 speaker companions; SoundWire endpoints/address descriptors; and link arrays `cml_rvp`, `cml_3_in_1_default`, `cml_3_in_1_mono_amp`, and `cml_3_in_1_sdca`.

## Control Flow, State, and Persistence
SSP matching is order-sensitive for multiple `10EC5682` RT5682 entries: companion speaker codec lists must be tested before the bare RT5682 fallback. SoundWire entries select `sof_sdw` and topology files based on link masks and codec descriptors. No mutable state is stored by the file.

## Dependencies and Integration
Depends on ASoC ACPI match helpers and SoundWire machine descriptors. Consumed by Comet Lake SOF platform selection and the shared SOF SoundWire machine driver.

## Risks and Test Signals
Risks include changing order of the RT5682 entries, mismatch between companion codec list and topology filename, SDCA versus non-SDCA endpoint confusion, and stale link masks. Test signals are CML board matching with RT5682 plus each amplifier type, DA7219 amplifier variants, ES8336 dynamic topology suffixes, and SoundWire 3-in-1/mono/RT700 playback-capture validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/common/soc-acpi-intel-cml-match.c -->
