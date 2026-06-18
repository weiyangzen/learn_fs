# sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hns/hns_dsaf_gmac.c

## Purpose
`hns_dsaf_gmac.c` implements the GMAC-specific `struct mac_driver` callbacks for sub-10G HNS ports. It programs GMAC registers for enable/disable, link mode, pause, frame length, loopback, unicast matching, statistics, register dumps, and MAC address configuration.

## Important APIs and Functions
The only exported factory is `hns_gmac_config`, which allocates and fills a `struct mac_driver`. Important callbacks include `hns_gmac_init`, `hns_gmac_enable`, `hns_gmac_disable`, `hns_gmac_adjust_link`, `hns_gmac_need_adjust_link`, `hns_gmac_config_max_frame_length`, `hns_gmac_pause_frm_cfg`, `hns_gmac_set_mac_addr`, `hns_gmac_get_info`, `hns_gmac_update_stats`, `hns_gmac_get_stats`, and `hns_gmac_get_regs`.

## Control Flow
The shared MAC layer calls `hns_gmac_config` during MAC initialization. `hns_gmac_init` resets the GE port through `dsaf_dev->misc_op->ge_srst`, disables RX/TX, disables TX loop packets, configures debug-port matching, enables pad/CRC, enables mode-change support, and adjusts TX waterline to avoid half-duplex hangs. Start/stop calls later map directly to GMAC RX/TX enable bits. Link adjustment writes duplex and port-mode register fields based on 10/100/1000 speed.

## State and Persistence
Persistent state is the allocated `struct mac_driver` and cumulative counters stored in `mac_cb->hw_stats`. Hardware state is register-resident: enable bits, port mode, pause timer/enable, max frame length, station address, filter mode, and counters. Statistics are accumulated by reading hardware counters and adding them into software 64-bit fields.

## Dependencies and Integration Points
The file depends on `hns_dsaf_reg.h` register offsets and field definitions, DSAF register helper macros, `hns_dsaf_mac.h` callback types, and `misc_op` reset hooks. It integrates with `hns_dsaf_mac.c`, which treats the returned `mac_driver` as the GMAC implementation behind generic MAC APIs.

## Risks
`hns_gmac_need_adjust_link` compares `mac_cb->half_duplex == duplex`, which is subtle because `duplex` is full-duplex truth from the upper path. Incorrect interpretation could cause missed or excessive link reprogramming. Statistics are cumulative software additions of hardware register reads; if hardware counters are not clear-on-read, values may be overcounted. `hns_gmac_set_mac_addr` shifts signed `char` values unless callers provide unsigned-safe bytes. FIFO-clean polling can stall stop/link flows until timeout.

## Test Signals
Useful signals are register-dump length `ETH_GMAC_DUMP_NUM`, ethtool GMAC stats count matching `g_gmac_stats_string`, link adjust for all supported speeds, pause enable/disable, max-frame programming after MTU changes, FIFO-clean timeout handling, and station-address writes for the primary VF.
