<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/common/soc-acpi-intel-mtl-match.c -->
# sources/distributed-fs/ceph-client/sound/soc/intel/common/soc-acpi-intel-mtl-match.c

## Purpose
Meteor Lake ACPI match data for SSP/I2S codec boards and a large set of SoundWire topologies spanning Realtek, Cirrus, TI, Maxim, mockup, SDCA, and function-topology-enabled designs.

## APIs, Types, and Functions
Exports `snd_soc_acpi_intel_mtl_machines[]` and `snd_soc_acpi_intel_mtl_sdw_machines[]`. SSP entries cover ES83x6, RT5682/RT5682S, CS42L42, DA7219, NAU8825, RT5650, and LT6911 HDMI, with topology quirk masks for dynamic amplifier/codec/DMIC suffixes. SoundWire descriptors cover RT711/RT712/RT712-VB/RT713/RT714/RT722/RT1316/RT1318/RT1712/RT1713, MAX98373, TAS2783, CS42L42, CS42L43, CS35L56, CS35L63, MAX98363, and mockup layouts.

## Control Flow, State, and Persistence
Static ACPI/companion-codec entries choose SSP machine drivers. SoundWire entries match link masks and address arrays to `sof_sdw` topologies; several entries call `sof_sdw_get_tplg_files` to augment base topology selection. RT712-VB entries use `snd_soc_acpi_intel_sdca_is_device_rt712_vb` as a machine check. No table state is mutated by this file.

## Dependencies and Integration
Depends on SoundWire Intel context types, SDCA definitions, ASoC ACPI matching, SSP common helpers, SOF function topology library, SDCA quirks, and SoundWire mockup descriptors. It is one of the central inputs to MTL SOF machine selection.

## Risks and Test Signals
Risks include high overlap among link masks, wrong topology for variants sharing filenames, SDCA filter false positives/negatives, endpoint aggregation mistakes for multi-amp Cirrus designs, and stale SSP topology suffix masks. Test signals are ACPI machine selection for each SSP board class, SoundWire match ordering across RT/Cirrus/TI/Maxim/mockup entries, generated function topology files, RT712-VB quirk filtering, and full playback/capture/jack/DMIC/speaker validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/common/soc-acpi-intel-mtl-match.c -->
