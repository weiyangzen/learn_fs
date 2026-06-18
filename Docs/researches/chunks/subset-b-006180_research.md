# sources/distributed-fs/ceph-client/net/core/filter.c lines 1-9866

Chunk ID: `subset-b-006180`

Source range researched: `sources/distributed-fs/ceph-client/net/core/filter.c` lines 1-9866. This is a chunk report only. The final source-tree-aligned per-file report for `sources/distributed-fs/ceph-client/net/core/filter.c` is intentionally left to the merge/reconciliation lane.

## Purpose

This chunk is the front and middle of Linux `net/core/filter.c`, copied under the Ceph client source tree. It implements most of the networking BPF runtime surface: classic socket filter import and conversion, socket filter attachment and lifetime management, SKB and XDP helper implementations, redirect execution, tunnel metadata helpers, socket option helpers, FIB and MTU lookup helpers, SRv6 LWT helpers, socket lookup helpers, TCP syncookie/header-option helpers, and the first part of helper dispatch plus verifier context access policy.

The code is not Ceph-specific at this layer. Its purpose is to provide kernel networking BPF infrastructure used by socket filters, traffic control, XDP, cgroup networking hooks, lightweight tunnel programs, sockmap/sk_msg programs, sock_ops, flow dissector programs, and related BPF attach types. Ceph only inherits the behavior indirectly through the vendored or mirrored kernel networking stack.

The range ends inside `bpf_convert_ctx_access()` at the `__sk_buff.pkt_type` conversion case. Context field conversions after line 9866, verifier ops tables, detach paths, reuseport/sk_lookup handling, dispatcher/kfunc registration, and remaining end-of-file setup continue in later chunks.

## Major Responsibilities In This Chunk

- Import user `sock_fprog` data in native and compat layouts.
- Run socket filters on receive SKBs and trim/drop packets based on BPF return values.
- Validate classic BPF instructions and convert cBPF to eBPF instructions when no JIT code is available.
- Allocate, charge, attach, reference, release, and RCU-free socket filters and reuseport programs.
- Implement SKB byte load/store, checksum, VLAN, protocol, head/tail/room adjustment, redirect, tunnel, XFRM, cgroup, socket cookie, netns cookie, and timestamp helpers.
- Implement XDP data/meta/tail adjust, multi-buffer load/store, redirect enqueue/flush, XSK/devmap/cpumap integration, and invalid-action warning.
- Implement sk_msg scatterlist transformations for sockmap message programs.
- Implement BPF setsockopt/getsockopt subsets for socket, TCP, IPv4, IPv6, sock_addr, sock_create, and sock_ops hooks.
- Implement IPv4/IPv6 FIB lookup, MTU checks, LWT encapsulation, SRv6 local actions, socket lookup, syncookie, TCP option, `tcp_sock`, and `xdp_sock` helper/access surfaces.
- Map `BPF_FUNC_*` helper IDs to `struct bpf_func_proto` by program type and attach type.
- Define verifier access checks and prologues for `__sk_buff`, `xdp_md`, `bpf_sock`, `bpf_sock_addr`, `bpf_sock_ops`, `sk_msg_md`, and flow dissector contexts.

## Important APIs, Types, And Functions

### Socket filter import, execution, and cBPF conversion

