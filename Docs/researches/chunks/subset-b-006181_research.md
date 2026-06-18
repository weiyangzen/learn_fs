# sources/distributed-fs/ceph-client/net/core/filter.c lines 9867-12622

## Scope

This chunk covers the tail of Linux networking BPF support in `net/core/filter.c`. It begins inside `bpf_convert_ctx_access()` while lowering `struct __sk_buff` virtual fields into real `struct sk_buff`, `qdisc_skb_cb`, `sock_common`, and `skb_shared_info` loads/stores, then continues through the context access converters and verifier/prog operation tables for socket, TC, XDP, cgroup sock address, sock ops, SK_SKB, SK_MSG, flow dissector, SO_REUSEPORT, and SK_LOOKUP programs.

The latter part wires runtime helper behavior: classic socket filter detach/get, SO_REUSEPORT selection helpers, SK_LOOKUP assignment, XDP dispatcher replacement, BTF socket type cast helpers, skb metadata and dynptr kfuncs, TCP request-socket assignment, socket timestamp enabling, XDP non-linear pull-up, and late BTF kfunc registration.

## Purpose

The code in this range is the ABI translation and helper-registration layer that makes high-level BPF network contexts usable by verified eBPF programs. BPF programs see stable UAPI structs such as `__sk_buff`, `bpf_sock`, `xdp_md`, `bpf_sock_addr`, `bpf_sock_ops`, `sk_msg_md`, `sk_reuseport_md`, and `bpf_sk_lookup`. The kernel actually stores packet, socket, and XDP state in internal structs with different layouts. The converter functions here generate replacement BPF instructions that translate each allowed context access into safe internal loads/stores.

The same section also defines the verifier hooks and program test hooks that bind each network BPF program type to its access rules, helper whitelist, prologue, and test-run entry point. It ends by publishing BTF kfunc sets so selected program types can create dynptrs over skb/XDP data, mutate socket address paths, synthesize TCP request sockets, enable TCP tx timestamps, pull non-linear XDP data into the linear area, and destroy sockets from tracing iterators.

## Important APIs, Types, and Functions

