# Research: subset-b-004587

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/flower/main.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/flower/main.h

## Purpose
`main.h` is the shared Flower app contract for the Netronome NFP driver. It defines the feature bits, flow/mask/stat metadata, tunnel-neighbor state, QoS/meter state, merge-flow links, and exported APIs used by Flower match compilation, action compilation, metadata allocation, tunnel configuration, QoS, LAG, conntrack, and tc setup code.

## Important APIs, Types, And Functions
Key feature flags include `NFP_FL_FEATS_*` for firmware capabilities such as Geneve, QinQ, PPS QoS, meter offload, decap v2, IPv6 tunnel, and tunnel-neighbor LAG, and `NFP_FL_ENABLE_*` for enabled runtime features such as flow merge and LAG. `struct nfp_flower_priv` is the central persistent per-app state: flow and stats rhashtables, mask-id and stats-id allocators, control-message queues, tunnel offload tables, LAG state, indirect block callbacks, QoS and meter tables, merge and conntrack tables, pre-tunnel neighbor state, and `nfp_fl_lock`.

Other important types are `struct nfp_fl_payload` for one offloaded flow payload, `struct nfp_fl_rule_metadata` for firmware message metadata, `struct nfp_fl_payload_link` for merge-flow/sub-flow references, `struct nfp_tun_neigh_v4/v6` and `struct nfp_neigh_entry` for tunnel neighbor programming, `struct nfp_meter_entry` for shared police action meters, and `struct nfp_flower_repr_priv`/`nfp_flower_non_repr_priv` for per-port offload bookkeeping.

The header exports the main integration functions: metadata init/cleanup and lookup, tc setup, merge offload, match/action compilation, tunnel start/stop and route/MAC/IP programming, LAG helpers, QoS setup/stats, indirect tc callback setup, internal-port helpers, and meter-table operations.

## Control Flow
The header itself has no runtime control flow beyond small helpers. `nfp_flower_internal_port_can_offload()` gates internal Open vSwitch ports on flow-merge enablement and rtnl link kind. `nfp_flower_is_merge_flow()` identifies synthetic merge flows by using the payload address as the cookie. `nfp_flower_is_supported_bridge()` currently recognizes OVS masters.

## State And Persistence
All state is kernel-resident and driver-lifetime scoped. `nfp_flower_priv` aggregates mutable state protected by mutexes, spinlocks, RCU, rhashtable internals, IDR/IDA allocators, list heads, and delayed work. Nothing is persisted to disk. Firmware-visible state is reflected by control messages built by implementation files using the structures declared here.

## Dependencies And Integration Points
The header depends on Flower control-message formats from `cmsg.h`, generic NFP netdev state from `nfp_net.h`, Linux tc flower/matchall/action APIs, rhashtable, IDA/IDR, notifier/workqueue primitives, and netdevice bridge/OVS helpers. It is the binding point between tc offload callbacks, firmware control-message encoding, NFP representor ports, tunnel/neighbor offload, conntrack offload, and NFD datapath control RX/TX.

## Risks
Because this header centralizes shared state, field lifetime and locking assumptions are spread across many files. Risks include mismatched feature-gating against firmware capabilities, stale `nfp_fl_payload` references in merge/pre-tunnel lists, incorrect refcount handling for tunnel endpoint or MAC tables, and lock-order bugs between `nfp_fl_lock`, `predt_lock`, QoS locks, and notifier/workqueue paths.

## Test Signals
Useful signals include tc flower add/delete/stats coverage on representors and indirect OVS ports, QinQ/Geneve/IPv6 tunnel feature-gating tests, flow merge add/delete/stats tests, tunnel neighbor update tests with bridge/LAG transitions, QoS/meter police action tests, and teardown tests that verify rhashtables and lists empty without warnings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/flower/main.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/flower/match.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/flower/match.c

