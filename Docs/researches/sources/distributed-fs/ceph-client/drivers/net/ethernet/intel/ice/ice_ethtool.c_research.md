# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_ethtool.c

## Purpose

`ice_ethtool.c` is the primary ethtool integration layer for the Intel ICE Ethernet driver. It binds Linux `struct ethtool_ops` callbacks to ICE PF, safe-mode, and port-representor behavior, exposing driver metadata, register and EEPROM reads, self tests, statistics, link settings, FEC, pause, RSS, channel counts, ring sizing, interrupt coalescing, Wake-on-LAN, module EEPROM data, timestamping information, reset requests, and Flow Director classifier rule operations.

The file is intentionally broad because ethtool is the user-facing control and observability surface for a netdev. Most functions translate ethtool structures into ICE PF/VSI/hardware state, then call lower-level ICE admin queue, flow, filter, RSS, PTP, DCB, or queue-management helpers.

## Important APIs, Types, and Functions

The file defines local mapping structures such as `struct ice_stats`, `struct ice_priv_flag`, and uses `struct ice_port_topology` plus register-dump types from `ice_ethtool.h`. `ice_gstrings_vsi_stats`, `ice_gstrings_pf_stats`, `ice_gstrings_test`, and `ice_gstrings_priv_flags` define userspace-visible string tables. The stability of `ice_get_sset_count()`, `__ice_get_strings()`, and `__ice_get_ethtool_stats()` matters because ethtool statistics are a multi-call ABI where string count, order, and values must remain synchronized.

Driver identity and low-level access are provided through `ice_get_drvinfo()`, `ice_get_regs_len()`, `ice_get_regs()`, `ice_get_extended_regs()`, `ice_get_eeprom_len()`, and `ice_get_eeprom()`. Extended register dumping maps logical ports to PCS/SerDes topology and reads SerDes equalization through admin queue calls.

Diagnostics are implemented by `ice_self_test()` and helpers `ice_link_test()`, `ice_eeprom_test()`, `ice_reg_test()`, `ice_intr_test()`, and `ice_loopback_test()`. Offline diagnostics stop the netdev if needed, set `ICE_TESTING`, reject active VFs, create a temporary loopback VSI, program MAC loopback, send test frames, validate receive descriptors, and restore the device.

Link and PHY management is centered around `ice_get_link_ksettings()` and `ice_set_link_ksettings()`. Helper layers map ICE PHY type bits to ethtool link modes (`ice_phy_type_to_ethtool()`), convert requested speed advertisements to admin queue speed masks (`ice_ksettings_find_adv_link_speed()`, `ice_speed_to_aq_link()`), validate autonegotiation (`ice_setup_autoneg()`), and save requested PHY state in `pi->phy`. FEC is exposed with `ice_get_fecparam()`, `ice_set_fecparam()`, `ice_set_fec_cfg()`, and FEC counter callbacks.

Queue and traffic steering management includes `ice_get_ringparam()`, `ice_set_ringparam()`, `ice_get_channels()`, `ice_set_channels()`, `ice_get_rxfh()`, `ice_set_rxfh()`, `ice_get_rxfh_fields()`, `ice_set_rxfh_fields()`, `ice_get_rxnfc()`, and `ice_set_rxnfc()`. The RX NFC functions integrate with `ice_ethtool_fdir.c` through `ice_add_fdir_ethtool()`, `ice_del_fdir_ethtool()`, `ice_get_ethtool_fdir_entry()`, and `ice_get_fdir_fltr_ids()`.

Interrupt coalescing is exposed by `ice_get_coalesce()`, `ice_set_coalesce()`, and the per-queue variants. These read and update `ice_ring_container` ITR mode/settings and queue-vector INTRL values. Timestamping and PTP observability is provided by `ice_get_ts_info()` and `ice_get_ts_stats()`.

The exported setup functions are `ice_adv_lnk_speed_maps_init()`, `ice_set_ethtool_safe_mode_ops()`, `ice_set_ethtool_repr_ops()`, and `ice_set_ethtool_ops()`.

## Control Flow and Integration

The final registration point is one of three ethtool ops tables. `ice_ethtool_ops` is the full PF/netdev table. `ice_ethtool_safe_mode_ops` exposes a reduced set when package download or advanced features are unavailable. `ice_ethtool_repr_ops` exposes driver info, link, stats, and VF reset for port representors.

Most callbacks begin by resolving `netdev_priv(netdev)` or `ice_netdev_to_pf(netdev)` into an `ice_vsi`, `ice_pf`, and `ice_hw`. They then validate the VSI type, feature flags, reset state, media type, or queue availability before touching hardware. Configuration callbacks generally serialize with `ICE_CFG_BUSY`, netdev carrier state, queue-down/up flows, or explicit device locks.

