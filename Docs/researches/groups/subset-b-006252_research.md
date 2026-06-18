# subset-b-006252 netfilter nftables expression and set backend research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nft_payload.c -->
# sources/distributed-fs/ceph-client/net/netfilter/nft_payload.c

## Purpose

`nft_payload.c` implements nftables payload load and payload write expressions. It extracts bytes from link, network, transport, inner, and tunnel-relative headers into nft registers, writes register data back into packets, handles hardware-accelerated VLAN tag compensation, supports selected flow offload translation, and repairs checksums for payload modification.

## Important APIs, Types, and Functions

The main expression type is `nft_payload_type`, whose `select_ops` chooses normal load, fast load, or set/write operations. `nft_payload_eval()` reads packet bytes into `regs->data`; `nft_payload_set_eval()` writes bytes from a source register into an skb. `nft_payload_inner_eval()` is called by inner tunnel parsing support using an explicit `nft_inner_tun_ctx`. `nft_payload_inner_offset()` derives inner payload offsets for UDP, TCP, GRE version 0, and IP-in-IP. The offload helpers map common Ethernet, VLAN, IPv4, IPv6, TCP, and UDP fields to flow dissector keys. `struct nft_payload_set` extends payload attributes with checksum type, checksum offset, and L4 pseudo-header checksum flags.

## Control Flow

Initialization parses base, offset, length, and register attributes, then validates register load or store size. Read evaluation chooses a base offset from skb metadata, applies VLAN reconstruction when offloads stripped the VLAN header, adds the configured offset, and copies bytes with `skb_copy_bits()`. Write evaluation chooses the same base classes, optionally updates checksum state by comparing old bytes to new register bytes, ensures skb writability, and stores data with `skb_store_bits()`. SCTP checksum mode recomputes the whole SCTP checksum after modification. Unsupported header bases, missing L4 metadata, fragments, and short packets break rule evaluation via `NFT_BREAK`.

## State and Persistence Behavior

The expression stores only static netlink configuration in private expression data. Runtime state is packet-local: destination/source registers, skb header offsets, VLAN tag fields, checksum fields, and `regs->verdict`. Payload writes mutate the skb persistently for later expressions and later network stack stages. Inner offset caching mutates `nft_pktinfo` flags and `inneroff`.

## Dependencies and Integration Points

The file integrates with nf_tables core register parsing, skb accessors, VLAN helpers, TCP/UDP/SCTP/ICMPv6 headers, GRE parsing, and nf_tables flow offload. It is used by nft payload syntax and by tunnel inner expression support. Offload support depends on `nft_offload_ctx`, `nft_flow_rule`, and Linux flow dissector keys.

## Risks and Test Signals

Risks concentrate around offset arithmetic, fragments, non-linear skbs, VLAN hardware acceleration, and checksum repair. Incorrect checksum flags can corrupt transport checksums; incorrect inner offset handling can read attacker-controlled wrong bytes. Test signals include nftables payload get/set tests, VLAN-tagged packets with hwaccel tags, fragmented IPv4 packets, TCP/UDP/SCTP checksum validation, GRE/IPIP encapsulation, and flowtable offload rules matching Ethernet/IP/port fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nft_payload.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nft_queue.c -->
# sources/distributed-fs/ceph-client/net/netfilter/nft_queue.c

## Purpose

`nft_queue.c` implements the nftables `queue` expression, which returns an `NF_QUEUE` verdict to send matching packets to nfnetlink_queue userspace consumers. It supports fixed queue numbers, register-supplied queue numbers, queue ranges, hash-based load distribution, CPU fanout, and bypass behavior.

## Important APIs, Types, and Functions

`struct nft_queue` stores queue register, base queue number, queue count, and flags. `nft_queue_eval()` handles fixed/ranged queues and uses either CPU modulo fanout or `nfqueue_hash()`. `nft_queue_sreg_eval()` uses a runtime queue id from `regs->data`. `nft_queue_validate()` restricts families and hooks to places with a queue continuation path. `nft_queue_select_ops()` chooses fixed or source-register operations and initializes `jhash_initval`.

## Control Flow

Rule creation rejects ambiguous fixed and register queue attributes. Fixed queue initialization validates `queues_total`, computes the highest queue id, checks `U16_MAX`, and stores optional flags. Register-based initialization validates a 32-bit register load and disallows CPU fanout because there is no static queue range. Evaluation computes the queue id, wraps it in `NF_QUEUE_NR()`, ORs bypass when configured, and writes the verdict code.

## State and Persistence Behavior

