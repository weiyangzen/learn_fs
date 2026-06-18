<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/common/soc-acpi-intel-skl-match.c -->
# sources/distributed-fs/ceph-client/sound/soc/intel/common/soc-acpi-intel-skl-match.c

## Purpose
Skylake ACPI match table for early Intel I2S machine drivers using ALC286, NAU88L25/SSM4567, and NAU88L25/MAX98357A combinations.

## APIs, Types, and Functions
Exports `snd_soc_acpi_intel_skl_machines[]`. Defines `skl_codecs` companion codec list for `10508825` and `MX98357A`, then provides entries for `INT343A` -> `skl_alc286s_i2s`, `INT343B` -> `skl_n88l25_s4567`, and `MX98357A` -> `skl_n88l25_m98357a`.

## Control Flow, State, and Persistence
Static ACPI and companion-codec matching selects the machine driver. No SOF topology filenames or mutable state are present, reflecting legacy SST-era machine data.

## Dependencies and Integration
Depends on ASoC ACPI matching and `snd_soc_acpi_codec_list`. Consumed by Skylake Intel platform audio driver selection.

## Risks and Test Signals
Risks include companion codec ambiguity between NAU88L25 plus SSM4567/MAX98357A variants, lack of SOF topology metadata in this table, and ordering sensitivity between HIDs and companion IDs. Test signals are SKL ACPI match selection, correct legacy machine driver binding, and playback/capture on ALC286 and NAU88L25 amplifier designs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/common/soc-acpi-intel-skl-match.c -->
