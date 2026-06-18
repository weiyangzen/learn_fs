# subset-b-004400

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb4/cxgb4_mps.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb4/cxgb4_mps.c

Purpose: wraps firmware MPS MAC filter allocation/free/update with an adapter-local reference list so shared MAC TCAM entries are not released while another user still references the same hardware index.

Important APIs/functions: `cxgb4_alloc_mac_filt`, `cxgb4_free_mac_filt`, `cxgb4_update_mac_filt`, `cxgb4_init_mps_ref_entries`, and `cxgb4_free_mps_ref_entries`; internal helpers `cxgb4_mps_ref_inc` and `cxgb4_mps_ref_dec_by_mac` manage `struct mps_entries_ref` records under `adap->mps_ref_lock`.

Control flow: allocation delegates to `t4_alloc_mac_filt`, then records every returned non-`0xffff` index; on local ref allocation failure it frees the just-allocated filters. Freeing decrements by MAC and only calls `t4_free_mac_filt` when the reference count reaches zero. Updating calls `cxgb4_change_mac` and then adds a reference for the returned TCAM index.

State and persistence: state is in the in-memory `adap->mps_ref` list with `refcount_t` counts, address, mask, and MPS index. It is initialized during adapter setup and torn down during driver cleanup; hardware state persists until explicit firmware filter frees.

Dependencies/integration: depends on `cxgb4.h`, Ethernet address helpers, Chelsio firmware helpers `t4_alloc_mac_filt`/`t4_free_mac_filt`/`cxgb4_change_mac`, and adapter lifecycle code in `cxgb4_main.c`.

Risks: `cxgb4_update_mac_filt` increments the reference list but does not roll back on later caller failure. The dec-by-MAC path ignores `-EBUSY` and only frees hardware on zero ref, so callers must interpret the returned freed-count contract carefully. Locking uses `GFP_ATOMIC` under a bottom-half spinlock.

Test signals: useful tests include duplicate allocation/free sequencing for the same MAC, update and teardown paths, ENOMEM injection after firmware allocation, and adapter remove with non-empty `mps_ref`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb4/cxgb4_mps.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb4/cxgb4_ptp.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb4/cxgb4_ptp.c

Purpose: implements Chelsio T5/T6 Precision Time Protocol support: packet classification for timestamping, firmware commands for RX/TX timestamp modes, and PHC operations registered with Linux `ptp_clock`.

Important APIs/functions: exports `cxgb4_ptp_init`, `cxgb4_ptp_stop`, `cxgb4_ptp_is_ptp_tx`, `cxgb4_ptp_is_ptp_rx`, `is_ptp_enabled`, `cxgb4_ptp_read_hwstamp`, `cxgb4_ptprx_timestamping`, `cxgb4_ptp_txtype`, and `cxgb4_ptp_redirect_rx_packet`; PHC callbacks include `cxgb4_ptp_adjfine`, `cxgb4_ptp_adjtime`, `cxgb4_ptp_gettime`, and `cxgb4_ptp_settime`.

Control flow: TX timestamp eligibility checks skb hardware timestamp flags and UDP/IPv4 PTP event-port packets. RX/TX mode functions build `FW_PTP_CMD` mailbox commands. PHC registration copies `cxgb4_ptp_clock_info`, initializes firmware timer state, sets PHC time to wall clock, and unregisters if settime fails. TX timestamp completion reads MAC timestamp registers, stamps `adapter->ptp_tx_skb`, frees it, and clears the pointer under `ptp_lock`.

State and persistence: adapter state includes `ptp_clock`, `ptp_clock_info`, `ptp_tx_skb`, and `ptp_lock`; hardware clock state is in MAC/PTP registers and firmware PTP timer settings. State is runtime-only and removed by `cxgb4_ptp_stop`.

Dependencies/integration: uses Linux PTP clock, skb timestamp, UDP/IP header, and net timestamp APIs plus Chelsio `t4_wr_mbox` and `t4_read_reg`. `cxgb4_main.c` initializes it for devices with PTP support.

Risks: `cxgb4_ptp_is_ptp_rx` manually offsets from skb data and assumes an Ethernet + IPv4 layout. `cxgb4_ptp_read_hwstamp` assumes `adapter->ptp_tx_skb` is valid before lock clearing. Large time adjustments use firmware `ADJ_TIME`, small ones use `ADJ_FTIME`, so edge cases around the 10 ms threshold need coverage.

