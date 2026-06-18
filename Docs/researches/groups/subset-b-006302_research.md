# sources/distributed-fs/ceph-client/net/xfrm subset-b-006302 research

Work item `subset-b-006302` covers XFRM build configuration and selected IPsec datapath, offload, interface, IPComp, IP-TFS, NAT keepalive, and ESP-in-TCP sources under `sources/distributed-fs/ceph-client/net/xfrm`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/xfrm/Kconfig -->
# sources/distributed-fs/ceph-client/net/xfrm/Kconfig

Purpose: This Kconfig fragment defines the selectable build surface for the XFRM/IPsec subsystem. It establishes the hidden core `XFRM` symbol, the crypto algorithm helper `XFRM_ALGO`, user ABIs (`XFRM_USER`, `XFRM_USER_COMPAT`, `NET_KEY`), optional policy/state features, protocol helpers (`XFRM_AH`, `XFRM_ESP`, `XFRM_IPCOMP`), virtual interfaces, IP-TFS, and ESP-in-TCP.

Important symbols and dependencies: `XFRM` depends on `INET` and selects `GRO_CELLS` and `SKB_EXTENSIONS`, which matches `xfrm_input.c` use of GRO cells and secpath skb extensions. `XFRM_ALGO` selects crypto AEAD/hash/skcipher support used by `xfrm_algo.c`. `XFRM_USER_COMPAT` depends on 64-bit alignment compatibility and unaligned access because `xfrm_compat.c` translates 32-bit netlink layouts. `XFRM_INTERFACE` depends on `XFRM && IPV6` and builds the `xfrm_interface` module. `XFRM_IPTFS` is a tristate RFC 9347 mode. `XFRM_ESPINTCP` is hidden and selected by IPv4/IPv6 ESP Kconfig entries elsewhere.

Control flow and integration: Kconfig selection drives `net/xfrm/Makefile`, which either links core objects into built-in networking or emits feature modules. The options also select crypto algorithms that userspace key managers expect to be present for mandatory IPsec profiles.

State and persistence: No runtime state is stored here. The persistent effect is the configured kernel build graph and module availability.

Risks: Dependency mistakes can produce build configurations where netlink exposes features whose objects are absent, or where protocol code is built without required crypto. Hidden `XFRM_ESPINTCP` relies on selectors outside this file, so regressions can appear only in IPv4/IPv6 ESP builds.

Test signals: Build matrix coverage should include `XFRM=y/m`, `XFRM_USER_COMPAT`, `XFRM_INTERFACE=m/y` with BTF on and off, `XFRM_IPCOMP`, `XFRM_IPTFS`, and ESP-in-TCP selection through IPv4 and IPv6 ESP. Runtime smoke tests should verify `ip xfrm`, PF_KEY legacy behavior if enabled, xfrm interfaces, IPComp SAs, and IP-TFS netlink attributes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/xfrm/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/xfrm/Makefile -->
# sources/distributed-fs/ceph-client/net/xfrm/Makefile

Purpose: This Makefile maps XFRM Kconfig symbols to object files. It defines the core object set for `CONFIG_XFRM`, feature modules for algorithms, user ABI, compatibility, IPComp, xfrm interfaces, IP-TFS, ESP-in-TCP, and BTF helper objects.

Important build rules: `obj-$(CONFIG_XFRM)` includes `xfrm_policy.o`, `xfrm_state.o`, `xfrm_hash.o`, `xfrm_input.o`, `xfrm_output.o`, `xfrm_sysctl.o`, `xfrm_replay.o`, `xfrm_device.o`, and `xfrm_nat_keepalive.o`. `xfrm_interface-$(CONFIG_XFRM_INTERFACE)` contributes `xfrm_interface_core.o`, with `xfrm_interface_bpf.o` included only when the interface and BTF debug-info configuration match built-in or module mode. Feature symbols add `xfrm_algo.o`, `xfrm_user.o`, `xfrm_compat.o`, `xfrm_ipcomp.o`, `xfrm_iptfs.o`, and `espintcp.o`.

Control flow and integration: The build graph matters because many files register callbacks at init time: `xfrm_iptfs.o` registers mode callbacks, `xfrm_interface.o` registers rtnl/protocol/BPF hooks, and `xfrm_compat.o` registers the translator. Core XFRM always includes NAT keepalive support, even though keepalives activate only when states carry intervals.

State and persistence: No runtime state is persisted here; it shapes compiled objects and module boundaries. The composite `xfrm_interface.o` module conditionally contains BPF kfunc registration depending on BTF.

Risks: The conditional BPF object logic is sensitive to built-in vs module mode. Missing `xfrm_interface_bpf.o` silently removes TC-BPF kfunc support, while including it without BTF support would break build or registration assumptions. Adding core dependencies must account for built-in and modular link order.

Test signals: Build with `CONFIG_XFRM_INTERFACE=y` and `m`, with `CONFIG_DEBUG_INFO_BTF` and `CONFIG_DEBUG_INFO_BTF_MODULES`. Confirm generated modules export expected aliases (`xfrm`) and that `objdump`/`modinfo` includes IP-TFS, IPComp, or ESP-in-TCP only when selected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/xfrm/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/xfrm/espintcp.c -->
# sources/distributed-fs/ceph-client/net/xfrm/espintcp.c