## Purpose
`match.c` compiles Linux tc flower `flow_rule` dissector matches into the exact and mask key byte streams consumed by NFP Flower firmware. It serializes metadata, ingress port, Ethernet/MPLS, VLAN/QinQ, IPv4/IPv6, transport ports, TCP/IP extension flags, and VXLAN/Geneve/GRE tunnel keys into `nfp_fl_payload::{unmasked_data,mask_data}`.

## Important APIs, Types, And Functions
The main entry point is `nfp_flower_compile_flow_match()`. Helper compilers include `nfp_flower_compile_meta()`, `nfp_flower_compile_tci()`, `nfp_flower_compile_ext_meta()`, `nfp_flower_compile_port()`, `nfp_flower_compile_mac()`, `nfp_flower_compile_mpls()`, `nfp_flower_compile_tport()`, `nfp_flower_compile_vlan()`, `nfp_flower_compile_ipv4()`, `nfp_flower_compile_ipv6()`, Geneve option handling, and IPv4/IPv6 UDP/GRE tunnel compilers.

## Control Flow
`nfp_flower_compile_flow_match()` obtains the NFP ingress port ID, clears the key/mask buffers, emits fixed metadata/port fields, conditionally emits extended metadata, then walks the layer bits calculated earlier by `offload.c`. For each selected layer it appends the corresponding struct in firmware-defined order. Tunnel matches also record tunnel destination state: IPv4 destinations are refcounted through `nfp_tunnel_add_ipv4_off()`, and IPv6 destinations through `nfp_tunnel_add_ipv6_off()` with a pointer retained in the flow payload. The function finally validates that the compiled key length does not exceed `NFP_FLOWER_KEY_MAX_LW`.

## State And Persistence
Most helpers are pure encoders, but tunnel compilation mutates Flower tunnel endpoint lists through add/refcount helpers and stores the tunnel destination in the flow payload for later deletion. The compiled key and mask are persistent while the flow payload is installed in the driver and firmware.

## Dependencies And Integration Points
The file depends on the Linux flow dissector API, `FIELD_PREP`, NFP cmsg key structs, netdevice-to-port translation, and tunnel endpoint management from `tunnel_conf.c`. It is called after key-layer calculation in `offload.c` and before action compilation and metadata allocation.

## Risks
The byte layout is order-sensitive; a mismatch between `key_layer` calculation and emission order corrupts firmware interpretation. Tunnel endpoint adds happen during match compilation, so later failure paths must release them. Mask handling uses OR-with-previous-mask semantics for some fields, which is correct for layered compilation but risky if a field is compiled twice unexpectedly. MPLS only supports one LSE, tunnel destination must be exact, and key-size overflow is rejected late after buffer population.

## Test Signals
Exercise tc flower rules for L2-only, IPv4/IPv6, TCP flags, MPLS, single and double VLAN, VXLAN, Geneve with/without options, GRE, IPv6 tunnels, wildcard masks, invalid ingress ports, and key-size-limit failures. Failure-path tests should verify IPv4/IPv6 tunnel endpoint references are not leaked when later action or metadata compilation fails.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/flower/match.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/flower/metadata.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/flower/metadata.c

## Purpose
`metadata.c` owns Flower flow identity and lookup metadata: stats context allocation, mask ID allocation/reuse, flow-table hashing, stats updates from firmware, merge/conntrack/neigh rhashtable parameters, metadata initialization, and cleanup.

## Important APIs, Types, And Functions
The public APIs are `nfp_flower_metadata_init()`, `nfp_flower_metadata_cleanup()`, `nfp_compile_flow_metadata()`, `nfp_modify_flow_metadata()`, `__nfp_modify_flow_metadata()`, `nfp_flower_search_fl_table()`, `nfp_flower_get_fl_payload_from_ctx()`, and `nfp_flower_rx_flow_stats()`. Internal types map mask hashes to IDs (`nfp_mask_id_table`) and stats contexts to payloads (`nfp_fl_stats_ctx_to_flow`).

