# sources/distributed-fs/ceph-client/drivers/net/ethernet/aquantia/atlantic/hw_atl2/hw_atl2_utils.h

## Purpose
This header defines the A2 firmware shared-buffer ABI used by the ATL2 driver. It describes host-to-firmware input structures, firmware-to-host output structures, link and capability bitfields, stats formats, health monitors, sleep proxy data, cable diagnostics, filter capabilities, and firmware ops declarations.

## Important APIs, types, and functions
Major input-side types include `link_options_s`, `link_control_s`, `thermal_shutdown_s`, `mac_address_aligned_s`, `sleep_proxy_s`, `pause_quanta_s`, `request_policy_s`, and `fw_interface_in`. Output-side types include `transaction_counter_s`, `version_s`, `link_status_s`, `wol_status_s`, health monitors, `device_link_caps_s`, `sleep_proxy_caps_s`, `lkp_link_caps_s`, `statistics_s` with A0/B0 variants, `filter_caps_s`, `management_status_s`, and `fw_interface_out`. It also declares `hw_atl2_utils_initfw`, `hw_atl2_utils_soft_reset`, `hw_atl2_utils_get_fw_version`, `hw_atl2_utils_get_action_resolve_table_caps`, and `aq_a2_fw_ops`.

## Control flow
The header has no executable flow, but its layout drives the shared-buffer macros in `hw_atl2_utils_fw.c`. Offsets in `fw_interface_in` and `fw_interface_out` are used as dword indexes into firmware shared memory, and the transaction counter fields provide consistent multiword reads.

## State and persistence
These structures represent firmware-persistent and hardware-shared state: link policy, MTU, MAC address, sleep proxy/WoL, pause quanta, cable diagnostics, firmware version, link status, health, caps, management status, stats, and trace/core-dump data. The driver reads/writes them through MMIO windows rather than storing them on disk.

## Dependencies and integration points
The header includes `aq_hw.h` and is used by ATL2 firmware utilities and internal hardware code. It is the ABI contract between driver and A2 firmware; layout, packing, alignment, and bitfield order must match firmware expectations.

## Risks
C bitfield layout is compiler- and endian-sensitive, so this ABI assumes the kernel/compiler layout used by the target driver. The shared-buffer macros enforce dword alignment for many fields, but not semantic validity. Any firmware ABI revision that changes field order or size can break link, stats, WoL, or filter capability handling.

## Test signals
Version reads, link speed/EEE/pause round-trips, stable multiword stats reads, ART capability retrieval, WoL programming, and health temperature reads validate the ABI. Build-time `BUILD_BUG_ON_MSG` checks in the C file catch unaligned shared-buffer accesses.
