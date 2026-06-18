<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mediatek/mtk_ppe_offload.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mediatek/mtk_ppe_offload.c

## Purpose
`mtk_ppe_offload.c` connects Linux TC flower flow offload to MediaTek PPE FOE programming. It parses `flow_cls_offload` rules, validates supported match/action combinations, converts matches and actions into `mtk_foe_entry` data, chooses an output PSE/DSA/WED path, manages the global flow rhashtable keyed by TC cookie, and reports offload stats.

## Important APIs And Functions
`struct mtk_flow_data` is a temporary parser result containing Ethernet addresses, IPv4/IPv6 endpoints, ports, input VLAN, pushed VLANs, and PPPoE session data. Helper functions parse or apply action data: `mtk_flow_offload_mangle_eth`, `mtk_flow_mangle_ports`, `mtk_flow_mangle_ipv4`, `mtk_flow_set_ipv4_addr`, and `mtk_flow_set_ipv6_addr`. `mtk_flow_get_wdma_info` resolves a forwarding path ending in `DEV_PATH_MTK_WDMA`; `mtk_flow_get_dsa_port` detects MediaTek DSA conduit/port data. `mtk_flow_set_output_device` chooses PSE port, queue, DSA tag, or WDMA metadata. Public APIs are `mtk_flow_offload_cmd`, `mtk_eth_setup_tc`, and `mtk_eth_offload_init`.

## Control Flow
`mtk_flow_offload_cmd` serializes replace, destroy, and stats under `mtk_flow_offload_mutex`. Replace first rejects duplicate cookies. It requires meta, control, and basic dissector keys; NETSYS v2 or newer can select a PPE index based on ingress netdev `mac->ppe_idx`. Address type chooses bridge, IPv4 HNAPT, or IPv6 5T. It parses flower actions in two passes: the first captures Ethernet mangle, redirect device, VLAN push/pop, PPPoE push, and checksum; the second applies IP and port mangles after original tuple setup. It then prepares a FOE entry, fills tuple fields, applies VLAN/PPPoE metadata, resolves output device and WED index, optionally enables WED offload, allocates `mtk_flow_entry`, commits it to the PPE, and inserts it into `eth->flow_table`.

Destroy looks up the cookie, clears the PPE entry, removes it from the flow rhashtable, decrements WED flow state if used, and frees the entry. Stats refresh idle time through `mtk_foe_entry_idle_time`, reports `lastused`, and adds MIB deltas when the flow has a bound hardware hash. TC block setup registers or unregisters flow block callbacks for ingress clsact binders.

## State And Persistence
The persistent software state is `eth->flow_table`, keyed by `f->cookie`, plus the `mtk_flow_entry` linked into PPE software buckets or L2 tables. Each entry records PPE index and WED index for later stats/destroy. WED flow reference state is maintained separately by `mtk_wed_flow_add` and `mtk_wed_flow_remove`. No flow survives driver teardown; hardware state is cleared by PPE lifecycle and destroy paths.

## Dependencies And Integration Points
This file depends on flow dissector, TC flower, DSA, rhashtable, `mtk_eth_soc.h`, and `mtk_wed.h`. It is called from Ethernet netdev TC setup and from WED TC setup. It programs FOE entries through `mtk_ppe.c` APIs and delegates Wi-Fi path information through `dev_fill_forward_path` and WED path data. It uses netdev arrays in `struct mtk_eth` to map redirect devices to PSE ports.

## Risks
Supported flow coverage is deliberately narrow; unsupported actions must reliably return `-EOPNOTSUPP` so software fallback remains correct. Error cleanup is critical: if insertion fails after WED enable or PPE commit, the code clears the entry, frees it, and removes the WED flow. A notable bug risk is reference underflow in WED flow removal if callers mismatch add/remove. Meta ingress selection compares netdev ops in `mtk_flow_is_valid_idev`, which is broad and assumes MediaTek netdevs share ops. IPv6 mangle support is absent; bridge offload rejects mangle and ports. WDMA forwarding depends on external WLAN path data being valid.

## Test Signals
Use `tc flower` add/delete/stats for IPv4 NAT, IPv6 route, pure L2 bridge, VLAN push, PPPoE push, DSA egress, and WED/WLAN redirect. Verify duplicate cookies return `-EEXIST`, unsupported keys/actions fall back, stats update packets/bytes/lastused, WED offload enable/disable callbacks balance, and destroy removes debugfs FOE entries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mediatek/mtk_ppe_offload.c -->
