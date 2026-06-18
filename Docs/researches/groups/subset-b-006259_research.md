# subset-b-006259 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/openvswitch/drop.h -->
# sources/distributed-fs/ceph-client/net/openvswitch/drop.h

## Purpose
`drop.h` defines the Open vSwitch datapath-specific skb drop reason namespace. It is a small integration header that lets action execution, conntrack, fragmentation, meter handling, and explicit drop actions report a structured `SKB_DROP_REASON_SUBSYS_OPENVSWITCH` reason instead of freeing packets anonymously.

## Important APIs, Types, and Functions
`OVS_DROP_REASONS(R)` is the authoritative list of OVS drop reason symbols. The macro is reused by this header to build `enum ovs_drop_reason` and by datapath registration code to publish string names through the kernel drop reason subsystem. Listed causes include action errors, explicit drop actions, meter drops, recursion/deferred action limits, fragmentation failures, conntrack failures, and IP TTL drops.

`enum ovs_drop_reason` starts from the Open vSwitch subsystem offset by deriving `__OVS_DROP_REASON` from `SKB_DROP_REASON_SUBSYS_OPENVSWITCH << SKB_DROP_REASON_SUBSYS_SHIFT`. This keeps OVS reasons disjoint from core skb reasons and other subsystem reason ranges.

`ovs_kfree_skb_reason(struct sk_buff *skb, enum ovs_drop_reason reason)` is the local convenience wrapper over `kfree_skb_reason()`. Call sites can pass an OVS enum value and avoid repeating casts to `u32`.

## Control Flow and Integration
The header itself has no runtime state. Its values are consumed by files such as `actions.c`, `conntrack.c`, and `datapath.c`: packet execution paths call `ovs_kfree_skb_reason()` when they intentionally drop an skb, and module init registers the generated reason strings with `drop_reasons_register_subsys()`.

## State and Persistence
The only persisted behavior is the ABI-like ordering of reason identifiers inside the subsystem range. Reordering or removing entries can change observed reason values and trace/drop monitor output.

## Dependencies
It depends on `linux/skbuff.h` and `net/dropreason.h`. It assumes the kernel provides subsystem-scoped skb drop reasons.

## Risks
Adding a reason requires updating the macro list and ensuring datapath registration still exports matching strings. Because drop reasons are externally observable through tracing and packet drop monitoring, careless renumbering can break diagnostics. Callers must pass only OVS subsystem reasons to the wrapper.

## Test Signals
Useful signals are kernel build coverage, drop monitor/trace output showing OVS-specific reason strings, action paths that trigger explicit drop, meter drop, TTL drop, and conntrack drop, and module load/unload exercising drop reason registration in `datapath.c`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/openvswitch/drop.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/openvswitch/flow.c -->
# sources/distributed-fs/ceph-client/net/openvswitch/flow.c

## Purpose
`flow.c` extracts kernel `sk_buff` packets into `struct sw_flow_key`, and maintains per-flow packet, byte, last-used, and TCP flag statistics. It is the parser between raw ingress packets or userspace-supplied packets and the datapath's flow table key representation.

## Important APIs, Types, and Functions
`ovs_flow_used_time()` converts a stored jiffies timestamp into an approximate millisecond wall-clock used time. `ovs_flow_stats_update()`, `ovs_flow_stats_get()`, and `ovs_flow_stats_clear()` manage per-CPU `struct sw_flow_stats` entries allocated by `flow_table.c`.

The packet parsing core is `key_extract()`, which prepares skb header offsets, handles Ethernet or L3-only packets through `mac_proto`, parses outer and inner VLAN tags, determines EtherType or 802.2 framing, and delegates to `key_extract_l3l4()`. `key_extract_l3l4()` fills IPv4, IPv6, ARP/RARP, MPLS, NSH, and transport fields. It treats later IP fragments as having no transport key, records first fragments, handles UDP GSO as first fragments, extracts TCP flags with `TCP_FLAGS_BE16()`, and maps ICMP/ICMPv6 type/code into the transport source/destination fields.

IPv6 parsing is split across `get_ipv6_ext_hdrs()` and `parse_ipv6hdr()`. The former records OpenFlow IPv6 extension header pseudo-field bits, including repeated or unexpected sequence flags. The latter uses `ipv6_find_hdr()` to locate the transport header and handles fragment state. `parse_icmpv6()` additionally extracts neighbor discovery target and link-layer options, with duplicate option detection that clears invalid ND fields. `parse_nsh()` validates NSH version and metadata type and copies MD type 1 context.

Public extraction entry points are `ovs_flow_key_update_l3l4()`, `ovs_flow_key_update()`, `ovs_flow_key_extract()`, and `ovs_flow_key_extract_userspace()`. `ovs_flow_key_extract()` adds tunnel metadata, ingress port, skb priority, mark, optional TC skb extension recirc and post-conntrack state, then fills conntrack fields via `ovs_ct_fill_key()`. `ovs_flow_key_extract_userspace()` parses key metadata from netlink before parsing the packet payload and validates conntrack original-tuple placement.

## Control Flow
Ingress vports call `ovs_vport_receive()`, which stores the input vport in `OVS_CB(skb)` and calls `ovs_flow_key_extract()`. Extraction first initializes tunnel and physical metadata, derives `mac_proto` from `skb->dev->type`, then parses L2/L3/L4. On success, conntrack metadata is appended and datapath lookup can proceed. For userspace packet execute, netlink key attributes provide metadata first, then `key_extract()` reads packet headers.

## State and Persistence
The file does not own persistent datapath objects, but it mutates skbs while parsing: it pulls/pushes Ethernet/VLAN bytes, sets mac/network/transport header offsets, updates `skb->protocol`, may pop non-accelerated VLAN tags into hw-accelerated skb tags, and may linearize ICMPv6 ND packets. Flow stats are per-flow persistent counters protected by spinlocks and RCU pointers; CPU-specific stats are allocated lazily after contention on the preallocated CPU 0 stats slot.

## Dependencies and Integration Points
It depends on kernel network header helpers, VLAN, MPLS, IPv6, NSH, tunnel metadata, TC skb extensions, and OVS `conntrack.h`, `datapath.h`, `flow_netlink.h`, and `vport.h`. Its output layout must match `flow.h`, `flow_table.c`, and `flow_netlink.c`, because masked lookup and netlink serialization compare and encode byte ranges of `struct sw_flow_key`.

## Risks
Parser correctness is security-sensitive because malformed packets can drive skb pulls, header offset changes, and key fields used for matching. Important risks include incomplete header handling, VLAN double-tag corner cases, truncated headers producing wildcard-like zero fields, IPv6 extension sequencing compatibility, NSH length validation, and userspace metadata that overlaps with packet-derived fields. Stats paths must maintain lock/RCU discipline and avoid allocation in hot paths except the intended best-effort per-CPU allocation.

## Test Signals
Good coverage includes packet-in tests for Ethernet, L3-only, VLAN and QinQ, 802.2, IPv4 and IPv6 fragments, TCP/UDP/SCTP/ICMP, ARP/RARP, MPLS stacks, NSH MD1/MD2 rejection, tunnel metadata extraction, TC recirc/post-CT metadata, userspace packet execute keys, and flow stat aggregation/clear under multiple CPUs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/openvswitch/flow.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/openvswitch/flow.h -->
# sources/distributed-fs/ceph-client/net/openvswitch/flow.h