## Control Flow
New flow setup calls `nfp_get_stats_entry()`, inserts a stats-context-to-flow entry, allocates or reuses a mask ID unless the flow is a pre-tunnel rule, stamps a monotonically increasing `flower_version`, writes the mask ID into the compiled exact key, initializes stats, and checks for duplicate `(cookie, ingress_dev)` flow table entries. Flow modification/deletion clears manage-mask intent, increments version, releases mask ID when appropriate, removes stats-context mapping, and returns the stats context ID to the free ring. Firmware stats messages are parsed as repeated `nfp_fl_stats_frame` records and accumulated under `stats_lock`.

## State And Persistence
State is in memory only. Stats IDs use a circ_buf plus an initial unallocated range spread over firmware memory units. Mask IDs use a circ_buf, a hash table keyed by `jhash(mask_data)`, refcounts, and a `NFP_FL_MASK_REUSE_TIME_NS` holdoff before reuse. Flow table keys are tc cookie plus ingress netdev. Cleanup destroys flow, stats, merge, conntrack zone/map, and neighbor tables and frees rings and stats arrays.

## Dependencies And Integration Points
The file uses rhashtable, Jenkins hashes, vmalloc/kvmalloc, Flower conntrack cleanup helpers, and the app-private `nfp_flower_priv`. It is on the critical path for add/delete/stats in `offload.c`, CT handling, merge-flow tracking, and tunnel neighbor table cleanup.

## Risks
`nfp_search_mask_table()` compares only the mask hash, not the mask bytes, so a hash collision would incorrectly share a mask ID. Stats array sizing uses encoded field preparation and assumes firmware-provided counts align with host context ID encoding. Error paths must unwind stats context, mask IDs, and hash inserts in the right order. Cleanup warns and forcibly clears non-empty conntrack lists, indicating teardown expects higher layers to delete flows first.

## Test Signals
Important tests include duplicate tc cookie rejection per ingress device, mask ID refcounting and delayed reuse, stats context exhaustion/reuse, firmware stats accumulation and TC stats drain, pre-tunnel metadata without mask allocation, teardown with empty and deliberately non-empty CT tables, and hash-collision or fault-injection tests for insert/allocation failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/flower/metadata.c -->

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

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/flower/qos_conf.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/flower/qos_conf.c

## Purpose
`qos_conf.c` implements Flower QoS offload for tc matchall police rate limiters on VF representors and shared tc police actions as firmware meters. It sends QoS add/delete/stats control messages and maintains cached delayed hardware stats for both ingress port policers and action meters.

## Important APIs, Types, And Functions
The main exported functions are `nfp_flower_setup_qos_offload()`, `nfp_flower_qos_init()`, `nfp_flower_qos_cleanup()`, `nfp_flower_stats_rlim_reply()`, `nfp_flower_stats_meter_request_all()`, `nfp_act_stats_reply()`, `nfp_setup_tc_act_offload()`, `nfp_init_meter_table()`, `nfp_flower_setup_meter_entry()`, `nfp_flower_search_meter_entry()`, and `nfp_flower_offload_one_police()`.

## Control Flow
Ingress matchall replace validates firmware VF rate-limit support, representor type, non-shared block, VF port type, priority 1, police action count, action semantics, and BPS/PPS support. It sends one or two QoS_MOD messages and starts the delayed stats poller on the first active limiter. Destroy clears the per-representor QoS table, decrements the shared limiter count, cancels work when count reaches zero, and sends QoS_DEL for BPS and optionally PPS. Stats commands return deltas from the cached current/previous values.

Shared police actions are handled through `nfp_setup_tc_act_offload()`. Replace validates police actions, creates/updates a meter table entry keyed by `hw_index`, sends meter QoS_MOD, and starts the same poller. Destroy sends QoS_DEL with the meter flag and removes the table entry. Stats compute pass/dropped deltas from cached meter stats.

