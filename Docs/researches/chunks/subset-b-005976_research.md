# sources/distributed-fs/ceph-client/include/uapi/linux/bpf.h lines 6944-7705

## Scope

This chunk covers the final UAPI definitions in `include/uapi/linux/bpf.h`, starting in the tail of `struct bpf_sock_ops` and ending at the header guard close. The range is not Ceph-specific despite living under the Ceph client source mirror; it is the Linux userspace/kernel ABI surface for BPF programs, BPF loaders, libbpf, generated `vmlinux.h`, and kernel helper call sites.

The chunk defines TCP `sock_ops` packet metadata and callback flags, sock_ops operation IDs, BPF-visible TCP state IDs, TCP sockopt numbers used by sock_ops programs, perf event values, device cgroup context values, raw tracepoint argument layout, FIB/neighbor/MTU lookup contracts, flow dissector keys, BTF function/line metadata, opaque in-map synchronization/container objects, sysctl/sockopt/SK_LOOKUP contexts, BTF pointer formatting flags, CO-RE relocation records, timer/kfunc flags, numeric iterator state, and instruction-array map values.

## Purpose

This section is an ABI contract layer. It lets BPF programs and BPF-aware userspace tools share stable numeric constants and data layouts with the kernel for networking, tracing, typed BTF formatting, CO-RE relocation, and newer map-value managed objects.

For TCP sock_ops programs, the chunk describes when a program can inspect or write TCP header option state, which callbacks can be requested, and how callback arguments are interpreted. For packet forwarding helpers, it defines the input/output structures and return codes that BPF programs pass to helpers such as FIB lookup, redirect-neighbor, and MTU checking. For tracing and loader integration, it provides metadata records consumed by BPF program loaders, verifier paths, and BTF/CO-RE relocation machinery.

The range contains no executable functions. Control flow is expressed through enums, callback operation IDs, input/output fields, and comments that define when the kernel invokes BPF programs or mutates fields.

## Important APIs, Types, and Data

The chunk begins with final fields of `struct bpf_sock_ops`: `skb_data`, `skb_data_end`, `skb_len`, `skb_tcp_flags`, and `skb_hwtstamp`. `skb_data` and `skb_data_end` expose a TCP-header byte range to sock_ops callbacks when a packet/header exists. `skb_len` is the whole packet length including header, options, and payload. `skb_tcp_flags` is a parsed shortcut for TCP flags and is available even in `BPF_SOCK_OPS_HDR_OPT_LEN_CB`, where the outgoing header has not yet been written. `skb_hwtstamp` carries hardware timestamp data for timestamp-aware callbacks.

`bpf_sock_ops_cb_flags` bits select callback delivery. The low bits request RTO, retransmission, TCP state, and RTT callbacks. `BPF_SOCK_OPS_PARSE_ALL_HDR_OPT_CB_FLAG` asks the kernel to call BPF for every received TCP header. `BPF_SOCK_OPS_PARSE_UNKNOWN_HDR_OPT_CB_FLAG` limits parsing callbacks to TCP options the kernel cannot handle. `BPF_SOCK_OPS_WRITE_HDR_OPT_CB_FLAG` enables the two-stage option-write flow: first reserve space under `BPF_SOCK_OPS_HDR_OPT_LEN_CB`, then write options under `BPF_SOCK_OPS_WRITE_HDR_OPT_CB`. `BPF_SOCK_OPS_ALL_CB_FLAGS` is the supported mask, currently `0x7F`.

`SK_BPF_CB_TX_TIMESTAMPING` and `SK_BPF_CB_MASK` define socket-level BPF callback flags for TX timestamping phases. The timestamping callbacks in the sock_ops op enum only fire when this feature is enabled.

The sock_ops operation enum is append-only and includes:

