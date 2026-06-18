# sources/distributed-fs/ceph-client/net/bridge/netfilter/nft_meta_bridge.c

## Purpose
Adds bridge-family nftables `meta` expression support for bridge-specific keys, while delegating generic meta keys to the common nft meta implementation.

## Important APIs, Types, And Functions
Important functions are `nft_meta_bridge_get_eval`, `nft_meta_bridge_get_init`, `nft_meta_bridge_set_eval`, `nft_meta_bridge_set_init`, `nft_meta_bridge_set_validate`, `nft_meta_bridge_select_ops`, and helper `nft_meta_get_bridge`. The expression type is `nft_meta_bridge_type`.

## Control Flow
Get expressions return bridge input/output interface names, input PVID, bridge VLAN protocol, and bridge hardware address when the packet device is a bridge port and required VLAN state is enabled; otherwise they break rule evaluation. Set expressions currently support bridge broute by writing `BR_INPUT_SKB_CB(skb)->br_netfilter_broute`. Init selects get or set ops based on destination/source register attributes, and validation restricts broute and input hardware address keys to prerouting.

## State And Persistence Behavior
Get paths read device, bridge, and VLAN state under packet context. Set path mutates only the skb bridge control block. Nft expression configuration is stored in nftables rulesets, not by this module directly.

## Dependencies And Integration Points
Depends on nftables core/meta helpers, bridge private APIs, `br_vlan_enabled`, `br_vlan_get_pvid_rcu`, `br_vlan_get_proto`, bridge port/master relationships, and NF_BR hook validation.

## Risks And Test Signals
Risks include missing bridge-device checks, invalid register lengths, hook validation gaps, and broute flag semantics. Tests should cover all bridge meta keys, absent/non-bridge devices, VLAN disabled behavior, broute set in prerouting, invalid get/set attribute combinations, and generic meta fallback.
