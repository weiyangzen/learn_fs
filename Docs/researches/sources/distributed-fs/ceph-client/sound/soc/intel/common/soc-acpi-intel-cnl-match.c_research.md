<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/common/soc-acpi-intel-cnl-match.c -->
# sources/distributed-fs/ceph-client/sound/soc/intel/common/soc-acpi-intel-cnl-match.c

## Purpose
Cannon Lake ACPI machine-match data for RT274/ES8336 SSP designs and early SoundWire/mockup topologies.

## APIs, Types, and Functions
Exports `snd_soc_acpi_intel_cnl_machines[]` and `snd_soc_acpi_intel_cnl_sdw_machines[]`. Defines an ES83x6 codec list, an RT5682-on-link2 SoundWire address array, and SDW mockup links reused from `soc-acpi-intel-sdw-mockup-match.h`.

## Control Flow, State, and Persistence
Static machine arrays select `cnl_rt274` or dynamic ES8336 topology names for SSP boards. SoundWire entries select `sof_sdw` topologies for RT5682 link2 or mockup headset/amplifier/mic layouts. No runtime state is stored.

## Dependencies and Integration
Depends on ASoC ACPI match headers and the SoundWire mockup descriptor header. Used by Cannon Lake SOF platform matching and test/mockup SoundWire enumeration.

## Risks and Test Signals
Risks include ES8336 topology prefix using a CML filename stem, mockup entries matching only synthetic/test devices, and link2 assumptions for RT5682. Test signals are CNL ACPI matching, topology suffix generation for ES8336, SoundWire mockup matching in validation setups, and RT274/RT5682 stream tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/common/soc-acpi-intel-cnl-match.c -->