Link setting control is a multi-step flow: get PHY caps, compute supported/advertised modes, reject unsupported advertisement bits, check autoneg, read current link status, convert advertisement to ICE PHY types, intersect with media or lenient-mode NVM masks, optionally mark carrier down, call `ice_aq_set_phy_cfg()`, then persist `curr_user_speed_req` and `req_speeds`. FEC, pause, and N-way reset follow the same design pattern: map ethtool semantics to the current ICE PHY/admin queue representation and persist requested state only after accepted hardware calls.

Ring resizing is cautious. It validates descriptor counts and AF_XDP state, allocates replacement Tx/Rx/XDP rings while the old netdev remains live, then brings the VSI down and swaps rings. If the netdev is down, it only updates stored descriptor counts for the next open. Channel changes reject safe mode, ADQ, active Flow Director filters, invalid TC counts, and active RDMA clients before calling `ice_vsi_recfg_qs()` and updating RSS LUT sizing.

Flow Director enters through `ice_set_rxnfc()` and `ice_get_rxnfc()`. Insert and delete commands are delegated to `ice_ethtool_fdir.c`; count/list/read commands use `hw->fdir_active_fltr`, `ice_get_fdir_cnt_all()`, and the Flow Director in-memory list.

## State and Persistence Behavior

The file mutates several long-lived driver fields. `pf->msg_enable` and, without dynamic debug, `pf->hw.debug_mask` hold message-level settings. `pf->flags` stores private flags such as FW LLDP agent, VF true promiscuous support, VF VLAN pruning, and link-down-on-close; `ice_set_priv_flags()` computes changed bits and may trigger LLDP/DCB reconfiguration.

PHY user state persists in `pi->phy.curr_user_phy_cfg`, `pi->phy.curr_user_fec_req`, `pi->phy.curr_user_speed_req`, and `pi->phy.link_info.req_speeds`. Flow control persists in `pi->fc.req_mode`. Queue/ring configuration persists in `vsi->num_tx_desc`, `vsi->num_rx_desc`, ring `count` fields, `vsi->hsplit`, `vsi->rss_size`, `vsi->rss_lut_user`, `vsi->rss_hkey_user`, and `vsi->rss_hfunc`. Coalescing persists in q-vector/ring-container ITR and INTRL fields. WoL persists in `pf->wol_ena` and the device wakeup setting.

Statistics are not written to disk but are long-lived counters in PF/VSI/ring/PTP structures. EEPROM and module reads acquire hardware resources and copy bytes to ethtool buffers without modifying NVM.

## Dependencies and Integration Points

This file depends heavily on `ice.h`, `ice_ethtool.h`, `ice_flow.h`, `ice_fltr.h`, `ice_lib.h`, `ice_dcb_lib.h`, Linux ethtool/netdev APIs, DCBNL, libeth RX buffer types, PCI device naming, admin queue calls, register accessors `rd32()`/`wr32()`, queue setup/teardown helpers, RSS helpers, Flow Director helpers, PTP state, RDMA auxiliary device state, and representor operations.

Externally visible integration points are ethtool commands such as driver info, stats, tests, link settings, pause/FEC, RSS, ntuple classifier, module EEPROM, ring/channel/coalesce configuration, reset, and timestamping. In-driver integration is strongest with Flow Director, DCB/LLDP, queue reconfiguration, PTP, safe mode, ADQ, XDP/AF_XDP, and VF representors.

## Risks and Edge Cases

The main ABI risk is changing statistic string counts or ordering without matching value output. Hardware access risk is concentrated in register tests, NVM access, module EEPROM reads, and admin queue PHY changes. Offline tests can disrupt traffic, so active VFs are rejected and the netdev is reopened on exit.

Concurrency risks include `ICE_CFG_BUSY` timeout handling, reset-in-progress interaction, queue reconfiguration while AF_XDP/ADQ/RDMA/Flow Director are active, and representor readiness. Link-mode handling has media-specific edge cases, especially lenient mode, link override TLVs, 1000M copper/optical mapping, and FEC/autoneg semantics. Ring resizing must avoid leaking partially allocated rings and must preserve timestamps, tails, XDP ring identity, and head split state.

## Test Signals

Useful test signals include `ethtool -i`, `ethtool -S`, `ethtool --show-priv-flags`, private flag toggles for LLDP/VF settings, online and offline `ethtool -t`, `ethtool -s` link speed/autoneg cases, `ethtool --show-fec/--set-fec`, pause changes with and without PFC, ring size changes while up/down and with AF_XDP attached, channel changes with ADQ/FDir/RDMA constraints, RSS key/LUT/symmetric hash changes, `ethtool -n/-N` classifier paths, module EEPROM reads, reset flags, and PTP timestamp info when PTP is ready.
