<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mpls/af_mpls.c -->
# sources/distributed-fs/ceph-client/net/mpls/af_mpls.c

## Purpose
Implements the MPLS address-family core for the kernel networking stack. It owns MPLS packet receive/forwarding, LFIB route storage, route netlink operations, MPLS per-device state, MPLS netconf/sysctl exposure, per-network-namespace MPLS platform-label tables, and module registration for packet handling, rtnetlink, rtnl address-family stats, netdevice events, and optional MPLS-over-GRE encap sizing.

## Important APIs, Types, and Functions
The main packet path is `mpls_forward()`, registered as a packet handler for `ETH_P_MPLS_UC`. `mpls_route_input_rcu()`, `mpls_platform_label_rcu()`, `mpls_select_multipath()`, `mpls_egress()`, and `mpls_multipath_hash()` implement route lookup, RCU-safe table reads, ECMP selection, penultimate-hop pop egress, and hash selection over labels or inner IP headers. Route construction and mutation flow through `rtm_to_route_config()`, `mpls_route_add()`, `mpls_route_del()`, `mpls_rt_alloc()`, `mpls_nh_build*()`, and `mpls_route_update()`. Netlink dump/get/notify paths use `mpls_dump_route()`, `mpls_dump_routes()`, `mpls_getroute()`, and `rtmsg_lfib()`. Device and namespace state is handled by `mpls_add_dev()`, `mpls_dev_notify()`, `resize_platform_label_table()`, `mpls_net_init()`, and `mpls_net_exit()`. Exported helpers include `mpls_output_possible()`, `mpls_dev_mtu()`, `mpls_pkt_too_big()`, `mpls_stats_inc_outucastpkts()`, `nla_put_labels()`, and `nla_get_labels()`.

## Control Flow
Incoming MPLS frames are accepted only on devices with an `mpls_dev` and enabled input. The packet path decodes the top shim, looks up the label under RCU, selects a live nexthop, pops the top label, rejects bad TTL/LRO/MTU/headroom cases, then either performs PHP egress to IPv4/IPv6 or pushes replacement labels before neighbor transmit. Route add netlink messages are parsed into `mpls_route_config`, validated against MPLS-specific rtmsg restrictions, allocated as one contiguous `mpls_route` plus nexthop/via blocks, then installed under `net->mpls.platform_mutex` using RCU pointer replacement. Netdevice events mark nexthops dead/linkdown, clone routes when unregistering one nexthop from multipath routes, delete routes with no remaining nexthops, and recreate per-device sysctl paths on rename. `platform_labels` sysctl resizes the LFIB table, populating explicit-null IPv4 and IPv6 labels to loopback when the table is large enough.

## State and Persistence
Persistent namespace state lives in `net->mpls`: platform-label RCU array, label count, seqcount, mutex, global TTL propagation/default TTL, and sysctl header. Per-device persistent state is `struct mpls_dev`, including input flag, stats, and device sysctl. Routes own references to output devices through `netdev_hold()` and release them from RCU callbacks. Per-CPU MPLS link counters are updated in forwarding paths and exported through rtnl AF stats. Route objects and label tables are volatile kernel state controlled by sysctl/netlink, not durable storage.

## Dependencies and Integration Points
Depends on core netdevice, rtnetlink, neighbor, IPv4/IPv6 route lookup, packet handlers, sysctl, netconf notifications, pernet operations, GSO helpers, MPLS UAPI, and optional IP tunnel encap APIs. It integrates with `mpls_iptunnel.c` through exported label and output helpers, with `mpls_gso.c` through MPLS GSO expectations, with user space via route netlink and `/proc/sys/net/mpls`, and with netdevice lifecycle events through the notifier.

## Risks
The forwarding path is RCU-sensitive while device events mutate nexthop flags under rtnl/mutex protection. Multipath alive counts and `READ_ONCE()` flag usage must stay consistent or traffic can select dead nexthops. LFIB resizing must preserve old entries, publish table pointer/count atomically with the seqcount, and free old tables after an RCU grace period. Netlink label parsing is strict about BOS, TTL, TC, and implicit-null labels; relaxing it can permit invalid encap. MTU calculations subtract pushed-label headroom and can underflow conceptually if changed without care. Device unregister route cloning must keep netdev references balanced. Netconf/sysctl table copies must free copied tables exactly once.

## Test Signals
Useful signals include `ip -f mpls route add/del/get/show`, multipath route dumps and hash selection, route replace/excl/create error paths, sysctl resize of `platform_labels`, explicit-null behavior for labels 0 and 2, per-interface `net/mpls/conf/*/input` notifications, device down/up/unregister/rename while routes reference the device, MPLS MTU/GSO oversized traffic, PHP to IPv4 and IPv6 with TTL propagation enabled and disabled, and rtnl group notifications for MPLS route/netconf changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mpls/af_mpls.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mpls/internal.h -->
# sources/distributed-fs/ceph-client/net/mpls/internal.h

## Purpose
Defines private MPLS data structures and helpers shared by MPLS core, GSO, and lightweight tunnel support. It centralizes route/nexthop layout, decoded label representation, per-device state, counter update macros, payload type constants, and netlink label helper prototypes.

## Important APIs, Types, and Functions
`struct mpls_entry_decoded` holds decoded label, TTL, traffic class, and BOS. `struct mpls_dev` stores per-netdevice MPLS enablement, stats, sysctl, and RCU freeing. `struct mpls_nh` and `struct mpls_route` define the contiguous LFIB route memory layout. `MPLS_NH_VIA_OFF()`, `MPLS_NH_SIZE()`, `for_nexthops()`, and `change_nexthops()` encode iteration and alignment rules. `mpls_entry_decode()`, `mpls_dev_rcu()`, and `mpls_dev_get()` are inline helpers. Prototypes expose `nla_put_labels()`, `nla_get_labels()`, `mpls_output_possible()`, `mpls_dev_mtu()`, `mpls_pkt_too_big()`, and `mpls_stats_inc_outucastpkts()`.

## Control Flow
This header has no runtime control flow beyond inline decode and RCU dereference helpers. Its macros shape the route allocation and iteration control flow used by `af_mpls.c`: every route contains a fixed-size sequence of nexthop records, each followed by an aligned via address area whose offset is computed from the route's maximum label and address sizes.