Test signals: exercise `ethtool -T`, `phc2sys`/`ptp4l`, TX and RX hardware timestamp requests, negative and positive adjtime/adjfine operations, stop during pending TX timestamp, and firmware command failure injection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb4/cxgb4_ptp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb4/cxgb4_ptp.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb4/cxgb4_ptp.h

Purpose: declares the cxgb4 PTP interface and small skb timestamp helpers shared by transmit, receive, and adapter lifecycle code.

Important APIs/types: constants `MAX_PTP_FREQ_ADJ`, `PTP_CLOCK_MAX_ADJTIME`, `PTP_MIN_LENGTH`, `PTP_IN_TRANSMIT_PACKET_MAXNUM`, and `PTP_EVENT_PORT`; enum `ptp_rx_filter_mode`; inline helpers `cxgb4_xmit_with_hwtstamp` and `cxgb4_xmit_hwtstamp_pending`; prototypes for PTP initialization, stop, packet classification, timestamp configuration, and hardware timestamp readout.

Control flow/state: the header has no owning control flow. Callers use the inline helpers to test/set `skb_shinfo(skb)->tx_flags` before the implementation in `cxgb4_ptp.c` stores pending TX skbs and programs firmware.

Dependencies/integration: relies on `struct sk_buff`, `struct adapter`, `struct net_device`, and `struct port_info` definitions from surrounding cxgb4 headers. It is included by main driver paths that configure hwtstamp and TX paths that mark packets in progress.

Risks: helper use assumes skb shared info is valid and that only appropriate packets get `SKBTX_IN_PROGRESS`. Constants constrain packet recognition to IPv4 UDP PTP event packets of a bounded size.

Test signals: compile coverage with PTP enabled/disabled, timestamp flag propagation in TX tests, and hwtstamp ioctl paths selecting `PTP_TS_NONE`, L2, L4, or combined modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb4/cxgb4_ptp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb4/cxgb4_tc_flower.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb4/cxgb4_tc_flower.c

Purpose: implements TC flower offload by validating flower matches/actions, translating them into Chelsio `ch_filter_specification` records, creating/deleting hardware filters, and reporting hardware counters.

Important APIs/functions: `cxgb4_tc_flower_replace`, `cxgb4_tc_flower_destroy`, `cxgb4_tc_flower_stats`, `cxgb4_flow_rule_replace`, `cxgb4_flow_rule_destroy`, `cxgb4_validate_flow_actions`, `cxgb4_process_flow_actions`, `cxgb4_init_tc_flower`, and `cxgb4_cleanup_tc_flower`. Internal helpers cover match parsing, pedit/NAT mode translation, rhashtable lookup, hash-priority tracking, and periodic stats polling.

Control flow: replace validates actions and match keys, parses basic/IP/ports/VLAN/VNI/TOS fields, applies actions such as drop/pass/redirect/VLAN/pedit/queue, selects TCAM versus hash filter placement, waits for asynchronous filter set completion, then inserts the entry keyed by TC cookie. Destroy removes the rhashtable entry, deletes the hardware filter, updates hash-priority tracking, and RCU-frees the entry. Stats read filter counters and update TC stats deltas.

State and persistence: per-adapter `flower_tbl` stores `ch_tc_flower_entry` objects, with spinlock-protected stats. `flower_stats_timer` and `flower_stats_work` periodically refresh `last_used`. Hardware filter state persists until explicit delete or cleanup.

Dependencies/integration: depends on Linux flow dissector/action APIs, rhashtable/RCU/timers/workqueues, `cxgb4_filter` allocation and counter APIs, and shared `tid_info` priority bookkeeping.

Risks: only selected match keys/actions are supported, and pedit is valid only with egress redirect. NAT mode support is chip-specific. The periodic stats worker walks the table while rules can be removed, so RCU/rhashtable lifetime rules are important. Filter creation waits up to 10 seconds and must handle firmware timeout cleanly.

Test signals: TC flower add/delete/stats for IPv4/IPv6, VLAN, VNI, queue steering, redirect, pedit combinations on T5 and T6, hash versus LETCAM placement, timeout/error injection from `__cxgb4_set_filter`, and cleanup while the stats timer is active.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb4/cxgb4_tc_flower.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb4/cxgb4_tc_flower.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb4/cxgb4_tc_flower.h