## Purpose
`flow.h` defines the in-kernel Open vSwitch flow key, mask, identifier, action, statistics, and flow object contracts. It is the shared ABI inside the OVS kernel module between packet parsing, netlink conversion, flow table lookup, action execution, conntrack, and vport receive paths.

## Important APIs, Types, and Functions
`enum sw_flow_mac_proto` distinguishes L3-only packets from Ethernet-framed packets and reserves `SW_FLOW_KEY_INVALID` as a high-bit validity marker. `enum ofp12_ipv6exthdr_flags` mirrors OpenFlow IPv6 extension header bits.

`struct sw_flow_key` is the central match key. It includes tunnel metadata and variable tunnel options, physical metadata (`priority`, `skb_mark`, `in_port`), `mac_proto`, tunnel address family, datapath hash, recirculation id, Ethernet addresses and two VLAN headers, conntrack state, IP common fields, L4 ports and TCP flags, IPv4/IPv6/ARP/ND/MPLS/NSH unions, and conntrack original tuple fields. Alignment is enforced so masked comparisons can operate on longs. `TUN_METADATA_OFFSET()` and `TUN_METADATA_OPTS()` store short tunnel options at the end of the fixed array so variable-length options can be matched efficiently.

`struct sw_flow_mask`, `struct sw_flow_match`, and `struct sw_flow_key_range` describe byte ranges of the key that are significant for lookup. `struct sw_flow_id` is either a UFID or an allocated unmasked key pointer. `struct sw_flow_actions` holds an RCU-freed netlink action blob. `struct sw_flow_stats` and `struct sw_flow` define flow counters, per-CPU stats pointers, mask pointer, action pointer, flow-table hash nodes, and optional UFID hash nodes.

Inline helpers include `sw_flow_key_is_nd()`, `ovs_key_mac_proto()`, `ovs_mac_header_len()`, `ovs_identifier_is_ufid()`, and `ovs_identifier_is_key()`. Public functions declare stats operations and packet/user key extraction.

## Control Flow and Integration
Most OVS modules include this header. `flow.c` fills `sw_flow_key`, `flow_netlink.c` parses and emits it, `flow_table.c` masks and hashes it, `datapath.c` stores flows and actions, and action/conntrack code updates or consumes fields during recirculation.

## State and Persistence
The structures in this header are runtime state, not disk persistence. However, their binary layout is crucial inside the module: mask ranges, hashing, and comparisons assume stable offsets and long alignment. The UFID/key choice changes ownership: key identifiers allocate and free an unmasked key, while UFIDs store bytes inline.

## Dependencies
It depends on Linux netlink, Open vSwitch UAPI, tunnel metadata, destination metadata, NSH, cpumasks, RCU, and common network protocol headers.

## Risks
Changing `struct sw_flow_key` layout affects hashing, mask range generation, netlink conversion, and action validation. Overlapping union fields, especially ND versus conntrack original IPv6 tuple, require strict validation. Tunnel option length and placement must remain synchronized with tunnel netlink parsing.

## Test Signals
Build-time `BUILD_BUG_ON()` checks in `flow_table.c`, flow insertion/lookup tests with masks over every key family, netlink round-trip tests, and packet extraction tests are the main signals that this contract remains correct.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/openvswitch/flow.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/openvswitch/flow_netlink.c -->
# sources/distributed-fs/ceph-client/net/openvswitch/flow_netlink.c

## Purpose
`flow_netlink.c` is the Open vSwitch kernel datapath translator between generic-netlink attributes and internal flow keys, masks, identifiers, and actions. It validates userspace flow programming, converts packets and installed flows back to netlink form, allocates action blobs, and normalizes several user-facing action formats into execution-friendly internal formats.

## Important APIs, Types, and Functions
Length tables (`struct ovs_len_tbl`, `ovs_key_lens`, `ovs_tunnel_key_lens`, `ovs_nsh_key_attr_lens`, and `ovs_vxlan_ext_key_lens`) define accepted attribute sizes and nested grammars. `parse_flow_nlattrs()` and `parse_flow_mask_nlattrs()` reject duplicate, unsupported, oversized, or malformed key attributes. Mask parsing skips all-zero attributes so wildcard masks remain compact.

`ovs_nla_get_match()` is the main key/mask parser. It parses key attributes, unwraps nested VLAN `OVS_KEY_ATTR_ENCAP` layers, fills `struct sw_flow_match`, synthesizes exact masks when userspace omits a mask, parses explicit masks, forces exact TCI matching, and calls `match_validate()` to ensure protocol-dependent fields are present and only legal masks are supplied.

`metadata_from_nlattrs()` handles non-packet-derived metadata: datapath hash, recirc id, priority, in_port, skb mark, tunnel metadata, conntrack state/zone/mark/labels, and conntrack original tuples. `ip_tun_from_nlattr()` validates IPv4/IPv6 tunnel keys, TTL requirements, bridge-mode tunnel info, and mutually exclusive Geneve/VXLAN/ERSPAN option blocks. `genev_tun_opt_from_nlattr()`, `vxlan_tun_opt_from_nlattr()`, and `erspan_tun_opt_from_nlattr()` copy variable tunnel metadata into `sw_flow_key::tun_opts`. NSH support is handled by `nsh_hdr_from_nlattr()` and `nsh_key_put_from_nlattr()`.

Serialization APIs include `ovs_nla_put_key()`, `ovs_nla_put_identifier()`, `ovs_nla_put_masked_key()`, `ovs_nla_put_mask()`, `ovs_nla_put_tunnel_info()`, and `ovs_nla_put_actions()`. They emit nested VLANs, tunnel keys, conntrack keys, NSH, MPLS labels, transport fields, and normalized action forms.

Action handling is centered on `ovs_nla_copy_actions()`, which allocates `struct sw_flow_actions` and delegates to `__ovs_nla_copy_actions()`. Validation covers output ports, userspace upcalls, truncation, hash algorithms, VLAN push/pop, MPLS push/pop/add semantics, set and masked set writeability, tunnel set metadata allocation, sample/clone/check-packet-length/decrement-TTL nested actions, conntrack actions, Ethernet and NSH push/pop, meter ids, explicit drop placement, and psample support. Nesting is capped by `OVS_COPY_ACTIONS_MAX_DEPTH`. `actions_may_change_flow()` decides whether nested sample/clone/check branches can execute immediately or must be deferred. Free helpers recursively release nested action resources and tunnel metadata dsts.

## Control Flow
Flow installation or packet execute paths parse netlink key attributes through `ovs_nla_get_match()` or `ovs_nla_get_flow_metadata()`, then parse actions through `ovs_nla_copy_actions()`. The action parser walks attributes in order while maintaining a simulated current `mac_proto`, `eth_type`, VLAN TCI, and MPLS label count so later actions and set operations are validated against packet shape after prior actions. For flow dumps, upcalls, and replies, serialization functions convert internal keys/actions back to userspace-visible attributes and reverse internal normalized forms such as `SET_TO_MASKED` and tunnel-info set actions.

## State and Persistence
The file allocates and owns action blobs until they are installed into flows. `sw_flow_actions` is RCU-freed, and nested action resources must be walked recursively. Tunnel set actions allocate `metadata_dst`, initialize a dst cache, and store the pointer inside an internal `OVS_KEY_ATTR_TUNNEL_INFO` action; this requires explicit `dst_release()` on free. There is no disk persistence, but the netlink grammar is a kernel/userspace ABI.

