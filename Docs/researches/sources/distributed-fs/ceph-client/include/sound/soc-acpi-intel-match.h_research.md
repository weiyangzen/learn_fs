<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/sound/soc-acpi-intel-match.h -->
# sources/distributed-fs/ceph-client/include/sound/soc-acpi-intel-match.h

## Purpose
`soc-acpi-intel-match.h` declares Intel ASoC ACPI machine match tables for many platform generations and SoundWire variants.

## Important APIs, types, and functions
The header exports mutable `struct snd_soc_acpi_mach` arrays for Broadwell, Bay Trail, Cherry Trail, Skylake, Kaby Lake, Broxton, Gemini Lake, Cannon Lake, Coffee Lake, Comet Lake, Ice Lake, Tiger Lake, Elkhart Lake, Jasper Lake, Alder Lake, Raptor Lake, Meteor Lake, Lunar Lake, Arrow Lake, Panther Lake, Nova Lake, SoundWire-specific platform tables, and generic HDA machines.

## Control flow
Intel audio platform drivers select the appropriate table for the detected SoC and pass it to ACPI matching helpers. Matched entries identify machine driver names, topology/firmware files, links, quirks, and platform data.

## State and persistence behavior
The arrays are not const because fields can be patched for platform data or machine operations at runtime. They are global kernel data, not persistent storage.

## Dependencies and integration points
It depends on ACPI, module definitions, and `snd_soc_acpi_mach` from `soc-acpi.h`. It integrates Intel ACPI enumeration with SST/SOF/HDA/SoundWire machine driver selection.

## Risks and test signals
Risks include choosing the wrong generation table, mutable shared entries being patched unexpectedly, missing SoundWire variant coverage, and topology filename mismatches. Test signals include ACPI ID matching across each platform generation, SoundWire link-mask matches, HDA fallback, and machine-quirk mutation behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/sound/soc-acpi-intel-match.h -->