- `copy_bpf_fprog_from_user()` copies a socket filter descriptor from a `sockptr_t`, accepting either `compat_sock_fprog` or native `sock_fprog` depending on `in_compat_syscall()`. It validates the descriptor length and translates compat pointers with `compat_ptr()`. It is exported GPL.
- `sk_filter_trim_cap()` is the socket receive filter wrapper. It rejects pfmemalloc packets unless the socket has `SOCK_MEMALLOC`, runs cgroup ingress BPF, runs LSM `security_sock_rcv_skb()`, then executes `sk->sk_filter` under RCU via `bpf_prog_run_save_cb()`. A zero return drops, otherwise the SKB is trimmed with `pskb_trim(skb, max(cap, pkt_len))`. Drop causes are reported with `enum skb_drop_reason`.
- `bpf_skb_get_pay_offset()`, `bpf_skb_get_nlattr()`, and `bpf_skb_get_nlattr_nest()` implement classic BPF ancillary load helpers for payload offset and netlink attributes.
- `bpf_skb_load_helper_convert_offset()` maps cBPF negative pseudo offsets such as `SKF_NET_OFF` and `SKF_LL_OFF` to actual SKB offsets, rejecting unavailable link-layer offsets with `INT_MIN`.
- `bpf_skb_load_helper_8/16/32()` and `_no_cache` variants read packet bytes for cBPF absolute/indirect loads, using direct head reads when possible and `skb_copy_bits()` otherwise.
- `convert_skb_access()`, `convert_bpf_extensions()`, and `convert_bpf_ld_abs()` translate cBPF ancillary accesses and packet loads into eBPF instruction sequences.
- `bpf_convert_filter()` performs cBPF to eBPF remapping. It has a length-only pass, then a conversion pass with address remapping for jumps. It emits cBPF prologue state for A/X/CTX and, if packet loads are present, caches `skb->data` and headlen into callee-saved BPF registers.
- `check_load_and_stores()` performs classic BPF stack-cell definite-assignment analysis, ensuring `mem[]` reads only occur on cells written on all incoming paths.
- `chk_code_allowed()`, `bpf_check_basics_ok()`, and `bpf_check_classic()` validate cBPF opcodes, jump bounds, memory indices, shift counts, division-by-zero, valid ancillary offsets, and required final `RET`.
- `bpf_migrate_filter()` converts a classic program held in `struct bpf_prog` to eBPF interpreter form if JIT did not produce native code.
- `bpf_prepare_filter()` is the shared validation/JIT/migration path. It runs classic validation, optional caller transformation, `bpf_jit_compile()`, and eBPF migration if needed.
- `bpf_prog_create()`, `bpf_prog_create_from_user()`, and `bpf_prog_destroy()` create and release unattached classic socket filters.

### Filter lifetime, attachment, and memory charging

- `bpf_prog_store_orig_filter()` stores an original cBPF copy in `fp->orig_prog` so `sk_get_filter()` style users can retrieve it later.
- `bpf_release_orig_filter()`, `__bpf_prog_release()`, `__sk_filter_release()`, `sk_filter_release_rcu()`, and `sk_filter_release()` implement the release chain. Socket-filter eBPF programs use `bpf_prog_put()`, while migrated classic programs free `orig_prog` and `bpf_prog` memory directly.
- `sk_filter_uncharge()`, `__sk_filter_charge()`, and `sk_filter_charge()` charge filter memory against `sk->sk_omem_alloc`, bounded by `sock_net(sk)->core.sysctl_optmem_max`, and maintain `sk_filter.refcnt`.
- `__sk_attach_prog()` allocates `struct sk_filter`, charges the socket, initializes the reference count, RCU-publishes `sk->sk_filter`, and uncharges the old filter.
- `__get_filter()`, `sk_attach_filter()`, `sk_reuseport_attach_filter()`, `__get_bpf()`, `sk_attach_bpf()`, and `sk_reuseport_attach_bpf()` implement classic and fd-based attach paths. The reuseport path accepts both socket-filter and `BPF_PROG_TYPE_SK_REUSEPORT` programs, with family/protocol/type checks for reuseport-specific programs.
- `sk_reuseport_prog_free()` handles reuseport program release. Classic migrated programs are released through RCU so readers cannot observe freed instruction/original-filter storage.

### SKB data, checksum, and shape helpers

- `bpf_try_make_writable()` and variants wrap `skb_ensure_writable()` and refresh BPF packet data pointers after potential linearization/unclone.
- `bpf_skb_store_bytes()` validates flags, makes the target range writable, optionally recomputes checksum around the memcpy, and optionally invalidates the SKB hash.
- `bpf_skb_load_bytes()`, `bpf_flow_dissector_load_bytes()`, and `bpf_skb_load_bytes_relative()` copy bytes out of SKBs or flow dissector contexts. On failure they zero the destination buffer before returning an error.
- `bpf_skb_pull_data()` and `sk_skb_pull_data()` make SKB head data writable/linear enough for direct packet access. The generic SKB variant recomputes verifier-visible data pointers.
- `bpf_l3_csum_replace()`, `bpf_l4_csum_replace()`, `bpf_csum_diff()`, `bpf_csum_update()`, and `bpf_csum_level()` implement checksum mutation primitives. They validate offsets, widths, flags, and `CHECKSUM_COMPLETE`/`CHECKSUM_UNNECESSARY` state.
- `bpf_skb_vlan_push()` and `bpf_skb_vlan_pop()` wrap VLAN helpers and maintain ingress checksum state and BPF data pointers.
- `bpf_skb_change_proto()` converts IPv4 to IPv6 or IPv6 to IPv4 by pushing/popping network header room, updating GSO type, protocol, hash, route dst, and BPF data pointers.
- `bpf_skb_change_type()` restricts packet type updates to `skb_pkt_type_ok()` values.
- `bpf_skb_adjust_room()` and `sk_skb_adjust_room()` adjust SKB MAC/NET or stream parser room. The generic variant enforces IPv4/IPv6 protocols, size caps, GSO constraints, decap/encap flag legality, checksum reset behavior, and route invalidation. The sk_skb variant is narrower and updates TLS stream parser message length when relevant.
- `bpf_skb_change_tail()` and `sk_skb_change_tail()` grow/trim tail length, linearize/unclone, reset GSO on success, and protect minimum lengths that include network/transport/checksum coverage.
- `bpf_skb_change_head()` and `sk_skb_change_head()` add headroom for L2 redirection while preserving protocol/network header semantics.