## Dependencies and Integration Points
It depends on OVS UAPI constants, netlink helpers, tunnel protocols, Geneve, VXLAN, ERSPAN, NSH, MPLS, conntrack helpers, `drop.h`, `flow.h`, and `datapath.h`. Datapath command handlers call it to parse user commands and emit flow/packet replies. Action execution consumes the normalized action blob shape produced here.

## Risks
This is one of the highest-risk files in the set. Invalid length tables, missed duplicate checks, wrong mask synthesis, or protocol-inconsistent action validation can admit flows that corrupt packets or produce mismatched userspace/kernel views. Nested action handling must enforce depth and free every internal resource on all error paths. Tunnel options are variable length and require key/mask length agreement. VLAN and MPLS state simulation must stay synchronized with real action behavior. `BUILD_BUG_ON(OVS_KEY_ATTR_MAX != 32)` and `BUILD_BUG_ON(OVS_ACTION_ATTR_MAX != 25)` intentionally force review when UAPI expands.

## Test Signals
Strong signals include OVS datapath netlink selftests for key parse/reject cases, mask exact/wildcard behavior, VLAN/QinQ nesting, IPv4/IPv6 tunnel metadata, Geneve/VXLAN/ERSPAN options, NSH push/pop, conntrack action round-trips, nested sample/clone/check-packet-length/decrement-TTL depth rejection, psample feature gating, action dump round-trips, and memory leak testing on failed flow installs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/openvswitch/flow_netlink.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/openvswitch/flow_netlink.h -->
# sources/distributed-fs/ceph-client/net/openvswitch/flow_netlink.h

## Purpose
`flow_netlink.h` exports the flow key, mask, identifier, tunnel, and action netlink conversion APIs implemented in `flow_netlink.c`. It is the boundary used by datapath command handling, packet execution, flow table management, and packet key extraction from userspace.

## Important APIs
Size helpers `ovs_tun_key_attr_size()` and `ovs_key_attr_size()` estimate skb space for netlink replies. `ovs_match_init()` initializes a `struct sw_flow_match` around caller-owned key and optional mask storage.

Key parsing and metadata APIs include `parse_flow_nlattrs()`, `ovs_nla_get_flow_metadata()`, and `ovs_nla_get_match()`. Identifier helpers include `ovs_nla_get_ufid()`, `ovs_nla_get_identifier()`, and `ovs_nla_get_ufid_flags()`. Serialization functions include `ovs_nla_put_key()`, `ovs_nla_put_identifier()`, `ovs_nla_put_masked_key()`, `ovs_nla_put_mask()`, and `ovs_nla_put_tunnel_info()`.

Action APIs include `ovs_nla_copy_actions()`, `ovs_nla_add_action()`, `ovs_nla_put_actions()`, `ovs_nla_free_flow_actions()`, and `ovs_nla_free_flow_actions_rcu()`. `nsh_hdr_from_nlattr()` is shared with NSH action code to construct an NSH header from validated attributes.

## Control Flow and Integration
Datapath netlink handlers call parse helpers before creating or updating flows, action execution and reply paths call put helpers, and flow object teardown calls free helpers. The header hides the large internal validation machinery while exposing the small contract needed by the rest of the datapath.

## State and Persistence
The exported action-free APIs encode ownership rules: actions may contain nested allocations and must be freed through this layer, either directly or after RCU grace. Identifier parsing may allocate an unmasked key when no UFID is supplied.

## Dependencies
It depends on kernel netlink/Open vSwitch UAPI types, tunnel headers, RCU, and `flow.h`.

## Risks
Misusing direct `kfree()` on `struct sw_flow_actions` can leak tunnel metadata or conntrack nested resources. Callers must pass appropriately initialized matches, masks, and net namespaces because field support can be per-netns and conntrack dependent.

## Test Signals
Compile-time coverage of every caller, netlink flow add/set/get/dump tests, action memory leak tests, and UFID/non-UFID flow lifecycle tests validate the header contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/openvswitch/flow_netlink.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/openvswitch/flow_table.c -->
# sources/distributed-fs/ceph-client/net/openvswitch/flow_table.c

## Purpose
`flow_table.c` implements Open vSwitch kernel flow object allocation, masked flow lookup, UFID lookup, mask management, hash table resizing/rehashing, flow flushing, and mask-cache rebalancing. It is the datapath's fast path match engine.

## Important APIs, Types, and Functions
`ovs_flow_mask_key()` applies a `struct sw_flow_mask` to a `struct sw_flow_key`, optionally initializing only the active mask range. `ovs_flow_alloc()` and `ovs_flow_free()` allocate and release `struct sw_flow` objects, default stats, per-CPU stats pointers, action blobs, unmasked identifiers, and cpumasks.

The table is split into `struct table_instance` for masked-key lookup and another `table_instance` for UFID lookup. `ovs_flow_tbl_init()`, `ovs_flow_tbl_destroy()`, `ovs_flow_tbl_flush()`, `ovs_flow_tbl_insert()`, and `ovs_flow_tbl_remove()` manage the lifecycle. `ovs_flow_tbl_dump_next()` iterates RCU buckets for dumps.

Mask management is handled by `struct mask_array`, `tbl_mask_array_alloc()`, `tbl_mask_array_add_mask()`, `tbl_mask_array_del_mask()`, `flow_mask_find()`, `flow_mask_insert()`, and `flow_mask_remove()`. Masks are refcounted under the OVS mutex and freed by RCU when the last flow using the mask is removed. Per-mask usage counters are maintained per CPU and rebased with `masks_usage_zero_cntr`.

Lookup starts in `ovs_flow_tbl_lookup_stats()`. It optionally uses a per-CPU `struct mask_cache` keyed by skb hash and recirc id, then calls `flow_lookup()`, which tries a cached mask index first and falls back to all masks. `masked_flow_lookup()` hashes the masked key range, finds a bucket, and compares masked longs. `ovs_flow_tbl_lookup()` is the preemptible netlink-facing lookup wrapper; `ovs_flow_tbl_lookup_exact()` and `ovs_flow_tbl_lookup_ufid()` support command handlers.

`ovs_flow_masks_rebalance()` sorts masks by observed use and replaces the mask array under RCU so frequently hit masks are tried earlier. `ovs_flow_init()` and `ovs_flow_exit()` manage the `sw_flow` and `sw_flow_stats` slab caches.

## Control Flow
On flow insert, the caller provides a masked key and mask. `flow_mask_insert()` reuses an existing equivalent mask or adds a new one, `flow_key_insert()` computes the masked hash and inserts into the main table, and `flow_ufid_insert()` optionally inserts into the UFID table. Packet lookup reads the current table, mask array, and mask cache under RCU, masks the incoming key for candidate masks, and returns the first matching flow. Removal deletes the flow from both tables, decrements mask references, and leaves actual memory release to the caller and RCU.

## State and Persistence
All state is in memory. Hash table instances, mask arrays, and mask caches are replaced under RCU so readers can continue during rehash, resize, and rebalance. `table->count`, `ufid_count`, mask refcounts, and mask usage counters are protected by OVS mutex for writes or per-CPU synchronization for counters. The mask cache is deliberately approximate and can contain stale entries; misses trigger full lookup and stale entries are cleared.

## Dependencies and Integration Points
It depends on `flow.h`, `flow_netlink.h`, jhash, RCU, per-CPU allocation, kernel sort, and OVS locking helpers. `datapath.c` uses it for packet lookup, flow command lookup, inserts, deletes, dumps, and periodic mask rebalancing.

