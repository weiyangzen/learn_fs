# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/wangxun/txgbe/txgbe_ethtool.c

## Purpose
`txgbe_ethtool.c` installs TXGBE ethtool operations and implements TXGBE-specific link settings, ring resizing, Flow Director rule get/set/delete, RX NFC reporting, and module EEPROM page reads.

## Important APIs, Types, and Functions
Public functions are `txgbe_get_link_ksettings()` and `txgbe_set_ethtool_ops()`. Local Flow Director helpers include `txgbe_get_ethtool_fdir_entry()`, `txgbe_get_ethtool_fdir_all()`, `txgbe_flowspec_to_flow_type()`, `txgbe_add_ethtool_fdir_entry()`, `txgbe_del_ethtool_fdir_entry()`, `txgbe_update_ethtool_fdir_entry()`, `txgbe_match_ethtool_fdir_entry()`, `txgbe_get_rxnfc()`, and `txgbe_set_rxnfc()`. `txgbe_get_module_eeprom_by_page()` proxies module EEPROM reads to AML firmware.

## Control Flow
Probe assigns the ethtool ops table. Ring resizing follows the same reset-lock/down/up pattern as `ngbe`, but calls `txgbe_down()`/`txgbe_up()`. RX NFC get paths report rule count, a single rule, or all rule locations from the sorted hlist. Rule insert validates perfect-filter mode, ring/VF target, location bounds, flow type, and one-mask-per-port constraint, computes the ATR perfect hash, optionally programs hardware if the netdev is running, then inserts the software rule. Delete erases hardware when needed and removes the software node under `fdir_perfect_lock`.

## State and Persistence Behavior
State includes runtime ring counts, reset state, `txgbe->fdir_filter_list`, `fdir_filter_count`, `fdir_mask`, and link mode masks in `struct txgbe`. Perfect filters are stored in memory and restored after Flow Director reinitialization; they are not persisted across driver unload.

## Dependencies and Integration Points
It depends on shared `wx_ethtool` helpers, TXGBE Flow Director programming, AML EEPROM access, phylink linkmode helpers, ethtool RX NFC APIs, and shared ring reset helpers.

## Risks and Edge Cases
Hardware supports only one perfect-filter mask per port; users must delete all rules to change masks. Rule duplicate detection uses bucket hash plus action, so different raw flows with the same bucket/action can be treated as duplicates. `ring_cookie` VF/ring mapping must match SR-IOV queue layout. Module EEPROM reads are only supported when `WX_FLAG_SWFW_RING` is set.

## Test Signals
Test `ethtool -k/-S/-g/-G/-n/-N`, perfect rule add/delete/list for TCP/UDP/SCTP/IPV4, drop and queue actions, VF queue actions, mask mismatch, duplicate rules, interface down/up restoration, and module EEPROM page reads on AML devices.
