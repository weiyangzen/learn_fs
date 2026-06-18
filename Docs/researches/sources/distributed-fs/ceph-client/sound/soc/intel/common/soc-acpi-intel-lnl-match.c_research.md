<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/common/soc-acpi-intel-lnl-match.c -->
# sources/distributed-fs/ceph-client/sound/soc/intel/common/soc-acpi-intel-lnl-match.c

## Purpose
Lunar Lake ACPI SoundWire match data, with placeholder SSP machine array and extensive descriptors for mockup, RT71x/RT13xx, CS42L43/CS35L56, RT712/RT713/RT722, and SDCA-quirked topologies.

## APIs, Types, and Functions
Exports `snd_soc_acpi_intel_lnl_machines[]` and `snd_soc_acpi_intel_lnl_sdw_machines[]`. Defines endpoint/address arrays for CS42L43, CS35L56, RT711-SDCA, RT712/RT712-VB, RT1712, RT722, RT1316, RT1318, RT1320, RT713, RT714, and multiple link arrays. Some entries call `sof_sdw_get_tplg_files`; RT712-VB/RT713-VB entries use `snd_soc_acpi_intel_sdca_is_device_rt712_vb`.

## Control Flow, State, and Persistence
The normal machine array is sentinel-only, so SoundWire matching is the substantive path. Static link masks and address arrays select `sof_sdw` topology files. Mockup entries provide synthetic/test layouts. SDCA entries can be skipped at match time by the machine-check callback when enumerated peripherals do not expose the expected RT712-VB quirk.

## Dependencies and Integration
Depends on ASoC ACPI matching, SOF function topology library, SDCA quirk helper, and SoundWire mockup descriptors. Integrated by the Intel match aggregate and SOF SoundWire machine driver.

## Risks and Test Signals
Risks include missing non-SoundWire LNL board entries, machine-check behavior depending on `sdw_intel_ctx` shape, topology function-file generation drift, and many near-overlapping link masks. Test signals are LNL SoundWire enumeration for each supported topology, SDCA RT712-VB filter acceptance/rejection, function topology file list validation, and audio tests for CS42L43/CS35L56, RT722-only, RT1320, and mockup paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/common/soc-acpi-intel-lnl-match.c -->