## State And Persistence
State lives in `repr_priv->qos_table` for per-port rate limiters and `priv->meter_table` for action meters. `qos_rate_limiters` counts both kinds of active objects and controls the delayed `qos_stats_work`. Per-port stats use `qos_stats_lock`; meter stats and table walking use `meter_stats_lock`. Firmware state is represented by `NFP_FLOWER_CMSG_TYPE_QOS_MOD`, `QOS_DEL`, and `QOS_STATS`.

## Dependencies And Integration Points
The file integrates with tc matchall, tc action offload, NFP representor ports, Flower feature flags `NFP_FL_FEATS_VF_RLIM`, `NFP_FL_FEATS_QOS_PPS`, and `NFP_FL_FEATS_QOS_METER`, and firmware police message formats. `offload.c` calls this from direct block callbacks and indirect no-netdev action setup.

## Risks
`qos_rate_limiters` is shared between per-port rate limiters and meters, so imbalanced add/delete paths can leave stats work running or canceled prematurely. Some install loops continue after unsupported rate entries and may report success if at least one action was added. Destroy assumes the firmware can safely clear unconfigured BPS/PPS entries. Stats are delayed and delta-based, so counter wrap or firmware reset can produce zeroed deltas due to defensive comparisons in meter stats but not in per-port stats.

## Test Signals
Test VF-only matchall replace/destroy/stats, non-VF rejection, shared block rejection, priority rejection, BPS and PPS combinations with/without firmware PPS support, police conform/exceed action validation, shared action add/delete/stats, meter-table duplicate add, delayed stats polling start/cancel behavior, and firmware stats replies for ingress and meter messages.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/flower/qos_conf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/flower/tunnel_conf.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/flower/tunnel_conf.c

## Purpose
`tunnel_conf.c` manages Flower tunnel offload control-plane state: active tunnel keep-alives, route and neighbor resolution requested by firmware, tunnel endpoint IP lists, offloaded MAC address indexes, pre-tunnel rule programming, and netevent-driven neighbor updates.

## Important APIs, Types, And Functions
Public APIs include `nfp_tunnel_config_start()`, `nfp_tunnel_config_stop()`, `nfp_tunnel_keep_alive()`, `nfp_tunnel_keep_alive_v6()`, `nfp_tunnel_request_route_v4()`, `nfp_tunnel_request_route_v6()`, `nfp_tunnel_add_ipv4_off()`, `nfp_tunnel_del_ipv4_off()`, `nfp_tunnel_add_ipv6_off()`, `nfp_tunnel_put_ipv6_off()`, `nfp_tunnel_mac_event_handler()`, `nfp_flower_xmit_pre_tun_flow()`, `nfp_flower_xmit_pre_tun_del_flow()`, and pre-tunnel neighbor link helpers.

## Control Flow
Keep-alive handlers validate message length/count, resolve egress ports to netdevs, look up IPv4/IPv6 neighbors, and refresh neighbor timestamps. Route request handlers perform namespace-local route lookups based on ingress port, find the neighbor, and force-write the neighbor to firmware. Netevent notifications allocate work items, hold the neighbor, and on a high-priority workqueue populate flowi source/destination data and call `nfp_tun_write_neigh()`.

`nfp_tun_write_neigh()` is the central neighbor state machine. It creates a neighbor table entry and sends it when a valid neighbor is first seen, sends a zero/delete-style payload and removes the table entry when invalid, or refreshes MAC data on override/MAC change. It also links neighbor entries to decap pre-tunnel rules by matching local/remote MACs and sets host context/VLAN extension fields. MAC offload tracks shared MAC addresses in an rhashtable, chooses physical-port or global IDA-backed indexes, adjusts bridge/pre-tunnel bits, and sends add/delete/mod firmware messages on netdev up/down/address/upper changes.

## State And Persistence
State includes `tun.offloaded_macs`, IPv4 and IPv6 endpoint lists with refcounts, `mac_off_ids`, `neigh_table`, `predt_list` links, per-representor/non-representor MAC offload flags, and `pre_tun_rule_cnt`. Firmware state is sent through tunnel control messages for neighbor, endpoint IP, MAC, and pre-tunnel rule types. All state is in memory and should be drained by flow deletion and tunnel config stop.