- `bpf_convert_ctx_access()` handles many `__sk_buff` fields. This chunk includes `queue_mapping`, VLAN fields, `cb[]`, `tc_classid`, packet pointer fields, `tc_index`, `napi_id`, socket tuple fields, timestamp fields, GSO fields, `wire_len`, `sk`, and hardware timestamp access. It uses `BPF_LDX_MEM`, `BPF_EMIT_STORE`, `bpf_target_off()`, and helper converters such as `bpf_convert_tstamp_read/write()` and `bpf_convert_shinfo_access()`.
- `bpf_sock_convert_ctx_access()` lowers `struct bpf_sock` fields to `struct sock`, `struct sock_common`, and IPv6 address arrays. It permits writes for `bound_dev_if`, `mark`, and `priority`, exposes family/type/protocol/IP/port/state, and maps missing `rx_queue_mapping` to `-1`.
- `tc_cls_act_convert_ctx_access()` special-cases `__sk_buff.ifindex` through `skb->dev->ifindex`, then falls back to generic skb conversion. This keeps TC cls/act ifindex semantics tied to the ingress/egress `net_device`.
- `xdp_convert_ctx_access()` maps `xdp_md` packet pointers, RX queue fields, ingress ifindex, and egress ifindex to `struct xdp_buff`, `xdp_rxq_info`, `xdp_txq_info`, and `net_device`.
- `SOCK_ADDR_LOAD_NESTED_FIELD*()` and `SOCK_ADDR_STORE_NESTED_FIELD_OFF()` are instruction-emitting macros for `bpf_sock_addr_kern` nested pointer access. Stores borrow a temporary BPF register and preserve it through `bpf_sock_addr_kern.tmp_reg`.
- `sock_addr_convert_ctx_access()` maps user address family/IP/port fields through `uaddr`, socket metadata through `sk`, source-message fields through `t_ctx`, and exposes `sk`. It supports writes to user IP/port and message source IP fields where verifier policy allows them.
- `sock_ops_convert_ctx_access()` translates `bpf_sock_ops` to `bpf_sock_ops_kern`, `sock_common`, `sock`, `tcp_sock`, and skb fields. Macros `SOCK_OPS_GET_FIELD`, `SOCK_OPS_SET_FIELD`, and `SOCK_OPS_GET_SK` guard full-socket or locked-TCP-only reads/writes and preserve registers via `bpf_sock_ops_kern.temp`.
- `bpf_convert_data_end_access()` computes `skb->data + skb_headlen(skb)` as `skb->data + skb->len - skb->data_len` for SK_SKB contexts.
- `sk_skb_convert_ctx_access()` overrides `__sk_buff.data_end` and SK_SKB `cb[]` mapping, using `struct sk_skb_cb` instead of `qdisc_skb_cb`, then falls back to generic skb conversion.
- `sk_msg_convert_ctx_access()` maps `sk_msg_md` packet pointers and socket tuple fields to `struct sk_msg`, `sk_msg_sg`, and `sock_common`.
- Verifier and prog ops tables include `sk_filter_verifier_ops`, `tc_cls_act_verifier_ops`, `xdp_verifier_ops`, `cg_skb_verifier_ops`, `lwt_*_verifier_ops`, `cg_sock_verifier_ops`, `cg_sock_addr_verifier_ops`, `sock_ops_verifier_ops`, `sk_skb_verifier_ops`, `sk_msg_verifier_ops`, `flow_dissector_verifier_ops`, `sk_reuseport_verifier_ops`, and `sk_lookup_verifier_ops`.
- `sk_detach_filter()` removes `sk->sk_filter` under socket locking unless `SOCK_FILTER_LOCKED` is set, then uncharges the filter.
- `sk_get_filter()` returns the original classic BPF program attached to a socket, if one exists, through a socket option buffer. eBPF-only filters without `orig_prog` are not dumpable through this API.
- `bpf_run_sk_reuseport()` initializes `struct sk_reuseport_kern`, runs a reuseport BPF program, and returns the selected socket on `SK_PASS` or `ERR_PTR(-ECONNREFUSED)` otherwise.
- `sk_select_reuseport()` validates a socket selected from a reuseport sockarray or other sock map: membership, reuseport id, protocol, family, and reference ownership are checked before assigning `reuse_kern->selected_sk`.
- `sk_reuseport_is_valid_access()` and `sk_reuseport_convert_ctx_access()` define readable `sk_reuseport_md` fields and translate them to `sk_reuseport_kern`, nested `sk_buff`, and nested `sock` fields.
- `bpf_sk_lookup_assign()` implements the SK_LOOKUP `bpf_sk_assign()` helper. It validates flags, rejects refcounted sockets, enforces TCP LISTEN and UDP CLOSE states, checks protocol/family compatibility, honors replace/no-reuseport flags, and stores `selected_sk`.
- `sk_lookup_is_valid_access()` and `sk_lookup_convert_ctx_access()` define read-only `bpf_sk_lookup` access to selected socket, family/protocol, v4/v6 addresses, ports, and ingress ifindex.
- `bpf_prog_change_xdp()` updates the XDP BPF dispatcher target through `bpf_dispatcher_change_prog()`.
- BTF socket cast helpers include `bpf_skc_to_tcp6_sock()`, `bpf_skc_to_tcp_sock()`, `bpf_skc_to_tcp_timewait_sock()`, `bpf_skc_to_tcp_request_sock()`, `bpf_skc_to_udp6_sock()`, `bpf_skc_to_unix_sock()`, `bpf_skc_to_mptcp_sock()`, and `bpf_sock_from_file()`. Their `bpf_func_proto` objects return typed nullable BTF pointers.
- `bpf_sk_base_func_proto()` exposes those BTF socket casts and `ktime_get_coarse_ns`, with CAP_PERFMON token gating for socket casts.
- `bpf_skb_meta_pointer()` and `__bpf_skb_meta_store_bytes()` provide mutable skb metadata access after making the skb writable.
- Kfuncs in this chunk include `bpf_dynptr_from_skb()`, `bpf_dynptr_from_skb_meta()`, `bpf_dynptr_from_xdp()`, `bpf_sock_addr_set_sun_path()`, `bpf_sk_assign_tcp_reqsk()`, `bpf_sock_ops_enable_tx_tstamp()`, `bpf_xdp_pull_data()`, `bpf_dynptr_from_skb_rdonly()`, and `bpf_sock_destroy()`.
- `bpf_kfunc_init()` registers BTF kfunc id sets for relevant program types; `init_subsystem()` registers the tracing iterator socket-destroy kfunc set with `tracing_iter_filter()`.