### SKB redirect and neighbor output

- `bpf_clone_redirect()` clones the SKB, validates flags and GSO type, looks up the target ifindex, makes the original head writable for direct write invariants, and sends the clone through `__bpf_redirect()`.
- `bpf_redirect()`, `bpf_redirect_peer()`, and `bpf_redirect_neigh()` populate the per-CPU `struct bpf_redirect_info` from `bpf_net_ctx_get_ri()` and return `TC_ACT_REDIRECT` or `TC_ACT_SHOT`.
- `skb_do_redirect()` consumes `bpf_redirect_info`, resolves the target device, handles peer-device ingress redirection, and dispatches to regular redirect or neighbor redirect. It resets `ri->tgt_index` and `ri->flags`.
- `__bpf_redirect_common()` preserves MAC header semantics for devices transmitting link-layer headers. `__bpf_redirect_no_mac()` strips MAC headers for devices that do not transmit them.
- `bpf_out_neigh_v4()`, `bpf_out_neigh_v6()`, `__bpf_redirect_neigh_v4()`, and `__bpf_redirect_neigh_v6()` perform route lookup, neighbor lookup, headroom expansion, `neigh_output()`, and drop accounting for neighbor redirects.

### sk_msg scatterlist helpers

- `bpf_msg_apply_bytes()` and `bpf_msg_cork_bytes()` set `sk_msg` apply/cork counters.
- `bpf_msg_pull_data()` finds the requested range inside the scatterlist ring, linearizes shared or multi-entry data into a new page when necessary, removes replaced entries, updates `msg->data`/`data_end`, and resets iteration state.
- `bpf_msg_push_data()` inserts a zeroed page-backed region at the requested message offset, optionally copying and splitting an existing SGE when no ring space remains. It charges socket memory, updates `sg.size`, and recomputes BPF data pointers.
- `bpf_msg_pop_data()` removes bytes from the message, handling partial front/back SGE preservation, shifting the ring left or right, uncharging memory, and recomputing data pointers.
- `sk_msg_shift_left()`, `sk_msg_shift_right()`, and `sk_msg_reset_curr()` maintain the scatterlist ring and current/copybreak cursor.

### XDP buffer and redirect helpers

- `bpf_xdp_get_buff_len()`, `bpf_xdp_adjust_head()`, `bpf_xdp_adjust_tail()`, and `bpf_xdp_adjust_meta()` implement XDP length and pointer adjustment. They enforce frame boundary, metadata, ETH header, multi-buffer, and XSK zero-copy constraints.
- `bpf_xdp_copy_buf()` and `bpf_xdp_pointer()` provide XDP multi-buffer copy/address resolution across the linear area and page frags.
- `bpf_xdp_load_bytes()` and `bpf_xdp_store_bytes()` use `bpf_xdp_pointer()` for direct or cross-fragment copies.
- `xdp_do_flush()` flushes used devmap, cpumap, and XSK redirect queues for a NAPI cycle. `xdp_do_check_flushed()` warns under debug configs if a driver forgot to flush.
- `xdp_master_redirect()` supports master-device XDP redirection by selecting a slave and storing a direct ifindex redirect in `bpf_redirect_info`.
- `xdp_do_redirect()`, `xdp_do_redirect_frame()`, `xdp_do_generic_redirect()`, and `xdp_do_generic_redirect_map()` execute XDP redirect for XSKMAP, DEVMAP, DEVMAP_HASH, CPUMAP, broadcast, direct ifindex, and generic-SKB XDP paths.
- `bpf_xdp_redirect()` stores an ifindex redirect marker using `map_id == INT_MAX`; `bpf_xdp_redirect_map()` delegates to `map->ops->map_redirect()`.
- `bpf_warn_invalid_xdp_action()` emits a one-time warning for illegal or driver-unsupported XDP return values.

### Tunnel, metadata, cgroup, cookie, and output helpers