- Connection setup/tuning operations such as `BPF_SOCK_OPS_TIMEOUT_INIT`, `BPF_SOCK_OPS_RWND_INIT`, `BPF_SOCK_OPS_TCP_CONNECT_CB`, active/passive established callbacks, `BPF_SOCK_OPS_NEEDS_ECN`, and `BPF_SOCK_OPS_BASE_RTT`.
- TCP lifecycle and measurement callbacks such as `BPF_SOCK_OPS_RTO_CB`, `BPF_SOCK_OPS_RETRANS_CB`, `BPF_SOCK_OPS_STATE_CB`, `BPF_SOCK_OPS_TCP_LISTEN_CB`, and `BPF_SOCK_OPS_RTT_CB`.
- TCP header option callbacks `BPF_SOCK_OPS_PARSE_HDR_OPT_CB`, `BPF_SOCK_OPS_HDR_OPT_LEN_CB`, and `BPF_SOCK_OPS_WRITE_HDR_OPT_CB`, which integrate with helpers such as `bpf_load_hdr_opt()`, `bpf_reserve_hdr_opt()`, and `bpf_store_hdr_opt()`.
- TX timestamp callbacks `BPF_SOCK_OPS_TSTAMP_SCHED_CB`, `BPF_SOCK_OPS_TSTAMP_SND_SW_CB`, `BPF_SOCK_OPS_TSTAMP_SND_HW_CB`, `BPF_SOCK_OPS_TSTAMP_ACK_CB`, and `BPF_SOCK_OPS_TSTAMP_SENDMSG_CB`.

The BPF TCP state enum mirrors kernel TCP states and is guarded by a build check in `net/ipv4/tcp.c`. Values run from `BPF_TCP_ESTABLISHED = 1` through `BPF_TCP_BOUND_INACTIVE`, with `BPF_TCP_MAX_STATES` reserved as the terminal sentinel.

TCP BPF sockopt constants `TCP_BPF_IW`, `TCP_BPF_SNDCWND_CLAMP`, `TCP_BPF_DELACK_MAX`, and `TCP_BPF_RTO_MIN` let BPF programs adjust initial congestion window, cwnd clamp, delayed ACK behavior, and minimum RTO. `TCP_BPF_SYN`, `TCP_BPF_SYN_IP`, and `TCP_BPF_SYN_MAC` copy SYN data into an optval buffer, choosing between the just-received SYN during SYNACK generation and a previously saved SYN. `TCP_BPF_SOCK_OPS_CB_FLAGS`, `SK_BPF_CB_FLAGS`, and `SK_BPF_BYPASS_PROT_MEM` expose socket option state for callback flags and protected-memory bypass.

`BPF_LOAD_HDR_OPT_TCP_SYN` is a flag for loading TCP SYN header options. `BPF_WRITE_HDR_TCP_CURRENT_MSS` and `BPF_WRITE_HDR_TCP_SYNACK_COOKIE` are `args[0]` values for the header option reservation/write callbacks, distinguishing MSS computation without an actual skb from syncookie SYNACK generation.

`struct bpf_perf_event_value` exposes `counter`, `enabled`, and `running` values for perf-event helper results. Device cgroup constants `BPF_DEVCG_ACC_*` and `BPF_DEVCG_DEV_*`, plus `struct bpf_cgroup_dev_ctx`, encode device access operations and block/char device identity through `access_type`, `major`, and `minor`.

`struct bpf_raw_tracepoint_args` is a flexible raw tracepoint argument array, represented as `__u64 args[0]`. `enum bpf_task_fd_type` classifies BPF-owned file descriptors attached to raw tracepoints, tracepoints, kprobes/kretprobes, and uprobes/uretprobes.

FIB lookup definitions include flags `BPF_FIB_LOOKUP_DIRECT`, `BPF_FIB_LOOKUP_OUTPUT`, `BPF_FIB_LOOKUP_SKIP_NEIGH`, `BPF_FIB_LOOKUP_TBID`, `BPF_FIB_LOOKUP_SRC`, and `BPF_FIB_LOOKUP_MARK`; return codes from success through route blackhole/unreachable/prohibit, forwarding disabled, unsupported lightweight tunnel, no neighbor, fragmentation needed, and source-address failure; and `struct bpf_fib_lookup`. That structure is both input and output: family, L4 protocol/ports, length or returned MTU, ifindex, TOS/flowinfo or returned route metric, source/destination addresses, VLAN fields or routing table ID, policy routing mark, and returned source/destination MAC addresses.

`struct bpf_redir_neigh` supplies a nexthop family and address for redirect-neighbor helper paths that skip full FIB lookup to find the gateway. `enum bpf_check_mtu_flags` currently has `BPF_MTU_CHK_SEGS`; `enum bpf_check_mtu_ret` reports MTU check success, fragmentation required, or GSO resegmentation needed.