Expression configuration persists in `struct nft_queue`. The only global state is the read-mostly `jhash_initval` seed, initialized when operations are selected. Runtime evaluation does not retain packet state beyond setting `regs->verdict.code`.

## Dependencies and Integration Points

The module registers `nft_queue_type` with nf_tables and integrates with `nf_queue.h`, `nfqueue_hash()`, netfilter verdict encoding, and nfnetlink_queue userspace listeners. It supports IPv4, IPv6, inet, and bridge families but rejects netdev.

## Risks and Test Signals

Risks include invalid queue range arithmetic, unsupported hook placement, and queue bypass policy surprises when no userspace listener is present. Test with fixed queues, register queues, multi-queue fanout, CPU fanout, bypass enabled/disabled, bridge family rules, and attempts to attach queue rules to netdev ingress.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nft_queue.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nft_quota.c -->
# sources/distributed-fs/ceph-client/net/netfilter/nft_quota.c

## Purpose

`nft_quota.c` implements nftables quota matching both as a stateful expression and as a named nft object. It counts packet bytes against a configured quota, supports inverted matching, exposes consumed byte counters, supports reset-on-dump, and sends an object notification when a quota object becomes depleted.

## Important APIs, Types, and Functions

`struct nft_quota` contains an atomic quota limit, flags, and an allocated atomic consumed counter. `nft_overquota()` atomically adds `skb->len` and tests the boundary. `nft_quota_do_init()`, `nft_quota_do_dump()`, and `nft_quota_do_destroy()` are shared by expression and object paths. `nft_quota_obj_eval()` adds depletion notification via `nft_obj_notify()`. `nft_quota_clone()` duplicates stateful expression counters.

## Control Flow

Initialization requires `NFTA_QUOTA_BYTES`, rejects quota values above `S64_MAX`, rejects initially consumed values above quota, and rejects userspace setting the depleted flag. Evaluation always increments consumed bytes, then breaks evaluation when over quota XOR inverted. Object evaluation also computes a report condition when consumption reaches quota and sends a single notification guarded by `NFT_QUOTA_DEPLETED_BIT`. Dump optionally resets consumed bytes and clears depletion state.

## State and Persistence Behavior

Quota state persists across packets in atomic counters. Object updates replace quota and flags but leave the existing consumed counter in place. Expression clone allocates a new consumed counter and copies its value, preserving snapshot behavior for transaction cloning. Dump caps reported consumed bytes at quota even though internal consumed may exceed quota.

## Dependencies and Integration Points

The file integrates with nf_tables expression registration, nft object registration, netlink quota attributes, atomic64 counters, and nft object notifications. The expression is marked `NFT_EXPR_STATEFUL`; the object type is `NFT_OBJECT_QUOTA`.

## Risks and Test Signals

Risks include byte counter overflow assumptions, reset races with packet evaluation, notification storms if depleted state is mishandled, and confusing inclusive/exclusive boundary behavior: report at `>= quota`, overquota at `> quota`. Test quota objects and expressions with reset dumps, inverted rules, object update, clone/transaction paths, and packets crossing the quota exactly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nft_quota.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nft_range.c -->
# sources/distributed-fs/ceph-client/net/netfilter/nft_range.c

## Purpose

`nft_range.c` implements the nftables `range` expression. It compares register data against an inclusive byte range and either accepts values inside the range (`NFT_RANGE_EQ`) or outside the range (`NFT_RANGE_NEQ`) by breaking evaluation on mismatch.

## Important APIs, Types, and Functions

`struct nft_range_expr` stores `data_from`, `data_to`, source register, data length, and operation. `nft_range_eval()` performs two `memcmp()` comparisons against the register bytes. `nft_range_init()` parses nested nft data values, validates matching lengths, validates register load size, and accepts only EQ/NEQ operations. `nft_range_dump()` serializes the expression.

## Control Flow

Initialization requires all range attributes. It initializes the lower bound first, then the upper bound, releases already-initialized data on later errors, and stores the common length. Evaluation compares register bytes to both endpoints. EQ breaks when the register value is below `from` or above `to`; NEQ breaks when the value is inside the inclusive range.

## State and Persistence Behavior

All persistent state is immutable expression configuration after rule creation. There is no dynamic per-packet state except reads from registers and possible `NFT_BREAK` in the verdict register.

## Dependencies and Integration Points

The file depends on nf_tables core data parsing, register validation, and netlink nested data attributes. It is a generic expression module independent of protocol families; callers normally pair it with payload/meta/rt/socket expressions that populate registers.

## Risks and Test Signals