Purpose: `espintcp.c` implements the TCP ULP named `espintcp`, allowing ESP packets and non-ESP/IKE traffic to be multiplexed over a framed TCP stream. It is used by ESP code through `espintcp_queue_out()` and `espintcp_push_skb()` and is initialized from core XFRM policy init when `CONFIG_XFRM_ESPINTCP` is enabled.

Important APIs and types: The file uses `struct espintcp_ctx` and `struct espintcp_msg` from `include/net/espintcp.h`, `strparser` for two-byte length-framed input, saved TCP protocol/proto_ops clones, and an `ike_queue` for non-ESP messages. Exported APIs are `espintcp_queue_out()`, `espintcp_push_skb()`, and `tcp_is_ulp_esp()`. `espintcp_init()` registers `tcp_ulp_ops`.

Control flow: Receive path starts in `espintcp_data_ready()`, which drives `strp_data_ready()`. `espintcp_parse()` reads the 16-bit length, rejects lengths below two, and returns the full framed size. `espintcp_rcv()` removes the length field, drops one-byte `0xff` keepalives, distinguishes non-ESP marker zero from ESP SPI, queues non-ESP data for userspace `recvmsg()`, or passes ESP into `xfrm4_rcv_encap()`/`xfrm6_rcv_encap()` with `TCP_ENCAP_ESPINTCP`. Send path stores either skb output from ESP or userspace sk_msg data in `ctx->partial`, pushes with `skb_send_sock_locked()` or `tcp_sendmsg_locked()`, and preserves partial state across `-EAGAIN`.

State and persistence: Per-socket ULP state stores parser state, saved callbacks, work item, IKE/out queues, and a partial transmit. It is attached through `icsk_ulp_data`, freed in the socket destructor, and purged on close.

Dependencies and integration: It depends on TCP internals, strparser, XFRM IPv4/IPv6 receive encapsulation, ESP output, socket memory accounting, and `net_hotdata.max_backlog`. It rejects sockmap use by checking `sk_user_data`.

Risks: Framing and partial-send accounting are security-sensitive. Bugs can misclassify IKE vs ESP, leak skb/sk_msg pages, deadlock callback replacement, or lose data under TCP backpressure. IPv6 proto cloning is protected by `tcpv6_prot_mutex`; races here affect all sockets using the ULP.

Test signals: Exercise TCP ULP attach, IKE marker delivery through `recvmsg()`, ESP delivery to XFRM, keepalive drop, large send rejection above `MAX_ESPINTCP_MSG`, nonblocking `EAGAIN`, socket close with pending partials, and IPv4/IPv6 ESP-in-TCP interop.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/xfrm/espintcp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/xfrm/trace_iptfs.h -->
# sources/distributed-fs/ceph-client/net/xfrm/trace_iptfs.h

Purpose: This trace header defines tracepoints for the IP-TFS implementation in `xfrm_iptfs.c`. It exposes packet geometry, queue decisions, aggregation/fragmentation events, and timer activity for debugging RFC 9347 AGGFRAG behavior.

Important events: `iptfs_egress_recv` records inbound IP-TFS payload skb layout and block offset. The `iptfs_ingress_preq_event` class backs `iptfs_enqueue`, `iptfs_no_queue_space`, and `iptfs_too_big`, capturing queue capacity, protocol hints, PMTU, and GSO status before enqueue. The `iptfs_ingress_postq_event` class backs first dequeue/fragmenting/final-fragment/toobig events. `iptfs_ingress_nth_peek` and `iptfs_ingress_nth_add` track aggregation of subsequent inner packets. `iptfs_timer_start` and `iptfs_timer_expire` expose output timer scheduling and expiry.

Control flow and dependencies: The header expects helper functions `__trace_ip_proto()` and `__trace_ip_proto_seq()` plus `struct xfrm_iptfs_data` fields from `xfrm_iptfs.c`. It follows the standard Linux tracepoint pattern with `TRACE_INCLUDE_PATH`, `TRACE_INCLUDE_FILE`, and `trace/define_trace.h` outside the include guard.

State and persistence: Tracepoints do not persist state, but they read live skb and IP-TFS state fields. Their output becomes runtime observability through ftrace/perf/tracefs.

Integration points: Included by `xfrm_iptfs.c` after defining `CREATE_TRACE_POINTS`; trace events align with enqueue, dequeue, fragment sharing, timer, and receive parsing code.

Risks: Trace field expressions access skb fragment metadata and page addresses, so changes to skb layout handling in IP-TFS must keep trace-only code valid. Trace helpers are compiled under tracepoint conditions; missing helper definitions or field drift can produce build failures that appear only with tracing enabled.

Test signals: Build with tracing enabled, enable `iptfs:*` events in tracefs, and run IP-TFS traffic that triggers enqueue, no-space drops, PMTU too-big, fragmentation, aggregation, and timers. Validate no tracepoint dereference warnings occur for linear, paged, frag_list, and GSO skbs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/xfrm/trace_iptfs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/xfrm/xfrm_algo.c -->
# sources/distributed-fs/ceph-client/net/xfrm/xfrm_algo.c

