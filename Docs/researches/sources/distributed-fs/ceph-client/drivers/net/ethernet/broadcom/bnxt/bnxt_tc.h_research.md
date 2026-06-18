# sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnxt/bnxt_tc.h

## Purpose
Defines the in-memory model for bnxt TC flower offload and exposes feature entry points with real implementations under `CONFIG_BNXT_FLOWER_OFFLOAD` and stubs otherwise.

## Important APIs, Types, And Functions
`struct bnxt_tc_l2_key`, `bnxt_tc_l3_key`, and `bnxt_tc_l4_key` represent parsed match keys and masks. `struct bnxt_tc_actions` stores parsed forwarding, drop, VLAN, tunnel, L2 rewrite, and NAT actions. `struct bnxt_tc_flow` combines source FID, keys/masks, tunnel keys, actions, accumulated stats, prior stats, last-used time, and a stats spinlock. `struct bnxt_tc_tunnel_node`, `bnxt_tc_l2_node`, and `bnxt_tc_flow_node` are the rhashtable/list nodes used for sharing firmware handles and tracking TC cookies. Exported functions are `bnxt_tc_setup_flower()`, `bnxt_init_tc()`, `bnxt_shutdown_tc()`, `bnxt_tc_flow_stats_work()`, and `bnxt_tc_flower_enabled()`.

## Control Flow
The header is declarative. Compile-time control flow selects real prototypes and structures only when flower offload is enabled. Without the config, static inline stubs report unsupported setup and no-op init/shutdown/stats behavior, allowing other bnxt code to call TC helpers without preprocessor clutter.

## State And Persistence Behavior
The structures defined here are the persistent in-memory state for offloaded flows. Firmware handles are stored in flow and tunnel nodes; flow stats are maintained as cumulative software counters plus previous snapshots for TC delta reporting. RCU heads on nodes define deferred free semantics.

## Dependencies And Integration Points
The header depends on netdev, rhashtable, list, RCU, spinlock, `struct ip_tunnel_key`, and TC flower offload types. It is consumed by `bnxt_tc.c` and by representor code that forwards VF-rep TC rules into the PF offload engine.

## Risks
Hash key lengths are important: `BNXT_TC_L2_KEY_LEN` hashes only the first 16 bytes of the L2 key, so structure layout changes can affect sharing semantics. Action and flow flag bits must remain synchronized with parser and HWRM allocation code. Stub behavior must match callers' expectations in non-offload builds.

## Test Signals
Build with `CONFIG_BNXT_FLOWER_OFFLOAD=y` and disabled. Runtime signals come from add/delete/stats paths in `bnxt_tc.c`; structural risk is best covered by compile tests and flow cases that share L2/tunnel keys.