Risks are mostly semantic: `memcmp()` gives network-byte-order lexicographic comparison, so producers must load values in the intended byte order and length. Bounds with mismatched lengths are rejected. Test exact lower/upper boundary matches, one-byte and multi-register ranges, NEQ inversion, missing attributes, and register length validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nft_range.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nft_redir.c -->
# sources/distributed-fs/ceph-client/net/netfilter/nft_redir.c

## Purpose

`nft_redir.c` implements nftables NAT redirect expressions for IPv4, IPv6, and inet families. Redirect rewrites packet destination to a local address, optionally using protocol port ranges loaded from registers.

## Important APIs, Types, and Functions

`struct nft_redir` stores source registers for min/max protocol ports and NAT range flags. `nft_redir_validate()` requires NAT chain type and restricts hooks to prerouting and local output. `nft_redir_init()` parses port registers and flags and obtains conntrack/NAT namespace support with `nf_ct_netns_get()`. `nft_redir_eval()` builds `struct nf_nat_range2` and dispatches to `nf_nat_redirect_ipv4()` or `nf_nat_redirect_ipv6()`.

## Control Flow

On rule creation, optional min/max protocol registers imply `NF_NAT_RANGE_PROTO_SPECIFIED`; missing max defaults to min. Evaluation zeroes a NAT range, fills flags and optional port range, switches on packet family, and stores the NAT helper verdict. Module init registers IPv4, optionally IPv6, and optionally inet expression types, unwinding prior registrations on failure.

## State and Persistence Behavior

The expression keeps only register and flag configuration. NAT connection persistence is owned by conntrack/NAT subsystems, not this file. Namespace references acquired at init are released by family-specific destroy callbacks.

## Dependencies and Integration Points

Dependencies include nf_tables, `nf_nat.h`, `nf_nat_redirect.h`, conntrack namespace reference management, and family-specific NAT redirect helpers. The expression is only valid in NAT chains, so it integrates with nft chain dependency validation.

## Risks and Test Signals

Risks include losing `NF_NAT_RANGE_PROTO_SPECIFIED` when flags are overwritten by `NFTA_REDIR_FLAGS`, invalid hook use, family dispatch surprises in inet chains, and namespace reference leaks on registration or destroy errors. Test IPv4/IPv6/inet redirect, port min-only and min/max registers, NAT chain validation, local-output vs prerouting behavior, and module unload cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nft_redir.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nft_reject.c -->
# sources/distributed-fs/ceph-client/net/netfilter/nft_reject.c

## Purpose

`nft_reject.c` provides shared reject expression policy, initialization, dumping, hook validation, and ICMPX-to-family-code mapping used by family-specific reject implementations.

## Important APIs, Types, and Functions

Exported symbols include `nft_reject_policy`, `nft_reject_validate()`, `nft_reject_init()`, `nft_reject_dump()`, `nft_reject_icmp_code()`, and `nft_reject_icmpv6_code()`. The private data type is `struct nft_reject` from `nft_reject.h`, storing reject type and ICMP code.

## Control Flow

Initialization requires `NFTA_REJECT_TYPE`. ICMP and ICMPX unreachable modes require `NFTA_REJECT_ICMP_CODE`; ICMPX codes are range-checked against `NFT_REJECT_ICMPX_MAX`. TCP reset requires no code. Dump emits type and emits code only for unreachable modes. Shared validation allows local-in, forward, local-out, and prerouting hooks.

## State and Persistence Behavior

State is immutable expression configuration. ICMP mapping arrays are static module data. The file performs no packet mutation or verdict setting by itself; family modules call the helpers.

## Dependencies and Integration Points

This module exports helper symbols to IPv4, IPv6, inet, bridge, and netdev reject modules. It depends on nf_tables netlink policies and Linux ICMP/ICMPv6 constants.

## Risks and Test Signals

Risks include accepting invalid ICMPX codes, mismatched family mapping, or using reject in hooks where generated errors are invalid. Test reject rule creation for each type, invalid codes, dump round trips, and family modules' use of ICMPX mappings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nft_reject.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nft_reject_inet.c -->
# sources/distributed-fs/ceph-client/net/netfilter/nft_reject_inet.c

## Purpose

`nft_reject_inet.c` implements the inet-family nftables `reject` expression. It emits IPv4 or IPv6 ICMP unreachable messages or TCP resets according to the packet family, then drops the original packet.

## Important APIs, Types, and Functions

`nft_reject_inet_eval()` dispatches on `nft_pf(pkt)` and `priv->type`. It calls `nf_send_unreach()`, `nf_send_reset()`, `nf_send_unreach6()`, or `nf_send_reset6()`. The expression ops reuse shared `nft_reject_init()`, `nft_reject_dump()`, and `nft_reject_policy`.