Key state carriers are `struct sk_buff`, `struct __sk_buff`, `struct bpf_sock`, `struct sock`, `struct sock_common`, `struct xdp_buff`, `struct xdp_md`, `struct bpf_sock_addr_kern`, `struct bpf_sock_ops_kern`, `struct sk_msg`, `struct sk_reuseport_kern`, `struct bpf_sk_lookup_kern`, `struct bpf_dynptr_kern`, `struct request_sock`, `struct inet_request_sock`, `struct tcp_request_sock`, and `struct btf_kfunc_id_set`.

## Control Flow

Context conversion is switch-driven. The verifier has already decided a field offset, access size, and access type are valid for a program type. Each converter receives the original BPF instruction and emits one or more real BPF instructions into `insn_buf`. Simple fields become direct loads/stores at internal offsets. Virtual fields become instruction sequences: skb socket tuple fields first load `skb->sk`, XDP ifindexes traverse queue info to `net_device`, skb shared-info fields calculate the `skb_shared_info` base, and SK_SKB `data_end` computes the linear head end.

Several converters add semantic checks in generated BPF. `__sk_buff.queue_mapping` writes skip invalid immediate values or guard register values against `NO_QUEUE_MAPPING`; `napi_id` reports zero below `MIN_NAPI_ID`; socket RX queue mapping normalizes `NO_QUEUE_MAPPING` to `-1`; nullable skb accesses in sock ops skip nested loads if `skops->skb` is null; SK_LOOKUP IPv6 loads skip through a null v6 pointer and otherwise return zero when IPv6 is disabled.

Sock-address and sock-ops conversion use nested access macros because the UAPI context often points to an internal object. For writes, the converter cannot clobber the source value or context pointer, so it saves a scratch register into a temporary field in the kernel context, uses the scratch register to hold the nested pointer, performs the raw store, and restores the scratch register. Sock-ops field access also checks `is_locked_tcp_sock` or `is_fullsock` before reading/writing fields that are only safe on full or locked TCP sockets; failed guarded reads return zero.

Verifier ops tables are the handoff point from generic BPF verification into network-specific rules. Each program type gets a helper prototype provider, valid-access checker, context converter, and optional prologue, load-absolute generator, BTF struct access hook, or test-run function. Runtime BPF execution then sees only the lowered instructions and program-type-specific helper set.

Classic socket filter removal starts from socket lock context. `sk_detach_filter()` refuses locked filters, clears the RCU socket filter pointer, uncharges memory/accounting, and reports whether a filter existed. `sk_get_filter()` locks the socket, fetches the current filter, rejects eBPF filters without a saved classic `orig_prog`, optionally returns only the instruction count, and copies the classic filter program to the socket pointer.

SO_REUSEPORT BPF selection starts by building `sk_reuseport_kern` from the reuseport group, initial socket, packet, optional migrating socket, and hash. The BPF program may call `sk_select_reuseport()` to look up a candidate socket in a map. That helper verifies the socket is still reuseport-attached, belongs to the same reuseport group, or at least reports protocol/family/address mismatch precisely. On success it stores `selected_sk`; after program return, `bpf_run_sk_reuseport()` returns that socket only when the action is `SK_PASS`.

SK_LOOKUP flow exposes a read-only lookup context and lets the program assign a result socket. `bpf_sk_lookup_assign()` rejects unsupported flags, sockets with unsuitable lifetime semantics, TCP sockets outside LISTEN, UDP sockets outside CLOSE, protocol/family mismatches, and attempts to replace an existing selection without the replace flag. It stores both the selected socket and whether reuseport should be bypassed.

Socket BTF cast helpers are simple type refinements. Each helper receives a socket-common pointer, validates fullness/protocol/type/family/state as needed, and returns either the same pointer typed as the requested BTF id or null. `bpf_sk_base_func_proto()` exposes these helpers only to programs with a CAP_PERFMON-capable token, then falls back to base helper prototypes for unrelated helper ids.

Dynptr and metadata kfuncs initialize structured BPF dynptrs over existing network buffers. They reject nonzero flags, mark the dynptr null on flag errors, and initialize with the current skb length, skb metadata length, or XDP buffer length. `bpf_dynptr_from_skb_rdonly()` wraps the skb dynptr initializer and marks it read-only for contexts that should not mutate skb data.

`bpf_sk_assign_tcp_reqsk()` is the most stateful helper in the chunk. With SYN cookies enabled, it validates attributes size/reserved fields, requires TC ingress, checks network namespace match, picks IPv4 or IPv6 request-sock ops from packet protocol, requires a non-MPTCP TCP LISTEN socket, validates MSS and TCP option/sysctl compatibility, allocates a request socket, populates request and TCP-request attributes, orphans the skb, attaches `skb->sk` to the new request socket, and installs `sock_pfree` as destructor. Without SYN cookies it returns `-EOPNOTSUPP`.