Flow dissector definitions include `BPF_FLOW_DISSECTOR_F_PARSE_1ST_FRAG`, `BPF_FLOW_DISSECTOR_F_STOP_AT_FLOW_LABEL`, `BPF_FLOW_DISSECTOR_F_STOP_AT_ENCAP`, and `struct bpf_flow_keys`. The keys contain network and transport header offsets, address protocol, fragment/encapsulation booleans, IP protocol, L2 protocol, ports, IPv4 or IPv6 source/destination addresses, flags, and IPv6 flow label.

BTF and loader metadata starts with `struct bpf_func_info` and `struct bpf_line_info`, plus `BPF_LINE_INFO_LINE_NUM()` and `BPF_LINE_INFO_LINE_COL()` extractors. `struct bpf_func_info` maps instruction offsets to BTF type IDs. `struct bpf_line_info` maps instruction offsets to file-name, line-string, and packed line/column data.

Opaque map-value objects include `struct bpf_spin_lock`, `struct bpf_timer`, `struct bpf_task_work`, `struct bpf_wq`, `struct bpf_dynptr`, `struct bpf_list_head`, `struct bpf_list_node`, `struct bpf_rb_root`, `struct bpf_rb_node`, and `struct bpf_refcount`. These structs intentionally expose only fixed-size storage and alignment; operational semantics are enforced by the verifier and helpers/kfuncs, not by fields visible in the UAPI header.

Program context structs include `struct bpf_sysctl`, with read/write direction and file position, `struct bpf_sockopt`, with socket pointer, optval range, level, optname, optlen, and return value, `struct bpf_pidns_info`, and `struct bpf_sk_lookup`. `struct bpf_sk_lookup` is explicitly append-only and exposes selected socket/cookie, address family, protocol, remote/local IPs and ports, and ingress interface for SK_LOOKUP programs.

`struct btf_ptr` packages a pointer, BTF type ID, and reserved flags for typed rendering via `bpf_snprintf_btf()`. Formatting flags include `BTF_F_COMPACT`, `BTF_F_NONAME`, `BTF_F_PTR_RAW`, and `BTF_F_ZERO`.

CO-RE relocation definitions include `enum bpf_core_relo_kind` and `struct bpf_core_relo`. Relocation kinds cover field offset/size/existence/signedness/bitfield shifts, local and target type IDs, type existence/size/matching, and enum value existence/value. `struct bpf_core_relo` records the instruction offset, root BTF type ID, string-table offset for the access pattern, and relocation kind.

Timer and kfunc flags include `BPF_F_TIMER_ABS`, `BPF_F_TIMER_CPU_PIN`, and `BPF_F_PAD_ZEROS`. `struct bpf_iter_num` is opaque state for number iterators. `struct bpf_insn_array_value` defines `BPF_MAP_TYPE_INSN_ARRAY` map values, where `orig_off` is initialized by userspace before load, and `xlated_off`/`jitted_off` are filled or adjusted after verifier/JIT processing.

## Control Flow

TCP sock_ops header-option control flow is a staged kernel-to-BPF callback sequence. A program enables parsing and/or writing by setting callback flags through the sock_ops callback flag mechanisms. For parsing, the kernel invokes `BPF_SOCK_OPS_PARSE_HDR_OPT_CB` with `skb_data` and `skb_data_end` pointing at the received TCP header; programs can parse the byte range directly or use `bpf_load_hdr_opt()` to search for a specific option.

For writing TCP options, the kernel first invokes `BPF_SOCK_OPS_HDR_OPT_LEN_CB` so the program can reserve option space with `bpf_reserve_hdr_opt()`. At this point no outgoing header exists, so `skb_data` is unavailable, but `skb_tcp_flags` still describes the future packet. Later, after the kernel and any earlier BPF programs have written header/options, the kernel invokes `BPF_SOCK_OPS_WRITE_HDR_OPT_CB`; the program can use `bpf_store_hdr_opt()` to write its option and `bpf_load_hdr_opt()` to inspect options already written.