- `bpf_skb_event_output()` and `bpf_xdp_event_output()` copy SKB/XDP context bytes into perf event output using `bpf_event_output()`. BTF-tracing variants expose `bpf_skb_output_proto` and `bpf_xdp_output_proto`.
- `bpf_skb_get_tunnel_key()` and `bpf_skb_get_tunnel_opt()` read tunnel metadata from `skb_tunnel_info()`, including compatibility handling for older `struct bpf_tunnel_key` sizes.
- `bpf_skb_set_tunnel_key()` lazily allocates and reuses per-CPU `metadata_dst` storage (`md_dst`) and installs TX tunnel metadata on the SKB dst. `bpf_skb_set_tunnel_opt()` writes options into that per-CPU tunnel metadata.
- `bpf_get_skb_set_tunnel_proto()` lazily allocates `md_dst` with `metadata_dst_alloc_percpu()` and returns the set-key/set-opt prototypes.
- `bpf_skb_under_cgroup()`, `bpf_skb_cgroup_id()`, `bpf_skb_ancestor_cgroup_id()`, `bpf_sk_cgroup_id()`, and `bpf_sk_ancestor_cgroup_id()` expose socket/cgroup relationships when cgroup data is available.
- `bpf_get_socket_cookie*()` and `bpf_get_socket_ptr_cookie()` expose stable socket cookies across SKB, sock_addr, sock, sock_ops, and pointer contexts.
- `bpf_get_netns_cookie*()` returns the net namespace cookie for SKB, sock, sock_addr, sock_ops, and sk_msg contexts, falling back to `init_net` when no socket is available.
- `bpf_get_socket_uid()` returns the socket owner uid mapped through the socket net namespace user namespace, or `overflowuid` when no full socket is available.
- `bpf_skb_get_xfrm_state()` copies selected XFRM state fields out of an SKB security path when `CONFIG_XFRM` is enabled.

### Socket option and bind helpers

- `sol_socket_sockopt()`, `sol_tcp_sockopt()`, `sol_ip_sockopt()`, and `sol_ipv6_sockopt()` define the permitted BPF getsockopt/setsockopt option subset and length rules. They delegate to normal kernel sockopt implementations after validation.
- `bpf_sol_tcp_setsockopt()` supports BPF-specific TCP options such as initial window, cwnd clamp, delayed ACK max, RTO min, and sock_ops callback flags.
- `sol_tcp_sockopt_congestion()` handles `TCP_CONGESTION` with loop prevention through `tp->bpf_chg_cc_inprogress` and rejects `cdg` because it allocates in the CA private area.
- `__bpf_setsockopt()` and `__bpf_getsockopt()` are the shared unlocked core, while `_bpf_setsockopt()` and `_bpf_getsockopt()` assert socket ownership for full locked sockets.
- `bpf_sk_setsockopt()`, `bpf_sk_getsockopt()`, `bpf_sk_setsockopt_nodelay()`, `bpf_unlocked_sk_setsockopt()`, and `bpf_unlocked_sk_getsockopt()` expose sock pointer variants.
- `bpf_sock_addr_setsockopt()` and `bpf_sock_addr_getsockopt()` expose sock_addr context variants.
- `bpf_sock_create_setsockopt()` and `bpf_sock_create_getsockopt()` additionally handle `SK_BPF_BYPASS_PROT_MEM`.
- `bpf_sock_ops_setsockopt()` and `bpf_sock_ops_getsockopt()` restrict usage to locked sock_ops callbacks and special-case SYN data reads.
- `bpf_sock_ops_cb_flags_set()` updates `tcp_sock.bpf_sock_ops_cb_flags` with mask validation.
- `bpf_bind()` allows cgroup connect programs to bind IPv4 or IPv6 sockets, optionally forcing no-port address binding for port zero.

### FIB, MTU, LWT, SRv6, and socket lookup helpers

