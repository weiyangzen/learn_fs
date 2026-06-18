## sources/distributed-fs/ceph-client/sound/hda/core/intel-sdw-acpi.c

Purpose: discovers Intel SoundWire controllers and enabled links from the ACPI namespace below an HDAS device.

Important APIs, types, and functions: module parameters `sdw_link_mask` and `sdw_ctrl_addr`, `sdw_intel_acpi_scan()`, `sdw_intel_acpi_cb()`, `sdw_intel_scan_controller()`, and `is_link_enabled()`. The exported function is namespaced as `SND_INTEL_SOUNDWIRE_ACPI`.

Control flow: `sdw_intel_acpi_scan()` walks ACPI device children to depth two, looking for `_ADR` values whose upper nibble marks SoundWire and whose address matches `sdw_ctrl_addr`. After finding the controller, `sdw_intel_scan_controller()` reads firmware properties: preferred `mipi-sdw-manager-list` or fallback `mipi-sdw-master-count`. It bounds link count, applies the module link mask, and checks each `mipi-sdw-link-%hhu-subproperties` child for a disable quirk.

State and persistence: result state is written into caller-provided `struct sdw_intel_acpi_info` as handle, count, and link mask. Module parameters globally override controller address and enabled links.

Dependencies and integration points: used by Intel DSP selection and SoundWire probe paths before hardware is powered. Depends on ACPI fwnode properties, SoundWire Intel constants, firmware child-node naming, and Linux property APIs.

Risks: firmware property absence prevents initialization. `count` and bit-list semantics differ when firmware supplies manager-list versus master-count, so sparse masks need coverage. Module overrides can hide links required by machine drivers. ACPI walk depth assumes SNDW is child or grandchild.

Test signals: test ACPI with manager-list, master-count, disabled link quirks, sparse link masks, no links, and too many links; exercise `sdw_link_mask=` and `sdw_ctrl_addr=`; confirm `info->link_mask` matches expected firmware.