Purpose: defines the data structures and public interface for cxgb4 TC flower and generic flow-rule offload.

Important APIs/types: `struct ch_tc_flower_stats`, `struct ch_tc_flower_entry`, pedit field identifiers and offsets, `enum cxgb4_action_natmode_flags`, `struct cxgb4_natmode_config`, and prototypes for flow action processing/validation, TC flower replace/destroy/stats, lower-level flow rule replace/destroy, and init/cleanup.

Control flow/state: the header encodes the shape of per-rule persistent state: hardware filter spec, stats, cookie key, rhashtable node, RCU head, stats lock, and filter id. Pedit macros map TC mangle offsets into `struct ch_filter_specification` fields.

Dependencies/integration: includes `<net/pkt_cls.h>` and requires `struct ch_filter_specification` from cxgb4 filter definitions. It is shared by flower code and matchall ingress code, which reuses flow action validation and processing.

Risks: pedit offsets and sizes must stay synchronized with hardware filter-spec layout. Adding actions or fields requires updating both validation and processing paths or invalid offloads may be accepted.

Test signals: build tests after filter-spec layout changes, TC flower pedit/NAT regression tests, and matchall ingress tests that rely on the shared action parser.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb4/cxgb4_tc_flower.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb4/cxgb4_tc_matchall.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb4/cxgb4_tc_matchall.c

Purpose: offloads TC matchall rules for cxgb4, supporting egress policing through scheduler classes and ingress mirror/redirect/filter actions through hardware filters.

Important APIs/functions: `cxgb4_tc_matchall_replace`, `cxgb4_tc_matchall_destroy`, `cxgb4_tc_matchall_stats`, `cxgb4_init_tc_matchall`, and `cxgb4_cleanup_tc_matchall`; internal helpers validate policers, allocate/free scheduler traffic classes, bind/unbind queues, allocate mirror VI state, and add/delete per-family ingress filters.

Control flow: egress replace validates a single police action, link speed limits, non-shared blocks, and queue class conflicts, then allocates a channel rate-limit scheduler class and binds every Ethernet TX queue. Ingress replace validates shared flow actions, optionally allocates a mirror VI, installs IPv4 and IPv6 matchall filters, and marks state enabled. Destroy checks cookies before freeing either scheduler state or ingress filters. Stats aggregate counters from all ingress filter types.

State and persistence: per-port state lives in `adap->tc_matchall->port_matchall[port]`, split into egress class/cookie/state and ingress filter ids/specs/mirror/counters. Hardware state includes scheduler classes, queue bindings, mirror VI allocation, and filter entries.

Dependencies/integration: uses shared scheduler APIs from `sched.c`, filter APIs from `cxgb4_uld.h`/`cxgb4_filter`, flow action validation from `cxgb4_tc_flower.c`, and TC classifier callbacks from `cxgb4_main.c`.

Risks: only one ingress and one egress matchall can be active per port. Cleanup calls hardware delete/free routines and may encounter partial failures. Egress policing uses bytes-per-second to Kbps conversion and must respect link speed. Shared TC blocks are rejected.

Test signals: TC matchall ingress mirror/drop/redirect, egress police at/beyond link rate, duplicate rule rejection, cookie mismatch destroy, shared-block rejection, queue bind conflict with mqprio/scheduler users, and driver removal with active offloads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb4/cxgb4_tc_matchall.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb4/cxgb4_tc_matchall.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb4/cxgb4_tc_matchall.h

Purpose: declares per-port matchall offload state and the cxgb4 TC matchall operations.

Important APIs/types: `enum cxgb4_matchall_state`, `struct cxgb4_matchall_egress_entry`, `struct cxgb4_matchall_ingress_entry`, `struct cxgb4_tc_port_matchall`, `struct cxgb4_tc_matchall`, and prototypes for replace/destroy/stats/init/cleanup.

Control flow/state: the header captures matchall persistence: egress stores hardware scheduler class and cookie; ingress stores filter TIDs and specs for `CXGB4_FILTER_TYPE_MAX`, mirror VI id, byte/packet counters, and `last_used` timestamp.

Dependencies/integration: includes `<net/pkt_cls.h>` and depends on filter specification types from cxgb4 headers. It is used by TC setup dispatch in `cxgb4_main.c` and by cleanup during adapter teardown.