## Control Flow

Evaluation switches first on IPv4 versus IPv6. For raw ICMP unreachable it uses the configured code; for TCP reset it sends a reset through the family helper; for ICMPX it maps generic codes to family-specific ICMP constants. It always sets `regs->verdict.code = NF_DROP`. Validation permits local-in, forward, local-out, prerouting, and ingress hooks for inet.

## State and Persistence Behavior

Persistent state is just reject type and ICMP code. Generated response packets and TCP reset construction are delegated to nf_reject helpers. No cross-packet state is kept.

## Dependencies and Integration Points

The file integrates with the shared reject module, nf_tables inet family registration, IPv4 and IPv6 reject helpers, packet hook metadata, and socket metadata for reset generation.

## Risks and Test Signals

Risks include incorrect family dispatch in inet chains, generated replies in unsupported hook contexts, and TCP reset helper behavior when socket metadata is absent. Test IPv4 and IPv6 ICMP unreachable, ICMPX mappings, TCP reset, ingress hook validation, and packet capture of generated errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nft_reject_inet.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nft_reject_netdev.c -->
# sources/distributed-fs/ceph-client/net/netfilter/nft_reject_netdev.c

## Purpose

`nft_reject_netdev.c` implements reject support for netdev ingress. Because netdev hooks operate before normal IP stack output context, it builds reject packets with nf_reject helpers, adds an Ethernet header, queues them on the ingress device, and drops the original packet.

## Important APIs, Types, and Functions

`nft_reject_queue_xmit()` creates the L2 header with swapped old Ethernet addresses and calls `dev_queue_xmit()`. Family helpers wrap `nf_reject_skb_v4_tcp_reset()`, `nf_reject_skb_v4_unreach()`, `nf_reject_skb_v6_tcp_reset()`, and `nf_reject_skb_v6_unreach()`. `nft_reject_netdev_eval()` dispatches by Ethernet protocol and reject type.

## Control Flow

Evaluation ignores broadcast and multicast destination frames and simply drops them. For IPv4 and IPv6 unicast frames it generates ICMP unreachable, TCP reset, or ICMPX-mapped unreachable as requested. Unsupported EtherTypes fall through to drop without a generated response. Validation restricts the expression to `NF_NETDEV_INGRESS`.

## State and Persistence Behavior

There is no dynamic persistent state. The expression stores reject type/code. Response skbs are transient and immediately transmitted; the original skb receives an `NF_DROP` verdict.

## Dependencies and Integration Points

Dependencies include Ethernet helpers, netdevice transmit, shared nft reject helpers, nf_reject IPv4/IPv6 skb constructors, and nf_tables netdev family registration.

## Risks and Test Signals

Risks include malformed Ethernet headers, generating replies to multicast/broadcast traffic, wrong ingress device selection, and behavior for non-IP EtherTypes. Test netdev ingress reject rules with IPv4, IPv6, TCP reset, ICMPX codes, multicast/broadcast frames, and packet captures confirming L2 source/destination handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nft_reject_netdev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nft_rt.c -->
# sources/distributed-fs/ceph-client/net/netfilter/nft_rt.c

## Purpose

`nft_rt.c` implements the nftables `rt` expression, which reads route-derived metadata into registers: route class id, IPv4 or IPv6 nexthop, TCP MSS estimate, and optional XFRM presence.

## Important APIs, Types, and Functions

`struct nft_rt` stores selected `enum nft_rt_keys` and destination register. `nft_rt_get_eval()` reads `skb_dst()` and fills the register. `get_tcpmss()` derives a conservative MSS from the current dst MTU and a reverse route lookup to the packet source. `nft_rt_get_init()` maps keys to register store lengths. `nft_rt_validate()` restricts families and TCPMSS hook placement.

## Control Flow

Evaluation fails with `NFT_BREAK` when the skb has no dst or the key is incompatible with packet family. Nexthop reads use `rt_nexthop()` for IPv4 and `rt6_nexthop()` for IPv6. TCPMSS computes a minimum of current route MTU and reverse-route MTU, subtracting minimum IP+TCP header sizes, with `TCP_MSS_DEFAULT` fallback. Initialization rejects unsupported compile-time keys when their configs are absent.

## State and Persistence Behavior

The expression stores static key/register configuration only. It reads live route state from dst entries and may perform a transient route lookup. It does not retain dst references beyond the helper-local reverse lookup release.

## Dependencies and Integration Points