## State and Persistence
No global state is defined. The header specifies the persistent in-memory state owned elsewhere: `mpls_dev` attached to `net_device::mpls_ptr`, per-CPU link stats, and `mpls_route` objects stored in namespace LFIB arrays. The stat macros select different synchronization strategies for 32-bit versus 64-bit architectures.

## Dependencies and Integration Points
Depends on `<net/mpls.h>`, netdevice RCU pointers, netlink attributes, and kernel per-CPU stat synchronization. It is consumed by `af_mpls.c` and `mpls_iptunnel.c`, and its exported prototypes also serve MPLS tunnel code that needs label serialization and output feasibility checks.

## Risks
The route memory layout is ABI-like inside the module: offset and size macros must stay synchronized with allocation, nexthop iteration, and via access. `rt_nh_size` and `rt_via_offset` are `u8`, so allocation limits in `af_mpls.c` are part of the safety contract. Counter macros assume a valid allocated per-CPU stats pointer and correct BH/seqcount protection on 32-bit systems.

## Test Signals
Compile-time coverage from MPLS core and tunnel modules is the main header signal. Runtime signals include correct route dumps for multipath nexthops with labels/via addresses, no KASAN/alignment faults under route add/delete, and correct per-device stats on 32-bit and 64-bit builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mpls/internal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mpls/mpls_gso.c -->
# sources/distributed-fs/ceph-client/net/mpls/mpls_gso.c

## Purpose
Registers Generic Segmentation Offload support for MPLS unicast and multicast Ethernet protocol types. It temporarily exposes the inner packet to the generic GSO machinery, then restores MPLS headers and skb metadata on each output segment.

## Important APIs, Types, and Functions
`mpls_gso_segment()` is the packet offload callback. `mpls_uc_offload` and `mpls_mc_offload` are `struct packet_offload` registrations for `ETH_P_MPLS_UC` and `ETH_P_MPLS_MC`. `mpls_gso_init()` adds both offloads with `dev_add_offload()`, and `mpls_gso_exit()` removes them.

## Control Flow
The callback requires an inner network header, computes the MPLS header length between current and inner network headers, validates that it is non-zero, pullable, and a multiple of `MPLS_HLEN`, then changes `skb->protocol` to the inner protocol and pulls the MPLS stack. It segments with `skb_mac_gso_segment()` using `skb->dev->mpls_features & features`. On failure it unwinds protocol/header state. On success it iterates each segment, restores MPLS protocol, resets inner/network/mac headers, and pushes back the original MAC plus MPLS header length.

## State and Persistence
The module stores only static offload descriptors. Per-packet state is skb header offsets, protocol, mac length, inner protocol, and segment chain metadata. No durable state or sysctl exists here.

## Dependencies and Integration Points
Depends on the GSO core, packet offload registration, `skbuff` header manipulation, `netdev_features_t`, and MPLS EtherTypes. It complements `af_mpls.c` and `mpls_iptunnel.c`, allowing MPLS-encapsulated packets to be segmented according to inner protocol capabilities advertised in `dev->mpls_features`.

## Risks
Correctness depends on valid inner header metadata being set by the encapsulation path. Header length arithmetic must restore exactly the bytes pulled before segmentation. Bad MPLS header length validation can corrupt skb layout. Device `mpls_features` must be set conservatively; otherwise inner segmentation can produce segments unsupported by the output device.

## Test Signals
Exercise large TCP payloads over MPLS with GSO enabled and disabled, both unicast and multicast MPLS EtherTypes, invalid or missing inner header metadata, multi-label stacks, segmentation failure unwind paths, and packet captures verifying each segment retains the expected MPLS stack and inner protocol.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mpls/mpls_gso.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mpls/mpls_iptunnel.c -->
# sources/distributed-fs/ceph-client/net/mpls/mpls_iptunnel.c

## Purpose
Implements MPLS lightweight tunnel encapsulation for IP routes. It parses MPLS tunnel netlink attributes, builds `lwtunnel_state`, pushes MPLS labels during route transmit, handles TTL propagation/default TTL policy, emits tunnel state back to netlink, and registers the MPLS lwtunnel ops.

## Important APIs, Types, and Functions
`mpls_xmit()` is the lwtunnel transmit hook. `mpls_build_state()` parses `MPLS_IPTUNNEL_DST` and optional `MPLS_IPTUNNEL_TTL` into `struct mpls_iptunnel_encap`. `mpls_fill_encap_info()`, `mpls_encap_nlsize()`, and `mpls_encap_cmp()` support route dump/compare. `mpls_iptun_ops` registers the lwtunnel methods with `lwtunnel_encap_add_ops()`.

## Control Flow
Netlink build validates the nested policy, requires a destination label stack, counts labels using `nla_get_labels()`, allocates enough state for the variable label array, fills labels, and sets TTL propagation mode. Transmit resolves the output device from `skb_dst()`, rejects unsupported devices or LRO, chooses TTL from IPv4 TTL, IPv6 hop limit, per-lwt default, or namespace default according to propagation settings, checks MPLS MTU after label insertion, ensures headroom, records inner protocol/network header, pushes labels with BOS on the bottom entry, updates stats, then sends through ARP or ND depending on IPv4/IPv6 route gateway details including 6PE v4-mapped IPv6 gateways.

## State and Persistence
Per-route tunnel state is stored in `lwtunnel_state` with variable-length `mpls_iptunnel_encap`: labels, default TTL, and TTL propagation mode. The file itself has no global mutable state beyond the registered lwtunnel ops. Runtime stats are updated on the output MPLS device or IP counters through helpers in `af_mpls.c`.

## Dependencies and Integration Points
Depends on lwtunnel infrastructure, route and destination entries, IPv4/IPv6 routing structs, neighbor transmit, MPLS label netlink helpers, output feasibility/MTU/stats helpers, and UAPI MPLS tunnel attributes. It integrates with `ip route ... encap mpls ...` user operations and soft-depends on `mpls_gso` for offload support.