Risks: structure indexes are per physical port, so callers must use the same port id for allocation and teardown. Counter fields are not individually locked here; access discipline is implemented in the `.c` file.

Test signals: compile coverage for classifier callbacks, per-port state allocation/free, and active ingress/egress offload cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb4/cxgb4_tc_matchall.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb4/cxgb4_tc_mqprio.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb4/cxgb4_tc_mqprio.c

Purpose: implements TC mqprio full hardware offload for cxgb4 by allocating scheduler classes, ETHOFLD hardware queues, ETHOFLD software queues, and EOTID-backed flow contexts per traffic class.

Important APIs/functions: `cxgb4_setup_tc_mqprio`, `cxgb4_mqprio_stop_offload`, `cxgb4_init_tc_mqprio`, and `cxgb4_cleanup_tc_mqprio`; internal helpers validate mqprio settings, allocate/free ETHOFLD resources, create/free scheduler classes, initialize/free software queues, and bind/unbind flow contexts.

Control flow: setup validates full TC hardware offload, channel mode, bandwidth shaper, non-overlapping queue ranges, rate totals, and EOTID capacity. It stops queues/carrier if the interface is running, disables existing offload, allocates scheduler classes, creates ETHOFLD queues/EOTIDs, binds flow contexts, updates netdev TC queue maps, and restores carrier. Clear requests disable existing offload only.

State and persistence: adapter-wide `tc_mqprio` holds a refcount and mutex; per-port state stores current mqprio parameters, `sge_eosw_txq` array, hardware scheduler class map, and active/disabled state. Hardware state includes RX/TX ETHOFLD queues, IRQ/MSI-X allocation, scheduler classes, and flowc bindings.

Dependencies/integration: depends on Linux mqprio offload API, netdev TC queue APIs, cxgb4 SGE allocation/free helpers, EOTID helpers in `cxgb4_uld.h`, scheduler APIs in `sched.c`, and ETHOFLD completion handlers.

Risks: setup is invasive: queue counts and carrier state change while resources are rebuilt. Error unwinds must unbind flow contexts, free EOTIDs, kill tasklets, release MSI-X indices, and reset netdev TC state. `cxgb4_get_free_eotid`/bitmap updates are inline and need external serialization from the mqprio mutex.

Test signals: mqprio enable/disable while interface is up and down, overlapping queue rejection, rate sum rejection, EOTID exhaustion, IRQ allocation failure unwind, flowc completion timeout, device shutdown path that skips waits, and concurrent per-port mqprio operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb4/cxgb4_tc_mqprio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb4/cxgb4_tc_mqprio.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb4/cxgb4_tc_mqprio.h

Purpose: defines mqprio offload constants, per-port state, adapter-level state, and public mqprio lifecycle functions for cxgb4.

Important APIs/types: queue descriptor defaults for ETHOFLD software/hardware queues, RX queue interrupt defaults, `CXGB4_FLOWC_WAIT_TIMEOUT`, `enum cxgb4_mqprio_state`, `struct cxgb4_tc_port_mqprio`, `struct cxgb4_tc_mqprio`, and prototypes for setup, stop, init, and cleanup.

Control flow/state: the structures define the persistent mqprio state used by `cxgb4_tc_mqprio.c`: per-port active flag, saved `tc_mqprio_qopt_offload`, software TX queue array, TC-to-hardware-class map, plus adapter-wide refcount and mutex.

Dependencies/integration: includes `<net/pkt_sched.h>` and relies on SGE queue types from core cxgb4 headers. It is consumed by TC setup dispatch and adapter teardown.

Risks: `tc_hwtc_map` is sized with `TC_QOPT_MAX_QUEUE`; validation must keep requested TCs within that range and hardware scheduler limits. Timeout constants affect setup latency and shutdown behavior.

Test signals: compile coverage with mqprio enabled, resource allocation/free paths, and netdev queue mapping validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb4/cxgb4_tc_mqprio.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb4/cxgb4_tc_u32.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb4/cxgb4_tc_u32.c

Purpose: implements TC `u32` classifier offload by parsing u32 keys and links into Chelsio filter specs and installing/removing hardware filters.