Dependencies include dst entries, IPv4 and IPv6 routing, XFRM conditional fields, nf_tables register validation, and chain hook validation. It is normally used before comparisons or payload modification rules.

## Risks and Test Signals

Risks include missing dst metadata in early hooks, stale route assumptions, TCPMSS use in hooks without meaningful egress route state, and conditional build coverage for classid/XFRM. Test IPv4/IPv6 nexthop reads, TCPMSS in forward/local-out/postrouting, no-dst packets, XFRM-enabled routes, and config variants without route classid or XFRM.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nft_rt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nft_set_bitmap.c -->
# sources/distributed-fs/ceph-client/net/netfilter/nft_set_bitmap.c

## Purpose

`nft_set_bitmap.c` implements a compact O(1) nftables set backend for small integer keys of one or two bytes. A two-bit bitmap records element active state across current and next nftables generations while a list holds full element extensions for API operations.

## Important APIs, Types, and Functions

`struct nft_bitmap` contains the element list and bitmap bytes. `struct nft_bitmap_elem` contains `nft_elem_priv`, list node, and extension block. `nft_bitmap_lookup()` tests the bitmap only and returns a static found extension for set membership. `nft_bitmap_insert()`, `nft_bitmap_deactivate()`, `nft_bitmap_activate()`, `nft_bitmap_flush()`, and `nft_bitmap_remove()` update generation bits and list membership. `nft_bitmap_estimate()` accepts only key lengths up to two bytes and no element expressions.

## Control Flow

Key bytes map to a two-bit location by shifting the numeric key left by one. Insert checks for an active duplicate in the next generation, sets the next-generation active bit, and appends the element to the RCU list. Deactivate clears the next-generation bit and toggles element active metadata. Abort/commit behavior is driven by nf_tables generation handling via backend callbacks.

## State and Persistence Behavior

Persistent state is the bitmap plus RCU list of element extensions. The two-bit encoding distinguishes stable active, stable inactive, pending insert, and pending delete states across transactions. Lookups intentionally do not return per-element extensions; maps, objects, timeouts, and expressions are not supported by the estimate path.

## Dependencies and Integration Points

The backend integrates with nf_tables set type registration through exported `nft_set_bitmap_type`, nft generation masks, RCU list walking, and element destroy helpers.

## Risks and Test Signals

Risks include endian-sensitive key interpretation, bitmap bounds for two-byte keys, generation-bit mistakes during abort/commit, and stale list entries after remove. Test one-byte and two-byte sets, duplicate insert, delete/abort, flush, walk/get, and backend selection avoiding maps or expression-bearing sets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nft_set_bitmap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nft_set_hash.c -->
# sources/distributed-fs/ceph-client/net/netfilter/nft_set_hash.c

## Purpose

`nft_set_hash.c` implements three nftables hash set backends: fixed hash, fixed hash fast path for 32-bit keys, and resizable `rhashtable` for dynamic sets with timeouts and expression evaluation.

## Important APIs, Types, and Functions

`struct nft_rhash` wraps `rhashtable` and delayed GC work; `struct nft_rhash_elem` adds rhash node, walk node, GC sequence, and extensions. `nft_rhash_lookup()`, `nft_rhash_update()`, `nft_rhash_delete()`, and `nft_rhash_gc()` serve dynamic sets. `struct nft_hash` stores seed and bucket array for fixed sets; `nft_hash_lookup()`, `nft_hash_lookup_fast()`, and `nft_hash_insert()` serve declared-size sets. The exported set types are `nft_set_rhash_type`, `nft_set_hash_type`, and `nft_set_hash_fast_type`.

## Control Flow

Resizable lookup constructs a compare argument with key, generation mask, and timestamp; the rhashtable comparator rejects dead, expired, inactive, or mismatched elements. Dynamic update first looks up any-generation element, otherwise creates a dynset element and races insertion with `rhashtable_lookup_get_insert_key()`. GC walks the rhashtable, marks expired/dead or expression-needing-GC entries, batches them into async transactions, and reschedules itself. Fixed hash uses jhash plus reciprocal bucket scaling and RCU hlist traversal.

## State and Persistence Behavior

Resizable hash state persists in the rhashtable and delayed work item; GC sequence fields avoid double-queuing elements during unstable walks. Fixed hash state is a seeded bucket table sized from the declared element hint. Element active/dead/expired state lives in nf_tables extensions.

## Dependencies and Integration Points

Dependencies include Linux rhashtable, jhash, workqueues, nf_tables dynset helpers, set GC transaction APIs, RCU, and nft generation masks. The rhash backend supports maps, objects, timeouts, and evaluated element expressions; fixed hash supports maps and objects but not timeouts.