## Risks
Transmit assumes `dst->ops->family` is AF_INET or AF_INET6 and that route gateway fields match the selected neighbor table. TTL behavior has three layers of policy and can regress interoperability if default and propagate cases are mixed. MTU checking subtracts label stack size from device MTU and must stay aligned with GSO validation. Netlink state comparison must include labels, TTL mode, and default TTL or route deduplication can be wrong.

## Test Signals
Signals include adding IPv4 and IPv6 routes with MPLS encap, routes with TTL 0 versus fixed TTL, multi-label stacks, route dumps preserving labels and TTL, MTU exceeded drops, output to down/non-MPLS devices, ARP/ND/6PE gateway transmit, and packet captures confirming BOS and label order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mpls/mpls_iptunnel.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mptcp/Kconfig -->
# sources/distributed-fs/ceph-client/net/mptcp/Kconfig

## Purpose
Defines kernel configuration switches for Multipath TCP support, IPv6 support, SOCK_DIAG monitoring, and KUnit tests.

## Important APIs, Types, and Functions
`CONFIG_MPTCP` is the main boolean depending on `INET`; it selects `SKB_EXTENSIONS`, `CRYPTO_LIB_SHA256`, and `CRYPTO_LIB_UTILS`. `CONFIG_INET_MPTCP_DIAG` follows `INET_DIAG` and enables MPTCP sock-diag support. `CONFIG_MPTCP_IPV6` gates IPv6 MPTCP support when IPv6 is built-in. `CONFIG_MPTCP_KUNIT_TEST` builds MPTCP crypto/token tests.

## Control Flow
There is no runtime flow. The file controls compile-time inclusion: the rest of the MPTCP objects are considered only inside `if MPTCP`, and tests default to `KUNIT_ALL_TESTS` when requested.

## State and Persistence
Configuration state persists in the kernel build configuration. It controls whether MPTCP code, diagnostics, IPv6 branches, and KUnit modules exist in the compiled kernel.

## Dependencies and Integration Points
Integrates with the top-level networking Kconfig and the local `Makefile`. The selected crypto and skb extension options are required by `crypto.c`, option parsing, and skb MPTCP extension storage.

## Risks
The `MPTCP_IPV6` dependency is `IPV6=y`, so module-style IPv6 combinations are intentionally excluded. Missing selected crypto/skb extensions would cause compile or runtime failures in MPTCP option handling. Test config should remain non-production by default.

## Test Signals
Build matrix signals include `CONFIG_MPTCP=n`, MPTCP IPv4-only builds, IPv6-enabled builds, `INET_MPTCP_DIAG=m/y`, and `MPTCP_KUNIT_TEST=m/y` with KUnit execution.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mptcp/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mptcp/Makefile -->
# sources/distributed-fs/ceph-client/net/mptcp/Makefile

## Purpose
Declares which object files compose the MPTCP core module/built-in object and optional companion modules for syncookies, diagnostics, KUnit tests, and BPF integration.

## Important APIs, Types, and Functions
`mptcp-y` aggregates protocol, subflow, options, token, crypto, control, path manager, diagnostics, MIB, netlink/userspace/kernel PM, sockopt, fastopen, scheduler, and generated PM netlink objects. Optional objects are controlled by `CONFIG_SYN_COOKIES`, `CONFIG_INET_MPTCP_DIAG`, `CONFIG_MPTCP_KUNIT_TEST`, and `CONFIG_BPF_SYSCALL`.

## Control Flow
There is no runtime flow. Kbuild uses these lists to link `mptcp.o`, `mptcp_diag.o`, `mptcp_crypto_test.o`, `mptcp_token_test.o`, and `bpf.o`.

## State and Persistence
Build composition is persistent in kernel build artifacts. Object ordering matters for link-time symbol resolution and initialization availability.

## Dependencies and Integration Points
Integrates Kconfig selections with Kbuild. It connects the files researched in this subset to the larger MPTCP implementation: `options.o`, `crypto.o`, `ctrl.o`, `pm.o`, `diag.o`, `mib.o`, `fastopen.o`, `mptcp_pm_gen.o`, and `pm_kernel.o`.

## Risks
Generated PM netlink code must remain in the core object list because kernel PM backend uses generated policies/ops. Optional `bpf.o` must stay tied to `CONFIG_BPF_SYSCALL`; otherwise BTF kfunc registration would compile without BPF infrastructure. Test object names must match their `*-objs` definitions.

## Test Signals
Build tests for builtin and module configurations, MPTCP without BPF, diagnostics as module, KUnit test modules, and symbol resolution for generated PM netlink functions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mptcp/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mptcp/bpf.c -->
# sources/distributed-fs/ceph-client/net/mptcp/bpf.c

## Purpose
Provides BPF-facing MPTCP helpers and registers an fmodret BTF kfunc allowlist for MPTCP-related protocol selection.

## Important APIs, Types, and Functions
`bpf_mptcp_sock_from_subflow()` returns the owning `struct mptcp_sock` for a full TCP MPTCP subflow socket. `bpf_mptcp_fmodret_ids` includes `update_socket_protocol` as a function-modify-return target. `bpf_mptcp_kfunc_init()` registers the BTF fmodret ID set at late init.

## Control Flow
The helper validates that the supplied socket is non-null, full, TCP, and MPTCP, then follows `mptcp_subflow_ctx(sk)->conn` to return the MPTCP meta-socket. Late init registers the static BTF set with the BPF subsystem.

## State and Persistence
Persistent state is the registered BTF kfunc ID set owned by this module/object. No per-socket state is mutated.

## Dependencies and Integration Points
Depends on BPF BTF kfunc registration and MPTCP protocol internals from `protocol.h`. It is built only under `CONFIG_BPF_SYSCALL` and exposes MPTCP context to BPF programs that operate on subflow sockets.

## Risks
The helper assumes a valid MPTCP subflow context after `sk_is_mptcp()`. Any future socket state where `conn` is unavailable would need guarding. BTF registration failures propagate only from late init; users relying on the kfunc need build/runtime registration coverage.

## Test Signals
BPF selftests should confirm helper return on MPTCP subflows and NULL on plain TCP, non-full, or null sockets. Boot logs or BTF queries can validate fmodret registration for `update_socket_protocol`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mptcp/bpf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mptcp/crypto.c -->
# sources/distributed-fs/ceph-client/net/mptcp/crypto.c

