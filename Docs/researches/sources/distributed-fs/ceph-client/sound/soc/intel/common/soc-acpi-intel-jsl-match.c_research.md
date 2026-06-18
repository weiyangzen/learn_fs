<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/common/soc-acpi-intel-jsl-match.c -->
# sources/distributed-fs/ceph-client/sound/soc/intel/common/soc-acpi-intel-jsl-match.c

## Purpose
Jasper Lake ACPI match table for DA7219, RT5682/RT5682S, CS42L42, RT5650, ES8336, and several speaker-amplifier companion variants.

## APIs, Types, and Functions
Exports `snd_soc_acpi_intel_jsl_machines[]`. Defines codec lists for ES83x6, MAX98373, RT1015, RT1015P, MAX98360A, RT5650, and RT5682/RT5682S. Uses `snd_soc_acpi_codec_list` and `.quirk_data` to distinguish machine/topology variants with shared headset codec IDs.

## Control Flow, State, and Persistence
Matching is static but order and `.quirk_data` matter for shared IDs such as `DLGS7219` and RT5682-compatible companions. ES8336 uses runtime topology suffix generation for SSP/DMIC variation. No mutable state is stored.

## Dependencies and Integration
Depends on ASoC ACPI match helpers and the Intel match aggregate. Used by JSL SOF platform selection and board machine drivers.

## Risks and Test Signals
Risks include companion codec list ordering selecting the wrong amplifier topology, reusing `sof-jsl-rt5682-rt1015.tplg` for RT1015 and RT1015P variants, and ES8336 suffix mismatch. Test signals are matching each DA7219/RT5682 amplifier variant, RT5650 probe, topology load, and speaker/headset/DMIC validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/common/soc-acpi-intel-jsl-match.c -->