## Risks
The fast path depends on strict RCU, bottom-half, and OVS mutex discipline. `flow_lookup()` must run with BH disabled because it updates this-CPU mask counters. Mask range alignment and key layout must remain valid. Rehash and node version toggling must not lose flows. Mask cache staleness is expected, but stale indexes must not return incorrect matches. Flow free must release UFID/key ownership and nested action resources.

## Test Signals
Signals include flow insert/remove/flush/dump tests, exact-match and wildcard lookup tests, UFID lookup tests, concurrent packet lookup with flow updates, mask cache resize/rebalance tests, RCU stall/leak checks, and high-mask-count performance counters showing reduced `n_mask_hit` after rebalance.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/openvswitch/flow_table.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/openvswitch/flow_table.h -->
# sources/distributed-fs/ceph-client/net/openvswitch/flow_table.h

## Purpose
`flow_table.h` declares the in-memory flow table structures and public table operations used by the Open vSwitch datapath. It exposes enough structure layout for datapath code to hold a table while keeping lookup, mask, and allocation algorithms in `flow_table.c`.

## Important APIs and Types
`struct mask_cache_entry` and `struct mask_cache` define the per-CPU skb-hash to mask-index cache. `struct mask_array_stats`, `struct mask_array`, and `struct mask_count` support ordered mask arrays and per-mask usage accounting. `struct table_instance` is an RCU-replaceable hash bucket array with a node version bit and random hash seed. `struct flow_table` owns the main key table, UFID table, mask cache, mask array, rehash timestamp, and counts.

Public APIs include module slab lifecycle (`ovs_flow_init()`, `ovs_flow_exit()`), flow object lifecycle (`ovs_flow_alloc()`, `ovs_flow_free()`), table lifecycle (`ovs_flow_tbl_init()`, `ovs_flow_tbl_destroy()`, `ovs_flow_tbl_flush()`), insertion/removal, count and mask-cache sizing, dump iteration, packet/stat lookup, exact key lookup, UFID lookup, comparison, key masking, mask rebalance, and flush helper `table_instance_flow_flush()`.

## Control Flow and Integration
`datapath.c` initializes a `struct flow_table` per datapath, calls lookup from the packet processing fast path, and uses insert/remove/flush from generic-netlink flow commands. The action and flow netlink layers rely on `ovs_flow_mask_key()` to derive stored masked keys from user-provided masks.

## State and Persistence
Every field is runtime memory only. RCU pointer annotations on table instances, mask cache, and mask array establish reader/writer replacement semantics. Counts are maintained by writers under OVS locking.

## Dependencies
The header depends on Linux netlink, Open vSwitch UAPI, RCU, time/jiffies, tunnel headers, and `flow.h`.

## Risks
Callers must respect locking comments from the implementation: insert/remove/flush under OVS mutex, lookup under RCU or explicit BH-disabled wrappers as required, and deferred flow free after deletion. Direct manipulation of the structures outside `flow_table.c` risks RCU and refcount bugs.

## Test Signals
Build coverage, datapath flow command tests, packet lookup selftests, UFID dump/get/delete tests, and lockdep/KCSAN runs are useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/openvswitch/flow_table.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/openvswitch/meter.c -->
# sources/distributed-fs/ceph-client/net/openvswitch/meter.c

## Purpose
`meter.c` implements Open vSwitch datapath meter management and packet metering execution. It exposes the OVS meter generic-netlink family, stores per-datapath meters in an RCU array, and implements a token-bucket-like drop band decision used by action execution.

## Important APIs, Types, and Functions
Netlink attribute policies `meter_policy` and `band_policy` validate `OVS_METER_ATTR_*` and `OVS_BAND_ATTR_*` command attributes. `dp_meter_instance_alloc()`, `dp_meter_instance_realloc()`, insert/remove helpers, `attach_meter()`, and `detach_meter()` manage a dynamically resized array indexed by `meter_id % n_meters`.

Command handlers are `ovs_meter_cmd_features()`, `ovs_meter_cmd_set()`, `ovs_meter_cmd_get()`, and `ovs_meter_cmd_del()`, exported through `dp_meter_genl_family`. `dp_meter_create()` validates a meter definition, requires at least one band and no more than `DP_MAX_BANDS`, supports only nonzero rates, initializes bucket size from burst size, computes `max_delta_t`, and optionally preserves supplied stats when clear is not requested. `ovs_meter_cmd_reply_stats()` serializes meter and band counters.

`ovs_meter_execute()` is the fast-path action helper. It looks up a meter, locks it, computes elapsed milliseconds since last use, caps delta to avoid bucket wrap, updates global meter stats, refills each band bucket by `delta_ms * rate`, charges either packet bits for kbps meters or `1000` units for packet-rate meters, chooses the exceeded band with the highest rate, updates band stats, and returns true when a drop band is triggered. Missing meters are ignored rather than dropping.

`ovs_meters_init()` allocates the initial meter table and caps allowed meters to the smaller of `DP_METER_NUM_MAX` or about 3.12 percent of available memory. `ovs_meters_exit()` frees all meters and the instance.

## Control Flow
Datapath creation initializes `dp->meter_tbl`. Userspace configures meters through generic netlink; set replaces any old meter under OVS mutex, replies with old stats when present, then RCU-frees the old object. Action validation in `flow_netlink.c` accepts meter ids without requiring existence. During action execution, `actions.c` calls `ovs_meter_execute()` and drops with `OVS_DROP_METER` when it returns true.

## State and Persistence
Meter state is volatile per datapath. `struct dp_meter` stores id, flags, bands, stats, `used` time, and per-meter spinlock. The containing `dp_meter_instance` is RCU-replaceable for resize and shrink. Meter stats and token buckets persist until meter replacement, deletion, datapath teardown, or explicit clear semantics on set.

## Dependencies and Integration Points
It depends on OVS datapath locking and lookup, generic netlink, RCU, `meter.h`, and `datapath.h`. It integrates with action execution via `ovs_meter_execute()` and with `datapath.c` module registration through `dp_meter_genl_family`.

## Risks
The array uses direct modulo hashing and expects userspace/id-pool allocation to avoid occupied slots; collisions return `-EBUSY`. Resize and shrink must preserve slot positions to keep modulo lookup valid. Token bucket arithmetic depends on units being consistent for kbps and packet-rate modes. Concurrent execution is serialized per meter, but command replacement relies on RCU grace before freeing old meters. `DP_MAX_BANDS` is one, so userspace expecting multi-band meters will be rejected.

## Test Signals
Useful tests include meter feature/get/set/delete generic-netlink commands, replacement preserving or clearing stats, nonexistent meter actions being no-ops, drop behavior around rate/burst boundaries, kbps versus packet-rate accounting, concurrent packet execution against meter replacement, and datapath teardown leak checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/openvswitch/meter.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/openvswitch/meter.h -->
# sources/distributed-fs/ceph-client/net/openvswitch/meter.h

## Purpose
`meter.h` declares Open vSwitch datapath meter structures and public functions. It is included by datapath and action code to initialize meter tables and execute meter actions.