`bpf_xdp_pull_data()` pulls fragmented XDP data into the linear area. It exits early if the requested length is already linear, rejects lengths beyond total XDP buffer length, calculates available headroom and tailroom, shifts metadata/data down if tailroom is insufficient, copies bytes from fragments into the linear tail, shrinks consumed fragments, compacts the fragment array when fragments are fully consumed, and clears XDP frag flags when no fragments remain.

Kfunc registration is late-init. `bpf_kfunc_init()` chains `register_btf_kfunc_id_set()` calls and stops on the first error, registering skb dynptr kfuncs for skb-like program types, skb-meta dynptrs for TC, XDP kfuncs for XDP, Unix-path mutation for cgroup sock address, TCP request-socket assignment for TC cls, and tx timestamp enabling for sock ops. A separate `late_initcall()` registers `bpf_sock_destroy()` for tracing programs, with a filter that allows it only for `BPF_TRACE_ITER` attach type.

## State and Persistence Behavior

The context converters do not persist state directly, but the generated instruction sequences define persistent ABI behavior for loaded programs. They also set side flags such as `prog->cb_access` when a program touches skb control-buffer fields, which affects later program handling.

Socket filter state persists in `sk->sk_filter` under RCU. `sk_detach_filter()` clears that pointer and releases accounting through `sk_filter_uncharge()`. `sk_get_filter()` only observes and copies the saved original classic program; it does not mutate the filter.

SO_REUSEPORT and SK_LOOKUP helpers mutate per-invocation kernel contexts, not global state. `sk_reuseport_kern->selected_sk` and `bpf_sk_lookup_kern->selected_sk/no_reuseport` persist only for the current lookup/selection operation, but the selected socket pointer can affect packet delivery. Helpers carefully avoid taking ownership of sockets unless map lookup semantics require a `sock_put()` on error.

Sock-address conversion can mutate the in-flight userspace sockaddr in `bpf_sock_addr_kern->uaddr` and associated transient state. `bpf_sock_addr_set_sun_path()` changes `sockaddr_un.sun_path` and updates `uaddrlen`; it does not allocate or persist a separate path object.

`bpf_sk_assign_tcp_reqsk()` creates persistent request-socket state and attaches it to the skb. The new request socket carries syncookie, MSS, timestamp, window-scale, SACK, ECN, and timestamp-offset state. The skb is orphaned before `skb->sk` is replaced and `skb->destructor` is set to `sock_pfree`, shifting lifetime/accounting responsibilities to the request socket.

Dynptr kfuncs initialize caller-provided stack dynptr objects. The dynptr itself is transient, but it references live skb, skb metadata, or XDP storage and inherits the lifetime constraints of the current BPF program invocation. Invalid flags set a null dynptr explicitly to avoid accidental use.

`bpf_xdp_pull_data()` mutates the XDP buffer geometry. It can move `data_meta`, `data`, and `data_end`, copy bytes from page frags to the linear area, reduce `sinfo->xdp_frags_size`, shrink or remove fragments, decrement `sinfo->nr_frags`, and clear fragment flags. Any verifier-approved direct packet pointers from before the call must be treated as invalid.

BTF kfunc id sets persist after late init and are owned by `THIS_MODULE`. The XDP dispatcher static target is persistent dispatcher state updated by `bpf_prog_change_xdp()`.

## Dependencies and Integration Points

