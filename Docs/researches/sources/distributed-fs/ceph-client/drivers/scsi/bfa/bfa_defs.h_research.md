# sources/distributed-fs/ceph-client/drivers/scsi/bfa/bfa_defs.h

## Purpose
`bfa_defs.h` defines base BFA public data contracts: manufacturing/VPD records, status codes, booleans, adapter and IOC attributes, asynchronous event categories, PCI and ASIC identifiers, boot configuration, adapter block configuration, SFP EEPROM/diagnostic layouts, flash partition metadata, diagnostics, and PHY status/statistics.

## Important APIs and Types
The most widely consumed definitions are `enum bfa_status` and aliases `bfa_status_t`, `enum bfa_boolean`, `struct bfa_adapter_attr_s`, `struct bfa_ioc_attr_s`, `struct bfa_ioc_stats_s`, and PCI/ASIC helper macros `bfa_asic_id_cb`, `bfa_asic_id_ct`, `bfa_asic_id_ct2`, and `bfa_asic_id_ctc`. Manufacturing records include packed `struct bfa_mfg_vpd_s` and `struct bfa_mfg_block_s`, with card type macros such as `bfa_mfg_is_mezz` used by FAA validation in `bfa_core.c`. Boot-related structs include `bfa_boot_bootlun_s`, `bfa_boot_cfg_s`, `bfa_boot_pbc_s`, and `bfa_ethboot_cfg_s`.

## Control Flow and State
This header does not implement executable control flow, but it strongly shapes control decisions. Status codes distinguish retryable busy/non-operational states, unsupported features, adapter mode restrictions, invalid media, D-port and BB credit recovery failures, and firmware/config failures. ASIC id macros select hardware callback tables during IOCFC attach. Port speeds are bit-style constants consumed by FC link and RPSC conversion helpers.

## State and Persistence Behavior
Several structs mirror persistent adapter content in flash or module EEPROM. Manufacturing/VPD blocks are explicitly packed and documented as big-endian. Flash partition attributes describe persistent regions for firmware, option ROM, boot config, PBC, port config, logs, and manufacturing data. SFP structs map serial id, diagnostic, and user EEPROM pages. Boot configs persist SAN/PXE boot policy and target LUNs.

## Dependencies and Integration Points
It includes `bfa_fc.h` for WWN, MAC, SCSI LUN, port speed, and FC constants, plus `bfad_drv.h` for kernel types. It feeds IOC, flash, SFP, diagnostics, PHY, port, and adapter management modules. `bfa_core.c` uses manufacturing/card type and ASIC id helpers directly.

## Risks and Test Signals
Risks are ABI/layout drift, packed struct alignment, endian conversion omissions, duplicated or sparse status codes, and card-type logic becoming stale for new hardware. Test signals include compile-time size/layout checks where available, flash/VPD parsing with checksum failures, ASIC callback selection for all supported device ids, boot config reads, SFP diagnostic parsing, and management tooling that displays every status/state enum.
