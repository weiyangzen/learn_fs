# sources/distributed-fs/ceph-client/sound/soc/intel/common/soc-acpi-intel-tgl-match.c

## Purpose
Defines Tiger Lake ACPI and SoundWire machine-match tables used by Intel ASoC/SOF enumeration to select the correct machine driver, topology file, SoundWire link layout, codec endpoint aggregation, and codec-specific quirk handling.

## Important APIs, Types, And Functions
The file exports `snd_soc_acpi_intel_tgl_machines[]` for non-SoundWire ACPI codec matching and `snd_soc_acpi_intel_tgl_sdw_machines[]` for SoundWire-only layouts. Most content is static `snd_soc_acpi_endpoint`, `snd_soc_acpi_adr_device`, `snd_soc_acpi_link_adr`, and `snd_soc_acpi_codecs` data. It covers Realtek RT711/RT1308/RT715/RT5682, RT711/RT1316/RT714 SDCA, RT712 combinations, Cirrus CS42L43/CS35L56 combinations, Maxim MX8373, ESSX83x6, LT6911 HDMI, and mockup links.

## Control Flow, State, And Persistence
There is no executable control flow beyond module export. Runtime behavior comes from the core ACPI/SoundWire matcher traversing the arrays in order. Earlier entries have priority, so mockups and more-specific four-link layouts are placed before generic or fallback layouts. Endpoint fields such as `aggregated`, `group_position`, and `group_id` persist only as static description data consumed by the SoundWire machine driver.

## Dependencies And Integration Points
Depends on `sound/soc-acpi.h`, `sound/soc-acpi-intel-match.h`, Intel SSP common IDs, and `soc-acpi-intel-sdw-mockup-match.h`. The arrays integrate with SOF `sof_sdw` and TGL-specific machine drivers through `drv_name`, `sof_tplg_filename`, `link_mask`, `links`, `machine_quirk`, and `quirk_data`.

## Risks And Test Signals
Risks include match-order regressions, wrong SoundWire ADR values, endpoint aggregation mistakes, and topology filename drift. The local source also shows syntax-looking damage in the CS35L56 right feedback endpoint block, which would be a compile-time failure if present in a build path. Test signals are compile coverage, ACPI/SoundWire enumeration logs, topology load success for each `sof_tplg_filename`, and mockup table selection tests.