Important APIs/functions: `cxgb4_config_knode`, `cxgb4_delete_knode`, `cxgb4_init_tc_u32`, and `cxgb4_cleanup_tc_u32`; internal helpers `fill_match_fields` and `fill_action_fields` translate u32 selectors/actions.

Control flow: config rejects unsupported devices/protocols, reserves a free filter id by priority, validates root or linked u32 handles, records jump-table links for supported IPv4/IPv6 TCP/UDP next-header transitions, copies linked specs for child buckets, fills match fields and one supported action, sets ingress port/hitcount/type defaults, and calls `cxgb4_set_filter`. Delete searches both high-priority and normal filter tables for the cookie, validates linked-bucket ownership, deletes the filter, clears bitmaps, and recursively deletes filters associated with a deleted link handle.

State and persistence: `adapter->tc_u32` points to a variable-sized table of link entries, each with a saved partial filter spec, link handle, next-header match table, and tid bitmap. Hardware filter entries persist until deleted.

Dependencies/integration: depends on Linux TC u32 structures/actions, Chelsio filter table/TID state, parser tables in `cxgb4_tc_u32_parse.h`, and `cxgb4_filter` add/delete helpers.

Risks: u32 offload accepts a narrow selector grammar; unsupported offsets, masks, actions, or jump shapes fail. Delete path manually scans filter bitmaps and must account for multi-slot IPv6 filters on pre-T6 chips. Link table size is based on available filter IDs and allocates a bitmap per entry, so memory use grows quadratically with max filter count.

Test signals: root IPv4/IPv6 drop and redirect filters, linked TCP/UDP port matches, unsupported action rejection, duplicate link rejection, delete of link with child filters, high-priority table scanning, and memory allocation failure in `cxgb4_init_tc_u32`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb4/cxgb4_tc_u32.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb4/cxgb4_tc_u32.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb4/cxgb4_tc_u32.h

Purpose: exposes the cxgb4 TC u32 offload entry points and a capability helper.

Important APIs/types: `can_tc_u32_offload`, `cxgb4_config_knode`, `cxgb4_delete_knode`, `cxgb4_init_tc_u32`, and `cxgb4_cleanup_tc_u32`.

Control flow/state: `can_tc_u32_offload` gates offload on `NETIF_F_HW_TC` and initialized `adap->tc_u32`. The implementation owns all parser state and hardware filter state.

Dependencies/integration: includes `<net/pkt_cls.h>` and assumes `netdev2adap` plus `struct adapter` are available from core cxgb4 headers. TC dispatch in `cxgb4_main.c` calls these functions for `TC_SETUP_CLSU32`.

Risks: capability is per-netdev feature plus adapter table pointer; callers must avoid invoking config/delete after cleanup clears `adap->tc_u32`.

Test signals: TC setup dispatch with `NETIF_F_HW_TC` toggled, init failure fallback, and cleanup after active or absent u32 state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb4/cxgb4_tc_u32.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb4/cxgb4_tc_u32_parse.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb4/cxgb4_tc_u32_parse.h

Purpose: provides static parser tables and field-fill helpers that map supported TC u32 offsets/masks into `ch_filter_specification` match fields.

Important APIs/types: `struct cxgb4_match_field`, IPv4/IPv6 fill helpers for TOS, fragment flag, protocol, source/destination addresses, L4 port fill helper, field arrays `cxgb4_ipv4_fields`, `cxgb4_ipv6_fields`, `cxgb4_tcp_fields`, `cxgb4_udp_fields`, `struct cxgb4_next_header`, jump arrays `cxgb4_ipv4_jumps`/`cxgb4_ipv6_jumps`, `struct cxgb4_link`, and `struct cxgb4_tc_u32_table`.

Control flow/state: the `.c` parser walks these tables by selector offset and invokes `val` callbacks. Jump arrays describe supported u32 link shapes from IPv4 IHL/protocol or fixed IPv6 header to TCP/UDP port parsing. Link entries persist partial specs and a bitmap of hardware filter TIDs associated with each linked bucket.

Dependencies/integration: depends on Linux TC u32 selector/key layouts and Chelsio filter specification fields. It is private to `cxgb4_tc_u32.c` but encodes much of the supported offload grammar.

Risks: byte-order and offset assumptions are precise; incorrect masks can silently encode wrong hardware matches. Fragment parsing only supports specific MF/DF patterns. IPv6 extension headers are not modeled; jumps assume the fixed 40-byte header.