- `bpf_ipv4_fib_lookup()` and `bpf_ipv6_fib_lookup()` implement IPv4/IPv6 route lookups for BPF, including forwarding-enabled checks, direct table lookup, optional table id, mark, source address selection, multipath selection, MTU checking, LWT rejection, neighbor lookup, and DMAC/SMAC output.
- `bpf_xdp_fib_lookup()` and `bpf_skb_fib_lookup()` validate `struct bpf_fib_lookup` length and flags, call the family-specific lookup, and for SKBs optionally check actual SKB forwardability against the returned device MTU.
- `bpf_skb_check_mtu()` and `bpf_xdp_check_mtu()` validate an SKB/XDP packet or supplied L3 length against a device MTU, including SKB GSO segment checks when requested.
- `bpf_lwt_in_push_encap()` and `bpf_lwt_xmit_push_encap()` dispatch LWT encapsulation to SRv6 or IP tunnel helpers depending on configuration and ingress/egress mode.
- `bpf_lwt_seg6_store_bytes()`, `bpf_lwt_seg6_action()`, and `bpf_lwt_seg6_adjust_srh()` modify SRH bytes, execute supported SEG6 local actions, and grow/shrink SRH TLV space. They rely on per-CPU `seg6_bpf_srh_states` and lockdep-held `bh_lock`.
- `sk_lookup()`, `__bpf_skc_lookup()`, `__bpf_sk_lookup()`, `bpf_skc_lookup()`, and `bpf_sk_lookup()` implement TCP/UDP socket lookup by tuple, network namespace id, ifindex, and sdif. They handle request-sock conversion and reference release with `sock_gen_put()`.
- `bpf_skc_lookup_tcp()`, `bpf_sk_lookup_tcp()`, `bpf_sk_lookup_udp()`, TC-specific variants, XDP variants, and sock_addr variants expose lookup helpers with return types either `RET_PTR_TO_SOCK_COMMON_OR_NULL` or `RET_PTR_TO_SOCKET_OR_NULL`.
- `bpf_sk_release()` drops a lookup-acquired reference when the returned socket is refcounted.
- `bpf_tcp_sock()` returns a TCP full socket pointer, `bpf_get_listener_sock()` returns a listening socket when safe under RCU, and `bpf_skb_ecn_set_ce()` sets ECN CE for IPv4/IPv6 SKBs if the header is writable.
- `bpf_tcp_check_syncookie()`, `bpf_tcp_gen_syncookie()`, and raw IPv4/IPv6 syncookie helpers implement syncookie validation/generation with listener, header, protocol, sysctl, and CONFIG gating.
- `bpf_sk_assign()` assigns an ingress TC SKB to a socket after netns, hash, and refcount checks.
- `bpf_sock_ops_load_hdr_opt()`, `bpf_sock_ops_store_hdr_opt()`, and `bpf_sock_ops_reserve_hdr_opt()` let sock_ops programs read, reserve, and write TCP options in the appropriate callbacks. `bpf_search_tcp_opt()` handles TCP option parsing, EOL/NOP, malformed lengths, and experimental option magic.
- `bpf_skb_set_tstamp()` sets SKB timestamp and timestamp type for IPv4/IPv6 SKBs.

### Helper dispatch and verifier support

- `bpf_helper_changes_pkt_data()` declares helpers that invalidate packet pointers or otherwise mutate packet data; verifier code uses this to force pointer revalidation.
- `sock_filter_func_proto()`, `sock_addr_func_proto()`, `sk_filter_func_proto()`, `cg_skb_func_proto()`, `tc_cls_act_func_proto()`, `xdp_func_proto()`, `sock_ops_func_proto()`, `sk_msg_func_proto()`, `sk_skb_func_proto()`, `flow_dissector_func_proto()`, `lwt_out_func_proto()`, `lwt_in_func_proto()`, `lwt_xmit_func_proto()`, and `lwt_seg6local_func_proto()` map `BPF_FUNC_*` IDs to helper prototypes for each program type and attach type.
- Weak function prototype declarations such as `bpf_event_output_data_proto`, `bpf_sk_storage_get_proto`, sockmap/sk_msg redirect/update prototypes, and cgroup socket storage prototypes let optional subsystems supply helpers without hard dependencies.
- `bpf_skb_is_valid_access()` is the common `__sk_buff` verifier policy. It enforces offset/size alignment, writable field set, packet pointer register types, padding denial, timestamp/hwtstamp rules, and socket pointer typing.
- Program-type access policies refine the common SKB rules: `sk_filter_is_valid_access()`, `cg_skb_is_valid_access()`, `lwt_is_valid_access()`, `tc_cls_act_is_valid_access()`, and `sk_skb_is_valid_access()`.
- `bpf_sock_is_valid_access()`, `bpf_sock_common_is_valid_access()`, and `sock_filter_is_valid_access()` validate `struct bpf_sock` fields with attach-type-specific read/write allowances through `__sock_filter_check_attach_type()`.
- `xdp_is_valid_access()` validates `xdp_md` access, including offloaded write allowance for `rx_queue_index`, DEVMAP `egress_ifindex` gating, and packet/meta/end pointer typing.
- `sock_addr_is_valid_access()` validates `bpf_sock_addr` access by attach family and operation type, including writable IP/port fields and read-only socket pointer typing.
- `sock_ops_is_valid_access()`, `sk_msg_is_valid_access()`, and `flow_dissector_is_valid_access()` validate their context-specific field sets.
- `bpf_unclone_prologue()` emits a direct-write prologue that checks `skb->cloned`, calls `bpf_skb_pull_data(skb, 0)`, and returns the program-type drop verdict on failure. `tc_cls_act_prologue()` and `sk_skb_prologue()` specialize this for TC and SK_SKB.
- `bpf_gen_ld_abs()` emits no-cache packet load helper calls for eBPF `LD_ABS/LD_IND`.
- `flow_dissector_convert_ctx_access()` converts flow dissector pseudo-`__sk_buff` data/data_end/flow_keys accesses.
- `bpf_convert_tstamp_type_read()`, `bpf_convert_shinfo_access()`, `bpf_convert_tstamp_read()`, and `bpf_convert_tstamp_write()` are support routines for SKB context conversion. The chunk ends as `bpf_convert_ctx_access()` begins mapping `__sk_buff` fields to real `struct sk_buff`/`net_device` loads and stores.