- BPF verifier core: `struct bpf_verifier_ops`, `struct bpf_prog_ops`, access-type validation, target-size recording, register type annotations, prologue generation, `gen_ld_abs`, and BTF struct access hooks.
- BPF instruction generation: `BPF_LDX_MEM`, `BPF_STX_MEM`, `BPF_RAW_INSN`, `BPF_EMIT_STORE`, ALU/JMP helpers, `bpf_target_off()`, `bpf_ctx_record_field_size()`, and narrow-access helpers.
- Networking core structs: `sk_buff`, `skb_shared_info`, `skb_shared_hwtstamps`, `qdisc_skb_cb`, `sk_skb_cb`, `tcp_skb_cb`, `sock`, `sock_common`, `tcp_sock`, `xdp_buff`, `xdp_rxq_info`, `xdp_txq_info`, and `net_device`.
- Conditional kernel configuration: `CONFIG_NET_SCHED`, `CONFIG_NET_RX_BUSY_POLL`, `CONFIG_SOCK_RX_QUEUE_MAPPING`, `CONFIG_IPV6`, `CONFIG_INET`, and `CONFIG_SYN_COOKIES` all alter exposed values or helper availability.
- Socket and TCP internals: reuseport groups, sock maps, socket cookies, TCP request-sock ops, TCP sysctls, TCP timestamp conversion, MPTCP subflow lookup, protocol-specific `diag_destroy`, and socket file conversion.
- Packet data helpers: `____bpf_skb_load_bytes()`, `____bpf_skb_load_bytes_relative()`, skb metadata helpers, `bpf_try_make_writable()`, skb shared-info access, and XDP fragment helpers.
- BTF/kfunc infrastructure: `BTF_ID_LIST`, `BTF_KFUNCS_START/END`, `BTF_ID_FLAGS`, `register_btf_kfunc_id_set()`, BTF type emission, kfunc attach filters, and BPF token capability checks.
- Program-type integration: SCHED_CLS/ACT, SOCKET_FILTER, CGROUP_SKB, LWT, NETFILTER, TRACING, XDP, CGROUP_SOCK_ADDR, SK_SKB, SK_MSG, SOCK_OPS, SK_REUSEPORT, SK_LOOKUP, and FLOW_DISSECTOR.
- Test-run integration: skb, XDP, flow dissector, and SK_LOOKUP program ops expose test-run hooks for BPF selftests and userspace `BPF_PROG_TEST_RUN`.

## Risks and Edge Cases

- Context conversion is ABI-sensitive. Any wrong offset, size, endian adjustment, or conditional fallback changes what existing BPF programs observe. The `BUILD_BUG_ON()` checks catch layout assumptions at compile time, but semantic mistakes in generated instruction sequences can still pass compilation.
- Register preservation in nested store macros is fragile. The converters must not clobber the context pointer or source value and must choose a scratch register distinct from both. Missing restore paths would corrupt later program execution.
- Guarded sock-ops fields depend on `is_locked_tcp_sock` and `is_fullsock`. Returning real TCP fields without those checks risks unsafe access to request/timewait/non-full sockets or unlocked mutable TCP state.
- Null skb handling in sock ops must keep destination registers deterministic. Paths that load `skops->skb` and skip nested loads on null need clear zero/default behavior matching verifier expectations.
- IPv6-disabled builds return zeros for IPv6 tuple fields. Tests must cover both compile-time IPv6 enabled and disabled behavior because target-size handling differs in some branches.
- `queue_mapping` writes intentionally suppress invalid immediate stores and guard register stores. A mistake here can install `NO_QUEUE_MAPPING` or larger queue ids into skb state.
- `sk_select_reuseport()` must distinguish reuseport sockarray guarantees from generic sock maps. On error, refcounted sockets from maps need `sock_put()`; missing this leaks sockets, while putting sockets from non-refcounted paths can corrupt lifetimes.
- `bpf_sk_lookup_assign()` rejects refcounted sockets because lookup result sockets are RCU-lifetime objects. Relaxing this without verifier/runtime lifetime changes would create use-after-free risk.
- SK_LOOKUP family compatibility is subtle for dual-stack sockets: a socket with a different family can still be acceptable unless it is IPv4 or IPv6-only.
- `sk_get_filter()` exposes only classic BPF `orig_prog`. Returning converted eBPF instructions would break the legacy socket option ABI.
- `bpf_sk_base_func_proto()` gates BTF socket casts on CAP_PERFMON token capability. Exposing these casts without the gate would widen socket introspection privileges.
- `bpf_sk_assign_tcp_reqsk()` has many protocol and sysctl gates. Incorrect MSS minimums, timestamp offset calculation, network namespace checks, or request-socket initialization can break SYN-cookie flows or attach an skb to an invalid listener.
- `bpf_sock_ops_enable_tx_tstamp()` assumes the sock-ops callback has a valid skb and is exactly `BPF_SOCK_OPS_TSTAMP_SENDMSG_CB`. Calling it from other callbacks would set timestamp flags on invalid state.
- `bpf_xdp_pull_data()` physically moves packet pointers and fragments. Off-by-one headroom/tailroom math, incorrect metadata shifting, or fragment compaction mistakes can corrupt packet data or leave stale fragment accounting.
- Dynptr kfuncs rely on current buffer lengths. If callers mutate skb/XDP geometry after creating dynptrs, verifier invalidation and runtime semantics must remain coherent.
- `bpf_sock_destroy()` depends on the BPF context already holding socket locks and only allows TCP/UDP protocols with `diag_destroy`. Making it available outside tracing iterators or unlocked contexts could race protocol state.
- Late kfunc registration chains errors. A failure registering an earlier set prevents later sets from being registered, so boot logs/selftests should catch missing kfunc availability by program type.