## Important APIs and Types
Constants define current limits: `DP_MAX_BANDS` is one, `DP_METER_ARRAY_SIZE_MIN` is 1024, and `DP_METER_NUM_MAX` is 200000. `struct dp_meter_band` stores band type, rate, burst size, current bucket, and stats. `struct dp_meter` stores a per-meter spinlock, RCU head, id, kbps and keep-stats flags, band count, maximum delta, last-used time, aggregate stats, and flexible bands. `struct dp_meter_instance` is an RCU-freeable flexible array of meter pointers. `struct dp_meter_table` stores the current instance, count, and maximum allowed meters.

The public API is `ovs_meters_init()`, `ovs_meters_exit()`, and `ovs_meter_execute()`. `dp_meter_genl_family` is externally visible for datapath module generic-netlink registration.

## Control Flow and Integration
`datapath.c` embeds `struct dp_meter_table` in each datapath and registers `dp_meter_genl_family` with other OVS netlink families. `actions.c` calls `ovs_meter_execute()` for `OVS_ACTION_ATTR_METER`.

## State and Persistence
The structures hold volatile in-memory state. Locking is split between OVS mutex/RCU for table membership and per-meter spinlock for bucket and stats mutation.

## Dependencies
It depends on Open vSwitch UAPI types, skbuffs, bit helpers, module initialization headers, and `flow.h` for `struct sw_flow_key` and stats.

## Risks
Any change to limits, flexible-array layout, or locking rules must stay synchronized with `meter.c` and userspace feature replies. Callers must not free meters directly.

## Test Signals
Build coverage, meter generic-netlink tests, action execution tests, and lockdep under concurrent meter updates validate this header contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/openvswitch/meter.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/openvswitch/openvswitch_trace.c -->
# sources/distributed-fs/ceph-client/net/openvswitch/openvswitch_trace.c

## Purpose
`openvswitch_trace.c` instantiates the Open vSwitch tracepoints declared in `openvswitch_trace.h`. It exists as the single translation unit that defines `CREATE_TRACE_POINTS`, which causes the kernel tracepoint machinery to generate storage and registration code for OVS trace events.

## Important APIs and Control Flow
The file includes `linux/module.h` to satisfy tracepoint macro requirements, defines `CREATE_TRACE_POINTS`, and includes `openvswitch_trace.h` unless sparse checking is active. There are no callable functions in this file; the generated tracepoint symbols are referenced by action execution and datapath upcall paths through `trace_ovs_do_execute_action()` and `trace_ovs_dp_upcall()`.

## State and Persistence
Tracepoint state is kernel runtime instrumentation state. No OVS datapath state is stored here.

## Dependencies and Integration Points
It depends entirely on the kernel tracepoint infrastructure and must be compiled with `CFLAGS_openvswitch_trace.o = -I$(src)` so `TRACE_INCLUDE_PATH .` in the header resolves. It integrates with `openvswitch_trace.h`.

## Risks
There must be exactly one `CREATE_TRACE_POINTS` instantiation for the header. Including the header incorrectly in multiple C files would create duplicate definitions; omitting this file would leave tracepoint declarations without definitions.

## Test Signals
Build/link success, tracefs listing of OVS events, and enabling `openvswitch:ovs_do_execute_action` or `openvswitch:ovs_dp_upcall` while running datapath traffic validate the file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/openvswitch/openvswitch_trace.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/openvswitch/openvswitch_trace.h -->
# sources/distributed-fs/ceph-client/net/openvswitch/openvswitch_trace.h

## Purpose
`openvswitch_trace.h` declares trace events for key Open vSwitch datapath operations. The events expose packet, datapath, flow key, action, and upcall metadata to ftrace/perf-style tracing.

## Important APIs and Types
`TRACE_EVENT(ovs_do_execute_action)` records datapath pointer/name, skb device/name, skb length/data_len/truesize/frags/GSO fields, key hash/recirc/eth type/conntrack fields/validity, action type/length/data pointer, and whether the action is last in the list. `actions.c` emits it around action execution when the tracepoint is enabled.

`TRACE_EVENT(ovs_dp_upcall)` records similar datapath, skb, and key details plus upcall command, portid, and MRU. `datapath.c` emits it before queueing an upcall.

Both tracepoints use `ovs_dp_name(dp)`, `skb->dev->name`, `nla_type()`, `nla_len()`, `nla_data()`, and OVS key fields. The header ends with the standard trace include path/file macros and `include <trace/define_trace.h>`.

## Control Flow and Integration
The header is included normally by callers for tracepoint declarations and included once from `openvswitch_trace.c` with `CREATE_TRACE_POINTS` for definitions. Callers use the generated `trace_..._enabled()` checks to avoid unnecessary work.

## State and Persistence
Trace events are transient. Their field names and print formats are externally visible tracing ABI and useful for diagnostics.

## Dependencies
It depends on Linux tracepoint infrastructure and `datapath.h`. Because it references skb, netlink attribute, datapath, and flow key internals, changes to those structures can require trace field updates.

## Risks
Tracepoints must not dereference invalid skb, action, or key pointers. They are placed in hot paths, so enabled checks and field collection cost matter. Field naming typos or format mismatches can break trace consumers. The header must keep include guards and `TRACE_HEADER_MULTI_READ` semantics intact.

## Test Signals
Kernel build, trace event registration, enabling both events while running OVS traffic, and verifying printed key/action/upcall fields in tracefs are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/openvswitch/openvswitch_trace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/openvswitch/vport-geneve.c -->
# sources/distributed-fs/ceph-client/net/openvswitch/vport-geneve.c

## Purpose
`vport-geneve.c` implements the OVS Geneve tunnel vport type. It creates metadata-collecting Geneve netdevices, links them into the datapath as netdev-backed vports, reports configuration options, and registers a module alias for dynamic vport-type loading.

## Important APIs, Types, and Functions
`struct geneve_port` stores the destination UDP port in vport private data. `geneve_vport()` maps a `struct vport` to that private data. `geneve_get_options()` emits `OVS_TUNNEL_ATTR_DST_PORT`.

`geneve_tnl_create()` validates that options exist and contain a u16 `OVS_TUNNEL_ATTR_DST_PORT`, allocates a vport with private storage, creates a fallback/metadata Geneve device through `geneve_dev_create_fb()`, brings it up with `dev_change_flags()`, stores the netdev pointer, and takes a netdev reference. `geneve_create()` then calls `ovs_netdev_link(vport, true)` so the generic netdev vport layer attaches RX handling and datapath upper-device linkage.

`ovs_geneve_vport_ops` supplies type `OVS_VPORT_TYPE_GENEVE`, create, destroy (`ovs_netdev_tunnel_destroy()`), get_options, and send (`dev_queue_xmit`). Module init/exit register and unregister the vport ops.

## Control Flow and Integration
Userspace requests a Geneve vport through OVS vport generic netlink. `vport.c` locates these ops, calls `geneve_create()`, and later dispatches send/destroy/get-options through the ops. Received packets arrive via the netdev RX handler in `vport-netdev.c` and are processed by `ovs_vport_receive()` with tunnel metadata from the skb.

## State and Persistence
Runtime state is a vport object, private destination-port copy, created net_device, and netdev reference. The underlying Geneve device is deleted when the tunnel vport is destroyed.

## Dependencies
It depends on `net/geneve.h`, rtnetlink/netdevice helpers, `vport.h`, and `vport-netdev.h`. It uses OVS tunnel option UAPI.

## Risks
Destination port is mandatory and must be validated. Error paths must release the vport and delete the netdevice if bring-up fails. The stored private dst port must remain consistent with the actual Geneve device because get-options reports the private copy.