## Control Flow

### Socket filter path

1. Userspace supplies a classic filter through `copy_bpf_fprog_from_user()` or an fd-based eBPF program.
2. Classic filters go through `__get_filter()`, `bpf_prog_create()`, or `bpf_prog_create_from_user()`, which allocate `struct bpf_prog`, copy instructions, optionally preserve the original cBPF, validate via `bpf_check_classic()`, run optional transformations, and JIT or migrate the program.
3. Attachment paths call `__sk_attach_prog()` or `reuseport_attach_prog()`. Socket-attached filters are charged to socket optmem and installed with RCU.
4. Receive path `sk_filter_trim_cap()` runs cgroup ingress, LSM, and socket filter. The BPF return value is interpreted as a desired packet length; zero drops the packet, nonzero trims to `max(cap, pkt_len)`.
5. Release paths decrement filter refs, RCU-defer `struct sk_filter` free, and release either fd-owned eBPF refs or migrated classic program memory.

### cBPF conversion flow

`bpf_convert_filter()` first computes the eBPF instruction count. On real conversion it emits the classic prologue, remaps every cBPF instruction into one or more eBPF instructions, stores original-to-new address mappings, and then repeats until jump offsets are stable. Arithmetic maps mostly one-to-one except for div/mod-by-zero guards. Packet loads become inline direct head loads when safe or helper calls when nonlinear/out-of-head/negative pseudo offsets require it. Branches are rewritten with signed 16-bit eBPF offsets and conditional inverse optimizations.

### Packet helper flow

Most SKB mutation helpers follow the same pattern: validate flags and bounds, make the SKB writable or unclone/cow as required, perform the data/header mutation, update checksums/hash/GSO/dst metadata as needed, and recompute BPF-visible data pointers when the helper is visible to direct packet access programs. The verifier marks many of these helpers through `bpf_helper_changes_pkt_data()` so packet pointers must be rechecked after calls.

### Redirect flow

TC redirect helpers do not transmit immediately. `bpf_redirect*()` stores intent in the per-CPU redirect info and returns `TC_ACT_REDIRECT`. The TC core later calls `skb_do_redirect()`, which resolves the device and sends the SKB through peer, neighbor, no-MAC, or normal redirect logic. XDP redirect mirrors this two-stage design: BPF helpers store target state, drivers call `xdp_do_redirect()` for `XDP_REDIRECT`, and finally call `xdp_do_flush()` before completing NAPI.

### Helper availability flow

Helper functions are implemented once, then exposed selectively through `*_func_proto()` dispatchers. Dispatch depends on BPF program type, expected attach type, Kconfig availability, GPL-only status, argument type descriptors, and sometimes cgroup common helper availability. This is the central policy surface for whether an otherwise implemented helper can be called from a given program.

### Verifier access flow

Verifier `is_valid_access` routines first check raw offset, alignment, and size, then refine by field and program type. They assign special register types for packet pointers, packet ends, metadata pointers, socket pointers, and flow keys. For direct-write-capable program types, prologue generators emit runtime unclone/pull logic before program execution.

## State And Persistence Behavior