Syncookie and SYN handling add special branches. In syncookie mode, a received SYN cannot necessarily be saved, so `TCP_BPF_SYN*` getters may copy the just-received SYN during SYNACK generation. `BPF_WRITE_HDR_TCP_SYNACK_COOKIE` in `args[0]` tells the program that the SYNACK path is operating in syncookie mode. `BPF_WRITE_HDR_TCP_CURRENT_MSS` marks an MSS-computation pass where option-space accounting is performed for an established socket without sending an skb.

Sock_ops measurement callbacks are event-driven. RTO, retransmission, state transition, listen, RTT, and TX timestamp operations are selected by callback flags and delivered with operation-specific `args[]` values. The enum comments define each argument meaning, such as old/new TCP state for `BPF_SOCK_OPS_STATE_CB` and retransmit sequence/segment count/transmit result for `BPF_SOCK_OPS_RETRANS_CB`.

FIB lookup helper flow treats `struct bpf_fib_lookup` as a mutable in/out record. The BPF program initializes family, addresses, length, interface, and optional L4/policy fields, then calls the helper. On success the helper may update the destination to a gateway address, fill source address, route metric, VLAN data, output ifindex, and MAC addresses. On non-success return codes, the program decides whether to drop, redirect differently, signal fragmentation, or fall back.

Flow dissector programs populate `struct bpf_flow_keys` to describe packet offsets and flow identity. Flags can stop dissection at selected packet boundaries, such as first fragment, IPv6 flow label, or encapsulation boundary.

BTF/CO-RE control flow spans compiler, loader, and kernel. Clang emits relocation records for `__builtin_preserve_access_index()` expressions. libbpf consumes these records and BTF data, rewrites instructions for the target kernel layout, and passes relocation information as needed to the kernel. The kernel verifier and loader paths consume function and line metadata to associate instructions with BTF type IDs and source locations.

`BPF_MAP_TYPE_INSN_ARRAY` values have a before/after load transition. Userspace sets `orig_off` to an instruction offset inside the program being loaded and clears the other fields. After verification/loading, the kernel maps that original offset to translated and JITed offsets, or marks deleted translated instructions with `(u32)-1`.

## State and Persistence Behavior

Most state in this chunk is transient per-callback or per-helper-call state. `struct bpf_sock_ops` packet fields are valid only for the documented callback contexts. `skb_data` ranges are packet/header views and must not be treated as persistent pointers. `skb_tcp_flags` is the stable shortcut when data bytes are absent, especially during header length reservation.

Callback flags persist in socket/sock_ops state after being set and determine future event delivery until changed. The all-flags mask is an ABI boundary for validation: unknown bits should be rejected or ignored according to the kernel-side setter path, and new flags can only be added compatibly.

TCP state numeric values are ABI-sensitive. The header notes an in-kernel build check against TCP's internal state enum; if values diverge, the kernel needs a conversion layer before invoking BPF. This matters for persistence across compiled BPF programs because programs may compare these constants directly.

FIB, MTU, redirect-neighbor, flow-dissector, sysctl, sockopt, and SK_LOOKUP structs are not persistent storage. They are context or helper argument records whose fields are valid during the program invocation. Some fields deliberately switch meaning from input to output after helper execution, such as `tot_len` versus `mtu_result`, `tos`/`flowinfo` versus `rt_metric`, routing table ID versus VLAN output, and mark input versus MAC output.

Opaque objects such as `bpf_timer`, `bpf_wq`, `bpf_dynptr`, BPF list/rbtree nodes, and `bpf_refcount` can live in BPF map values or verifier-tracked contexts, but their representation is intentionally hidden. Their size and alignment are ABI, while lifecycle rules are controlled by verifier checks and helper/kfunc APIs elsewhere in the header and kernel.

BTF function/line metadata and CO-RE relocation records persist inside BPF ELF objects and load-time metadata. They are not runtime mutable program state, but they are essential for reproducible loading against kernels with different type layouts. `btf_ptr` state is per formatting call.

`bpf_insn_array_value` map entries persist in a BPF map and are rewritten by the verifier/load path from original instruction offsets to translated/JITed offsets. Consumers must understand that optimized-away instructions are represented by `xlated_off == (u32)-1`.

## Dependencies and Integration Points