Test signals: parser unit coverage for each offset, endian-sensitive address/port/TOS extraction, supported and rejected fragment masks, IPv4 IHL jumps, IPv6 fixed-header jumps, and link bitmap accounting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb4/cxgb4_tc_u32_parse.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb4/cxgb4_thermal.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb4/cxgb4_thermal.c

Purpose: registers the adapter as a Linux thermal zone and reports firmware-provided board temperature and optional critical trip temperature.

Important APIs/functions: `cxgb4_thermal_init`, `cxgb4_thermal_remove`, internal `cxgb4_thermal_get_temp`, `cxgb4_thermal_ops`, and global `trip` configured as `THERMAL_TRIP_CRITICAL`.

Control flow: init queries firmware for max temperature threshold; if unavailable it registers with zero trips, otherwise it stores the threshold in millidegrees Celsius. It registers a thermal zone named `cxgb4_<adapter-name>`, enables it, and unwinds registration on enable failure. The get-temp callback queries firmware diagnostic temperature and returns millidegrees Celsius.

State and persistence: `adap->ch_thermal.tzdev` holds the registered thermal zone pointer. Firmware values are queried on demand; no temperature history is stored.

Dependencies/integration: depends on Chelsio `t4_query_params` firmware parameters and Linux thermal zone APIs. Called from adapter bring-up and removal paths.

Risks: `cxgb4_thermal_get_temp` returns `-1` instead of a specific errno for firmware failure or zero value. The global `trip` object is shared across adapters and its temperature is overwritten at init time. Enable failure unregisters but does not explicitly clear `tzdev`.

Test signals: firmware threshold present/absent, temperature query failure, multiple adapters with different thresholds, thermal zone registration and removal, and driver unload with registered zone.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb4/cxgb4_thermal.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb4/cxgb4_uld.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb4/cxgb4_uld.c

Purpose: implements the cxgb4 Upper Layer Driver registration and SGE queue management layer for RDMA, iSCSI, crypto, IPsec, TLS, and related offload clients.

Important APIs/functions: `t4_uld_mem_alloc`, `t4_uld_mem_free`, `t4_uld_clean_up`, `cxgb4_uld_enable`, `cxgb4_register_uld`, `cxgb4_unregister_uld`, and optional `cxgb4_set_ktls_feature`; internal helpers allocate/free ULD RX/TX queues, request/free MSI-X IRQs, enable/quiesce RX, populate `cxgb4_lld_info`, attach ULDs, and shut them down.

Control flow: a ULD registers global callbacks in `uld_list`; each enabled adapter is added to `adapter_list` and attempts resource allocation for every compatible registered ULD. Allocation configures RX/concentrator queues, SGE queues, MSI-X IRQs, RX enablement, shared or crypto TX queues, copies ULD callbacks, and calls the ULD `add` method with low-level device info. Shutdown clears callbacks/handle, releases TX queues, quiesces RX, frees IRQs, SGE queues, and queue metadata.

State and persistence: global `uld_list` and `adapter_list` are protected by `uld_mutex`; per-adapter `adap->uld[type]`, `sge.uld_rxq_info`, and `sge.uld_txq_info` hold runtime state. TX queue info has a users counter for shared offload queues. Optional kTLS state uses `chcr_ktls.ktls_refcount`.

Dependencies/integration: depends on SGE allocation/free helpers, MSI-X bitmap/affinity helpers, firmware params, netevent notifier registration, offload capability checks, and ULD callback contracts defined in `cxgb4_uld.h`.

Risks: multi-step resource allocation has many unwind labels; missed cleanup can leak IRQs, queue contexts, or bitmap indices. `cxgb4_uld_alloc_resources` skips unsupported adapter/ULD combinations, so registration success does not imply every adapter attached. kTLS enablement blocks when other ULD connections are active. Queue count rounding by port count can produce zero for crypto and returns `-EINVAL`.

Test signals: register/unregister each ULD type, attach failure at every allocation stage, MSI-X and non-MSI-X modes, full-init versus early-init paths, adapter removal with active ULDs, shared TX queue user counting, kTLS enable/disable refcounting, and state-change notification to attached ULDs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb4/cxgb4_uld.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb4/cxgb4_uld.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb4/cxgb4_uld.h

