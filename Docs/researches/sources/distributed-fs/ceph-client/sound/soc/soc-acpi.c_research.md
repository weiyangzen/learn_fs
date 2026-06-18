# sources/distributed-fs/ceph-client/sound/soc/soc-acpi.c

Purpose: provides ASoC ACPI and SoundWire enumeration helpers for machine-driver selection and ACPI package extraction.

Important APIs: `snd_soc_acpi_find_machine()` scans a machine table, tests primary `id` or composite codec IDs, applies optional `machine_quirk`, and returns the selected entry. `snd_soc_acpi_find_package_from_hid()` walks ACPI devices for a HID and extracts a typed package into caller-provided state. `snd_soc_acpi_codec_list()` validates that every codec in a quirk-provided list is present. `snd_soc_acpi_sdw_link_slaves_found()` verifies that all ACPI-described SoundWire slaves for a link are reported in the live peripheral list, including duplicate part-count and unique-ID handling.

Control flow and state: helpers are stateless except `snd_soc_acpi_id_present()` may copy a matching composite codec ID into `machine->id`. Package search terminates early when a valid package is found. SoundWire matching compares link ID, manufacturer, part, version, duplicate count, and unique ID when needed.

Dependencies and integration: uses ACPI device presence/evaluation APIs, `soc-acpi.h` machine descriptors, and SoundWire ID macros. Exported functions are used by platform machine drivers during probe.

Risks: mutating `machine->id` for composite matches can affect later table use. Duplicate SoundWire parts require exact expected/reported counts before unique IDs are considered. Package extraction ignores malformed/nonmatching devices and returns false rather than detailed errors.

Test signals: ACPI tables with single and composite codec IDs select expected machines; quirk rejection continues scanning; package extraction validates count/format; SoundWire duplicate slave configurations only pass when all unique IDs are present.