## Purpose
Implements MPTCP cryptographic primitives for deriving tokens/IDSNs from keys and computing HMAC-SHA256 authentication values used by MPTCP options.

## Important APIs, Types, and Functions
`mptcp_crypto_key_sha()` SHA256-hashes a 64-bit key in network byte order and returns the token from the first digest word and the IDSN from the final digest bytes. `mptcp_crypto_hmac_sha()` computes HMAC-SHA256 using two 64-bit keys as the raw 16-byte key. `mptcp_crypto_hmac_sha()` is exported when the KUnit crypto test is modular.

## Control Flow
Both functions are straight-line wrappers over crypto library helpers. They explicitly convert keys to big endian before hashing to match protocol wire format and use unaligned/big-endian reads from the digest for protocol outputs.

## State and Persistence
No persistent state is stored. Outputs are deterministic for input keys/messages and are consumed by token lookup, MP_JOIN validation, and ADD_ADDR HMAC validation.

## Dependencies and Integration Points
Depends on `crypto/sha2.h`, `CRYPTO_LIB_SHA256`, and `CRYPTO_LIB_UTILS`. Integrated by option parsing/writing, token handling, path manager ADD_ADDR HMAC generation, and KUnit tests.

## Risks
Endianness is the primary correctness risk: protocol-visible tokens, IDSNs, and HMACs depend on big-endian key/message layout. The raw-key HMAC API assumes a fixed 16-byte key made from key1/key2. Test modules require the conditional export.

## Test Signals
KUnit vectors in `crypto_test.c`, MP_CAPABLE token/IDSN interop, MP_JOIN HMAC validation, ADD_ADDR HMAC acceptance/rejection, and cross-endian build testing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mptcp/crypto.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mptcp/crypto_test.c -->
# sources/distributed-fs/ceph-client/net/mptcp/crypto_test.c

## Purpose
Provides KUnit coverage for MPTCP HMAC-SHA256 helper behavior using fixed protocol-shaped key and message vectors.

## Important APIs, Types, and Functions
`struct test_case` stores hex-like byte strings for key, message, and expected digest. `mptcp_crypto_test_basic()` converts test bytes through the same endian path used by MPTCP, invokes `mptcp_crypto_hmac_sha()`, renders the digest as hex, and compares with `KUNIT_EXPECT_STREQ()`. `mptcp_crypto_suite` registers the `mptcp-crypto` test suite.

## Control Flow
The test iterates each vector, splits the 16-byte key into two 64-bit values, splits the 8-byte message into two nonce words, writes the message in big-endian order, computes HMAC, converts the 32-byte digest to a 64-character hex string, and asserts equality.

## State and Persistence
The file owns static test vectors only. It does not mutate MPTCP runtime state.

## Dependencies and Integration Points
Depends on KUnit, `protocol.h`, and `mptcp_crypto_hmac_sha()` from `crypto.c`. It is built through `CONFIG_MPTCP_KUNIT_TEST`.

## Risks
The test covers HMAC only, not token/IDSN derivation. Vector strings are used as raw bytes rather than parsed hexadecimal, so future edits must preserve that convention. The comment typo "hmap" is harmless but indicates the code relies on matching crypto helper byte conversions.

## Test Signals
Running the `mptcp-crypto` KUnit suite should pass all vectors. Failures indicate changes in HMAC implementation, endian conversion, raw-key layout, or digest formatting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mptcp/crypto_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mptcp/ctrl.c -->
# sources/distributed-fs/ceph-client/net/mptcp/ctrl.c

## Purpose
Provides per-network-namespace MPTCP control state, sysctls, default scheduler/path-manager selection, active blackhole detection/backoff, and MPTCP subsystem initialization.

## Important APIs, Types, and Functions
`struct mptcp_pernet` stores sysctl-controlled namespace state. Getter APIs include `mptcp_is_enabled()`, `mptcp_get_add_addr_timeout()`, `mptcp_is_checksum_enabled()`, `mptcp_allow_join_id0()`, `mptcp_stale_loss_cnt()`, `mptcp_close_timeout()`, `mptcp_get_pm_type()`, `mptcp_get_path_manager()`, and `mptcp_get_scheduler()`. Sysctl handlers include scheduler/path-manager setters, available-list readers, `proc_pm_type()`, and blackhole timeout reset. Active fallback logic is in `mptcp_active_disable()`, `mptcp_active_should_disable()`, `mptcp_active_enable()`, and `mptcp_active_detect_blackhole()`. Initialization uses `mptcp_init()` and optionally `mptcpv6_init()`.

## Control Flow
Namespace init sets defaults and registers `/proc/sys/net/mptcp` entries. Sysctl writes validate scheduler/path-manager names against registered ops and keep `pm_type` and `path_manager` synchronized for kernel/userspace managers. Blackhole detection observes repeated SYN retransmissions for active MP_CAPABLE attempts, triggers fallback, records a disable timestamp/count, and applies exponential active-MPTCP disable windows capped at 64 times the configured timeout. Successful non-loopback active MPTCP connections reset disable count.

## State and Persistence
State is per-netns and persists for the namespace lifetime: enable flags, checksum setting, join-id0 allowance, stale loss count, close timeout, blackhole timeout, SYN retrans threshold, active-disable timestamp/counter, scheduler string, path-manager string, and PM type. Sysctl writes are runtime configuration, not durable across boot unless user space persists them.

## Dependencies and Integration Points
Depends on netns generic storage, sysctl, MPTCP scheduler/path-manager registries, MIB stats, TCP retransmission state, destination device lookup, and core protocol init. It integrates with connection setup, fallback, path manager, scheduler selection, and `/proc/sys/net/mptcp` user controls.

## Risks
Scheduler/path-manager string writes must validate under RCU or leave stale configuration. `pm_type` and `path_manager` can diverge if future names are added without updating the mapping logic. Blackhole detection relies on memory ordering between timestamp and atomic disable count. Loopback success intentionally does not reset blackhole state; changing that can mask real network middlebox failures. Non-init netns sysctl table copies must be freed correctly.