- Socket filter attachment persists in `sk->sk_filter` under RCU until replaced or detached. Memory is charged to `sk->sk_omem_alloc` and bounded by per-net `sysctl_optmem_max`.
- Classic program origin is optionally persisted in `bpf_prog.orig_prog` to support filter retrieval. Migrated classic programs are owned differently from fd-loaded socket-filter eBPF programs and must follow the custom release path.
- The per-CPU `bpf_redirect_info` is transient state used between helper calls and redirect execution. TC paths reset `ri->tgt_index`/`flags`; XDP paths reset `map_id`, `flags`, and `map_type` after consumption.
- `md_dst` is a lazily allocated per-CPU `metadata_dst` cache used for tunnel TX metadata. It is global static state in this file.
- `xfrm_bpf_md_dst` is an exported per-CPU pointer when XFRM interface BTF conditions are met.
- `bpf_master_redirect_enabled_key` is a static key exported for master-device XDP redirect enablement.
- sk_msg helpers persist message edits in `struct sk_msg` scatterlist rings, including page refcounts, `sg.size`, `sg.start/end/curr`, `copybreak`, `data`, and `data_end`.
- Socket option helpers persist changes in socket fields and protocol control blocks: examples include `sk_bpf_cb_flags`, `sk_bypass_prot_mem`, TCP cwnd/ssthresh, delayed ACK max, RTO min, congestion control, and sock_ops callback flags.
- `nf_conn_btf_access_lock` and function pointer `nfct_btf_struct_access` form an exported integration point for netfilter conntrack BTF struct access checks.
- Timestamp conversion records `prog->tstamp_type_access` during verifier access checking; later conversion behavior changes depending on whether the BPF program explicitly read `tstamp_type`.

## Dependencies And Integration Points

- Core BPF: `struct bpf_prog`, verifier helpers, `struct bpf_func_proto`, BTF IDs, JIT selection, program refcounting, map redirect ops, event output, static calls/dispatchers, weak optional helper prototypes.
- Networking core: `struct sk_buff`, `struct sock`, `struct net_device`, `struct net`, `dst_entry`, `neighbour`, routes, FIB tables, NAPI, devmap/cpumap, XSK, XDP frames/buffers, SKB checksum/GSO APIs, VLAN, tunnel metadata, and flow dissector.
- Cgroups and LSM: cgroup ingress programs, cgroup classid/cgroup ID helpers, socket cgroup data, and `security_sock_rcv_skb()`.
- Protocol stacks: IPv4, IPv6, TCP, UDP, MPTCP include surface, raw syncookies, TCP option parsing, saved SYN state, ECN, socket options, and bind/connect hooks.
- LWT/SRv6/XFRM: lightweight tunnel encapsulation, SRH state, segment routing actions, XFRM security path state, and metadata dst export for XFRM interface modules.
- Netfilter conntrack BPF: optional BTF struct access is synchronized through `nf_conn_btf_access_lock` and delegated through `nfct_btf_struct_access`.
- Kconfig gates heavily shape the compiled helper surface: `CONFIG_INET`, `CONFIG_IPV6`, `CONFIG_SYN_COOKIES`, `CONFIG_XFRM`, `CONFIG_IPV6_SEG6_BPF`, `CONFIG_LWTUNNEL_BPF`, `CONFIG_CGROUP_NET_CLASSID`, `CONFIG_SOCK_CGROUP_DATA`, `CONFIG_DEBUG_NET`, `CONFIG_BPF_SYSCALL`, and BTF module options.

## Risks And Edge Cases

- cBPF conversion is correctness-critical. Jump remapping, sign/zero extension of negative immediates, div/mod-by-zero behavior, stack depth tracking, and packet-load fast paths must preserve classic semantics.
- Socket filter lifetime has split ownership between fd-backed eBPF programs and migrated classic programs. Wrong release path can leak or free active programs; RCU and refcount rules are central.
- Many helpers mutate SKB data and headers. Missing `bpf_compute_data_pointers()` or missing verifier pointer invalidation can expose stale packet pointers.
- Checksum and GSO interactions are subtle. Helpers must update `ip_summed`, checksum levels, `gso_type`, `gso_size`, `gso_segs`, and `SKB_GSO_DODGY` correctly after protocol/room/tail mutations.
- Redirect paths consume or free SKBs on many error paths. Incorrect return-code or ownership handling can double-free, leak, or miscount drops.
- XDP redirect relies on drivers calling `xdp_do_flush()` in the same NAPI cycle. The code documents that RCU protection is implicit through NAPI/bottom-half context rather than an explicit top-level `rcu_read_lock()`.
- XDP multi-buffer and XSK zero-copy tail adjustment has fragile ownership/refcount behavior around fragments, `xdp_frags_size`, `nr_frags`, `xsk_buff_get_tail/head()`, and `__xdp_return()`.
- sk_msg scatterlist editing manually shifts ring entries and page refs. Partial entry splits, zero-length entries, unavailable SGE space, and memory charging are high-risk.
- Tunnel metadata uses a global per-CPU `md_dst` cache. Allocation races are handled with `cmpxchg()`, but helper users rely on per-CPU reuse and correct `dst_hold()`/`skb_dst_set()` behavior.
- Socket option helpers intentionally expose only a whitelist. Expanding this surface risks recursion, lock ordering, protocol-state corruption, or unsupported non-full sockets.
- FIB lookup and neighbor helpers assume appropriate RCU/bh context from XDP/TC. They also intentionally reject LWT encapsulation in lookup results and may return BPF-specific error codes rather than errno.
- `bpf_sk_assign()` only supports TC ingress and requires socket/netns/hash/refcount checks. Misuse could bind packets to wrong sockets or leak refs.
- Syncookie helpers depend on listener state, sysctl enablement, header lengths, and IP family. Raw helpers are GPL-only and gated by `CONFIG_SYN_COOKIES`.
- Verifier access policy is a security boundary. Incorrect field size, padding, write permission, or register type assignment can expose kernel memory or allow invalid writes.
- The chunk ends mid-function in `bpf_convert_ctx_access()`. Conclusions about complete `__sk_buff` field conversion require the following chunk.

