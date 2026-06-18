<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/common/soc-acpi-intel-sdw-mockup-match.c -->
# sources/distributed-fs/ceph-client/sound/soc/intel/common/soc-acpi-intel-sdw-mockup-match.c

## Purpose
Reusable SoundWire mockup ACPI link descriptors for Intel ASoC machine tables. These support validation and bring-up without real codec hardware by describing synthetic headset, amplifier, microphone, and multifunction mockup devices.

## APIs, Types, and Functions
Exports four descriptor arrays: `sdw_mockup_headset_1amp_mic[]`, `sdw_mockup_headset_2amps_mic[]`, `sdw_mockup_mic_headset_1amp[]`, and `sdw_mockup_multi_func[]`. Internal static data defines single and aggregated endpoints, multifunction jack/amp/DMIC endpoints, mockup SoundWire ADR devices for headset, amp, mic, and multifunction devices, and link masks for the exported layouts.

## Control Flow, State, and Persistence
The file is static descriptor data. Platform generation tables reference exported arrays in their `snd_soc_acpi_mach.links` fields; match logic then treats the synthetic ADR/link layout like real SoundWire devices. No mutable state is kept.

## Dependencies and Integration
Depends on ASoC ACPI and Intel match headers. Included in the Intel match aggregate and referenced by CNL/MTL/LNL/NVL/PTL match files for mockup `sof_sdw` entries.

## Risks and Test Signals
Risks include synthetic ADR values colliding with real devices, endpoint grouping not matching the topology reused by a generation, typo-prone `name_prefix` strings, and mockup entries matching ahead of production entries if ordering is wrong. Test signals are SoundWire mockup enumeration, expected link-mask matching, topology load for mockup entries, and absence of mockup matches on real hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/common/soc-acpi-intel-sdw-mockup-match.c -->