## Test Signals
Signals include sysctl read/write validation, available scheduler/path-manager lists, switching between kernel and userspace PM, active MP_CAPABLE SYN drop fallback, exponential blackhole timeout behavior, reset after successful non-loopback MPTCP, IPv6 init with `CONFIG_MPTCP_IPV6`, and per-netns isolation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mptcp/ctrl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mptcp/diag.c -->
# sources/distributed-fs/ceph-client/net/mptcp/diag.c

## Purpose
Adds MPTCP subflow-specific diagnostic data to TCP ULP inet-diag output.

## Important APIs, Types, and Functions
`subflow_get_info()` emits nested `INET_ULP_INFO_MPTCP` attributes for a subflow. `subflow_get_info_size()` computes the required netlink size. `mptcp_diag_subflow_init()` installs these callbacks into `tcp_ulp_ops`.

## Control Flow
For non-listening sockets, the get-info path starts a netlink nest, locks the socket with `lock_sock_fast()`, reads the MPTCP subflow context through RCU, builds a flag word from MP_CAPABLE, MP_JOIN, backup, establishment, connected, and mapping-valid states, then emits tokens, flags, and local/remote IDs. CAP_NET_ADMIN callers additionally receive relative write sequence and mapping sequence/counters. Errors cancel the nest and unwind locks.

## State and Persistence
No state is owned. The file reads live subflow context fields and TCP socket state. Exported diagnostics are snapshots.

## Dependencies and Integration Points
Depends on inet diag netlink attributes, MPTCP subflow context, TCP ULP registration, RCU, and socket locking. It integrates with the larger inet diag path and with `mptcp_diag.c`, which handles whole MPTCP socket diagnostics.

## Risks
Diagnostic size calculation must match emitted attributes or dumps can fail with `-EMSGSIZE`. Sequence-related fields are intentionally gated by `CAP_NET_ADMIN`; leaking them to unprivileged users would be a security regression. The callback must tolerate missing ULP data while sockets transition.

## Test Signals
Use `ss -M -i` or inet_diag requests against established/listening/plain TCP sockets, with and without CAP_NET_ADMIN. Verify flags and IDs for MP_CAPABLE and MP_JOIN subflows and that size estimates avoid truncation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mptcp/diag.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mptcp/fastopen.c -->
# sources/distributed-fs/ceph-client/net/mptcp/fastopen.c

## Purpose
Handles server-side MPTCP Fast Open receive-data handoff from the TCP subflow queue into the MPTCP meta-socket receive queue after SYNACK processing.

## Important APIs, Types, and Functions
`mptcp_fastopen_subflow_synack_set_params()` marks the subflow as MPTFO, extracts the first queued skb from the TCP subflow, adjusts subflow sequence accounting, rewrites MPTCP skb control block metadata, transfers memory ownership, queues the skb to the MPTCP socket, updates received bytes, and notifies data readiness.

## Control Flow
The function returns early if early fallback already removed the subflow. It peeks the first TCP receive skb, unlinks it, resets extensions, lends/borrows forward memory between subflow and MPTCP sockets, advances `copied_seq` and `ssn_offset` because Fast Open data is outside MPTCP sequence space, sets a negative `map_seq` delta and `cant_coalesce`, then enqueues the skb under the MPTCP data lock and calls `sk_data_ready()`.

## State and Persistence
Persistent changes include `subflow->is_mptfo`, `subflow->ssn_offset`, TCP `copied_seq`, MPTCP `bytes_received`, receive queue contents, and skb ownership/accounting. No global state is stored.

## Dependencies and Integration Points
Depends on MPTCP protocol internals, TCP Fast Open receive queue behavior, skb extension/control block helpers, socket memory accounting, and MPTCP data locking. It is called from subflow SYN receive handling when Fast Open data is accepted.

## Risks
The code assumes exactly one queued Fast Open skb exists and warns if absent. Sequence offsets are subtle: Fast Open bytes must not enter MPTCP sequence space. Memory-accounting transfer must remain balanced across subflow and meta-socket. The MPTCP socket must not be user-owned while the data lock section runs.

## Test Signals
Server-side MPTCP Fast Open with data in SYN, early fallback path, receive queue ownership/accounting checks, correct application-visible data delivery, no duplicate MPTCP sequence mapping, and WARN coverage for unexpected empty subflow queue.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mptcp/fastopen.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mptcp/mib.c -->
# sources/distributed-fs/ceph-client/net/mptcp/mib.c

## Purpose
Defines MPTCP SNMP/MIB counter names, allocates per-netns counter storage on demand, and renders counters through seq_file output.

## Important APIs, Types, and Functions
`mptcp_snmp_list` maps human-readable names to `enum linux_mptcp_mib_field` values. `mptcp_mib_alloc()` allocates per-CPU `struct mptcp_mib` storage using `cmpxchg()` so the first MPTCP socket initializes statistics once. `mptcp_seq_show()` emits the `MPTcpExt:` header and values.

## Control Flow
Allocation creates a per-CPU MIB block and installs it only if `net->mib.mptcp_statistics` is still NULL, freeing the loser on races. Rendering writes all names, batches per-CPU sums if stats exist, then writes matching values in the same order.

## State and Persistence
Counter storage is per network namespace in `net->mib.mptcp_statistics` and persists until namespace teardown. Counters are in-memory runtime statistics exposed through proc/net SNMP-style files.

## Dependencies and Integration Points
Depends on SNMP per-CPU helpers, seq_file, net namespace MIB storage, and field definitions from `mib.h`. Integrated throughout MPTCP via `MPTCP_INC_STATS()`, `MPTCP_ADD_STATS()`, and related macros.

## Risks
The list order must match enum fields or user-visible counters become misleading. Allocation is lazy; stat increments before allocation are intentionally ignored by macros. Adding enum values requires updating this string list and tests/monitoring expectations.

## Test Signals
Observe `/proc/net/netstat` MPTCP lines after creating MPTCP connections, MP_JOIN, ADD_ADDR/RM_ADDR, fallback, reset, and stale-subflow scenarios. Race tests should confirm one per-CPU allocation survives.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mptcp/mib.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mptcp/mib.h -->
# sources/distributed-fs/ceph-client/net/mptcp/mib.h