## Test Signals

Useful validation signals for this chunk include:

- Classic BPF socket filter tests covering valid/invalid opcodes, jumps, memory load-before-store, zero divisors, negative immediates, ancillary fields, `LD_ABS/LD_IND`, and migrated interpreter behavior.
- Socket attach tests for `SO_ATTACH_FILTER`, `SO_ATTACH_BPF`, reuseport classic/eBPF attach, `SOCK_FILTER_LOCKED`, optmem accounting failures, replacement, detach, and concurrent receive under RCU.
- SKB helper selftests for `bpf_skb_load_bytes`, `store_bytes`, checksum replacement/update/level, VLAN push/pop, `change_proto`, `adjust_room`, `change_head`, `change_tail`, timestamp setting, and packet pointer invalidation after mutating helpers.
- TC redirect tests for ifindex redirect, peer redirect, neighbor redirect with and without supplied nexthop, invalid flags, missing devices, GSO type rejection, no-MAC devices, and drop accounting.
- XDP selftests for adjust head/meta/tail, multi-buffer load/store, XSK zero-copy fragment grow/shrink, devmap/cpumap/xskmap redirect, broadcast redirect, generic XDP redirect, missing flush warnings under debug configs, and invalid action warnings.
- sk_msg/sockmap tests for apply/cork bytes and pull/push/pop data across single SGE, multi-SGE, shared-page, no-free-slot, and partial split cases.
- Tunnel metadata tests for IPv4/IPv6 tunnel key get/set, deprecated `bpf_tunnel_key` sizes, tunnel option size/alignment, per-CPU metadata reuse, and invalid flag handling.
- cgroup and socket cookie tests for classid, cgroup ID, ancestor ID, netns cookie, socket uid, sock storage helper availability, and attach-type-specific helper dispatch.
- Sockopt tests for allowed and rejected SOL_SOCKET/SOL_TCP/SOL_IP/SOL_IPV6 options, TCP congestion loop prevention, `TCP_NODELAY` rejection in sensitive callbacks, `SK_BPF_BYPASS_PROT_MEM`, SYN retrieval, and zeroing of unused get buffers.
- FIB/MTU tests for IPv4/IPv6 direct and full lookup, table id, mark, source selection, MTU failure, missing neighbor, disabled forwarding, non-unicast routes, LWT rejection, GSO segment MTU checks, and XDP/SKB parity.
- SRv6/LWT tests for push encap, store bytes, action variants, SRH adjust bounds, invalid SRH state, and payload length/header pointer updates.
- Socket lookup tests for TCP/UDP IPv4/IPv6 tuple sizes, netns id lookup, sdif behavior, request-sock to listener conversion, refcounted release, and verifier-enforced `bpf_sk_release()`.
- Verifier tests for helper availability by program type and attach type, `bpf_helper_changes_pkt_data()`, `__sk_buff` writable fields, packet pointer register typing, `xdp_md` DEVMAP `egress_ifindex`, sock_addr family gating, sock_ops writable fields, sk_msg read-only policy, flow dissector `flow_keys`, and timestamp/tstamp_type behavior.

## Boundary Notes For Merge Lane

- This chunk covers lines 1-9866 and stops inside `bpf_convert_ctx_access()` immediately after emitting the first instruction for the `__sk_buff.pkt_type` case.
- Later chunks must complete `bpf_convert_ctx_access()`, verifier ops/program ops tables, socket filter detach/retrieval paths, reuseport/sk_lookup program execution, dispatcher definitions, kfunc/kptr registrations, and file-level initialization/cleanup details.
- The final per-file report should synthesize this chunk with later chunks because helper dispatch and verifier conversion are split across the boundary.
