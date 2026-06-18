# sources/distributed-fs/ceph-client/drivers/net/ethernet/airoha/airoha_ppe.c

## Purpose
`airoha_ppe.c` implements Airoha Packet Processing Engine flow offload. It allocates hardware forwarding-entry memory, initializes PPE register tables, translates tc/netfilter flow rules into FOE entries, commits entries to SRAM/DRAM through MMIO/NPU cooperation, tracks software flow state, exposes stats, and coordinates PPE startup/shutdown with the NPU.

## Important APIs, types, and functions
- `airoha_ppe_init()` allocates `struct airoha_ppe`, coherent FOE memory, optional stats memory, flow hash arrays, check-time arrays, initializes rhashtables, flushes SRAM entries, and creates debugfs.
- `airoha_ppe_deinit()` detaches the NPU under `flow_offload_mutex`, calls firmware deinit, drops references, destroys rhashtables, and removes debugfs.
- `airoha_ppe_setup_tc_block_cb()` gates flow offload until all netdevs are registered, lazy-initializes NPU/PPE offload, and dispatches flow commands.
- `airoha_ppe_flow_offload_replace()`, `destroy()`, and `stats()` implement `FLOW_CLS_REPLACE`, `FLOW_CLS_DESTROY`, and `FLOW_CLS_STATS`.
- `airoha_ppe_foe_entry_prepare()` builds common FOE metadata for bridge, IPv4, and IPv6 flows, including VLAN/PPPoE, DSA, WDMA, PSE port, NBQ, QoS, multicast, and source MAC id handling.
- `airoha_ppe_foe_entry_set_ipv4_tuple()` and `set_ipv6_tuple()` populate hardware tuple fields from dissector keys and mangle actions.
- `airoha_ppe_foe_get_entry_hash()`, `commit_entry()`, `commit_sram_entry()`, and `get_entry()` manage hardware hash calculation and SRAM/DRAM interaction.
- `airoha_ppe_check_skb()` is the packet-path hook that rate-limits checks by hash and lazily commits matching software flows when hardware exposes a candidate PPE hash.
- `airoha_ppe_foe_entry_get_stats()` combines software high-word stats with NPU-mapped low-word counters.

## Control flow
Initialization creates the software/hardware backing state but defers NPU-backed PPE enablement until the first offload request. A replace command validates supported flower keys/actions, derives the offload type, builds a FOE entry, applies mangle data, inserts the software shadow into either the L4 hash bucket or L2 rhashtable, and then inserts the cookie into `eth->flow_table`. Packets later call `airoha_ppe_check_skb()` with a hardware hash; the PPE reads the FOE entry at that hash, compares it to software candidates, commits the prepared entry if matched, or builds L2 subflows from bridge rules. Destroy invalidates hardware state if a hash was committed and removes all related software nodes. Stats read idle time from hardware timestamps and flow counters from the NPU stats mapping.

## State and persistence behavior
State is volatile and split across coherent FOE memory, hardware SRAM/DRAM tables, NPU stat memory, `eth->flow_table`, `ppe->l2_flows`, per-hash `foe_flow` hlist buckets, and `foe_check_time` debounce bytes. The active NPU pointer is RCU-managed in `eth->npu`. `flow_offload_mutex` serializes setup/commands/deinit; `ppe_lock` protects FOE table and flow-list mutation.

## Dependencies and integration points
The file depends on flow dissector/classifier APIs, netfilter flowtable offload via flower commands, DSA, WDMA forward-path metadata, Airoha NPU firmware ops, FE/PPE registers from `airoha_regs.h`, and `airoha_offload` device export. `airoha_ppe_get_dev()` exports the PPE device by `airoha,eth` phandle for external consumers.

## Risks and edge cases
Unsupported flow keys/actions return `-EOPNOTSUPP`; bridge, IPv4 NAT, and IPv6 5-tuple paths have different hardware layouts. Hash collisions are handled by software candidate lists, but stale hardware entries can cause invalidation paths. The code contains a likely important limitation: SRAM flushing without NPU falls back to MMIO one entry at a time. Flow stats are disabled for EN7583 and when `CONFIG_NET_AIROHA_FLOW_STATS` is off. Correctness depends on RCU pointer lifetime, spinlock ordering, memory barriers before hardware commits, and endian/field preparation matching hardware ABI.

## Test signals
Exercise flowtable offload replace/destroy/stats for bridge, IPv4 NAT, IPv6 route, VLAN push/pop, PPPoE push, DSA, and WDMA paths. Validate that offload is rejected before all netdevs are registered, unsupported dissector/action combinations return expected errors, debugfs entries reflect committed state, stats monotonically increase, idle timestamps update, lockdep stays clean, and teardown removes NPU references and debugfs without use-after-free.
