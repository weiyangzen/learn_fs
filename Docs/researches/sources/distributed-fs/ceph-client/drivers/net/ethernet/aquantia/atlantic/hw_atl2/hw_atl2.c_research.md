# sources/distributed-fs/ceph-client/drivers/net/ethernet/aquantia/atlantic/hw_atl2/hw_atl2.c

## Purpose
This file implements the ATL2/A2 hardware operations for newer Atlantic devices such as AQC113, AQC115C, and AQC116C. It publishes device capability records and `hw_atl2_ops`, combining the existing Atlantic B0 ring datapath with A2-specific QoS, traffic-class mapping, RSS redirection, action-resolver receive filtering, interrupt moderation, VLAN filtering, firmware setup, and reset behavior.

## Important APIs, types, and functions
The public symbols are `hw_atl2_caps_aqc113`, `hw_atl2_caps_aqc115c`, `hw_atl2_caps_aqc116c`, and `const struct aq_hw_ops hw_atl2_ops`. Important internal functions include `hw_atl2_hw_reset`, `hw_atl2_hw_init`, `hw_atl2_hw_qos_set`, `hw_atl2_hw_queue_to_tc_map_set`, `hw_atl2_hw_rss_set`, `hw_atl2_hw_init_tx_tc_rate_limit`, `hw_atl2_hw_init_tx_path`, `hw_atl2_hw_init_rx_path`, `hw_atl2_hw_init_new_rx_filters`, `hw_atl2_act_rslvr_table_set`, `hw_atl2_hw_multicast_list_set`, `hw_atl2_hw_packet_filter_set`, `hw_atl2_hw_vlan_set`, `hw_atl2_hw_vlan_ctrl`, and `hw_atl2_hw_interrupt_moderation_set`.

## Control flow
Hardware prepare is delegated through `hw_atl2_utils_initfw`. Reset performs an A2 firmware soft reset, clears `struct hw_atl2_priv`, asks firmware for `MPI_RESET`, and checks hardware error flags. Initialization reads firmware action resolver table capabilities, computes a driver-owned ART base index, configures launch-time timing, initializes TX/RX paths, programs the MAC address, requests link up through firmware, applies QoS/RSS/hash settings, enables the new RPF block, snapshots counters, configures interrupts, and applies offloads. Runtime filtering updates go through ART records guarded by a firmware semaphore.

## State and persistence
Persistent driver state is minimal: `hw_atl2_priv` stores the last firmware statistics snapshot and the ART base index reserved by firmware. Hardware state resides in RX/TX scheduler registers, RPF filter tables, RSS tables, VLAN filter registers, interrupt moderation registers, and firmware-owned link settings. `aq_nic_cfg_s` drives traffic classes, priority mapping, flow control, RSS, VLAN filters, interrupt moderation, and rate limits.

## Dependencies and integration points
The implementation reuses many B0 helpers from `hw_atl_b0` and lower-level register helpers from `hw_atl_llh`, while A2-specific helpers come from `hw_atl2_llh.h` and `hw_atl2_utils.h`. The ops table is consumed by the Atlantic core driver through `aq_hw_ops`. Firmware provides ART capacity and link control through `aq_fw_ops`; the network stack reaches this file through netdev operations implemented in the shared Atlantic core.

## Risks
Traffic-class mapping assumes only 4-TC or 8-TC modes; invalid `tc_mode` returns `-EINVAL`. ART writes depend on semaphore acquisition and firmware-provided base indexes, so wrong capabilities can corrupt firmware-owned resolver entries. Rate-limit arithmetic uses link speed and configured min/max rates; zero or inconsistent rates may produce unexpected weights. Multicast programming uses unicast filter slots as multicast filters and rejects over-capacity lists with `-EBADRQC`.

## Test signals
Useful tests include probe on each advertised device capability, firmware reset/init success, RSS indirection across 4 and 8 traffic classes, VLAN filter routing to queues, promiscuous/all-multicast transitions, interrupt moderation in off/on/auto modes across link speeds, traffic-class max/min rate behavior, and counter updates through `hw_get_hw_stats`.
