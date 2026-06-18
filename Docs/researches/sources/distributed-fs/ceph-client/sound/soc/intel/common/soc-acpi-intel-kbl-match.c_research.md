<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/common/soc-acpi-intel-kbl-match.c -->
# sources/distributed-fs/ceph-client/sound/soc/intel/common/soc-acpi-intel-kbl-match.c

## Purpose
Kaby Lake ACPI match table for I2S codec boards, including RT286/NAU88L25/MAX98357A/MAX98927/RT5663/DA7219/RT5660/MAX98373 variants.

## APIs, Types, and Functions
Exports `snd_soc_acpi_intel_kbl_machines[]`. Defines companion codec lists `kbl_codecs`, `kbl_poppy_codecs`, `kbl_5663_5514_codecs`, and DA7219 amplifier lists for MAX98357A, MAX98927, and MAX98373. Entries map ACPI IDs to KBL machine drivers and, for SOF-capable entries, topology filenames.

## Control Flow, State, and Persistence
Static ACPI matching selects the first entry whose HID and companion-codec quirk match. No runtime state exists; selected machine data carries driver names, topology names, and quirk data.

## Dependencies and Integration
Depends on ASoC ACPI matching and `snd_soc_acpi_codec_list`. Consumed by KBL SST/SOF platform selection and machine drivers.

## Risks and Test Signals
Risks include overlapping MAX98927/DA7219 entries, missing topology filenames on legacy SST-only entries, companion-list ordering problems, and RT5660 alternative HID handling. Test signals are machine selection for KBL reference and Chromebook-style boards, topology load where present, and amplifier/headset playback validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/common/soc-acpi-intel-kbl-match.c -->