Purpose: defines the public cxgb4 ULD contract, TID/resource tables, WR initialization macros, offload send/filter APIs, and low-level information passed to upper-layer drivers.

Important APIs/types: WR macros `INIT_TP_WR`, `INIT_TP_WR_CPL`, `INIT_ULPTX_WR`; `struct tid_info`, TID lookup/allocation helpers, EOTID helpers, `struct filter_ctx`, `enum cxgb4_uld`, `enum cxgb4_state`, `enum cxgb4_control`, `struct cxgb4_virt_res`, `struct cxgb4_lld_info`, and `struct cxgb4_uld_info`; prototypes for ULD registration, offload sends, server/filter operations, stats, BAR2 queue register lookup, and hardware reads.

Control flow/state: inline TID helpers update pointer tables and atomic usage counters for regular, hash, connection, and ETHOFLD TIDs. `cxgb4_lld_info` is the snapshot of adapter resources handed to a ULD at attach time; `cxgb4_uld_info` is the callback table registered by a ULD.

Dependencies/integration: includes core cxgb4 definitions, skb, inetdevice, TLS, and spinlock/atomic headers. Used by RDMA/iSCSI/crypto/TLS consumers and by internal TC/filter code needing TID and filter APIs.

Risks: many helpers are inline and assume caller-side locking around bitmaps and tables. Resource ranges and queue counts must match firmware initialization. Optional structs under TLS/IPsec config guards change compiled surface. `set_wr_txq` encodes priority and queue into skb queue mapping, so users must preserve that convention.

Test signals: compile matrix for TLS/IPsec configs, TID/EOTID allocation under contention, ULD callback ABI changes, filter completion paths using `filter_ctx`, and offload send queue mapping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb4/cxgb4_uld.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb4/l2t.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb4/l2t.c

Purpose: manages the cxgb4 software mirror of the hardware Layer-2 table used by offload traffic to resolve next-hop MAC/VLAN/port information and queue packets while neighbor resolution is pending.

Important APIs/functions: `cxgb4_l2t_get`, `cxgb4_l2t_release`, `cxgb4_l2t_send`, `t4_l2t_update`, `t4_l2t_alloc_switching`, `t4_init_l2t`, `do_l2t_write_rpl`, `cxgb4_select_ntuple`, `cxgb4_check_l2t_valid`, and debugfs `t4_l2t_fops`; internal helpers hash addresses, allocate/reuse entries, write hardware L2 entries, and drain ARP queues.

Control flow: `cxgb4_l2t_get` hashes neighbor address plus ifindex, finds or allocates an entry, references the neighbor, records VLAN/logical port, and starts in resolving state. `cxgb4_l2t_send` sends immediately for valid/stale entries or queues packets for resolving/sync-write entries and triggers neighbor events. Neighbor updates write hardware entries, send queued packets, or invoke ARP error handlers on failure. Switching allocation creates non-hashed entries keyed by VLAN/port/MAC.

State and persistence: `struct l2t_data` holds a flexible array of entries, hash bucket heads embedded in entries, rover pointer, rwlock, and free count. Each `l2t_entry` has state, refcount, neighbor pointer, ARP queue, VLAN, lport, MAC, and lock. Hardware L2 table entries are updated by CPL work requests.

Dependencies/integration: uses Linux neighbor, VLAN, skb queue, debugfs/seq_file, jhash, and Chelsio CPL/management TX APIs. ULDs and offload paths call it before sending packets that require L2 resolution.

Risks: locking mixes table rwlocks, entry spinlocks, and bottom-half variants; ordering must remain consistent. Entries with refcount zero can remain hashed for reuse. `do_l2t_write_rpl` derives local index from firmware TID and assumes it falls within the adapter slice. ARP failure path releases entry lock while invoking handlers.

Test signals: IPv4/IPv6 neighbor resolution, VLAN priority handling, loopback path, stale-to-valid transitions, failed neighbor resolution with and without ARP error handler, switching entries, L2T_WRITE reply errors, debugfs dump, and refcount/free reuse races.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb4/l2t.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb4/l2t.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb4/l2t.h

Purpose: declares the Layer-2 table state machine, entry structure, skb ARP error callback storage, and exported L2T APIs for cxgb4 offload paths.