## Test Signals

- Verifier selftests should exercise each converted context field with allowed read/write sizes, including skb `queue_mapping`, VLAN fields, `cb[]`, `tc_classid`, `data_meta`, socket tuples, timestamps, GSO fields, `wire_len`, `hwtstamp`, and `sk`.
- Build-matrix tests should cover `CONFIG_IPV6`, `CONFIG_NET_SCHED`, `CONFIG_NET_RX_BUSY_POLL`, `CONFIG_SOCK_RX_QUEUE_MAPPING`, `CONFIG_INET`, and `CONFIG_SYN_COOKIES` toggles because this chunk changes verifier-visible behavior under those options.
- Sock context tests should validate writable `bpf_sock.bound_dev_if`, `mark`, and `priority`; IPv4/IPv6 tuple reads; destination-port endian/position behavior; and `rx_queue_mapping` normalization to `-1`.
- XDP tests should validate `data`, `data_meta`, `data_end`, ingress ifindex, RX queue index, and egress ifindex conversion, plus dispatcher updates via `bpf_prog_change_xdp()`.
- Cgroup sock-address tests should cover IPv4/IPv6 user address rewrites, user port rewrite with two-byte port size, `msg_src_ip4/6` rewrites, read-only socket metadata, and Unix `sun_path` mutation including zero-length and oversize rejection.
- Sock-ops tests should cover locked TCP field reads/writes, full-socket guarded `sk` exposure, null skb behavior for `skb_data`, `skb_len`, `skb_tcp_flags`, and `skb_hwtstamp`, plus tx timestamp enabling only from `BPF_SOCK_OPS_TSTAMP_SENDMSG_CB`.
- SK_SKB and SK_MSG tests should validate `data_end` computation for linear skb head length, SK_SKB control-buffer mapping, SK_MSG data/data_end/size fields, and socket tuple reads.
- Socket filter tests should cover detach success, detach blocked by `SOCK_FILTER_LOCKED`, no-filter `-ENOENT`, classic filter dump length-only queries, short output buffers, and eBPF filters without `orig_prog` returning `-EACCES`.
- SO_REUSEPORT tests should cover successful sockarray selection, stale unhashed sockets, generic sock map sockets outside reuseport groups, reuseport id mismatch, protocol/family mismatch errors, migrating socket exposure, and rejected program actions.
- SK_LOOKUP tests should cover assignment replacement rules, no-reuseport flag, TCP LISTEN requirement, UDP CLOSE requirement, refcounted socket rejection, IPv4/v6 family compatibility, remote-port padding reads, and nullable selected socket access.
- BTF socket cast tests should cover TCP, TCP6, timewait, request, UDP6, Unix, MPTCP, and file-to-socket conversion success/null paths, plus CAP_PERFMON-token gating.
- Dynptr and metadata tests should cover invalid flags producing null dynptrs, skb and skb-meta length bounds, read-only skb dynptr creation, metadata store making skb writable, and zero/nonzero metadata lengths.
- TCP request-socket kfunc tests should cover TC ingress requirement, namespace mismatch, IPv4/IPv6 protocol selection, non-listener and MPTCP rejection, MSS lower bounds, window-scale/SACK/timestamp sysctl gates, reserved attr rejection, allocation failure cleanup, and skb ownership/destructor updates.
- XDP pull-data tests should cover already-linear no-op, length beyond total buffer rejection, insufficient headroom+tailroom rejection, metadata shifting, copy from one and multiple fragments, full fragment removal, fragment-array compaction, and clearing frag flags when the last fragment is consumed.
- Kfunc registration tests should verify each kfunc is available only to the intended BPF program types and that `bpf_sock_destroy()` is rejected for tracing programs whose expected attach type is not `BPF_TRACE_ITER`.

## Chunk Boundary Notes

This chunk begins inside the generic skb context converter, so earlier parts of `bpf_convert_ctx_access()` and the corresponding valid-access checks live in previous chunks. It also references helper prototypes, BTF access hooks, prologues, and packet helper implementations defined earlier in `filter.c` or other networking/BPF files. The final per-file report should merge this chunk with surrounding chunks so the verifier access policy, helper whitelist, and generated context-conversion instructions are described as one continuous network BPF subsystem.