Purpose: `xfrm_algo.c` is the algorithm registry and lookup layer for IPsec. It maps XFRM/PF_KEY algorithm identifiers and names to Linux crypto API transform names, default IV generators, ICV sizes, block sizes, key lengths, compression thresholds, and PF_KEY support flags.

Important data and APIs: Static descriptor tables cover AEAD (`rfc4106(gcm(aes))`, `rfc4309(ccm(aes))`, GMAC, ChaCha20-Poly1305), authentication (`hmac(md5)`, SHA variants, AES-XCBC, CMAC, SM3), encryption (`ecb(cipher_null)`, CBC ciphers, AES-CTR, SM4), and compression (`deflate`, `lzs`, `lzjh`). Exported lookups include `xfrm_aalg_get_byid()`, `xfrm_ealg_get_byid()`, `xfrm_calg_get_byid()`, name lookups for auth/encryption/compression/AEAD, index lookups for PF_KEY enumeration, `xfrm_probe_algs()`, and PF_KEY supported counters.

Control flow: `xfrm_find_algo()` scans the chosen table, optionally probes crypto availability through `crypto_has_aead()`, `crypto_has_ahash()`, `crypto_has_skcipher()`, or `crypto_has_acomp()`, caches availability in the descriptor, and returns matching descriptors. `xfrm_probe_algs()` refreshes availability for PF_KEY registration outside softirq context.

State and persistence: The only mutable state is per-descriptor `available`, cached in memory for the running kernel. No user configuration is persisted.

Dependencies and integration: XFRM user and PF_KEY code use descriptors to validate SA algorithms and advertise supported algorithms. IPComp uses compression descriptors for thresholds. ESP/AH code relies on matching crypto transform names and ICV metadata.

Risks: Descriptor mistakes can allow invalid key sizes, advertise unsupported algorithms, break IKE negotiation, or mismatch PF_KEY IDs. Availability caching is unsynchronized; current use is simple integer updates, but new concurrent mutation would need care. `BUG_ON(in_softirq())` in probing signals that callers must not run full probes from softirq.

