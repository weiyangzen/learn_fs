<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/common/soc-acpi-intel-ptl-match.c -->
# sources/distributed-fs/ceph-client/sound/soc/intel/common/soc-acpi-intel-ptl-match.c

## Purpose
Panther Lake ACPI match data for SSP codec boards and ordered SoundWire topologies covering mockup, Realtek SDCA, CS42L43/CS35L56, RT722/RT1320, and RT712-VB/RT713-VB variants.

## APIs, Types, and Functions
Exports `snd_soc_acpi_intel_ptl_machines[]` and `snd_soc_acpi_intel_ptl_sdw_machines[]`. Defines SSP codec lists for RT5682/RT5682S, ES83x6, and LT6911 HDMI, endpoint/address descriptors for CS42L43, CS35L56, RT711-SDCA, RT712-VB, RT713-VB, RT722, and RT1320, plus link arrays for multi-link speaker/headset layouts. Several entries use `snd_soc_acpi_intel_sdca_is_device_rt712_vb` and/or `sof_sdw_get_tplg_files`.

## Control Flow, State, and Persistence
The file explicitly notes that order in `snd_soc_acpi_intel_ptl_sdw_machines[]` matters. Static link masks are matched in table order, with mockup and more-specific SDCA/CS/RT topologies preceding fallback-style entries. SSP entries use codec-list quirks and runtime topology suffix masks for dynamic configurations.

## Dependencies and Integration
Depends on ASoC ACPI matching, SSP common helpers, SOF function topology library, SDCA quirks, and SoundWire mockup descriptors. Integrated by PTL SOF platform selection and the SOF SoundWire machine driver.

## Risks and Test Signals
Risks include reordering SoundWire entries and changing match outcomes, SDCA machine-check context mismatch, topology filename reuse across hardware variants, and many similar endpoint group definitions for aggregated speakers. Test signals are PTL table-order regression tests, RT712-VB/RT713-VB quirk filtering, function topology file generation, and audio validation across mockup, RT722/RT1320, CS42L43/CS35L56, SSP RT5682/ES8336, and HDMI-SSP designs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/common/soc-acpi-intel-ptl-match.c -->
