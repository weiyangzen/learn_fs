<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/common/soc-acpi-intel-glk-match.c -->
# sources/distributed-fs/ceph-client/sound/soc/intel/common/soc-acpi-intel-glk-match.c

## Purpose
Gemini Lake ACPI match table for ALC298, DA7219/MAX98357A, RT5682/MAX98357A, CS42L42/MAX98357A, and ES8336 audio designs.

## APIs, Types, and Functions
Exports `snd_soc_acpi_intel_glk_machines[]`. Defines codec lists for ES83x6, MAX98357A companion, and RT5682/RT5682S headset codecs, with `snd_soc_acpi_codec_list` quirks on companion-dependent entries.

## Control Flow, State, and Persistence
Static entries match ACPI HID or companion codec lists. ES8336 uses topology quirk masks so SSP number, SSP MSB, and DMIC count are appended at runtime. No mutable state is kept.

## Dependencies and Integration
Depends on ASoC ACPI match helpers. Used by GLK SOF/SST platform selection and corresponding machine drivers/topologies.

## Risks and Test Signals
Risks include companion MAX98357A detection failures, CS42L42 HID encoding differences, RT5682 versus RT5682S companion matching, and dynamic ES8336 topology suffix drift. Test signals are machine selection for each listed codec combination, topology load, speaker/headset/DMIC function, and fallback behavior when amplifier companions are absent.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/common/soc-acpi-intel-glk-match.c -->