## Risks and Test Signals

Risks include missing NULL checks after deactivate lookup, rhashtable walk `-EAGAIN` handling, races between dynset insertion and GC, walk-list recursion during validation, and hash collision behavior. Test dynamic sets with timeouts, dynset update races, expression GC, fixed-size hash selection, 32-bit fast lookup, deletion, flush, and module teardown canceling delayed work.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nft_set_hash.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nft_set_pipapo.c -->
# sources/distributed-fs/ceph-client/net/netfilter/nft_set_pipapo.c

## Purpose

`nft_set_pipapo.c` implements the PIPAPO nftables set backend for concatenated interval/range keys. It converts ranges to netmask-like rule expansions, classifies packet fields through lookup-table bucket intersections, maps matching rules across fields, and supports maps, objects, timeouts, transactions, GC, and optional AVX2 acceleration.

## Important APIs, Types, and Functions

The exported types are `nft_set_pipapo_type` and, on x86-64, `nft_set_pipapo_avx2_type`. Lookup flows through `nft_pipapo_lookup()`, `pipapo_get_slow()`, and control-plane `nft_pipapo_get()`. Insertion uses `nft_pipapo_insert()`, `pipapo_expand()`, `pipapo_insert()`, and `pipapo_map()`. Transaction state is managed by `pipapo_maybe_clone()`, `pipapo_clone()`, `nft_pipapo_commit()`, and `nft_pipapo_abort()`. Removal and GC use `pipapo_drop()`, `nft_pipapo_remove()`, `pipapo_gc_scan()`, and `pipapo_gc_queue()`.

## Control Flow

Initialization creates an empty active match object with one field per concatenated component and per-CPU scratch pointers. Insertions operate on a mutable clone, reject exact duplicates and partial overlaps, validate per-field start/end ordering, expand each field range into one or more rules, resize lookup/mapping tables, ensure scratch capacity, and map final rules to the inserted element. Datapath lookup reads only the active RCU match copy and uses generation mask zero because pending elements live only in the clone. Commit optionally scans expired entries in the clone, atomically swaps clone into `match`, frees the old copy after RCU, and queues collected elements.

## State and Persistence Behavior

Persistent set state is split between active `match` and pending `clone`. Each field owns lookup tables, mapping tables, rule counts, allocation size, group width, and per-CPU scratch maps. Table group width dynamically switches between four-bit and eight-bit buckets based on size thresholds. Timeouts are collected opportunistically on commit rather than by periodic work.

## Dependencies and Integration Points

The backend depends on nf_tables set APIs, generation masks, set element extensions, transaction GC helpers, per-CPU local locks, bitmap helpers, RCU, and the optional AVX2 header. It is selected for interval sets with at least two concatenated fields.

## Risks and Test Signals

Risks include range expansion overflow, mapping-table compaction errors, clone/commit generation mismatches, scratch reallocation on possible CPUs, overlap detection, endian-sensitive range expansion, and timeout GC only running when commits occur. Test concatenated IPv4/port and IPv6 ranges, exact duplicate versus partial overlap, add/delete/abort/commit, timeout expiry, maps/objects, AVX2 and non-AVX2 kernels, and memory pressure paths in resize/clone.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nft_set_pipapo.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nft_set_pipapo.h -->
# sources/distributed-fs/ceph-client/net/netfilter/nft_set_pipapo.h

## Purpose

`nft_set_pipapo.h` defines the shared constants, data structures, sizing logic, and generic inline bucket operations for the PIPAPO set backend and its AVX2 companion.

## Important APIs, Types, and Functions

Key constants define maximum fields, minimum concatenation count, maximum field bytes, four-bit/eight-bit group widths, lookup-table size thresholds, mapping-table bit packing, and alignment headroom. Core types include `union nft_pipapo_map_bucket`, `struct nft_pipapo_field`, `struct nft_pipapo_scratch`, `struct nft_pipapo_match`, `struct nft_pipapo`, and `struct nft_pipapo_elem`. Shared helpers include `pipapo_refill()` declaration, `pipapo_and_field_buckets_4bit()`, `pipapo_and_field_buckets_8bit()`, `pipapo_estimate_size()`, and `pipapo_resmap_init()`.

## Control Flow

The header's inline matching helpers walk lookup-table groups and intersect the current result bitmap with the bucket selected by input bytes. Sizing estimates iterate set fields and compute worst-case rule expansion and mapping cost. Alignment macros become AVX2-aware when included after `nft_set_pipapo_avx2.h`.