## Purpose
Declares all MPTCP MIB counter fields and inline helpers for updating per-netns MPTCP statistics.

## Important APIs, Types, and Functions
`enum linux_mptcp_mib_field` contains counters for MP_CAPABLE, MP_JOIN, DSS, ADD_ADDR/RM_ADDR, priority/fail/fastclose/reset, stale subflows, shared windows, fallback, blackhole detection, and probes. `struct mptcp_mib` stores the per-CPU counter array. `MPTCP_ADD_STATS()`, `MPTCP_INC_STATS()`, `__MPTCP_INC_STATS()`, and `MPTCP_DEC_STATS()` wrap SNMP helpers with null-storage checks. `mptcp_mib_alloc()` is declared for allocation.

## Control Flow
The inline helpers perform a likely check that MPTCP stats storage exists before updating the selected field. They do not allocate or sleep.

## State and Persistence
The header defines the shape of per-CPU MPTCP statistics; actual storage lives in `net->mib.mptcp_statistics`. Counter values persist for the netns lifetime.

## Dependencies and Integration Points
Depends on inet/SNMP common helpers and is included across MPTCP implementation files that need accounting. It must stay synchronized with `mib.c` string names.

## Risks
Enum reordering breaks user-visible counter interpretation. Callers using `__MPTCP_INC_STATS()` must already be in a context suitable for the non-preempt-safe SNMP update variant. Missing allocation means increments are dropped silently.

## Test Signals
Compile coverage across all MPTCP files, counter-name alignment with `mib.c`, and runtime increases for each feature path in netstat/proc output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mptcp/mib.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mptcp/mptcp_diag.c -->
# sources/distributed-fs/ceph-client/net/mptcp/mptcp_diag.c

## Purpose
Registers an inet_diag handler for whole MPTCP sockets, supporting dump, single-socket lookup by token cookie, listener reporting, queue info, and `struct mptcp_info` export.

## Important APIs, Types, and Functions
`mptcp_diag_handler` is the registered `inet_diag_handler` for `IPPROTO_MPTCP`. `mptcp_diag_dump_one()` resolves sockets by token. `mptcp_diag_dump()` iterates token table entries and optionally listeners. `mptcp_diag_dump_listeners()` walks TCP listen hash buckets and maps MPTCP ULP listener subflows to MPTCP listener sockets. `mptcp_diag_get_info()` fills queue lengths and optional `mptcp_info`.

## Control Flow
Single lookup gets an MPTCP socket from the token table using `idiag_cookie[0]`, allocates a reply skb, fills inet diag data, and unicasts it. Dump iteration uses token iterator state stored in `cb->ctx`, filters by state, family, sport, and dport, and retries the same position if skb space runs out. Listener dumping walks listen buckets under RCU and bucket lock, filters MPTCP ULP sockets, references the owning MPTCP socket, and emits diag data. Init/exit register and unregister the handler.

## State and Persistence
The module owns only the registered handler. Dump cursors live in netlink callback context. Socket queue and MPTCP info are snapshots from live sockets.

## Dependencies and Integration Points
Depends on inet_diag, netlink diag sockets, MPTCP token table iteration, MPTCP listener/subflow context, and `mptcp_diag_fill_info()`. It complements `diag.c`, which adds per-subflow ULP details.

## Risks
Listener walking is lock-sensitive and must not hold stale references. Token iterator position correction on skb-full errors must remain correct to avoid skipped or duplicated sockets. Queue reporting overrides listener queues using the first TCP listener and must tolerate it being absent. The module alias encodes SOCK_DIAG protocol matching.

## Test Signals
Use `ss -M`, inet_diag dumps for established/listening MPTCP sockets, single lookup by token cookie, state/family/port filters, small skb dump continuation, CAP_NET_ADMIN info visibility, and module load/unload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mptcp/mptcp_diag.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mptcp/mptcp_pm_gen.c -->
# sources/distributed-fs/ceph-client/net/mptcp/mptcp_pm_gen.c

## Purpose
Generated Generic Netlink policy and ops table for the MPTCP path-manager family, derived from `Documentation/netlink/specs/mptcp_pm.yaml`.

## Important APIs, Types, and Functions
Defines `mptcp_pm_address_nl_policy` for nested endpoint address attributes and per-command policies for add, delete, get, flush, set/get limits, set flags, announce, remove, subflow create, and subflow destroy. `mptcp_pm_nl_ops` maps eleven `MPTCP_PM_CMD_*` commands to their doit/dump callbacks and policies.

## Control Flow
There is no custom runtime logic beyond static genl dispatch metadata. The genetlink core uses these policy arrays to validate and dispatch incoming messages to functions implemented by PM backend/userspace code.

## State and Persistence
The file owns static constant policy and ops tables. No mutable state is stored.

## Dependencies and Integration Points
Depends on genetlink/netlink policy APIs and `uapi/linux/mptcp_pm.h`. It is included in the MPTCP core build and consumed by the PM netlink family registration and callback implementations in files such as `pm_kernel.c` and userspace PM code.

## Risks
As generated code, manual edits risk divergence from the YAML spec. Callback prototypes, maxattr values, admin permission flags, and nested policy shapes must match UAPI expectations. `GENL_DONT_VALIDATE_STRICT` is used throughout, so callback-side validation remains important.

## Test Signals
YNL/genetlink selftests for every PM command, policy rejection of malformed nested address attributes, permission checks on admin commands, dump support for GET_ADDR, and regeneration diff checks from the YAML spec.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mptcp/mptcp_pm_gen.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mptcp/mptcp_pm_gen.h -->
# sources/distributed-fs/ceph-client/net/mptcp/mptcp_pm_gen.h

## Purpose
Generated header declaring MPTCP path-manager Generic Netlink policies, ops table, and command callback prototypes.

## Important APIs, Types, and Functions
Declares external policy arrays for each PM command and `mptcp_pm_nl_ops[11]`. It also declares doit/dump callbacks such as `mptcp_pm_nl_add_addr_doit()`, `mptcp_pm_nl_del_addr_doit()`, `mptcp_pm_nl_get_addr_dumpit()`, `mptcp_pm_nl_set_limits_doit()`, `mptcp_pm_nl_set_flags_doit()`, and userspace PM announce/remove/subflow operations.