Test signals: Use `ip xfrm state add` and PF_KEY registration with each advertised algorithm, including compat names like `aes` and `sha1`; test missing crypto modules, module autoload, AEAD ICV variants, IPComp threshold behavior, and PF_KEY algorithm counts before/after `xfrm_probe_algs()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/xfrm/xfrm_algo.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/xfrm/xfrm_compat.c -->
# sources/distributed-fs/ceph-client/net/xfrm/xfrm_compat.c

Purpose: `xfrm_compat.c` provides the 32-bit compatibility layer for XFRM netlink messages on 64-bit kernels. It translates request and response layouts where native structures include different padding/alignment around 64-bit lifetime fields.

Important APIs and types: The file defines compat variants for lifetime, policy, SA, acquire, SPI, expire, and policy-expire structures. `compat_msg_min[]` mirrors `xfrm_msg_min[]` with 32-bit layout lengths. `compat_policy[]` validates XFRM attributes for compat input. The module registers a `struct xfrm_translator` with `alloc_compat`, `rcv_msg_compat`, and `xlate_user_policy_sockptr`.

Control flow: Kernel-to-userspace translation uses `xfrm_alloc_compat()` to attach a translated skb frag_list and `xfrm_xlate64()` to create a compat netlink message. Attribute translation copies most attributes, uses `nla_put_64bit()` for u64-aligned values, and explicitly includes newer NAT keepalive and IP-TFS attributes. Userspace-to-kernel translation parses compat attributes, computes native length with `xfrm_user_rcv_calculate_len64()`, allocates a native message when needed, copies fixed headers with message-specific padding rules, and expands `XFRMA_SA`/`XFRMA_POLICY` attributes.

State and persistence: The module only registers/unregisters a global translator. Translated messages are temporary allocations. No XFRM policy or SA state is persisted here.

Dependencies and integration: It depends on `xfrm_user.c` policies and message sizes, the translator registry in `xfrm_state.c`, netlink attribute validation, nospec array indexing, and compat socket policy handling through `xlate_user_policy_sockptr`.

Risks: This is ABI-sensitive code. Missing a new XFRM attribute in `xfrm_xlate64_attr()` or `compat_policy[]` can break 32-bit userspace. Wrong padding can corrupt SA lifetime, policy, or expire messages. The `BUILD_BUG_ON(XFRMA_MAX != XFRMA_IPTFS_PKT_SIZE)` guards force updates when UAPI attributes grow.

Test signals: Run 32-bit `ip xfrm`/netlink tests on a 64-bit kernel for SA/policy add, update, dump, expire, acquire, NAT keepalive interval, and all IP-TFS attributes. Include malformed attribute lengths and dump requests that should bypass translation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/xfrm/xfrm_compat.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/xfrm/xfrm_device.c -->
# sources/distributed-fs/ceph-client/net/xfrm/xfrm_device.c

Purpose: `xfrm_device.c` manages hardware IPsec offload integration. It validates device capabilities, installs SA and policy offload state, prepares skbs for device encryption, resumes packets after async offload, and flushes offloaded state on netdevice events.

Important APIs: Under `CONFIG_XFRM_OFFLOAD`, exported functions include `validate_xmit_xfrm()`, `xfrm_dev_state_add()`, `xfrm_dev_policy_add()`, `xfrm_dev_offload_ok()`, `xfrm_dev_resume()`, and `xfrm_dev_backlog()`. Always-built notifier logic validates `NETIF_F_HW_ESP` feature combinations and flushes state/policy on device down or unregister.

Control flow: `validate_xmit_xfrm()` runs near transmit, skips already-resumed packets, checks packet-offload device affinity, handles GSO segmentation when rerouted or sequence overflow would occur, prepares mode-specific packet pointers, calls `x->type_offload->xmit()`, and queues async results through `xfrm_backlog` when needed. `xfrm_dev_state_add()` validates user offload flags, direction, TFC incompatibility, device lookup, ESN support, and type-offload presence before invoking `xdo_dev_state_add()`. Policy add is restricted to packet offload. `xfrm_dev_offload_ok()` checks MTU/GSO, tunnel header constraints, IPv4 options, IPv6 extension headers, and optional driver callback.

State and persistence: Offload state lives in `x->xso` and policy `xp->xdo`, holding device pointers, trackers, direction, and offload type. Per-CPU softnet `xfrm_backlog` temporarily stores packets requiring resume.

Dependencies and integration: The file depends on netdevice `xfrmdev_ops`, ESP type-offload callbacks, dst/MTU helpers, GSO, XFRM state/policy flushing, and network device notifiers.

Risks: Wrong pointer preparation can make hardware encrypt the wrong bytes. Device mismatch in packet offload must drop, not fall back, to avoid bypassing policy. ESN, GSO sequence overflow, and tunnel-size checks are subtle interoperability and security boundaries. Notifier failures can leave stale hardware state.

Test signals: Test crypto and packet offload devices, reroute to non-offload devices, GSO ESP segmentation, ESN support/no-support, IPv4 options, IPv6 extension headers, tunnel PMTU, device down/unregister flushing, async `-EINPROGRESS` resume, and policy offload direction validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/xfrm/xfrm_device.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/xfrm/xfrm_hash.c -->
# sources/distributed-fs/ceph-client/net/xfrm/xfrm_hash.c

Purpose: `xfrm_hash.c` provides common allocation and free helpers for XFRM hash tables used by policy and state databases.

Important APIs: `xfrm_hash_alloc(unsigned int sz)` returns a zeroed `struct hlist_head` array using `kzalloc()` for page-sized or smaller allocations, `vzalloc()` for distributed large allocations when `hashdist` is set, or contiguous pages via `__get_free_pages()` otherwise. `xfrm_hash_free()` mirrors the allocation path with `kfree()`, `vfree()`, or `free_pages()`.

Control flow and dependencies: Callers pass byte size, not element count. The helper chooses allocation strategy based on `PAGE_SIZE` and the global `hashdist` memory-allocation policy. It includes `xfrm_hash.h` for declarations and Linux memory APIs for allocation.

State and persistence: No state is retained by this file. Hash table contents are owned by callers; this helper only allocates zeroed bucket arrays and releases them.

Integration points: Used by XFRM policy/state hash infrastructure when resizing or initializing hash buckets. Correct zero initialization matters because empty hlist heads must begin as null.

Risks: Caller size mismatches or freeing with a different size than allocation can call the wrong free path. Large contiguous allocation without `hashdist` can fail under fragmentation; `vzalloc()` avoids that at the cost of vmalloc overhead. No overflow checking is performed here, so callers must compute `sz` safely.

Test signals: Exercise policy/state hash initialization and resize with small and large table sizes, with `hashdist` enabled and disabled. Use memory-pressure tests and KASAN/KMSAN to catch mismatched size/free paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/xfrm/xfrm_hash.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/xfrm/xfrm_hash.h -->
# sources/distributed-fs/ceph-client/net/xfrm/xfrm_hash.h

Purpose: `xfrm_hash.h` defines inline hash functions used by XFRM state and policy lookup tables, plus declarations for the allocation helpers in `xfrm_hash.c`.

Important APIs: Address helpers hash IPv4 and IPv6 addresses, destination/source pairs, prefixes, SPI/protocol/family tuples, replay sequence numbers, policy indexes, selectors, and explicit address/prefix pairs. `__sel_hash()` returns `hmask + 1` when a selector is less specific than configured hash thresholds, signaling callers to use inexact handling rather than a normal bucket.

Control flow: IPv4 address hashes mostly use host-order arithmetic plus Jenkins hashing for prefixes. IPv6 uses `jhash2()` across 128-bit addresses or prefix-sized words with an incomplete-word mask. Final bucket selection folds high bits and masks with caller-provided `hmask`.

State and persistence: No state is stored. Hash quality directly affects runtime distribution of state/policy buckets and lookup cost.

Dependencies and integration: Included by `xfrm_policy.c`, `xfrm_state.c`, and `xfrm_hash.c`. It depends on `xfrm_address_t`, selectors, address families, and `jhash` helpers. Hash threshold behavior integrates with policy inexact matching trees.

Risks: Hash changes alter bucket placement and can regress lookup performance or resizing behavior. Prefix masking must handle zero and partial prefixes correctly. Endianness mistakes would break IPv4 bucket consistency. The sentinel `hmask + 1` must not be treated as an actual bucket by callers.

Test signals: Add policies and states for IPv4/IPv6, exact and prefix selectors, zero-length prefixes, SPI collisions, and large hash tables. Validate lookup correctness before/after hash resize and with inexact policy thresholds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/xfrm/xfrm_hash.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/xfrm/xfrm_inout.h -->
# sources/distributed-fs/ceph-client/net/xfrm/xfrm_inout.h

Purpose: `xfrm_inout.h` contains shared inline helpers for saving inner IP header metadata before encapsulation/decapsulation and rebuilding BEET-mode headers afterward.

Important APIs: `xfrm4_extract_header()` stores IPv4 header length, ID, fragment offset, TOS, TTL, options length, and clears IPv6 flow label state in `XFRM_MODE_SKB_CB`. `xfrm6_extract_header()` stores IPv6 header length, synthesized DF state, DS field, hop limit, and flow label. `xfrm6_beet_make_header()` and `xfrm4_beet_make_header()` rebuild minimal IPv6/IPv4 BEET outer/inner headers from saved control-block values.

Control flow and integration: Output path calls extract helpers before moving headers for tunnel/BEET encapsulation. Input path uses saved metadata while removing encapsulation and restoring inner headers. BEET helpers are called by both `xfrm_input.c` and `xfrm_output.c`.

State and persistence: The helpers persist metadata only within `skb->cb` for the lifetime of a packet as it moves through XFRM mode processing.

Dependencies: They depend on IPv4/IPv6 header structures, DS field helpers, and `XFRM_MODE_SKB_CB`. IPv6 extraction is compiled conditionally and warns if called without IPv6 support.

Risks: `skb->cb` ownership is fragile; callers must not overwrite XFRM mode fields between extract and rebuild. Incorrect optlen or flow-label handling can break BEET interoperability. IPv6-disabled builds rely on WARN paths to catch invalid calls.

Test signals: Validate IPv4/IPv6 transport, tunnel, and BEET SAs; include IPv4 options, fragmentation fields, DSCP/ECN, TTL/hop-limit, and IPv6 flow labels. Use packet captures to ensure reconstructed headers preserve expected fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/xfrm/xfrm_inout.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/xfrm/xfrm_input.c -->
# sources/distributed-fs/ceph-client/net/xfrm/xfrm_input.c

Purpose: `xfrm_input.c` is the common inbound XFRM/IPsec processing state machine. It registers address-family callbacks, parses SPI/sequence values, looks up SAs, validates replay/expiry/mode, invokes protocol decrypt/authenticate input, removes encapsulation, and reinjects decapsulated packets.

Important APIs and types: Exported APIs include `xfrm_input_register_afinfo()`, `xfrm_input_unregister_afinfo()`, `secpath_set()`, `xfrm_parse_spi()`, `xfrm_input()`, `xfrm_input_resume()`, `xfrm_trans_queue_net()`, `xfrm_trans_queue()`, and `xfrm_input_init()`. Per-CPU `xfrm_trans_tasklet` queues transport reinjection work. `xfrm_input_afinfo[is_ipip][family]` stores callbacks under RCU.

Control flow: Normal input sets or copies secpath, parses AH/ESP/IPComp SPI and sequence, applies tunnel mark overrides, looks up state by mark/daddr/SPI/protocol/family, checks direction, updates skb mark, and records the state in secpath. It then validates state validity, encap type, replay, expiry, and tunnel mode under `x->lock`. Crypto is performed through `x->type->input()` or hardware offload `input_tail()`, with `-EINPROGRESS` resuming through `xfrm_input_resume()`. After replay advance and lifetime updates, mode-specific input removes transport/tunnel/BEET encapsulation or calls mode callbacks such as IP-TFS. Tunnel and GRO paths feed `gro_cells_receive()`, while transport mode calls AF `transport_finish()`.

State and persistence: Inbound packet state is recorded in skb secpath and XFRM skb control blocks. SA lifetime counters, `lastused`, replay windows, and integrity failure stats are updated. Per-CPU reinjection queues buffer packets temporarily.

Dependencies and integration: It depends on XFRM state lookup/replay/audit, AF protocol callbacks from IPv4/IPv6 code, GRO cells, offload metadata, `xfrm_inout.h`, netfilter conntrack reset, and mode callbacks.

Risks: This is a security boundary. Mistakes can bypass policy, accept replayed packets, leak device references on async paths, mishandle secpath depth, or reconstruct invalid inner headers. Encapsulation type matching is important for UDP/TCP ESP encapsulation correctness.

Test signals: Cover AH/ESP/IPComp, transport/tunnel/BEET/IP-TFS, IPv4/IPv6, UDP/TCP encapsulation, async crypto, hardware offload success/failure flags, replay failures, expired/acquire states, wrong direction, missing state audit, secpath max depth, GRO decap, and AF callback registration/unregistration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/xfrm/xfrm_input.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/xfrm/xfrm_interface_bpf.c -->
# sources/distributed-fs/ceph-client/net/xfrm/xfrm_interface_bpf.c

Purpose: `xfrm_interface_bpf.c` exposes unstable TC-BPF kfuncs for reading and writing XFRM metadata on skbs. It supports xfrm interfaces in collect-metadata mode, letting BPF programs steer packets by `if_id` and underlying link.

Important APIs: `struct bpf_xfrm_info` contains `if_id` and `link`. `bpf_skb_get_xfrm_info()` copies metadata from `skb_xfrm_md_info()` into BPF-provided memory. `bpf_skb_set_xfrm_info()` allocates or reuses a per-CPU `METADATA_XFRM` destination, stores metadata and original dst, and replaces `skb_dst`. `register_xfrm_interface_bpf()` registers the kfunc set for `BPF_PROG_TYPE_SCHED_CLS`.

Control flow: Set rejects skbs that already have metadata dst, lazily initializes `xfrm_bpf_md_dst` with `metadata_dst_alloc_percpu()` and `cmpxchg()`, uses the current CPU metadata destination, preserves original dst with a hold, and installs the metadata dst on the skb. Get fails with `-EINVAL` if no metadata exists.

State and persistence: The global per-CPU metadata dst pointer persists after first allocation. Each skb can carry temporary XFRM metadata and a held original dst until consumed by xfrm interface transmit logic.

Dependencies and integration: It depends on BTF kfunc registration, TC classifier BPF, metadata dst infrastructure, and `xfrm_interface_core.c` collect-md transmit path, which reads `skb_xfrm_md_info()`.

Risks: The interface is explicitly unstable. Incorrect dst reference handling can leak or use-after-free routes. Per-CPU metadata reuse assumes skb metadata lifetime is controlled by dst referenceing. Set rejects existing metadata to avoid overwriting unrelated tunnel metadata.

Test signals: Build with BTF/module BTF combinations, load TC-BPF programs using the kfuncs, test get-without-metadata failure, set-then-xmit on collect-md xfrm interface, original dst restoration in transmit, and verifier/BTF registration failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/xfrm/xfrm_interface_bpf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/xfrm/xfrm_interface_core.c -->
# sources/distributed-fs/ceph-client/net/xfrm/xfrm_interface_core.c

Purpose: `xfrm_interface_core.c` implements the `xfrm` virtual netdevice. It routes packets through XFRM SAs by `if_id`, receives decapsulated packets onto matching virtual devices, supports collect-metadata mode, registers lwtunnel XFRM encap, and wires protocol handlers for ESP/AH/IPComp/IPIP/IPIP6.

Important APIs and types: `struct xfrmi_net` stores per-net hash buckets of `struct xfrm_if` and one collect-md interface. Rtnetlink ops create/change/delete devices with `IFLA_XFRM_LINK`, `IFLA_XFRM_IF_ID`, and `IFLA_XFRM_COLLECT_METADATA`. LWT ops build/fill/compare `LWTUNNEL_ENCAP_XFRM` metadata. Protocol handlers call `xfrmi_input()` and `xfrmi_rcv_cb()`. Module init registers pernet state, IPv4/IPv6 protocol and tunnel handlers, rtnl link ops, BPF kfuncs, lwtunnel ops, and `xfrm_if_cb`.

Control flow: Receive callbacks locate an up xfrm interface by state `if_id` or collect-md, switch `skb->dev`, enforce inbound policy for cross-net delivery, scrub packet metadata, optionally attach metadata dst with if_id/link, and update rx stats. Transmit decodes IPv4/IPv6 flow, obtains or builds a route, performs `xfrm_lookup_with_ifid()`, rejects routing loops and wrong `if_id`, handles PMTU/ICMP errors, scrubs packet, switches to the underlying device, and calls `dst_output()`. Error handlers map ICMP/ICMPv6 PMTU and redirects back to matching SAs.

State and persistence: Per-net interface hash tables persist while net namespace lives. Each netdevice stores `xfrm_if_parms`, owning net, gro cells, and stats. Collect-md mode stores packet-specific metadata in dst metadata.

Dependencies and integration: Integrates with XFRM policy lookup, XFRM input callbacks, route/lwtunnel infrastructure, rtnetlink, IPv4/IPv6 tunnel/protocol registration, BPF kfuncs, gro cells, and namespace generic storage.

Risks: Cross-netns scrubbing and secpath reset are critical isolation points. Routing-loop detection prevents recursive xfrm output. Collect-md and fixed-if_id modes have different validation rules; allowing changes incorrectly could misroute traffic. Error handler SPI parsing must match AH/ESP/IPComp headers.

Test signals: Create fixed and collect-md xfrm devices, verify duplicate if_id rejection, change if_id, delete namespace cleanup, transmit IPv4/IPv6 through matching/missing policies, receive decapsulated traffic, PMTU errors, redirects, cross-netns paths, lwtunnel encap routes, TC-BPF metadata steering, and module unload cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/xfrm/xfrm_interface_core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/xfrm/xfrm_ipcomp.c -->
# sources/distributed-fs/ceph-client/net/xfrm/xfrm_ipcomp.c

Purpose: `xfrm_ipcomp.c` implements IP Payload Compression Protocol processing for XFRM states. It compresses outbound payloads, decompresses inbound payloads, manages async acomp requests, and initializes per-SA compression transforms.

Important APIs and types: Exported APIs are `ipcomp_input()`, `ipcomp_output()`, `ipcomp_destroy()`, and `ipcomp_init_state()`. `struct ipcomp_data` stores compression threshold and `crypto_acomp` transform. `struct ipcomp_skb_cb` overlays skb control block with XFRM cb plus request pointer. `struct ipcomp_req_extra` stores owning state and scatterlists after the acomp request.

Control flow: Inbound `ipcomp_input()` pulls the IPComp header, disables checksum offload, and calls `ipcomp_decompress()`. Request setup linearizes/cows skb as needed, builds source/destination scatterlists, allocates scratch pages, and starts `crypto_acomp_decompress()`. Completion calls `ipcomp_input_done2()` and resumes XFRM input. Outbound `ipcomp_output()` bypasses compression below threshold; otherwise it compresses, installs an IPComp header with CPI from state SPI, updates the previous protocol byte, and resumes XFRM output if async. `ipcomp_post_acomp()` rebuilds skb frags from destination pages and frees unused pages/request.

State and persistence: Per-SA `x->data` holds transform and threshold until state destroy. Async requests temporarily own pages and the request pointer in skb cb.

Dependencies and integration: Depends on Linux acomp crypto API, `xfrm_algo.c` compression descriptors, `xfrm_input_resume()`, `xfrm_output_resume()`, IPComp header definitions, skb fragment APIs, and XFRM state lifecycle.

Risks: Scatterlist/page ownership is delicate; error paths must free allocated pages and requests. skb control block overlay must remain within `skb->cb`. Compression is incompatible with encapsulation and rejects states with `x->encap`. Length validation prevents decompression truncation from producing invalid packets.

Test signals: Add IPComp SAs with deflate, missing calg rejection, encap rejection, below-threshold bypass, async and sync crypto completion, decompression length errors, memory-pressure request allocation failures, nonlinear skb input/output, and state destroy while no requests remain.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/xfrm/xfrm_ipcomp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/xfrm/xfrm_iptfs.c -->
# sources/distributed-fs/ceph-client/net/xfrm/xfrm_iptfs.c

Purpose: `xfrm_iptfs.c` implements IP-TFS/AGGFRAG tunnel mode for IPsec ESP, per RFC 9347. It aggregates multiple inner IP packets into one ESP payload, fragments large inner packets across multiple outer packets, reorders incoming tunnel packets, reassembles fragmented inner packets, and exposes mode-specific netlink attributes.

Important types and APIs: `struct xfrm_iptfs_config` stores packet size, queue size, reorder window, and dont-frag setting. `struct xfrm_iptfs_data` stores per-SA output queue, queue accounting, output hrtimer, payload MTU, reorder window, drop timer, and reassembly state. The mode registers `struct xfrm_mode_cbs` with `init_state`, `clone_state`, `destroy_state`, `user_init`, `copy_to_user`, `sa_len`, `get_inner_mtu`, `input`, `output`, and `prepare_output`.

Control flow: Output starts at `iptfs_output_collect()`, which optionally GSO-segments, enforces dont-frag PMTU, queues skbs under `x->lock`, marks ECN CE above 95 percent queue capacity, and starts `iptfs_timer`. Timer expiry drains the queue into `iptfs_output_queued()`. The first skb is converted into an IP-TFS packet; oversized packets are split by `iptfs_copy_create_frags()`, while following queued packets are appended by moving/sharing fragments or linking frag_list entries. Final packets go to `xfrm_output()`. Input starts at `iptfs_input()`, which uses a reorder window unless disabled. Ordered packets go to `iptfs_input_ordered()`, which validates IP-TFS headers, handles block offsets, calls reassembly helpers, extracts inner IPv4/IPv6 packets, completes DSCP/ECN metadata, and reinjects each inner packet through `xfrm_input(..., -2)`.

State and persistence: Per-SA mode data owns output queue bytes, timers, reorder array, pending reassembly skb/runt bytes, default/user config, and module reference. SA lifetime persists through XFRM state; queued packets and reorder entries are freed on destroy.

Dependencies and integration: Depends on XFRM mode callback registry, ESP AEAD block/auth sizes for MTU calculation, `xfrm_inout.h`, XFRM input/output resume semantics, skb fragment APIs, hrtimers, tracepoints from `trace_iptfs.h`, UAPI attributes parsed by `xfrm_user.c`, and compat handling in `xfrm_compat.c`.

Risks: The file is high risk because it rewrites skb geometry and shares page frags. Reorder/drop timer logic must avoid accepting stale fragments or leaking pending skbs. Queue accounting controls memory pressure and ECN marking. `dont_frag` PMTU behavior differs from classic ESP by ignoring inner DF unless configured. Timer and state destroy locking must prevent use-after-free.

Test signals: Validate IP-TFS SA add/dump with each attribute, aggregate small packets, fragment/reassemble large packets, disabled and nonzero reorder windows, out-of-order/duplicate/missing ESP sequences, drop timer expiry, runts at payload boundaries, IPv4/IPv6 inner packets, DSCP/ECN flags, GSO segmentation, queue overflow, dont-frag ICMP/local errors, configured packet size, module clone/destroy, and tracepoint output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/xfrm/xfrm_iptfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/xfrm/xfrm_nat_keepalive.c -->
# sources/distributed-fs/ceph-client/net/xfrm/xfrm_nat_keepalive.c

Purpose: `xfrm_nat_keepalive.c` sends NAT traversal keepalive packets for ESP-in-UDP XFRM states with `nat_keepalive_interval` configured. It periodically walks ESP states in a net namespace and emits one-byte UDP payload `0xff` to keep NAT mappings alive.

Important APIs and types: `struct nat_keepalive` snapshots net, family, addresses, UDP encapsulation ports, and mark from an XFRM state. Exported lifecycle functions are `xfrm_nat_keepalive_init()`, `xfrm_nat_keepalive_fini()`, `xfrm_nat_keepalive_net_init()`, `xfrm_nat_keepalive_net_fini()`, and `xfrm_nat_keepalive_state_updated()`. Per-CPU `sock_bh_locked` raw UDP sockets are allocated for IPv4 and optionally IPv6.

Control flow: State update schedules the namespace delayed work immediately when interval is nonzero. `nat_keepalive_work()` walks ESP states with `xfrm_state_walk()`. For each state, `nat_keepalive_work_single()` checks `lastused`, interval, and `nat_keepalive_expiration` under state lock, snapshots send parameters if due, and updates the earliest next run. Sending allocates a small skb, builds UDP header and payload, applies state mark, routes IPv4 with `ip_route_output_key()` and sends via `ip_build_and_send_pkt()`, or computes IPv6 UDP checksum, looks up dst, and sends via `ip6_xmit()`.

State and persistence: Per-net delayed work persists in `net->xfrm.nat_keepalive_work`. Per-state fields `nat_keepalive_interval`, `nat_keepalive_expiration`, and `lastused` drive scheduling. Per-CPU raw sockets persist for the address family until XFRM policy shutdown.

Dependencies and integration: Integrated with `xfrm_policy` net init/fini and AF init/fini, XFRM state update paths, `xfrm_user.c` NAT keepalive attribute, routing, raw control sockets, and socket net namespace switching.

Risks: Work scheduling must avoid stale namespace references. Sending after state lock release relies on a safe snapshot. Raw per-CPU socket net switching must be balanced. IPv6 checksum zero must be mangled. If intervals are too small across many SAs, the state walk and packet sends can become expensive.

Test signals: Configure ESP UDP-encap SAs with keepalive interval, verify one-byte UDP keepalives for IPv4 and IPv6, check no sends before interval after traffic updates `lastused`, namespace teardown cancellation, route failure skb freeing, mark propagation, and interval changes rescheduling work.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/xfrm/xfrm_nat_keepalive.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/xfrm/xfrm_output.c -->
# sources/distributed-fs/ceph-client/net/xfrm/xfrm_output.c

Purpose: `xfrm_output.c` is the common outbound XFRM/IPsec encapsulation engine. It prepares transport/tunnel/BEET/route-optimization/custom mode headers, applies state validation and replay/lifetime accounting, invokes protocol output or offload, handles netfilter post-routing loops, and emits PMTU errors.

Important APIs: Exported functions include `xfrm_output_resume()`, `xfrm_output()`, `xfrm4_tunnel_check_size()`, `xfrm6_tunnel_check_size()`, and `xfrm_local_error()`. Internal helpers cover skb head/tail expansion, dst stack popping, IPv4/IPv6 transport output, BEET and tunnel encapsulation, outer mode dispatch, GSO segmentation, packet offload direct output, and inner protocol recording for offload.

Control flow: `xfrm_output()` clears AF skb control blocks, handles packet offload early, resets secpath for software output, prepares offload secpath when allowed, segments GSO if needed, fixes partial checksums, then enters `xfrm_output_resume()`. `xfrm_output_one()` ensures skb space, applies state mark, calls `xfrm_outer_mode_output()` or mode callback `prepare_output`, validates state/expiry/replay under lock, updates lifetimes, invokes `x->type->output()` or `type_offload->encap()`, pops the dst stack, and repeats until a tunnel boundary. Resume then runs local_out, dst_output, and NF_INET_POST_ROUTING as needed.

State and persistence: Outbound processing updates SA byte/packet lifetime counters and `lastused`, advances replay sequence state through protocol output, manipulates skb dst/secpath/headers, and stores offload metadata such as `inner_ipproto`.

Dependencies and integration: Depends on XFRM state/mode/type callbacks, IPv4/IPv6 routing and PMTU helpers, netfilter, GSO, hardware offload from `xfrm_device.c`, `xfrm_inout.h`, and custom mode callbacks such as IP-TFS.

Risks: Header pointer arithmetic is fragile across transport, tunnel, BEET, IPv6 extension headers, and custom modes. PMTU behavior must avoid black holes while respecting DF semantics. Packet offload direct output must not bypass required software filtering in transport/local cases. Async protocol output must resume without double-freeing skbs.

Test signals: Cover IPv4/IPv6 transport, tunnel, BEET, route optimization, IP-TFS custom mode, nested bundles, post-routing reroute, GSO and partial checksum, packet and crypto offload, expired states, replay overflow, PMTU/local errors, IPv4 options/IPv6 extension headers, and async output resume from ESP/IPComp.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/xfrm/xfrm_output.c -->
