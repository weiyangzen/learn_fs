# sources/distributed-fs/ceph-client/drivers/soc/vt8500/wmt-socinfo.c

## Purpose
This file registers SoC bus information for VIA/WonderMedia VT8500-family systems by reading the SCC ID register and decoding family, revision, and raw SoC ID.

## Important APIs, Types, And Functions
Important data is `chip_id_table`, mapping SCC high-half IDs to chip names. Key functions are `sccid_to_name`, `wmt_socinfo_probe`, and `wmt_socinfo_remove`. It matches `via,vt8500-scc-id`.

## Control Flow
Probe maps the SCC ID register with `devm_of_iomap`, reads `sccid`, allocates SoC attributes, decodes family from bits 31:16, formats revision as letter/digit from low bytes, formats raw `soc_id`, registers the SoC device, logs the result, and stores the `soc_device` for remove. Remove unregisters the SoC device.

## State And Persistence
State is per-platform-device and mostly devm-managed strings plus the registered SoC device. The SCC ID register is hardware identity state.

## Dependencies And Integration Points
It depends on OF, MMIO, platform driver core, and SoC bus. Kconfig selects `SOC_BUS`.

## Risks And Test Signals
Risks include revision decoding producing odd characters for zero or unexpected fields, unknown chip IDs reported generically, and no custom attributes beyond standard SoC bus fields. Test signals include boot log `VIA/WonderMedia <family> rev <rev>`, `/sys/devices/soc*` values, and successful unregister on driver remove.