## Control Flow
The header has no runtime flow; it is a compile-time contract between generated netlink metadata and callback implementations.

## State and Persistence
No state is stored. It declares static objects defined in `mptcp_pm_gen.c` and functions defined elsewhere.

## Dependencies and Integration Points
Depends on netlink, genetlink, and MPTCP PM UAPI headers. Included by `mptcp_pm_gen.c` and PM implementation files that need generated policy and prototype declarations.

## Risks
The array size and prototypes must stay in sync with generated C and callback implementations. Manual edits can break YNL regeneration or genl family registration. Include order must provide `struct sk_buff`, `struct genl_info`, and `struct netlink_callback`.

## Test Signals
Compile coverage after YNL regeneration, all PM commands linking successfully, and no prototype mismatch warnings with callback implementations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mptcp/mptcp_pm_gen.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mptcp/options.c -->
# sources/distributed-fs/ceph-client/net/mptcp/options.c

## Purpose
Implements MPTCP TCP-option parsing, outgoing option selection/writing, DSS mapping and ACK handling, ADD_ADDR/RM_ADDR/MP_PRIO/MP_FAIL/MP_FASTCLOSE/MP_RST processing, receive-window sharing, checksum generation, and subflow establishment transitions.

## Important APIs, Types, and Functions
`mptcp_get_options()` parses TCP options into `struct mptcp_options_received` through `mptcp_parse_option()`. Outgoing selection is handled by `mptcp_syn_options()`, `mptcp_synack_options()`, and `mptcp_established_options()`, with specialized helpers for MPC/MPJ, DSS, ADD_ADDR, RM_ADDR, PRIO, FASTCLOSE, FAIL, and RST. `mptcp_write_options()` serializes `struct mptcp_out_options` to the TCP header. Receive-side state updates use `check_fully_established()`, `ack_update_msk()`, `rwin_update()`, `mptcp_update_rcv_data_fin()`, and `mptcp_incoming_options()`. Exported `mptcp_get_reset_option()` returns an MP_RST option word for reset skb extensions.

## Control Flow
Parsing walks TCP options, dispatches on MPTCP subtype, validates strict lengths, version, flags, BOS-like option semantics, and stores decoded keys, HMACs, sequence numbers, address IDs, ports, checksums, and reset/fail fields. Outgoing SYN/SYNACK paths advertise MP_CAPABLE or MP_JOIN. Established-option selection prioritizes fallback, reset-bearing packets, third-ACK MPC/MPJ, DSS/data-fin, MP_FAIL, ADD_ADDR/RM_ADDR, and MP_PRIO while respecting option-space limits and documented mutual exclusions. Incoming options first handle fallback, then establish subflows or reset protocol violations, process control options, update MPTCP-level ACK/window state, attach `SKB_EXT_MPTCP` mapping data for payload skbs, and schedule PM/work items as needed.

## State and Persistence
The file mutates MPTCP socket state such as `snd_una`, `bytes_acked`, `wnd_end`, `last_ack_recv`, `rcv_data_fin`, receive-window sent state, subflow establishment flags, MP_FAIL/FASTCLOSE/RST flags, ADD_ADDR timers through PM callbacks, and skb MPTCP extensions. It stores no global state.

## Dependencies and Integration Points
Depends on TCP option layout, skb extensions, MPTCP protocol structs, crypto helpers, path manager APIs, MIB counters, TCP checksum/window helpers, and MPTCP tracepoints. It is central to subflow connect/listen code, data receive/transmit, PM signaling, fallback, and diagnostics.

## Risks
Option-space composition is dense and mutually exclusive; adding options can silently overrun or suppress critical DSS/handshake data. Length parsing intentionally accepts checksum-presence mismatches for later reset enforcement, so downstream checks must remain intact. Sequence expansion from 32-bit to 64-bit ACK/DSN values can acknowledge future data if conflict guards regress. ADD_ADDR HMAC depends on key direction and address/port bytes. Receive-window sharing uses atomics across subflows and is race-prone. MP_JOIN fully-established handling must reject early data and retransmit third-ACK acks correctly.

## Test Signals
MPTCP selftests should cover MP_CAPABLE handshake with/without data/checksum, MP_JOIN success and early-data reset, DSS ACK/map/data-fin variants, 32-bit wrap expansion, ADD_ADDR IPv4/IPv6/port echo/HMAC failure, RM_ADDR, MP_PRIO, MP_FAIL infinite-map fallback, MP_FASTCLOSE and MP_RST on reset packets, receive-window conflict counters, fallback paths, and packet captures verifying serialized option bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mptcp/options.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mptcp/pm.c -->
# sources/distributed-fs/ceph-client/net/mptcp/pm.c

## Purpose
Provides common MPTCP path-manager infrastructure shared by kernel and userspace PM implementations: address comparison/extraction helpers, ADD_ADDR retransmission state, PM event scheduling, subflow acceptance limits, RM_ADDR/subflow teardown, MP_PRIO/MP_FAIL handling, stale subflow detection, PM data initialization/reset, and path-manager registration.

## Important APIs, Types, and Functions
Address helpers include `mptcp_pm_addr_families_match()`, `mptcp_addresses_equal()`, `mptcp_local_address()`, and `mptcp_remote_address()`. Announcement state uses `struct mptcp_pm_add_entry`, `mptcp_pm_alloc_anno_list()`, `mptcp_pm_del_add_timer()`, and `mptcp_pm_add_timer()`. Event APIs include `mptcp_pm_new_connection()`, `mptcp_pm_fully_established()`, `mptcp_pm_subflow_established()`, `mptcp_pm_add_addr_received()`, `mptcp_pm_rm_addr_received()`, and `mptcp_pm_worker()`. Command helpers include `mptcp_pm_announce_addr()`, `mptcp_pm_remove_addr()`, `mptcp_pm_mp_prio_send_ack()`, `mptcp_pm_rm_subflow()`, and `mptcp_pm_mp_fail_received()`. Registration uses `mptcp_pm_register()`, `mptcp_pm_unregister()`, and `mptcp_pm_get_available()`.