Important APIs/types: `VLAN_NONE`, `L2T_SIZE`, L2T state enum, `struct l2t_entry`, `arp_err_handler_t`, `struct l2t_skb_cb`, `L2T_SKB_CB`, `t4_set_arp_err_handler`, and prototypes for L2T lookup/send/release/update/switching allocation/init/debugfs support.

Control flow/state: the enum defines runtime states from valid/stale/resolving/sync-write to switching and unused. `struct l2t_entry` combines hash-chain node, bucket head, neighbor pointer, ARP queue, refcount, VLAN, lport, MAC address, and lock.

Dependencies/integration: includes spinlock, Ethernet, atomic, skb, neighbor, and net_device types. ULDs use the API to hold L2 entries and send queued offload packets.

Risks: `skb->cb` is reused for ARP error handling, so callers must not conflict with other skb control-block users. State values below `L2T_STATE_SWITCHING` are treated as hashed entries by implementation logic.

Test signals: compile coverage for ULD callers, skb control-block handler invocation, state transition tests, and debugfs file operation registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb4/l2t.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb4/sched.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb4/sched.c

Purpose: manages per-port hardware scheduling classes and binds either Ethernet queues or ETHOFLD flow contexts to those classes.

Important APIs/functions: `cxgb4_sched_queue_lookup`, `cxgb4_sched_class_bind`, `cxgb4_sched_class_unbind`, `cxgb4_sched_class_alloc`, `cxgb4_sched_class_free`, `t4_init_sched`, and `t4_cleanup_sched`; internal helpers issue firmware scheduler commands, bind/unbind queue or flowc entries, look up existing bindings, and unbind all users of a class.

Control flow: class allocation optionally reuses an existing FLOW-mode class with matching params, otherwise finds an unused class, programs firmware with `t4_sched_params`, and marks it active. Binding unbinds any previous class for the queue/flowc, sends firmware params or flowc work request, records the binding in the class list, and increments refcount. Unbind sends firmware reset, removes list entry, and frees the class if refcount reaches zero. Free resets class rates to link max or 100 Gbps fallback.

State and persistence: each port owns a `sched_table` with flexible array of `ch_sched_class` records, each containing class index, params, binding type, entry list, state, and atomic refcount. Hardware scheduler state persists until reset by free/cleanup.

Dependencies/integration: uses firmware `t4_sched_params` and `t4_set_params`, ETHOFLD `cxgb4_ethofld_send_flowc`, netdev port info, and link speed query. Matchall and mqprio are primary consumers.

Risks: `t4_sched_class_unbind_all` iterates lists while unbind deletes entries, which requires careful list traversal assumptions. Class reuse is limited to flow mode; queue mode always consumes a new class. `cxgb4_sched_class_free` indexes by classid without its own range check, relying on callers.

Test signals: scheduler class allocation/reuse/free, queue binding conflicts, flowc bind/unbind completion paths, link speed query failure fallback, cleanup with active bindings, and invalid class/queue/tid inputs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb4/sched.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb4/sched.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb4/sched.h

Purpose: defines cxgb4 scheduler class constants, state structures, bind types, capability helpers, and public scheduler APIs.

Important APIs/types: `SCHED_CLS_NONE`, `FW_SCHED_CLS_NONE`, `SCHED_MAX_RATE_KBPS`, scheduler state enum, `enum sched_fw_ops`, `enum sched_bind_type`, `struct sched_queue_entry`, `struct sched_flowc_entry`, `struct ch_sched_class`, `struct sched_table`, `can_sched`, `valid_class_id`, and prototypes for lookup/bind/unbind/alloc/free/init/cleanup.

Control flow/state: the header models a per-port scheduler table with active/unused class entries, binding lists, and refcounts. Inline helpers gate use on `pi->sched_tbl` presence and validate class ids while allowing `SCHED_CLS_NONE`.

Dependencies/integration: includes spinlock and atomic headers and relies on cxgb4 `port_info`, `ch_sched_params`, `ch_sched_queue`, and `ch_sched_flowc` definitions from core headers.

Risks: `sched_size` is an 8-bit field, so hardware class counts must fit. `valid_class_id` assumes a non-null scheduler table; callers should call `can_sched` first as the implementation does.

Test signals: build coverage where scheduler support is absent/present, validation of boundary class ids, and consumers in matchall/mqprio using queue and flowc bind types.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb4/sched.h -->
