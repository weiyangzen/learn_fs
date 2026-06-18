<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/common/soc-acpi-intel-sdw-mockup-match.h -->
# sources/distributed-fs/ceph-client/sound/soc/intel/common/soc-acpi-intel-sdw-mockup-match.h

## Purpose
Header exposing reusable SoundWire mockup link descriptors to Intel generation-specific ACPI match tables.

## APIs, Types, and Functions
Declares extern arrays `sdw_mockup_headset_1amp_mic[]`, `sdw_mockup_headset_2amps_mic[]`, `sdw_mockup_mic_headset_1amp[]`, and `sdw_mockup_multi_func[]` with type `const struct snd_soc_acpi_link_adr`.

## Control Flow, State, and Persistence
No runtime state or logic exists. The header establishes the compile-time interface for match files to reuse mockup topology descriptors.

## Dependencies and Integration
Included by CNL, MTL, LNL, NVL, PTL, and other match files that reference mockup layouts. The implementation lives in `soc-acpi-intel-sdw-mockup-match.c`.

## Risks and Test Signals
Risks include declaration/definition drift and use without linking the mockup object into `snd-soc-acpi-intel-match-y`. Test signals are successful builds of all referencing match files and correct mockup matching under SoundWire test configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/common/soc-acpi-intel-sdw-mockup-match.h -->
