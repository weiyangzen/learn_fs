# sources/distributed-fs/ceph-client/sound/soc/sdca/sdca_device.c

## Purpose
Small SDCA device helper library for reading ACPI/firmware metadata and matching device quirks.

## APIs, Types, and Functions
Exports `sdca_lookup_interface_revision()`, `sdca_lookup_swft()`, and `sdca_device_quirk_match()`. Internal quirk helpers are `sdca_device_quirk_rt712_vb()` and `sdca_device_quirk_skip_func_type_patching()`.

## Control Flow, State, and Persistence
`sdca_lookup_interface_revision()` reads `mipi-sdw-sdca-interface-revision` from the SoundWire slave fwnode into `slave->sdca_data`. `sdca_lookup_swft()` retrieves the ACPI SWFT table and registers a devm action to release it. Quirk matching inspects SoundWire IDs, interface revision, parsed function descriptors, and DMI vendor/SKU data; the RT712_VB quirk depends on Smart Mic function presence, while the Dell/Cirrus quirk skips old function-type patching for specific SKUs and part IDs.

## Dependencies and Integration
Depends on ACPI table APIs, DMI, device property APIs, SoundWire `sdw_slave`, and SDCA function descriptors. It is used by discovery code before function parsing and by the parser when deciding whether to patch draft-era function type values.

## Risks and Test Signals
Risks include ACPI table lifetime mistakes, DMI string fragility, requiring functions to be discovered before some quirks evaluate, and SKU-specific behavior becoming stale. Test signals are interface revision population, SWFT presence/absence handling, RT712 variants with Smart Mic descriptors, and Dell SKU systems where function type patching must be skipped.