## State and Persistence Behavior

The structures define all durable PIPAPO state: active and clone match pointers, per-field lookup/mapping tables, per-CPU scratch maps, and GC queues. Scratch `map_index` persists per CPU to alternate two working maps between lookups.

## Dependencies and Integration Points

The header depends on nf_tables register counts, IPv6 address sizing, bit operations, and optional architecture alignment. It is included by both generic and AVX2 implementations and must keep layout compatible with nf_tables element private casting.

## Risks and Test Signals

Risks include integer overflow in size estimates, layout drift that breaks `offsetof(..., priv) == 0` assumptions, wrong bucket grouping math, and alignment mismatches between generic and AVX2 code. Test build coverage across 32-bit and 64-bit, x86-64 AVX2 and non-AVX2, large field counts, IPv6-sized fields, and estimator/backend selection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nft_set_pipapo.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nft_set_pipapo_avx2.c -->
# sources/distributed-fs/ceph-client/net/netfilter/nft_set_pipapo_avx2.c

## Purpose

`nft_set_pipapo_avx2.c` provides x86-64 AVX2 vectorized lookup routines for the PIPAPO set backend. It accelerates bucket intersection and refill loops for common field widths while preserving the same mapping-table semantics as the generic implementation.

## Important APIs, Types, and Functions

Public functions are `nft_pipapo_avx2_estimate()`, `pipapo_get_avx2()`, and `nft_pipapo_avx2_lookup()`. Internal helpers include AVX2 load/AND/store/test macros, `nft_pipapo_avx2_refill()`, specialized lookup bodies for 4-bit and 8-bit grouping with 1, 2, 4, 6, 8, 12, 16, or 32 groups, and `nft_pipapo_avx2_lookup_slow()` for uncommon sizes.

## Control Flow

Datapath lookup disables BH, verifies FPU usability, RCU-dereferences active match data, and calls `pipapo_get_avx2()` or falls back to generic lookup. `pipapo_get_avx2()` locks the per-CPU scratch map, starts kernel FPU usage with a minimal mask, clears a YMM zero register, runs one specialized field function per field, and maps/refills results until it reaches a final element. Expired or inactive final elements are skipped by continuing refill on the remaining result bitmap.

## State and Persistence Behavior

The implementation uses the same `nft_pipapo_match`, field tables, mapping tables, and per-CPU scratch maps as generic PIPAPO. It does not own persistent state, but it depends on lookup tables being aligned to `NFT_PIPAPO_ALIGN` and bucket sizes being multiples of YMM-width longs.

## Dependencies and Integration Points

Dependencies include x86 FPU APIs, AVX2 CPU feature checks, inline assembly, `nft_set_pipapo.h`, and nf_tables set lookup contracts. Backend selection is exposed through `nft_set_pipapo_avx2_type` in the generic file when the architecture supports it.

## Risks and Test Signals

Risks include FPU use in invalid contexts, missing `kernel_fpu_end()` on error paths, alignment or bucket-size assumptions, inline assembly clobber mistakes, and divergence from generic semantics for expired/inactive elements. Test AVX2-capable and non-AVX2 systems, `irq_fpu_usable()` fallback paths, common IPv4/IPv6/port/MAC concatenations, timeout expiry during lookup, and comparison against generic backend results.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nft_set_pipapo_avx2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nft_set_pipapo_avx2.h -->
# sources/distributed-fs/ceph-client/net/netfilter/nft_set_pipapo_avx2.h

## Purpose

`nft_set_pipapo_avx2.h` is the architecture gate and public declaration header for the PIPAPO AVX2 implementation.

## Important APIs, Types, and Functions

When building for x86-64 outside UML, it includes xstate definitions, sets `NFT_PIPAPO_ALIGN` to the YMM save-area size in bytes, forward-declares `struct nft_pipapo_match`, and declares `nft_pipapo_avx2_estimate()` and `pipapo_get_avx2()`.

## Control Flow

The header has no runtime control flow. Its compile-time condition controls whether generic PIPAPO sees AVX2 alignment requirements and whether AVX2 declarations are available.

## State and Persistence Behavior

No state is stored here. The alignment macro affects allocation layout for lookup tables and scratch maps in the generic implementation.

## Dependencies and Integration Points

It integrates with `nft_set_pipapo.c`, `nft_set_pipapo_avx2.c`, x86 `xstate.h`, and nf_tables set estimation. Non-x86 or UML builds compile without declarations and use generic PIPAPO only.

## Risks and Test Signals

