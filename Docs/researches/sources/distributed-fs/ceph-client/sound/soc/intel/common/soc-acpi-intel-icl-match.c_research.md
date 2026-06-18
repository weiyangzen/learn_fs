<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/common/soc-acpi-intel-icl-match.c -->
# sources/distributed-fs/ceph-client/sound/soc/intel/common/soc-acpi-intel-icl-match.c

## Purpose
Ice Lake ACPI match tables for RT274, RT5682, ES8336 SSP designs and SoundWire RT700/RT711/RT1308/RT715 topologies.

## APIs, Types, and Functions
Exports `snd_soc_acpi_intel_icl_machines[]` and `snd_soc_acpi_intel_icl_sdw_machines[]`. Defines ES83x6 codec matching, SoundWire endpoint/address descriptors for RT700, RT711, RT1308, and RT715, and link arrays `icl_rvp`, `icl_3_in_1_default`, and `icl_3_in_1_mono_amp`.

## Control Flow, State, and Persistence
Static ACPI entries select SSP machine drivers/topologies, with ES8336 using runtime topology suffix masks. SoundWire entries select `sof_sdw` and topologies based on link masks for default 3-in-1, mono-amplifier, or RT700-only designs.

## Dependencies and Integration
Depends on ASoC ACPI match helpers and the Intel match aggregate. Consumed by ICL SOF machine selection and SoundWire machine probing.

## Risks and Test Signals
Risks include incorrect RT1308 stereo aggregation endpoint metadata, ES8336 suffix mismatch, and ambiguous SoundWire link masks if firmware reports unexpected devices. Test signals are ICL ACPI matching, topology load for RT274/RT5682/ES8336, SoundWire 3-in-1 and RT700 probe, and playback/capture/headset/mic validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/common/soc-acpi-intel-icl-match.c -->