## Test Signals
Module load via `vport-type-5`, creating/deleting Geneve OVS ports with a dst port, dumping options, receiving Geneve traffic with tunnel metadata, and error cases for missing/invalid options validate behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/openvswitch/vport-geneve.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/openvswitch/vport-gre.c -->
# sources/distributed-fs/ceph-client/net/openvswitch/vport-gre.c

## Purpose
`vport-gre.c` implements the OVS GRE tunnel vport type using a fallback gretap netdevice. It is a small module that registers `OVS_VPORT_TYPE_GRE` and delegates most receive/send/lifetime behavior to the shared netdev vport layer.

## Important APIs and Functions
`gre_tnl_create()` allocates a vport, creates a `gretap_fb_dev_create()` device in the datapath net namespace, brings it up, assigns it to the vport, and holds a netdev reference. `gre_create()` then calls `ovs_netdev_link(vport, true)`. `ovs_gre_vport_ops` defines create, send (`dev_queue_xmit`), and destroy (`ovs_netdev_tunnel_destroy`) for GRE. Module init/exit register and unregister the ops and expose `MODULE_ALIAS("vport-type-3")`.

## Control Flow and Integration
The core vport registry dynamically loads this module for GRE vport requests. Once linked, the generic netdev RX hook processes received GRE-decapsulated packets through `ovs_vport_receive()`, and transmit uses the kernel netdevice output path.

## State and Persistence
State consists of the vport, its created GRE net_device, and held reference. All state is runtime only; the netdevice is deleted on tunnel destroy.

## Dependencies
It depends on GRE, IP tunnel, rtnetlink, net namespace, and shared OVS vport/netdev helpers.

## Risks
Error paths must unlock RTNL, free the vport, and delete failed devices correctly. There are no vport options here, so userspace GRE configuration is limited to the fallback metadata mode created by the kernel helper.

## Test Signals
Creating and deleting GRE OVS ports, module autoload by type 3, traffic through GRE tunnel ports, and failure injection around device creation/bring-up are useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/openvswitch/vport-gre.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/openvswitch/vport-internal_dev.c -->
# sources/distributed-fs/ceph-client/net/openvswitch/vport-internal_dev.c

## Purpose
`vport-internal_dev.c` implements OVS internal vports, which are kernel-created Ethernet netdevices representing datapath ports such as the local port. They let packets enter the datapath from a netdevice transmit path and let datapath output deliver packets up to the host networking stack.

## Important APIs, Types, and Functions
`struct internal_dev` stores the owning `struct vport`. `internal_dev_xmit()` is the netdevice transmit function: it records skb length, calls `ovs_vport_receive()` under RCU, updates software TX stats on success, and increments tx_errors on failure.

`do_setup()` configures the netdevice: Ethernet setup, max MTU, netdev ops, no TX skb sharing, live address change, OVS/internal flags, no queue, software GSO and checksum features, VLAN offload features, random MAC, ethtool ops, and rtnl link kind. `internal_dev_create()` allocates the vport, allocates the netdevice, sets namespace and desired ifindex, records the vport in private data, marks the local port as netns immutable, registers the netdevice under RTNL, sets the destructor, enables promiscuity, and starts the queue.

`internal_dev_destroy()` stops the queue, drops promiscuity, and unregisters the netdevice; unregister waits for an RCU grace period. `internal_dev_recv()` is the vport send function for packets output to the internal device: it drops if the device is down, clears dst and conntrack state, sets host packet type and protocol via `eth_type_trans()`, updates RX stats, and injects with `netif_rx()`.

`ovs_internal_vport_ops` registers type `OVS_VPORT_TYPE_INTERNAL`. Public helpers identify internal devices, get their vport, and register/unregister rtnl link and vport ops.

## Control Flow
For host-originated packets sent on an internal interface, the netdevice start_xmit path calls into OVS receive and datapath processing. For datapath output to an internal vport, action execution calls the vport `send` op, which delivers to the Linux receive path. Creation and deletion are driven by vport generic-netlink commands and datapath lifecycle.

## State and Persistence
Runtime state is the netdevice, vport, private pointer, netdevice flags/features, queues, and per-device software stats. The vport is freed by the netdevice private destructor after unregister.

## Dependencies
It depends on Linux netdevice, ethtool, rtnetlink, dst/xfrm helpers, and shared OVS `datapath.h`, `vport.h`, and `vport-netdev.h`.

## Risks
Ownership between vport and netdevice is delicate: create failure, unregister, destructor, and vport free must not double free. Packets are consumed by `ovs_vport_receive()`, so xmit must not touch skb afterward. Output path must clear dst and conntrack references before host delivery. Local port namespace immutability prevents cross-netns surprises.

## Test Signals
Creating/deleting datapaths and internal ports, host ping/traffic through internal interfaces, output to down internal devices, netns teardown, stats correctness, and KASAN/lockdep around unregister validate behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/openvswitch/vport-internal_dev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/openvswitch/vport-internal_dev.h -->
# sources/distributed-fs/ceph-client/net/openvswitch/vport-internal_dev.h

## Purpose
`vport-internal_dev.h` declares the public helpers for OVS internal netdevices.

## Important APIs
`ovs_is_internal_dev()` identifies netdevices backed by OVS internal device ops. `ovs_internal_dev_get_vport()` returns the owning vport for an internal netdevice. `ovs_internal_dev_rtnl_link_register()` and `ovs_internal_dev_rtnl_link_unregister()` register/unregister both the rtnl link kind and the internal vport ops.

## Control Flow and Integration
`vport-netdev.c` uses `ovs_is_internal_dev()` to prevent adding an internal device as a normal netdev vport. Datapath module init/exit uses the rtnl registration helpers. Internal-device implementation provides the definitions.

## State and Persistence
No state is declared here. The API exposes lookups into runtime netdevice private data.

## Dependencies
It depends on `datapath.h` and `vport.h` for core OVS and vport types.

## Risks
Callers must pass valid netdevices. The registration helpers must be paired during module init/cleanup to avoid stale rtnl link kinds or vport ops.

## Test Signals
Build coverage, internal port creation, rejection of internal devices as external netdev vports, and module cleanup are relevant signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/openvswitch/vport-internal_dev.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/openvswitch/vport-netdev.c -->
# sources/distributed-fs/ceph-client/net/openvswitch/vport-netdev.c

## Purpose
`vport-netdev.c` implements OVS vports backed by existing or tunnel netdevices. It attaches a netdevice RX handler to feed ingress packets into the OVS datapath, links the device under the datapath local device, manages promiscuity/LRO, and supplies shared destroy logic for tunnel vports.

## Important APIs and Functions
`netdev_port_receive()` locates the vport from `skb->dev`, rejects LRO skbs, makes a private skb copy with `skb_share_check()`, pushes an Ethernet header for Ethernet devices, and calls `ovs_vport_receive()` with any skb tunnel info. `netdev_frame_hook()` consumes non-loopback RX packets and passes loopback packets through.

`ovs_netdev_link()` is shared by normal and tunnel netdev-backed vports. It takes RTNL, links the device as an upper/lower relation to the datapath local device, registers the RX handler, disables LRO, enables promiscuity, sets `IFF_OVS_DATAPATH`, and unwinds all steps on failure. `netdev_create()` allocates a vport for an existing device, takes a reference by name in the datapath namespace, rejects aliases, loopback, unsupported ARP types, and internal OVS devices, then links it.