## Dependencies And Integration Points
The file depends on ARP/ND neighbor tables, IPv4/IPv6 route lookup, netevent notifier, OVS bridge recognition, NFP representor and non-representor helpers, LAG metadata, Flower feature flags for decap v2 and tunnel-neighbor LAG, and match/offload code that stores tunnel endpoint refs and pre-tunnel metadata.

## Risks
Several paths run from notifier/workqueue context and use `GFP_ATOMIC` under `predt_lock`; allocation or firmware-send failures can leave host and firmware state divergent. MAC index transitions for bridge/shared/repr cases are subtle, especially when reverting global IDs back to physical-port IDs. `nfp_tunnel_request_route_v4/v6()` call `dev_put(netdev)` on failure labels even when `netdev` lookup failed, which is a fragile pattern to audit. Stop frees IPv4 list entries and destroys the IPv6 lock but does not explicitly walk/free IPv6 endpoint entries here, relying on flow reference cleanup before stop.

## Test Signals
Test IPv4/IPv6 route requests, keep-alive length/count validation, neighbor valid/invalid/MAC-change events, bridge upper link/unlink transitions, duplicate/shared MAC refcounts, LAG egress neighbor metadata, tunnel endpoint list limit handling, pre-tunnel rule count limit, decap v2 neighbor/pre-tunnel linking, and module/device teardown under outstanding neighbor work.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/flower/tunnel_conf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/nfd3/dp.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/nfd3/dp.c

## Purpose
`dp.c` implements the NFD3 datapath for normal packet TX/RX, XDP TX from RX buffers, metadata parsing, checksum/TSO/VLAN/TLS/IPsec metadata handling, NAPI polling, and control vNIC TX/RX.

## Important APIs, Types, And Functions
The key public functions are `nfp_nfd3_tx()`, `nfp_nfd3_tx_complete()`, `nfp_nfd3_rx_ring_fill_freelist()`, `nfp_nfd3_rx_csum()`, `nfp_nfd3_parse_meta()`, `nfp_nfd3_poll()`, `nfp_nfd3_ctrl_tx_one()`, and `nfp_nfd3_ctrl_poll()`. Important internal helpers include TX queue stop/wake predicates, `nfp_nfd3_tx_tso()`, `nfp_nfd3_tx_csum()`, `nfp_nfd3_prep_tx_meta()`, RX buffer allocation/give/drop, `nfp_nfd3_tx_xdp_buf()`, normal RX, XDP completion, and control RX validation.

## Control Flow
TX checks ring space, handles TLS transmit preparation, prepends metadata for port mux/TLS/VLAN/IPsec, DMA maps the head and fragments, fills NFD3 descriptors, sets TSO/checksum/IPsec/VLAN flags, advances ring pointers, stops the netdev queue if needed, and flushes write pointers according to xmit-more. TX completion reads the hardware completion pointer, unmaps head/fragments, consumes SKBs on the last descriptor, updates stats, completes netdev queue bytes, and wakes queues with memory-barrier protection.

RX polls descriptors until budget or no DD bit. It computes metadata and packet offsets, syncs DMA to CPU, parses descriptor or chained metadata, runs XDP when allowed, handles control-port packets, maps representor port IDs, builds SKBs, allocates replacement buffers before giving the old buffer to the stack, applies checksum/VLAN/TLS/IPsec metadata, and delivers via GRO or egress redirect. `nfp_nfd3_poll()` combines TX completion, RX, NAPI completion/IRQ unmask, and adaptive moderation samples.

Control path TX queues SKBs when full, optionally prepends control metadata, maps one descriptor, and flushes immediately. Control poll drains TX completions and queued control TX under a spinlock, then processes control RX up to a fixed budget and reschedules on overflow.