The chunk depends on Linux UAPI fixed-width and endian types such as `__u8`, `__u16`, `__u32`, `__u64`, `__s32`, `__be16`, and `__be32`, and on `__bpf_md_ptr()` for metadata pointers whose layout differs between kernel and userspace/BPF views.

TCP sock_ops integration is with the TCP stack, socket option handling, syncookie code, retransmission/RTO paths, RTT sampling, TCP state transitions, and TX timestamping points in the networking stack. The comments reference helper APIs documented earlier in the header, including `bpf_load_hdr_opt()`, `bpf_reserve_hdr_opt()`, `bpf_store_hdr_opt()`, `bpf_getsockopt()`, and `bpf_setsockopt()`.

Routing integration is with the kernel FIB, policy routing rules, route metrics, output/input interface lookup, neighbor resolution, VLAN metadata, MTU/GSO logic, and redirect-neighbor helpers. The `BPF_FIB_LOOKUP_DIRECT`, table-ID, source-address, and mark flags are explicit hooks into routing policy.

Tracing integration is with raw tracepoints, tracepoints, kprobes, kretprobes, uprobes, uretprobes, and task file-descriptor introspection. Perf integration uses `struct bpf_perf_event_value`.

Device-cgroup integration uses `struct bpf_cgroup_dev_ctx` and access/device bit encodings. Sysctl and sockopt program types use `struct bpf_sysctl` and `struct bpf_sockopt` to mediate kernel configuration and socket option operations. SK_LOOKUP programs use `struct bpf_sk_lookup` to select sockets based on packet tuple and ingress interface.

Loader/toolchain integration is substantial. `struct bpf_func_info`, `struct bpf_line_info`, `struct btf_ptr`, `enum bpf_core_relo_kind`, and `struct bpf_core_relo` are consumed by clang/LLVM, libbpf, the kernel verifier/loader, BTF render helpers, and generated `vmlinux.h` workflows.

Opaque container and synchronization types integrate with verifier-recognized map value fields and kfunc/helper families for spin locks, timers, task work, workqueues, dynptrs, linked lists, rbtree nodes, and refcounted objects.

## Risks

This chunk is ABI-sensitive. Reordering enum values, changing struct field order, altering alignment, or changing union overlays can break already compiled BPF programs and userspace loaders. The comments explicitly say sock_ops operation IDs are append-only and SK_LOOKUP fields can only be added at the end.

Mid-struct chunking is a documentation risk. The range starts inside the final comments and fields of `struct bpf_sock_ops`; the preceding chunk contains the structure beginning and earlier TCP metrics. Any final per-file reconciliation should merge both chunks before drawing conclusions about the full sock_ops ABI.

Pointer lifetime and range validation are critical for `skb_data`, `skb_data_end`, `optval`, `optval_end`, and selected socket pointers. BPF programs must obey verifier-proven bounds and callback-context availability. In particular, `skb_data` is unavailable during header length reservation and only covers TCP header bytes in parse/write contexts.

Endianness mistakes are likely in networking contexts. Remote ports, remote/local IPs, flow addresses, TCP SYN copies, FIB addresses, and flow dissector fields use network byte order in many places, while fields such as `local_port` in `bpf_sk_lookup` are host byte order. Programs comparing or writing these fields must use the expected conversions.

Helper input/output unions are easy to misuse. `struct bpf_fib_lookup` overlays input and output fields, so reading VLAN/MAC/metric/MTU results before helper execution or reusing a structure without clearing stale fields can produce wrong forwarding behavior. The `tbid` input only has meaning with the correct direct/table-ID flags.

TCP header option sequencing can corrupt options or produce wrong MSS calculations if programs reserve a different amount than they later write, assume `skb_data` exists during length reservation, ignore syncookie-specific paths, or leave parse-all callbacks enabled longer than necessary.

Callback flag overuse has runtime cost. `BPF_SOCK_OPS_PARSE_ALL_HDR_OPT_CB_FLAG` can invoke BPF for all received TCP headers; comments suggest programs normally turn it off in common cases after the special syncookie/resend need is gone.

TCP state constants must track kernel TCP internals. The header mentions a build-time check, but out-of-tree copies or generated headers can drift. A mismatch would make state comparisons in BPF programs wrong unless the kernel conversion layer is present.

