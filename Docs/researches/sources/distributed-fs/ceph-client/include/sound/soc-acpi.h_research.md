<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/sound/soc-acpi.h -->
# sources/distributed-fs/ceph-client/include/sound/soc-acpi.h

## Purpose
`soc-acpi.h` defines ACPI-based ASoC machine matching and board-description structures, with SoundWire, I2S, codec, topology, firmware, quirk, and PCI SSID metadata.

## Important APIs, types, and functions
Important types include `snd_soc_acpi_package_context`, `snd_soc_acpi_mach_params`, `snd_soc_acpi_endpoint`, `snd_soc_acpi_adr_device`, `snd_soc_acpi_link_adr`, `snd_soc_acpi_mach`, and `snd_soc_acpi_codecs`. APIs under ACPI include `snd_soc_acpi_find_machine()`, `snd_soc_acpi_find_package_from_hid()`, and `snd_soc_acpi_codec_list()`, with stubs when ACPI is disabled. Other helpers include `snd_soc_acpi_sof_parent()` and `snd_soc_acpi_sdw_link_slaves_found()`. Topology quirk flags select dynamic SSP, DMIC, amp, and codec suffixes.

## Control flow
Platform code passes a machine table to `snd_soc_acpi_find_machine()`. Matching may use ACPI ID, UID, compatible codec lists, SoundWire link ADR descriptors, DMI/quirk callbacks, machine-check callbacks, and topology quirk masks. Matched entries carry driver names, firmware/topology files, board names, platform data, and machine parameters into machine-driver probe.

## State and persistence behavior
Machine descriptors are mostly static table data, but `pdata` and `mach_params` can be updated at runtime with detected DMIC count, SoundWire links, I2S masks, PCI SSID, BT offload, and optional DAI drivers. Nothing is durable.

## Dependencies and integration points
It depends on ACPI, mod device tables, SoundWire descriptors, and ASoC core types. It integrates firmware enumeration with SST/SOF/HDA/SoundWire machine setup.

## Risks and test signals
Risks include ACPI-disabled stubs hiding machine support, malformed package contexts, link-mask/ADR mismatch, quirk callbacks mutating shared entries, topology suffix errors, and incomplete endpoint aggregation data. Test signals include ACPI and non-ACPI builds, codec-list matching, SoundWire slave discovery, UID disambiguation, DMI quirks, split topology callback behavior, PCI SSID propagation, and SOF-parent detection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/sound/soc-acpi.h -->
