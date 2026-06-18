<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/flower/offload.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/flower/offload.c

## Purpose
`offload.c` is the main Flower tc offload engine. It validates supported tc flower matches, allocates and compiles NFP flow payloads, sends add/delete/modify control messages, manages synthetic merged flows, validates pre-tunnel rules, handles tc stats, and registers direct and indirect tc block callbacks.

## Important APIs, Types, And Functions
Key exported functions are `nfp_flower_xmit_flow()`, `nfp_flower_calculate_key_layers()`, `nfp_flower_allocate_new()`, `nfp_flower_merge_offloaded_flows()`, `nfp_flower_del_linked_merge_flows()`, `nfp_flower_update_merge_stats()`, `nfp_flower_setup_tc()`, `nfp_flower_indr_setup_tc_cb()`, and `nfp_flower_setup_indr_tc_release()`. Internal add/delete/stats handlers are `nfp_flower_add_offload()`, `nfp_flower_del_offload()`, and `nfp_flower_get_stats()`.

## Control Flow
For `FLOW_CLS_REPLACE`, the path checks CT special cases, rejects unsupported chains or nonzero CT matches outside allowed cases, calculates key layers and size, allocates a payload, compiles match and action, validates pre-tunnel constraints if needed, allocates metadata, inserts into the flow table, then sends either a regular flow add or pre-tunnel programming message. `FLOW_CLS_DESTROY` resolves CT or normal flow state, releases metadata and tunnel endpoint refs, deletes pre-tunnel or normal firmware state when still in hardware, removes merge flows linked to the deleted flow, updates representor counters, removes the flow table entry, and RCU-frees the payload. `FLOW_CLS_STATS` looks up CT or normal flow state, merges synthetic-flow stats into subflows, updates tc stats, and clears the local accumulator.

Flow merge takes two already offloaded subflows, checks that subflow2 only matches fields matched or set by subflow1, composes an action list, links merge/subflow references, allocates metadata and a merge-table key based on parent stats contexts, sends a FLOW_MOD, marks subflow1 out of hardware, and keeps all link state for later deletion or stats distribution.

## State And Persistence
The file mutates `flow_table`, `merge_table`, per-flow action/key/mask allocations, tunnel endpoint refs, pre-tunnel neighbor lists, representor `tc_offload_cnt`, and in-memory stats accumulators. Firmware state is updated through `nfp_ctrl_tx()` via Flower control messages. All access through tc callbacks is serialized by `priv->nfp_fl_lock`; pre-tunnel neighbor linkage uses `predt_lock`; flow-link comments require RTNL for merge link manipulation.

## Dependencies And Integration Points
It depends on tc clsflower/matchall/action APIs, `match.c`, `action.c`, `metadata.c`, `tunnel_conf.c`, `qos_conf.c`, Flower conntrack handlers, NFP representor/port helpers, OVS/internal-port detection, and firmware control-message definitions from `cmsg.h`. Direct representor tc blocks support clsflower and matchall QoS; indirect blocks support clsflower for tunnel/internal/OVS style devices; no-netdev indirect action setup routes to police action offload.

## Risks
Validation is complex and feature-gated; missing a dissector dependency could allow firmware-invalid keys. Merge-flow lifetime is subtle because a merge flow can replace a subflow in hardware while stats and deletes still target subflows. `nfp_flower_xmit_flow()` temporarily shifts length fields from bytes to long words and back, so early returns would corrupt software state if added in the wrong place. Deletion falls through after firmware delete errors to free host state, which can desynchronize host and firmware. Pre-tunnel validation is strict and depends on action compiler setting `pre_tun_rule.dev` correctly.

## Test Signals
Run tc flower replace/destroy/stats on representors, shared blocks, indirect OVS ports, tunnels, CT pre/post flows, and unsupported chain/protocol cases. Exercise merge hints, deletion of either subflow, stats distribution from merged flows, pre-tunnel rule validation with VLAN and MAC variants, firmware xmit allocation failures, and lockdep under concurrent tc updates and stats polling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/flower/offload.c -->