`ovs_netdev_detach_dev()` removes the RX handler and upper link, drops promiscuity, and clears `IFF_OVS_DATAPATH` with memory barriers paired against destroy. `netdev_destroy()` handles explicit deletion and notifier-detached devices, then RCU-frees the vport and releases the netdev reference. `ovs_netdev_tunnel_destroy()` additionally deletes registered tunnel netdevices when appropriate and schedules vport release before RTNL unlock can run netdev cleanup.

`ovs_netdev_get_vport()` returns the RX handler data for OVS ports. `ovs_netdev_vport_ops` registers type `OVS_VPORT_TYPE_NETDEV`.

## Control Flow
Existing-device vport creation flows through `netdev_create()` and `ovs_netdev_link()`. Tunnel modules create their own netdevice and then call `ovs_netdev_link(vport, true)`. On ingress, the kernel RX handler routes packets into OVS. On egress, vport send uses `dev_queue_xmit()`.

## State and Persistence
Runtime state lives in the vport, netdev reference tracker, netdevice RX handler data, upper-device relationship, promiscuity count, and `IFF_OVS_DATAPATH` flag. RCU defers vport free after detach.

## Dependencies
It depends on Linux netdevice/rtnetlink APIs, VLAN/bridge helpers, OVS datapath/vport/internal-device headers, and tunnel metadata carried on skbs.

## Risks
RX handler registration and netdevice notifier paths can race with explicit deletion; barriers and double checks reduce detach races. Forgetting to drop promiscuity or upper links leaks device state. LRO packets are rejected because OVS expects parseable packets. The code must avoid attaching loopback or internal devices as normal netdev vports.

## Test Signals
Adding/removing physical devices as OVS ports, deleting underlying devices, netns teardown, ingress traffic reaching datapath, LRO rejection, tunnel vport destroy, and lockdep around RTNL/RCU paths are strong signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/openvswitch/vport-netdev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/openvswitch/vport-netdev.h -->
# sources/distributed-fs/ceph-client/net/openvswitch/vport-netdev.h

## Purpose
`vport-netdev.h` declares shared netdev-backed vport helpers used by normal netdev ports and tunnel vport modules.

## Important APIs
`ovs_netdev_get_vport()` maps an OVS-attached netdevice to its vport. `ovs_netdev_link()` attaches an allocated vport and its netdevice to datapath RX handling; the `tunnel` flag controls tunnel-device cleanup on failure. `ovs_netdev_detach_dev()` removes RX and upper-device attachment. `ovs_netdev_init()` and `ovs_netdev_exit()` register/unregister normal netdev vport ops. `ovs_netdev_tunnel_destroy()` is the common destroy function for tunnel vports.

## Control Flow and Integration
`vport-gre.c`, `vport-geneve.c`, and `vport-vxlan.c` create tunnel netdevices, hold references, then call `ovs_netdev_link()`. Datapath/device notifier code can call detach helpers when netdevices disappear.

## State and Persistence
The header declares APIs that manipulate runtime netdevice references, RX handlers, and vport lifetimes. It declares no standalone state.

## Dependencies
It depends on Linux netdevice/RCU headers and `vport.h`.

## Risks
Callers must pass vports with valid `dev` pointers and must use the correct destroy helper for tunnel-created devices. Mispaired link/detach can leave RX handlers or references behind.

## Test Signals
Build coverage for all tunnel modules, normal netdev port lifecycle tests, and notifier-triggered detach tests validate the contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/openvswitch/vport-netdev.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/openvswitch/vport-vxlan.c -->
# sources/distributed-fs/ceph-client/net/openvswitch/vport-vxlan.c

## Purpose
`vport-vxlan.c` implements the OVS VXLAN tunnel vport type. It creates collect-metadata VXLAN netdevices, supports a mandatory destination UDP port and optional GBP extension, and reuses the netdev vport layer for datapath attachment.

## Important APIs and Functions
`vxlan_get_options()` emits `OVS_TUNNEL_ATTR_DST_PORT` and, when enabled, nested `OVS_TUNNEL_ATTR_EXTENSION` with `OVS_VXLAN_EXT_GBP`. `exts_policy` validates VXLAN extension attributes. `vxlan_configure_exts()` parses nested extensions and sets `VXLAN_F_GBP`.

`vxlan_tnl_create()` requires `OVS_TUNNEL_ATTR_DST_PORT`, initializes `struct vxlan_config` with `no_share`, collect metadata, UDP zero checksum IPv6 receive, and `IP_MAX_MTU`, allocates a vport, parses optional extensions, creates a VXLAN device with `vxlan_dev_create()`, brings it up, stores the netdev, and holds a reference. `vxlan_create()` links it into OVS via `ovs_netdev_link(vport, true)`.

`ovs_vxlan_netdev_vport_ops` registers type `OVS_VPORT_TYPE_VXLAN`, destroy via `ovs_netdev_tunnel_destroy()`, get_options, and `dev_queue_xmit` send. Module alias `vport-type-4` supports autoload.

## Control Flow and Integration
Vport generic-netlink requests instantiate the VXLAN module ops. RX and TX after creation use the shared netdev-backed vport paths. Tunnel key parsing and emission in `flow_netlink.c` must agree with the GBP option represented here.

## State and Persistence
Runtime state is the created VXLAN netdevice, vport, netdev reference, configured destination port, and optional GBP flag in the VXLAN config/device.

## Dependencies
It depends on `net/vxlan.h`, UDP tunnel helpers, rtnetlink, OVS vport/netdev helpers, and OVS tunnel UAPI.

## Risks
Destination port is mandatory. Extension parsing must reject malformed nested attributes. Error paths must delete partially created devices and free vports. MTU is intentionally set high to avoid tunnel-device MTU limiting OVS output; changing it can alter datapath behavior.

## Test Signals
Creating VXLAN OVS ports with and without GBP, dumping options, rejecting missing dst port or invalid extension attributes, VXLAN tunnel traffic with metadata keys, and module autoload/unload are useful tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/openvswitch/vport-vxlan.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/openvswitch/vport.c -->
# sources/distributed-fs/ceph-client/net/openvswitch/vport.c

## Purpose
`vport.c` is the core Open vSwitch vport subsystem. It registers vport type implementations, allocates and frees vports, locates ports by name, stores upcall port ids and statistics, receives packets into the datapath, and sends packets out through vport ops with MTU and MAC-protocol checks.

## Important APIs, Types, and Functions
`ovs_vport_init()` allocates a 1024-bucket global `dev_table`; `ovs_vport_exit()` frees it. `__ovs_vport_ops_register()` and `ovs_vport_ops_unregister()` maintain the global type list under OVS mutex. `ovs_vport_lookup()` finds ops by `enum ovs_vport_type`; `ovs_vport_add()` creates a vport through ops, holds the module, hashes it by namespace/name, and can request autoload of `vport-type-%d`.

`ovs_vport_alloc()` allocates `struct vport` plus optional private storage, initializes per-vport upcall stats, datapath pointer, port number, ops, and initial upcall port ids. `ovs_vport_free()` releases RCU-protected portids, per-CPU upcall stats, and the vport. `ovs_vport_del()` removes the vport from the global name hash, drops the module reference, and calls type-specific destroy.

`ovs_vport_get_stats()` reads netdevice stats into OVS UAPI stats. `ovs_vport_get_upcall_stats()` aggregates per-CPU success/failure counters into nested netlink attributes. `ovs_vport_set_upcall_portids()` validates and replaces an RCU-protected `struct vport_portids`; `ovs_vport_find_upcall_portid()` selects a port id by skb hash and reciprocal division. `ovs_vport_get_options()` and `ovs_vport_set_options()` dispatch type-specific configuration.