Risks are compile-time: wrong architecture gating, missing alignment propagation, or declaration drift from the C implementation. Test x86-64 AVX2 builds, UML builds, non-x86 builds, and object files with and without `CONFIG_X86_64`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nft_set_pipapo_avx2.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nft_set_rbtree.c -->
# sources/distributed-fs/ceph-client/net/netfilter/nft_set_rbtree.c

## Purpose

`nft_set_rbtree.c` implements an interval-capable nftables set backend using an rb-tree for updates and a compact RCU-published sorted interval array for fast lookups.

## Important APIs, Types, and Functions

`struct nft_rbtree` owns the rb root, rwlock, active interval array, pending array, GC state, and overlap cookies. `struct nft_rbtree_elem` stores each interval boundary. Lookup uses `nft_rbtree_lookup()` and `bsearch()` over `struct nft_array_interval`. Updates use `nft_rbtree_insert()`, `__nft_rbtree_insert()`, `nft_rbtree_deactivate()`, `nft_rbtree_remove()`, and `nft_rbtree_commit()`. GC uses `nft_rbtree_gc_scan()` and `nft_rbtree_gc_queue()`.

## Control Flow

Insert allocates or resizes the pending interval array, then takes the write lock and walks the rb-tree to detect exact duplicates and partial overlaps, collecting expired elements as needed. Accepted elements are linked into the rb-tree in reversed ordering. Commit rebuilds `array_next` by reverse-walking the tree from smallest to largest logical interval, publishes it with RCU, frees the old array later, and queues expired elements. Read lookup never walks the tree; it binary-searches the current array and rejects expired starts.

## State and Persistence Behavior

Persistent state exists in both the mutable rb-tree and immutable lookup array. `array_next` is transaction state and is discarded on abort. Expired elements are moved to `expired` and freed after a new array is public. Start cookies correlate paired start/end operations for interval validation across a transaction timestamp.

## Dependencies and Integration Points

The backend integrates with rbtrees, rwlocks, RCU, bsearch, nf_tables interval semantics, generation masks, timeout GC, and set size hiding via `ksize`, `usize`, and `adjust_maxsize`.

## Risks and Test Signals

Risks include overlap detection mistakes, array rebuild capacity errors, reversed ordering confusion, stale array readers, anonymous adjacent interval packing, and GC removing interval ends before starts. Test interval add/delete, anonymous packed intervals, duplicate and partial overlap errors, timeout expiry, abort/commit, read lookup during updates, and max-size accounting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nft_set_rbtree.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nft_socket.c -->
# sources/distributed-fs/ceph-client/net/netfilter/nft_socket.c

## Purpose

`nft_socket.c` implements the nftables `socket` expression, which looks up the socket associated with a packet and stores socket attributes such as transparent flag, mark, wildcard bind status, or cgroup v2 id into a register.

## Important APIs, Types, and Functions

`struct nft_socket` stores key, cgroup level, output length, and destination register. `nft_socket_eval()` is the main evaluator. `nft_socket_do_lookup()` performs slow socket lookup for IPv4 or IPv6 when `skb->sk` is absent or from another net namespace. `nft_socket_wildcard()` checks whether the socket is bound to wildcard IPv4/IPv6 address. `nft_sock_get_eval_cgroupv2()` and `nft_socket_cgroup_subtree_level()` implement optional cgroup v2 extraction.

## Control Flow

Initialization restricts family to IPv4, IPv6, or inet, validates selected key, computes output size, and for cgroup v2 translates a user subtree level relative to the cgroup root visible in process context. Evaluation validates `skb->sk` namespace, falls back to nf_socket slow lookup using ingress device, breaks if no socket is found, then stores the selected attribute. Slow lookup references are released with `sock_gen_put()` when they are not the skb-owned socket.

## State and Persistence Behavior

The expression keeps static key/register/level configuration. It does not retain socket references after evaluation. Cgroup output is a copied 64-bit cgroup id; mark and transparent/wildcard reads are snapshots of live socket state.

## Dependencies and Integration Points

Dependencies include nf_tables, nf_socket lookup helpers, inet socket state, TCP headers indirectly through lookup, cgroup socket data when configured, and hook validation for prerouting, local-in, and local-out.

## Risks and Test Signals

Risks include reference leaks on slow lookup, use on packets without ingress device, net namespace mismatches, non-full sockets for mark/wildcard/cgroup reads, and cgroup level overflow. Test transparent proxy sockets, socket marks, wildcard binds for IPv4 and IPv6, cgroup v2 IDs, local-out packets with `skb->sk`, prerouting slow lookup, and unsupported family/hook rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nft_socket.c -->