CO-RE relocation correctness depends on exact BTF metadata and compiler-emitted access strings. Bad `insn_off`, `type_id`, `access_str_off`, or relocation kind values can cause load failures or incorrect field access rewrites. Enum value and bitfield relocations are especially sensitive to target-kernel layout differences.

Opaque object misuse is caught mostly by verifier/helper rules outside this chunk. Treating opaque bytes as ordinary data, copying lock/timer/list/rbtree nodes improperly, or violating alignment assumptions can cause verifier rejection or subtle runtime lifecycle bugs.

## Test and Validation Signals

ABI validation should compile the header for both kernel and userspace consumers and compare generated BTF/UAPI layouts against expected sizes, alignments, field offsets, and enum numeric values. Build checks should continue to verify BPF TCP state values against `net/ipv4/tcp.c`.

Sock_ops selftests should exercise RTO, retransmission, state, RTT, listen/connect, active/passive established, and TX timestamp callbacks with callback flags enabled and disabled. Tests should validate `args[]` meanings, `reply` handling for initialization operations, and correct rejection or masking of unsupported callback bits.

TCP header option tests should cover parse-all, parse-unknown-only, length reservation, option write, existing-option lookup, syncookie SYNACK generation, current-MSS pseudo-send handling, and the absence of `skb_data` during `BPF_SOCK_OPS_HDR_OPT_LEN_CB`. Negative tests should ensure out-of-range `skb_data` access and mismatched reservation/write behavior fail or are handled safely.

TCP_BPF_SYN getter tests should cover copying TCP-only, IP+TCP, and MAC+IP+TCP headers; too-small optval buffers returning `-ENOSPC`; missing saved/current SYN returning `-ENOENT`; and syncookie mode where only the just-received SYN path is available.

Routing helper tests should verify FIB lookup success and every documented non-success return code: blackhole, unreachable, prohibit, not forwarded, forwarding disabled, unsupported LWT, no neighbor, fragmentation needed, and no source address. Tests should cover direct lookup, egress lookup, skip-neighbor, table-ID lookup, source-address derivation, policy mark, IPv4, IPv6, gateway rewrite, VLAN output, MAC output, MTU output, and route metric output.

MTU and redirect-neighbor tests should exercise `BPF_MTU_CHK_SEGS`, fragmentation-needed, GSO segments-too-big, IPv4/IPv6 nexthop addresses, and behavior when neighbor state is absent or stale.

Flow dissector tests should feed IPv4, IPv6, fragmented packets, first and later fragments, encapsulated packets, and IPv6 flow-label cases, checking `nhoff`, `thoff`, protocol fields, address unions, ports, flags, and stop flags.

Tracing and perf tests should validate raw tracepoint argument indexing, task FD type reporting for tracepoint/kprobe/uprobe variants, and perf event value enabled/running/counter accounting.

BTF and CO-RE tests should compile BPF objects with function info, line info, bitfields, anonymous structs, arrays, type-existence checks, type-size checks, enum relocations, and type-match relocations. Load tests across kernels with intentionally different struct layouts should verify expected relocation rewrites and failures.

Opaque object tests should use verifier selftests for spin locks, timers, task work, workqueues, dynptrs, linked lists, rbtree nodes, and refcounts, including alignment, copy, lifetime, and map-value placement constraints.

Sysctl, sockopt, and SK_LOOKUP tests should validate read/write permission annotations, optval bounds, retval propagation, socket selection/cookie behavior under `PROG_TEST_RUN`, IPv4/IPv6 tuple matching, host/network byte order expectations, and append-only struct compatibility.

Instruction-array tests should initialize `struct bpf_insn_array_value` entries with only `orig_off`, load programs that preserve, translate, JIT, and delete selected instructions, and verify `xlated_off`, `jitted_off`, and `(u32)-1` deleted-instruction reporting.

## Cross-Chunk Notes

The first lines in this range are the end of `struct bpf_sock_ops`; earlier fields and the structure comment appear in the preceding chunk for the same file. This chunk also references helpers and program types documented earlier in `bpf.h`, including sockopt helpers, TCP header-option helpers, BTF formatting helpers, timers, and kfuncs. The merge lane should combine this document with the missing first chunk for `sources/distributed-fs/ceph-client/include/uapi/linux/bpf.h` before producing the final per-file research report.