## State And Persistence
State is ring-resident: software TX/RX buffers, DMA addresses, descriptor rings, `wr_p`, `rd_p`, `qcp_rd_p`, `wr_ptr_add`, queue stats, and NAPI/tasklet state. Metadata is transient per packet. No disk persistence exists; hardware state is synchronized through queue controller pointers and DMA-visible descriptors.

## Dependencies And Integration Points
The file depends on NFP net datapath structs, NFP app control RX, representor lookup/stats, XDP/BPF APIs, TLS device offload, IPsec offload, DMA mapping APIs, netdev queue APIs, NAPI/GRO, DIM adaptive coalescing, and AF_XDP helpers for XSK-enabled RX rings.

## Risks
Descriptor ownership depends on memory barriers and pointer arithmetic; off-by-one errors can corrupt rings. TX error unwind must unmap exactly the descriptors already mapped. Metadata prepend changes skb offsets and must remain consistent with TSO/checksum offsets. RX allocates replacement buffers after building the skb; failures must preserve or correctly free the original page. Control RX metadata validation differs depending on app metadata support. XDP and representor/control-port paths bypass parts of normal RX and need dedicated coverage.

## Test Signals
Exercise TX with linear, fragmented, TSO, encapsulated checksum, VLAN v1/v2 metadata, TLS, and IPsec packets; TX_BUSY and queue wake paths; RX with descriptor RSS and chained metadata, control port packets, representor redirects, XDP PASS/TX/DROP/ABORTED, replacement-buffer allocation failure, checksum/VLAN/TLS/IPsec metadata, and NAPI completion/IRQ unmask behavior. Ring corruption warnings and DMA debug are strong regression signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/nfd3/dp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/nfd3/ipsec.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/nfd3/ipsec.c

## Purpose
`ipsec.c` adds NFD3 TX descriptor checksum flags for packets using XFRM/IPsec hardware offload when the offload device advertises ESP TX checksum support.

## Important APIs, Types, And Functions
The only function is `nfp_nfd3_ipsec_tx(struct nfp_nfd3_tx_desc *txd, struct sk_buff *skb)`. It reads `xfrm_input_state()`, `xfrm_offload()`, and the skb IP header, then sets `NFD3_DESC_TX_CSUM`, optional `NFD3_DESC_TX_IP4_CSUM`, and TCP/UDP checksum flags.

## Control Flow
The function first checks that the XFRM state has an offload device with `NETIF_F_HW_ESP_TX_CSUM`. It marks checksum offload, adds IPv4 checksum when the outer header is IPv4, chooses L4 protocol from `xo->proto` in transport mode or `xo->inner_ipproto` in tunnel mode, and sets either UDP or TCP checksum flags. Unsupported modes or protocols leave only the generic checksum/IP flags already set.

## State And Persistence
There is no persistent state. It mutates only the in-flight NFD3 TX descriptor for one skb.

## Dependencies And Integration Points
This file is compiled only when `CONFIG_NFP_NET_IPSEC` enables the real prototype in `nfd3.h`; otherwise an inline no-op is used. It is called from `nfp_nfd3_tx()` after IPsec metadata has been prepared and instead of the generic checksum helper.

## Risks
The function assumes XFRM state/offload pointers are valid because the caller checked `xfrm_offload(skb)` and IPsec preparation succeeded. Unsupported protocols silently skip TCP/UDP flagging. Header interpretation uses `ip_hdr(skb)`, so callers must ensure skb network headers still point at the expected outer header after metadata prepend.