## Control Flow
PM events set bits in `msk->pm.status` and schedule the MPTCP worker. The worker handles pending ADD_ADDR ACKs, RM_ADDR receives, and delegates kernel-specific work to `__mptcp_pm_kernel_worker()`. ADD_ADDR announcements are placed in an annotation list with retransmission timers; timer expiry re-announces with exponential delay up to `ADD_ADDR_RETRANS_MAX`, then triggers PM work to try further subflows. Incoming ADD_ADDR is either echoed, dropped, or queued for PM processing based on userspace/kernel mode, id0 validation, accept limits, and special C-flag handling. RM_ADDR and RM_SUBFLOW walk live subflows and close matching sockets. Stale detection marks subflows idle after repeated loss with no receive timestamp progress and reinjects pending data when alternatives exist.

## State and Persistence
State is per MPTCP socket in `msk->pm`: locks, status bits, announcement list, local/remote pending addresses, RM lists, counters, id bitmap, PM type, accept flags, work pending flag, and remote join-id0 denial. Global PM registry state is an RCU list protected by `mptcp_pm_list_lock`. Timers hold socket references and entries are freed by RCU.

## Dependencies and Integration Points
Depends on MPTCP protocol/socket internals, PM kernel/userspace backends, TCP sockets, timers, MIB counters, MPTCP events, and scheduler/work machinery. It integrates directly with `options.c` for option signaling and with `pm_kernel.c` for endpoint-driven behavior.

## Risks
Locking is subtle: many helpers require `msk->pm.lock`, while ACK sending temporarily drops it to lock subflow sockets. Timer cancellation/removal uses RCU to avoid freeing entries under concurrent callbacks. Counters for accepted addresses, extra subflows, and used local addresses must remain balanced across failures and removals. Userspace and kernel PM modes have different acceptance semantics. MP_FAIL disables new subflows and enters infinite-map fallback; mishandling can corrupt recovery behavior.

## Test Signals
Signals include ADD_ADDR retransmission/echo/drop counters, timer cancellation on echo/removal/destroy, userspace versus kernel PM behavior, subflow accept limits, RM_ADDR and RM_SUBFLOW close behavior, MP_PRIO send/receive events, MP_FAIL fallback handshake, stale subflow marking and recovery counters, PM registry sysctl available list, and lockdep/KASAN under concurrent PM events.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mptcp/pm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mptcp/pm_kernel.c -->
# sources/distributed-fs/ceph-client/net/mptcp/pm_kernel.c

## Purpose
Implements the default "kernel" MPTCP path-manager backend. It stores per-netns endpoint configuration, handles Generic Netlink endpoint and limit commands, chooses local/remote address pairs for subflow creation, signals ADD_ADDR/RM_ADDR, tracks endpoint ID availability per MPTCP socket, creates port-based listener sockets, and registers the kernel PM ops.

## Important APIs, Types, and Functions
`struct pm_nl_pernet` stores endpoint list, ID bitmap, endpoint counters, and limits. Exported getters include `mptcp_pm_get_endp_signal_max()`, `mptcp_pm_get_endp_subflow_max()`, `mptcp_pm_get_endp_laminar_max()`, `mptcp_pm_get_endp_fullmesh_max()`, `mptcp_pm_get_limit_add_addr_accepted()`, and `mptcp_pm_get_limit_extra_subflows()`. Endpoint selection and connection logic is in `mptcp_pm_create_subflow_or_signal_addr()`, `fill_remote_addresses_vec()`, `fill_local_addresses_vec()`, and `mptcp_pm_nl_add_addr_received()`. Netlink callbacks include add/delete/flush/get/dump address, set/get limits, and set flags. Worker integration is `__mptcp_pm_kernel_worker()`.

## Control Flow
When an MPTCP socket is established, the backend lazily accounts the initial subflow endpoint, announces configured signal endpoints in list order, and creates subflows from configured subflow endpoints until endpoint and subflow limits are reached. Fullmesh endpoints combine a local endpoint with all known remote IDs; laminar endpoints pick one unused laminar local address; the C-flag special case uses subflow endpoints to respond to remote ADD_ADDR when default acceptance would otherwise reject it. Adding an endpoint validates flags/port rules, optionally creates a kernel MPTCP listener for signal-only port endpoints, appends the endpoint with automatic ID allocation, then iterates existing sockets to signal/connect. Removing or flushing endpoints sends RM_ADDR/RM_SUBFLOW and marks IDs available again.

## State and Persistence
Endpoint configuration is per netns in an RCU list protected by `pernet->lock`; entries can hold listener sockets for port endpoints. Per-socket PM state tracks `id_avail_bitmap`, `mpc_endpoint_id`, `local_addr_used`, `add_addr_signaled`, `add_addr_accepted`, and `extra_subflows`. Limits default to two extra subflows and are runtime netlink state.

## Dependencies and Integration Points
Depends on generated PM netlink policies, MPTCP PM common helpers, token table iteration, subflow connect/close helpers, endpoint parsing/fill helpers, socket creation/bind/listen APIs, netns generic storage, RCU, and MIB/event paths. It registers `mptcp_pm_kernel` with the PM registry and is selected by `ctrl.c` defaults.

## Risks
Endpoint ID accounting is complex, especially ID 0 aliasing to the initial subflow, automatic ID allocation, implicit endpoints, and reusing IDs after delete/flush. Fullmesh/laminar/C-flag modes can create too many or too few subflows if counters drift. Port-based endpoints create kernel sockets with special lock classes and must release them after RCU grace periods. Netlink validation must reject invalid flag combinations such as signal+fullmesh or port without signal-only semantics. Iterating all token sockets while adding/removing endpoints must handle sockets disappearing and avoid userspace PM sockets.

## Test Signals
Exercise `ip mptcp endpoint` add/delete/flush/show, automatic and explicit IDs, duplicate addresses, implicit endpoint replacement, port endpoints and listener events, set/get limits, backup/fullmesh flag changes, laminar endpoint selection, C-flag ADD_ADDR handling, endpoint removal sending RM_ADDR/RM_SUBFLOW, per-netns isolation, and stress with concurrent connections while endpoints change.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mptcp/pm_kernel.c -->