`ovs_vport_receive()` initializes OVS skb control block fields, scrubs packets crossing net namespaces while preserving mark, extracts a flow key with `ovs_flow_key_extract()`, and calls `ovs_dp_process_packet()`. `ovs_vport_send()` validates the outgoing MAC protocol against the netdevice type, checks non-GSO packets against MTU, sets skb device, clears timestamps, and dispatches the vport send op.

## Control Flow
Datapath vport commands call `ovs_vport_add()` and `ovs_vport_del()`. Receive paths from internal devices, physical netdev RX handlers, or tunnel netdevices call `ovs_vport_receive()`. Packet misses use upcall port ids maintained here. Action output paths call `ovs_vport_send()` to transmit or inject packets through the selected vport type.

## State and Persistence
State is in memory: global vport type list, global name hash table, per-vport netdevice pointer/reference, datapath pointer, port id array, per-CPU upcall stats, and private data. Port id arrays and vports are RCU-managed. Module references keep vport type modules loaded while ports exist.

## Dependencies and Integration Points
It depends on `datapath.h`, `flow.c` extraction, `flow_netlink.c` stats/options serialization indirectly, and internal/netdev vport implementations. It integrates with datapath port hash tables, generic-netlink vport commands, and action output.

## Risks
Name hashing must include net namespace to avoid cross-netns conflicts. Upcall PID arrays must be nonempty, u32-aligned, and no larger than CPU count. Receive consumes skbs on errors. MTU checks must account for VLAN headers and GSO. Module autoload returns `-EAGAIN` so callers retry after loading. Locking is split between OVS mutex for writes and RCU for lookup/receive.

## Test Signals
Vport add/delete for internal, netdev, and tunnels; module autoload; duplicate type registration; duplicate name lookup; upcall PID distribution; cross-netns receive scrubbing; MTU drop warnings; and packet ingress/egress through each vport type are key signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/openvswitch/vport.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/openvswitch/vport.h -->
# sources/distributed-fs/ceph-client/net/openvswitch/vport.h

## Purpose
`vport.h` defines the Open vSwitch virtual port abstraction shared by datapath code and vport implementations. It declares port lifecycle, configuration, stats, receive, send, and type registration APIs.

## Important APIs and Types
`struct vport_portids` stores an RCU-protected array of netlink upcall portids plus a reciprocal divisor for hash selection. `struct vport` stores netdevice pointer and tracker, datapath pointer, upcall portids, datapath port number, global and datapath hash nodes, vport ops, per-CPU upcall stats, detach list, and RCU head. `struct vport_parms` carries userspace creation parameters and datapath-internal creation fields. `struct vport_ops` is the type interface: create, destroy, optional set/get options, send, owner module, and list node.

Public functions cover subsystem init/exit, add/delete, locate, stats, options, upcall port ids, upcall port selection, allocation/free, receive, send, ops registration, and helper accessors. `vport_priv()` and `vport_from_priv()` implement aligned private storage after `struct vport`.

## Control Flow and Integration
Datapath command handlers create vports through `ovs_vport_add()`, implementations allocate objects with `ovs_vport_alloc()`, receive paths call `ovs_vport_receive()`, and action output calls `ovs_vport_send()`. Implementations register `struct vport_ops` with `ovs_vport_ops_register()`, which fills owner with `THIS_MODULE`.

## State and Persistence
The header declares runtime structures only. RCU annotations and comments establish lifetime rules for upcall port ids and vports. Per-CPU upcall stats use `u64_stats_sync`.

## Dependencies
It depends on Linux tunnel, netlink, Open vSwitch UAPI, skb, reciprocal division, spinlock/stat helpers, and `datapath.h`.

## Risks
Implementations must obey the ops contract: create under OVS mutex, destroy after detaching and with proper RCU grace before final free, and send must consume the skb. Private data alignment must remain consistent with allocation in `vport.c`. Upcall port id users must hold RCU or OVS lock.

## Test Signals
Build coverage across all vport types, lifecycle tests, RCU/lockdep checks, upcall stats reporting, private data use in tunnel modules, and packet output behavior validate this abstraction.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/openvswitch/vport.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/packet/Kconfig -->
# sources/distributed-fs/ceph-client/net/packet/Kconfig

## Purpose
`net/packet/Kconfig` declares configuration options for Linux packet sockets in this source tree. Packet sockets let applications such as tcpdump communicate directly with network devices below normal protocol stacks.

## Important Options
`config PACKET` is a tristate option named "Packet socket". When built in or as a module, it enables the AF_PACKET protocol implementation; as a module it is named `af_packet`. The help text recommends enabling it for direct device communication and says to choose Y if unsure.

`config PACKET_DIAG` is a tristate option named "Packet: sockets monitoring interface". It depends on `PACKET`, defaults to `n`, and enables the PF_PACKET socket diagnostic interface used by tools such as `ss`.

## Control Flow and Integration
Kconfig selections feed the packet directory Makefile. `CONFIG_PACKET` controls compilation of `af_packet.o`; `CONFIG_PACKET_DIAG` controls `af_packet_diag.o` and its `diag.o` component.

## State and Persistence
This file has no runtime state. It affects kernel build configuration and module availability.

## Dependencies
It depends on the kernel Kconfig system. `PACKET_DIAG` depends on `PACKET`, ensuring diagnostics cannot be built without the base packet socket support.

## Risks
Disabling `PACKET` removes common tooling support for packet capture and raw L2 access. Enabling packet sockets exposes AF_PACKET attack surface, so downstream hardening may choose module-only or disabled builds. The diagnostic option must remain gated on `PACKET`.

## Test Signals
Configuration tests should verify all tristate combinations allowed by dependencies, module names in generated builds, and runtime availability of AF_PACKET sockets and `ss` packet diagnostics when enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/packet/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/packet/Makefile -->
# sources/distributed-fs/ceph-client/net/packet/Makefile

## Purpose
`net/packet/Makefile` connects packet socket Kconfig symbols to object compilation in the kernel build.

## Important Build Rules
`obj-$(CONFIG_PACKET) += af_packet.o` builds the AF_PACKET implementation when packet socket support is enabled. `obj-$(CONFIG_PACKET_DIAG) += af_packet_diag.o` builds the packet diagnostic module or built-in object when diagnostics are enabled. `af_packet_diag-y += diag.o` defines `diag.o` as the component object for `af_packet_diag.o`.

## Control Flow and Integration
The file is consumed by kbuild. `CONFIG_PACKET` and `CONFIG_PACKET_DIAG` are provided by `Kconfig`; kbuild expands tristate values to built-in, module, or omitted objects.

## State and Persistence
There is no runtime state. The file determines build artifacts and module composition.

## Dependencies
It depends on kbuild conventions and on source files `af_packet.c` and `diag.c` existing in the packet directory.

## Risks
Incorrect object names would break packet socket or diagnostic builds. If new diagnostic source files are added, the composite `af_packet_diag-y` list must be updated.

## Test Signals
Builds with `CONFIG_PACKET=y/m/n` and `CONFIG_PACKET_DIAG=y/m/n` where valid, plus module artifact checks for `af_packet` and `af_packet_diag`, validate this Makefile.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/packet/Makefile -->