## Test Signals
Test ESP TX checksum with IPv4 and IPv6, transport and tunnel modes, TCP and UDP inner protocols, unsupported XFRM modes, offload devices without `NETIF_F_HW_ESP_TX_CSUM`, and interaction with the metadata-prepend path in `nfp_nfd3_tx()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/nfd3/ipsec.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/nfd3/nfd3.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/nfd3/nfd3.h

## Purpose
`nfd3.h` defines the NFD3 host TX descriptor layout, software TX buffer descriptor, descriptor flag constants, and public function prototypes used by the NFD3 datapath implementation.

## Important APIs, Types, And Functions
`struct nfp_nfd3_tx_desc` is the packed 16-byte hardware TX descriptor with DMA address, length, packet offset/EOP, MSS, LSO header length, flags, L3/L4 offsets or VLAN tag, and total data length. `struct nfp_nfd3_tx_buf` tracks the software owner for a descriptor: skb, page fragment, or AF_XDP buffer; DMA address; fragment index or XSK reuse state; packet count; and real byte length. The header declares NFD3 TX/RX, NAPI, control, freelist, AF_XDP, metadata parse, and optional IPsec helpers.

## Control Flow
No runtime control flow exists except the `CONFIG_NFP_NET_IPSEC` conditional: without IPsec support `nfp_nfd3_ipsec_tx()` is an inline no-op; with support it is implemented in `ipsec.c`.

## State And Persistence
The structures define per-descriptor transient ring state. Their fields are persisted only while descriptors are owned by the driver or hardware and are reset by ring cleanup paths.

## Dependencies And Integration Points
The header is included by `dp.c`, `rings.c`, `xsk.c`, and `ipsec.c`. It depends on NFP net datapath types declared elsewhere and on Linux bit macros for descriptor flags.

## Risks
Descriptor field packing is ABI with firmware; any layout or endian change breaks TX. `offset_eop` combines packet offset with EOP in one byte, so metadata prepend size must fit the mask. The union in `nfp_nfd3_tx_buf` is context-sensitive and relies on ring type and `is_xsk_tx`/`fidx` discipline.

## Test Signals
Compile coverage with and without `CONFIG_NFP_NET_IPSEC`, descriptor dump validation through `rings.c`, TX path tests for checksum/TSO/VLAN/IPsec flags, and AF_XDP completion tests that distinguish XSK TX completions from RX-buffer XDP_TX reuse.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/nfd3/nfd3.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/nfd3/rings.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/nfd3/rings.c

## Purpose
`rings.c` allocates, frees, resets, and debugs NFD3 TX rings, including special handling for XDP/AF_XDP rings, and publishes the NFD3 datapath operations table.

## Important APIs, Types, And Functions
Important functions are `nfp_nfd3_tx_ring_alloc()`, `nfp_nfd3_tx_ring_free()`, `nfp_nfd3_tx_ring_reset()`, `nfp_nfd3_tx_ring_bufs_alloc()`, `nfp_nfd3_tx_ring_bufs_free()`, `nfp_nfd3_print_tx_descs()`, and the `const struct nfp_dp_ops nfp_nfd3_ops` table. `NFP_NFD3_CFG_CTRL_SUPPORTED` lists firmware control bits supported by this datapath version.

## Control Flow
Allocation sets the descriptor count from `dp->txd_cnt`, allocates coherent descriptor memory, allocates zeroed software txbufs, and configures XPS for normal netdev TX queues. Reset walks outstanding normal TX descriptors, unmaps head/fragments, frees SKBs at the last fragment, and resets pointers. For XDP rings, reset delegates to AF_XDP buffer completion/free handling. XDP ring buffer allocation preallocates page-backed RX-style buffers for XDP_TX reuse and unwinds on failure. Debug printing dumps all descriptor words, associated skb/xdp pointers, DMA address, and host/device read/write markers.

## State And Persistence
The file owns ring memory lifetimes and pointer reset state. `txds` are coherent DMA memory, `txbufs` are kernel memory, XDP ring buffers are DMA-mapped pages, and `nfp_nfd3_ops` is static driver configuration. State persists for the netdev datapath lifetime, not across reload.

## Dependencies And Integration Points
It depends on `nfd3.h`, NFP net datapath ring structs, DMA allocation APIs, AF_XDP helpers, seq_file debug output, netdev XPS, and the core NFP datapath registration that selects `nfp_nfd3_ops`.

## Risks
Reset assumes non-XDP descriptors with non-null SKBs while `rd_p != wr_p`; corrupted or partially initialized rings can fault. `nfp_nfd3_tx_ring_bufs_free()` returns on the first empty XDP buffer, so partial allocation order must remain strictly sequential. The ops `cap_mask` advertises many offloads; unsupported firmware/hardware combinations must be filtered elsewhere.

## Test Signals
Test ring allocation failure injection, reset idempotence with empty/full/gather rings, XDP ring buffer partial allocation unwind, AF_XDP completion cleanup, descriptor debug output, XPS assignment, and datapath capability negotiation using `nfp_nfd3_ops`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/nfd3/rings.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/nfd3/xsk.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/nfd3/xsk.c

## Purpose
`xsk.c` implements the NFD3 AF_XDP polling path. It receives packets into XSK buffers, parses NFP metadata, runs XDP programs, converts selected packets to SKBs, handles XDP_TX and XDP_REDIRECT, transmits user-space XSK TX descriptors, and completes XDP/XSK TX buffers.

## Important APIs, Types, And Functions
The public functions are `nfp_nfd3_xsk_poll()` and `nfp_nfd3_xsk_tx_free()`. Internal helpers include `nfp_nfd3_xsk_tx_xdp()`, `nfp_nfd3_xsk_rx_skb()`, `nfp_nfd3_xsk_rx()`, `nfp_nfd3_xsk_complete()`, and `nfp_nfd3_xsk_tx()`.

## Control Flow
`nfp_nfd3_xsk_rx()` polls RX descriptors, detects buffer starvation, validates metadata length, updates stats, adjusts XDP buffer pointers for dynamic metadata, parses chained metadata, routes representor/control-port packets to SKB/control paths before BPF, runs the XDP program for host packets, and handles PASS/TX/REDIRECT/DROP/ABORTED. PASS allocates an skb and copies data from the XSK buffer, then frees the XSK RX buffer. XDP_TX builds an NFD3 TX descriptor using the RX XDP buffer and marks it as `is_xsk_tx` so completion frees it. REDIRECT calls `xdp_do_redirect()` and flushes at the end.

`nfp_nfd3_xsk_complete()` reads TX completion pointers, updates stats, frees RX-buffer-backed XDP_TX buffers, and reports user-space TX completions for descriptors not reused from RX. `nfp_nfd3_xsk_tx()` batches `xsk_tx_peek_desc()` descriptors while ring space is available, syncs DMA for device, fills descriptors, releases the XSK producer batch, and writes the hardware TX pointer with a barrier.

## State And Persistence
State lives in RX `xsk_rxbufs`, XDP/TX ring `txbufs`, XSK pool producer/consumer rings, TX descriptor pointers, and per-vector stats. Buffers are transferred among RX pool ownership, XDP program ownership, TX descriptor ownership, and userspace completion ownership.

## Dependencies And Integration Points
The file integrates with NFP metadata parsing/checksum/VLAN helpers from `dp.c`, NFP app representor/control dispatch, AF_XDP pool APIs, XDP redirect APIs, NAPI, NFD3 descriptor format, and XSK setup/wakeup support in `nfp_net_xsk.c`.

## Risks
Ownership is the main risk: XDP_TX buffers must be unstashed and freed exactly once on completion, while normal XSK TX descriptors must be completed back to userspace. The path supports only dynamic metadata layout. SKB conversion copies packet data, so it is slower than zero-copy and can fail under memory pressure. The NAPI completion uses `skbs` rather than all polled packets for `napi_complete_done()`, which is intentional but easy to misread when changing budgeting.

## Test Signals
Test AF_XDP RX with XDP PASS/TX/REDIRECT/DROP/ABORTED, metadata-present representor and control-port packets, RX buffer starvation, invalid metadata, XSK userspace TX batching, TX completion accounting with reused and non-reused buffers, xdp_do_flush behavior, and NAPI budget interactions with normal TX completion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/nfd3/xsk.c -->
