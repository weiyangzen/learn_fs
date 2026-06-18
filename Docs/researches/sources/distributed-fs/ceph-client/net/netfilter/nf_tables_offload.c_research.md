# sources/distributed-fs/ceph-client/net/netfilter/nf_tables_offload.c

## Purpose
`nf_tables_offload.c` translates eligible nftables netdev ingress chains and rules into flow classifier offload operations for NIC or indirect block drivers. It constructs `struct nft_flow_rule` objects from nft expression offload callbacks, binds nftables base chains to tc flow blocks, commits or aborts hardware rule changes during nft transactions, collects rule stats, and unbinds offload state when devices disappear.

## Important APIs, Types, and Functions
Public helpers include `nft_flow_rule_create()`, `nft_flow_rule_destroy()`, `nft_flow_rule_set_addr_type()`, `nft_offload_set_dependency()`, `nft_offload_update_dependency()`, `nft_chain_offload_support()`, `nft_flow_rule_stats()`, `nft_flow_rule_offload_commit()`, `nft_offload_init()`, and `nft_offload_exit()`.

Key internal flows use `struct nft_offload_ctx`, `struct nft_flow_rule`, `struct flow_rule`, `struct flow_cls_offload`, `struct flow_block_offload`, and `struct nft_base_chain::flow_block`. Chain binding is implemented by `nft_block_offload_cmd()`, `nft_indr_block_offload_cmd()`, `nft_chain_offload_cmd()`, `nft_flow_block_chain()`, and `nft_flow_offload_chain()`.

## Control Flow, State, and Persistence
`nft_flow_rule_create()` first counts expressions that produce flow actions, allocates a `flow_rule` with that action count, initializes an offload context, and calls every expression's `ops->offload()` callback. Any expression without offload support rejects the whole rule. VLAN dissector normalization in `nft_flow_rule_transfer_vlan()` rewrites basic/vlan/cvlan key placement so tc flower receives the expected protocol layout.

Chain support is intentionally narrow: hardware offload only accepts base chains with priority in the supported range and hook ops for `NFPROTO_NETDEV` ingress on devices that either expose `ndo_setup_tc` or have an indirect flow block provider. Bind/unbind creates a `flow_block_offload`, calls device or indirect setup, splices callbacks into the base chain, and on unbind sends `FLOW_CLS_DESTROY` for existing rules before freeing callback entries.

Transaction commit scans `nft_net->commit_list` for netdev-family offloaded chain/rule operations. New chains bind blocks, deleted chains unbind, appended new rules issue `FLOW_CLS_REPLACE`, and deleted rules issue `FLOW_CLS_DESTROY`; unsupported replace/non-append rule operations fail. On failure, `nft_flow_rule_offload_abort()` walks already-processed transactions in reverse and restores offload state. Persistent state is the base-chain flow block callback list, driver block callbacks, offloaded rule cookies, action device references, and netdevice notifier registration.

## Dependencies and Integration Points
This file integrates nftables transaction state with tc flower (`TC_SETUP_CLSFLOWER`), tc block setup (`TC_SETUP_BLOCK`), `flow_indr_dev_setup_offload()`, netdevice notifier events, and expression offload callbacks from payload/cmp/bitwise/meta/immediate-style expressions. It serializes indirect device cleanup under the nftables per-net `commit_mutex`.

## Risks and Test Signals
Risks include partial bind rollback across multiple hook devices, direct versus indirect block cleanup lifetime, offloaded redirect/mirred device reference release, transaction abort symmetry, VLAN key translation, and unsupported policy/rule replacement semantics. Tests should cover successful and failing multi-device binds, netdev unregister unbind, indirect block cleanup, append-only rule offload enforcement, stats retrieval, expression offload dependency propagation, and rollback when a later transaction in the commit list fails.
