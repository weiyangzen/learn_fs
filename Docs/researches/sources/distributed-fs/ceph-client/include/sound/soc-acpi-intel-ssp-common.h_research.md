<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/sound/soc-acpi-intel-ssp-common.h -->
# sources/distributed-fs/ceph-client/include/sound/soc-acpi-intel-ssp-common.h

## Purpose
`soc-acpi-intel-ssp-common.h` centralizes Intel SSP machine-driver codec detection constants and helper declarations for common I2S/SSP codec and amplifier combinations.

## Important APIs, types, and functions
It defines ACPI HID strings for Cirrus, Dialog, Everest, Maxim, Nuvoton, Realtek, and TI codecs/amps. `enum snd_soc_acpi_intel_codec` classifies headphone codecs and speaker amplifiers. Helper APIs detect codec and amp type from a device and map enum values to codec names and topology suffixes: `snd_soc_acpi_intel_detect_codec_type()`, `snd_soc_acpi_intel_detect_amp_type()`, `snd_soc_acpi_intel_get_codec_name()`, `snd_soc_acpi_intel_get_codec_tplg_suffix()`, and `snd_soc_acpi_intel_get_amp_tplg_suffix()`.

## Control flow
Intel machine selection or topology naming code scans ACPI devices, classifies the attached codec/amp, and appends the matching topology suffix or exposes a readable name.

## State and persistence behavior
The header defines constants and pure lookup APIs. Detection results are runtime decisions, not persisted.

## Dependencies and integration points
It is used by Intel SSP machine drivers and ACPI matching code to bridge codec ACPI IDs to machine topology names.

## Risks and test signals
Risks include missing HID aliases, ambiguous systems with multiple codecs/amps, stale topology suffixes, and returning `CODEC_NONE` on valid but newly supported hardware. Test signals include each HID string, codec-plus-amp combinations, topology filename generation, and machines with absent optional amps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/sound/soc-acpi-intel-ssp-common.h -->
