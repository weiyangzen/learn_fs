<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mvm/offloading.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mvm/offloading.c

## Purpose
Builds firmware protocol offload commands used for WoWLAN/D3 and related low-power operation, including ARP, IPv6 neighbor solicitation, BTM offload, and QoS sequence handoff.

## Important APIs, Types, And Functions
`iwl_mvm_set_wowlan_qos_seq` copies per-TID QoS sequence numbers from an AP station into a WoWLAN config command with firmware sequence semantics. `iwl_mvm_send_proto_offload` builds and sends `PROT_OFFLOAD_CONFIG_CMD` using one of several command layouts: v1, v2, v3 small, or v4/large. It uses `struct iwl_proto_offload_cmd_common`, `struct iwl_ns_config`, `struct iwl_targ_addr`, IPv6 address arrays stored in `struct iwl_mvm_vif`, and mac80211 vif ARP configuration.

## Control Flow
QoS sequence handoff subtracts `0x10` from each next sequence because firmware increments before use while the host stores the next value after use. Protocol offload command construction first selects IPv6 NS layout from firmware capability flags. For new NS offload layouts it groups target IPv6 addresses by solicited-node multicast address, skips tentative addresses when actual NS offload is enabled, fills target address to NS config mappings, and counts valid addresses. Older layouts copy up to their supported address count and set the NDP MAC. ARP offload is enabled from `vif->cfg.arp_addr_list[0]`; BTM offload is enabled if supported. The selected command size and pointer are adjusted for older large-NS command versions that lack `sta_id`, and the command is sent.

## State And Persistence
Reads `mvmvif->target_ipv6_addrs`, `mvmvif->tentative_addrs`, `vif->cfg.arp_addr_cnt`, `vif->cfg.arp_addr_list`, `vif->addr`, and AP station TID sequence state. It does not retain state itself; it serializes host network addressing and sequence state into firmware-owned low-power offload state.

## Dependencies And Integration Points
Depends on IPv6/addrconf helpers, firmware capability flags, WoWLAN command definitions, mac80211 vif configuration, and `iwl_mvm_send_cmd`. It is called by D3/WoWLAN setup paths declared in `mvm.h`.

## Risks And Edge Cases
Tentative IPv6 addresses must be skipped only when firmware will answer NS, otherwise wake filtering could hide duplicate-address-detection traffic. New NS layouts have independent limits for target addresses and NS config entries, so deduplication and counts must remain consistent. Command version `<4` for large NS offload shifts the command pointer to the common field; wrong sizing would corrupt firmware parsing. Only the first ARP address is offloaded.

## Test Signals
Cover no IPv6, tentative IPv6 with offload enabled/disabled, duplicate solicited-node multicast addresses, address counts above each firmware limit, ARP-only offload, BTM capability on/off, disable-offloading mode, command version `<4` large layout, and QoS sequence wrap/underflow behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mvm/offloading.c -->
