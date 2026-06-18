# sources/distributed-fs/ceph-client/include/net/netfilter/nf_tables_offload.h

Purpose: Defines nftables-to-flow-offload translation structures and helpers for offloading rule matches/actions to flow rules.

Important APIs/types/functions: `nft_offload_reg`, `nft_offload_ctx`, `nft_flow_key`, `nft_flow_match`, and `nft_flow_rule` model dependency tracking, register extraction, dissector keys, masks, and flow actions. APIs include dependency setters, `nft_flow_action_entry_next`, `nft_flow_rule_set_addr_type`, `nft_flow_rule_create/destroy/stats`, `nft_flow_rule_offload_commit`, `nft_chain_offload_support`, and offload init/exit. Macros map nft registers to flow dissector fields and exact masks.

Control flow: Rule translation walks expressions, fills match keys/masks and actions, tracks network/transport dependencies, and commits supported flow rules to devices. Datapath stats can be synchronized back to nft expressions.

State and persistence: Offload context is per-translation; generated `flow_rule` objects live until destroyed or chain updates commit.

Dependencies/integration: Depends on `flow_offload.h`, `nf_tables.h`, flow dissector key layouts, base-chain offload support, and device flow block operations.

Risks/test signals: Validate register-to-field offsets, action count bounds, dependency updates before payload matches, mask initialization, unsupported expression rejection, and stats sync. Test IPv4/IPv6/VLAN/Ethernet matches and rule replacement rollback.
