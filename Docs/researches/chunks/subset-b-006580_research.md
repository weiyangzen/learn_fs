# sources/distributed-fs/ceph-client/tools/include/uapi/linux/bpf.h lines 6944-7704

## Scope

This chunk covers the final 761 lines of the `tools/include/uapi/linux/bpf.h` UAPI header copy, starting at the tail of `struct bpf_sock_ops` and ending at the header guard close. This is the tools-side mirror of the Linux BPF UAPI contract. It is not Ceph-specific application logic; it supplies stable constants, structs, enum values, and documented callback/helper contracts used by kernel tooling, BPF loaders, selftests, bpftool/libbpf-adjacent consumers, generated headers, and BPF program builds.

The chunk defines TCP sock_ops packet metadata and callback flags, sock_ops operation IDs, BPF-visible TCP states, TCP sockopt numbers, perf and device-cgroup context records, raw tracepoint argument layout, FIB/neighbor/MTU helper contracts, flow-dissector keys, BTF function and line metadata, opaque BPF map-value objects, sysctl/sockopt/SK_LOOKUP program contexts, typed BTF pointer formatting, CO-RE relocation records, timer and kfunc flags, numeric iterator state, and `BPF_MAP_TYPE_INSN_ARRAY` entry layout.

## Purpose

The file section is an ABI declaration surface. Its main purpose is to let user-space tools and BPF C programs compile against the same numeric values and memory layouts the kernel expects. Because it lives under `tools/include/uapi`, it is especially important for in-tree tools that cannot include arbitrary kernel-internal headers directly.

For TCP sock_ops, the range describes which packet/header fields are visible in each callback, how programs opt into extra callbacks, and how the kernel reports TCP events or asks programs to reserve and write TCP header options. For networking helpers, it defines mutable input/output records used for FIB lookup, redirect-neighbor, MTU checking, and flow dissection. For tracing and loader integration, it defines metadata records that connect BPF instructions to BTF type IDs, source lines, typed formatting, and CO-RE relocation rewrites.

There are no executable functions in this chunk. Runtime behavior is encoded through enum values, struct layouts, helper argument records, and comments that define kernel-to-BPF callback sequencing.

## Important APIs, Types, and Data

The chunk begins with final fields of `struct bpf_sock_ops`: `skb_data`, `skb_data_end`, `skb_len`, `skb_tcp_flags`, and `skb_hwtstamp`. The pointer range `[skb_data, skb_data_end)` exposes the TCP header when the callback has a packet or written header. `skb_len` reports total packet length, including header, options, and payload. `skb_tcp_flags` provides parsed TCP flags even in `BPF_SOCK_OPS_HDR_OPT_LEN_CB`, where no outgoing header has been written. `skb_hwtstamp` carries hardware timestamp state for timestamp-aware sock_ops callbacks.

`bpf_sock_ops_cb_flags` controls callback delivery. The basic bits enable RTO, retransmission, state-change, and RTT callbacks. `BPF_SOCK_OPS_PARSE_ALL_HDR_OPT_CB_FLAG` asks the kernel to invoke BPF for all received TCP headers, while `BPF_SOCK_OPS_PARSE_UNKNOWN_HDR_OPT_CB_FLAG` limits parsing callbacks to header options the kernel does not understand. `BPF_SOCK_OPS_WRITE_HDR_OPT_CB_FLAG` enables the two-stage TCP option write flow: reserve space during `BPF_SOCK_OPS_HDR_OPT_LEN_CB`, then write bytes during `BPF_SOCK_OPS_WRITE_HDR_OPT_CB`. `BPF_SOCK_OPS_ALL_CB_FLAGS` is the currently supported mask.

`SK_BPF_CB_TX_TIMESTAMPING` and `SK_BPF_CB_MASK` define socket-level flags used to enable TX timestamping callback phases. The sock_ops op enum includes the corresponding timestamp callbacks: scheduling through the device layer, software send, hardware send, ACK completion, and sendmsg correlation.

The sock_ops operation enum is explicitly append-only. It includes connection setup and tuning operations (`BPF_SOCK_OPS_TIMEOUT_INIT`, `BPF_SOCK_OPS_RWND_INIT`, `BPF_SOCK_OPS_TCP_CONNECT_CB`, active/passive established callbacks, ECN need, and base RTT), lifecycle/measurement events (`BPF_SOCK_OPS_RTO_CB`, retransmit, state change, listen, RTT), TCP header option events (`PARSE_HDR_OPT`, `HDR_OPT_LEN`, `WRITE_HDR_OPT`), and TX timestamp events.

The BPF TCP state enum mirrors kernel TCP state numbers from `BPF_TCP_ESTABLISHED = 1` through `BPF_TCP_BOUND_INACTIVE`, with `BPF_TCP_MAX_STATES` as the sentinel. The header notes that `net/ipv4/tcp.c` has a build check to detect drift between kernel TCP state values and these UAPI constants.

TCP BPF sockopt constants start at `1001`. `TCP_BPF_IW`, `TCP_BPF_SNDCWND_CLAMP`, `TCP_BPF_DELACK_MAX`, and `TCP_BPF_RTO_MIN` tune connection behavior. `TCP_BPF_SYN`, `TCP_BPF_SYN_IP`, and `TCP_BPF_SYN_MAC` copy TCP-only, IP+TCP, or MAC+IP+TCP SYN packet data into an optval buffer, either from the just-received SYN during SYNACK generation or from a previously saved SYN. `TCP_BPF_SOCK_OPS_CB_FLAGS`, `SK_BPF_CB_FLAGS`, and `SK_BPF_BYPASS_PROT_MEM` get or set sock_ops callback and socket flags.

`BPF_LOAD_HDR_OPT_TCP_SYN` is a flag for loading TCP SYN header options. `BPF_WRITE_HDR_TCP_CURRENT_MSS` and `BPF_WRITE_HDR_TCP_SYNACK_COOKIE` are `args[0]` values for header-option reservation/write callbacks, distinguishing MSS option-space accounting from syncookie SYNACK generation.

`struct bpf_perf_event_value` exposes `counter`, `enabled`, and `running` values. Device cgroup constants `BPF_DEVCG_ACC_*` and `BPF_DEVCG_DEV_*`, plus `struct bpf_cgroup_dev_ctx`, encode device access type and block/char device major/minor identity.

`struct bpf_raw_tracepoint_args` is a flexible array of raw tracepoint arguments. `enum bpf_task_fd_type` classifies BPF-related task file descriptors attached to raw tracepoints, tracepoints, kprobes, kretprobes, uprobes, and uretprobes.

FIB lookup definitions include flags for direct lookup, egress lookup, skipping neighbor resolution, table-ID lookup, source-address derivation, and policy mark lookup. Return codes distinguish success from blackhole, unreachable, prohibit, not forwarded, forwarding disabled, unsupported lightweight tunnel, no neighbor, fragmentation needed, and source-address failure. `struct bpf_fib_lookup` is both input and output: it carries family, L4 protocol and ports, length or returned MTU, input/output ifindex, IPv4 TOS or IPv6 flowinfo or returned route metric, source and destination addresses, routing table ID or VLAN output, policy mark input, and source/destination MAC output.

`struct bpf_redir_neigh` supplies an IPv4 or IPv6 nexthop address for redirect-neighbor paths. `enum bpf_check_mtu_flags` currently exposes `BPF_MTU_CHK_SEGS`, and `enum bpf_check_mtu_ret` reports success, fragmentation needed, or GSO resegmentation needed.

Flow dissector definitions include stop/parse flags and `struct bpf_flow_keys`, which records network and transport header offsets, address protocol, fragment/encapsulation state, IP and L2 protocols, source/destination ports, IPv4 or IPv6 addresses, dissector flags, and IPv6 flow label.

BTF and loader metadata includes `struct bpf_func_info`, `struct bpf_line_info`, and the `BPF_LINE_INFO_LINE_NUM()` / `BPF_LINE_INFO_LINE_COL()` macros. Function info maps instruction offsets to BTF type IDs. Line info maps instruction offsets to BTF string-table offsets for file and line data plus packed line/column information.

Opaque BPF object definitions include `bpf_spin_lock`, `bpf_timer`, `bpf_task_work`, `bpf_wq`, `bpf_dynptr`, `bpf_list_head`, `bpf_list_node`, `bpf_rb_root`, `bpf_rb_node`, and `bpf_refcount`. These expose only ABI size and alignment; verifier rules and helper/kfunc implementations define legal operations and lifecycle.

Program context structs include `struct bpf_sysctl`, `struct bpf_sockopt`, `struct bpf_pidns_info`, and `struct bpf_sk_lookup`. `bpf_sockopt` exposes the socket pointer, optval bounds, level, optname, optlen, and retval. `bpf_sk_lookup` is explicitly append-only and exposes selected socket or test-run cookie, address family, protocol, remote/local IPv4 or IPv6 addresses, ports, and ingress ifindex.

`struct btf_ptr` packages a pointer, BTF type ID, and reserved flags for typed rendering through `bpf_snprintf_btf()`. Formatting flags include compact output, no member names, raw pointer values, and zero-valued member display.

CO-RE relocation support is represented by `enum bpf_core_relo_kind` and `struct bpf_core_relo`. Relocation kinds cover field byte offset, field size, field existence, signedness, bitfield shifts, local and target type IDs, type existence, type size, enum value existence/value, and type matching. `bpf_core_relo` records instruction offset, root BTF type ID, access-string offset, and relocation kind.

Timer and kfunc flags include `BPF_F_TIMER_ABS`, `BPF_F_TIMER_CPU_PIN`, and `BPF_F_PAD_ZEROS`. `struct bpf_iter_num` preserves opaque state for numeric iterators. `struct bpf_insn_array_value` defines map entries for `BPF_MAP_TYPE_INSN_ARRAY`: user space initializes `orig_off`, then the verifier/load path fills `xlated_off` and `jitted_off` or marks deleted translated instructions with `(u32)-1`.

## Control Flow

TCP header-option handling is the main callback sequence described in this range. A sock_ops program first enables parsing and/or writing through callback flags. For parsing, the kernel invokes `BPF_SOCK_OPS_PARSE_HDR_OPT_CB` with `skb_data` and `skb_data_end` pointing at the received TCP header; the program can parse the range directly or use `bpf_load_hdr_opt()`.

For option writing, the kernel first invokes `BPF_SOCK_OPS_HDR_OPT_LEN_CB`. No outgoing TCP header exists at that point, so `skb_data` is unavailable, but `skb_tcp_flags` still describes the packet being prepared. The program reserves space with `bpf_reserve_hdr_opt()`. Later, after kernel options and any earlier BPF programs have written their data, the kernel invokes `BPF_SOCK_OPS_WRITE_HDR_OPT_CB`; the program can call `bpf_store_hdr_opt()` and inspect already-written options with `bpf_load_hdr_opt()`.

Syncookie handling adds a special branch. During SYNACK generation, `TCP_BPF_SYN*` getters may copy the just-received SYN because syncookie mode cannot rely on a saved SYN skb. `BPF_WRITE_HDR_TCP_SYNACK_COOKIE` in `args[0]` tells the program this path is active. `BPF_WRITE_HDR_TCP_CURRENT_MSS` instead represents an established-socket MSS calculation pass where option space is computed without sending an skb.

Other sock_ops callbacks are event driven. RTO, retransmission, TCP state transition, listen, RTT, and timestamp callbacks are delivered when the corresponding callback flags or socket flags are enabled. The enum comments define the meaning of callback arguments, such as retransmit sequence/segment count/transmit result or old/new TCP states.

FIB lookup helper flow treats `struct bpf_fib_lookup` as a mutable in/out object. The BPF program initializes family, addresses, interface, length, and optional L4 or policy fields before calling the helper. On success, the helper may rewrite destination to a gateway, fill source address, output ifindex, route metric, VLAN fields, MTU, and MAC addresses. On non-success return codes, the program chooses whether to drop, redirect differently, fall back, or report fragmentation.

CO-RE relocation flow spans compiler, loader, and kernel. Clang emits relocation records for preserve-access-index expressions. libbpf consumes BTF and relocation data, rewrites instructions for the target kernel layout, and passes metadata through the load path. The tools copy of this header must match the kernel UAPI so loaders and generated artifacts agree on relocation kind values and record layout.

`BPF_MAP_TYPE_INSN_ARRAY` entries have a load-time transition. Before load, user space sets `orig_off` and clears the other fields. After verification and optional JIT compilation, the kernel updates translated and JITed offsets or records that the original instruction was optimized away.

## State and Persistence Behavior

Most fields here describe per-invocation context, not persistent storage. `skb_data` and `skb_data_end` are only valid in the callback contexts documented by the header and must not be retained. `optval` and `optval_end` in `bpf_sockopt` are similarly bounded invocation-local buffers.

Sock_ops callback flags persist in socket or sock_ops state after being set, controlling future callback delivery until changed. The supported mask is an ABI validation point for setter paths.

TCP state constants are persistent ABI values for compiled BPF programs. Programs may compare directly against these enum constants, so kernel TCP state drift requires explicit conversion rather than silent renumbering.

FIB lookup, MTU, redirect-neighbor, flow-dissector, sysctl, sockopt, and SK_LOOKUP records are short-lived helper arguments or program contexts. Several unions deliberately change meaning across a helper call, such as `tot_len` versus `mtu_result`, `tos`/`flowinfo` versus `rt_metric`, table ID versus VLAN output, and policy mark versus returned MAC addresses.

Opaque map-value objects can persist inside BPF maps. Their bytes are ABI-visible only for size and alignment; correctness depends on verifier-enforced placement, initialization, ownership, locking, and lifetime rules.

BTF function/line info and CO-RE relocation records persist inside BPF ELF objects and load metadata. They are consumed during program loading and debugging rather than changed at runtime. Instruction-array map entries persist in maps and are rewritten by the verifier/load path.

## Dependencies and Integration Points

This chunk depends on Linux UAPI fixed-width and endian types such as `__u8`, `__u16`, `__u32`, `__u64`, `__s32`, `__be16`, and `__be32`, plus the `__bpf_md_ptr()` metadata-pointer macro defined earlier in the header.

TCP sock_ops definitions integrate with the TCP stack, socket option code, syncookie handling, retransmission/RTO paths, RTT sampling, TCP state transitions, and TX timestamping. The comments reference helpers documented earlier in `bpf.h`, including `bpf_load_hdr_opt()`, `bpf_reserve_hdr_opt()`, `bpf_store_hdr_opt()`, `bpf_getsockopt()`, and `bpf_setsockopt()`.

Routing definitions integrate with kernel FIB lookup, policy routing, route metrics, input/output interface lookup, neighbor resolution, VLAN metadata, MTU/GSO checks, and redirect-neighbor helpers.

Tracing integration covers raw tracepoints, tracepoints, kprobes, kretprobes, uprobes, uretprobes, task FD introspection, and perf event value accounting. Device cgroup, sysctl, sockopt, and SK_LOOKUP program types consume their respective context structs.

Toolchain integration is central for this tools-side file. `bpf_func_info`, `bpf_line_info`, `btf_ptr`, `bpf_core_relo_kind`, and `bpf_core_relo` are shared with clang/LLVM output, libbpf relocation handling, BTF formatting helpers, bpftool-style inspection, generated `vmlinux.h` workflows, verifier diagnostics, and userspace build artifacts.

The opaque synchronization/container structs integrate with verifier-recognized map value fields and helper/kfunc families for spin locks, timers, task work, workqueues, dynptrs, linked lists, red-black trees, and refcounts.

## Risks and Edge Cases

This range is ABI-sensitive. Reordering enum values, changing struct field order, changing alignment attributes, or altering union overlays can break compiled BPF programs, loaders, and tools. The sock_ops op enum is append-only, and `bpf_sk_lookup` explicitly requires new fields to be added at the end.

The chunk starts in the middle of `struct bpf_sock_ops`; earlier fields are in the preceding chunk for the same file. Any full-file interpretation must combine the preceding sock_ops fields with this tail before assessing the complete context layout.

Pointer lifetime and bounds are critical. `skb_data`, `skb_data_end`, `optval`, `optval_end`, and socket pointers are only usable when the callback context and verifier allow them. `skb_data` is absent during header length reservation and only covers TCP header bytes where documented.

Endianness is easy to mishandle. Many networking fields use network byte order, including remote ports, IP addresses, FIB addresses, and flow dissector addresses, while `bpf_sk_lookup.local_port` is host byte order.

Input/output union overlays in `struct bpf_fib_lookup` require disciplined initialization and read ordering. Reusing a structure without clearing it or reading output fields before the helper returns can propagate stale route, VLAN, MTU, or MAC data. The `tbid` input is meaningful only with the documented direct/table-ID flags.

TCP header-option programs can corrupt option layout or skew MSS calculations if they reserve different lengths than they write, assume `skb_data` exists during `HDR_OPT_LEN`, ignore syncookie-specific SYN retrieval, or leave parse-all callbacks enabled after the exceptional need has passed.

CO-RE relocation correctness depends on exact BTF metadata, relocation-kind numeric values, and compiler-emitted access strings. Incorrect `insn_off`, `type_id`, `access_str_off`, or kind values can cause verifier/load failures or incorrect field-access rewrites.

Opaque object misuse is mostly detected outside this header by verifier and helper/kfunc rules. Copying, zeroing, moving, or misaligning locks, timers, work items, dynptrs, list nodes, rbtree nodes, or refcount objects as ordinary bytes can lead to verifier rejection or lifecycle bugs.

Tools-header drift is a specific risk for this copy. If `tools/include/uapi/linux/bpf.h` diverges from the kernel UAPI header, in-tree tools may compile with stale layouts or enum values even when the kernel side has changed.

## Test Signals

Useful validation signals for this chunk include:

- Header build coverage for both kernel and tools consumers, including bpftool/libbpf-related builds that use `tools/include/uapi`.
- ABI layout checks for struct sizes, field offsets, alignments, enum numeric values, and bit masks against the kernel UAPI copy.
- TCP sock_ops selftests for RTO, retransmission, TCP state, RTT, listen/connect, active/passive established, TX timestamping, callback flag get/set, unsupported flag masking/rejection, and callback `args[]` meanings.
- TCP header-option tests for parse-all, parse-unknown-only, length reservation, option writing, existing-option lookup, syncookie SYNACK handling, current-MSS option-space calculation, missing `skb_data` during `HDR_OPT_LEN`, and reservation/write length mismatches.
- `TCP_BPF_SYN*` tests for TCP-only, IP+TCP, and MAC+IP+TCP copies; too-small optval buffers returning `-ENOSPC`; missing saved/current SYN returning `-ENOENT`; and syncookie mode where only the just-received SYN path is usable.
- Routing helper tests for all FIB return codes, direct and egress lookup, skip-neighbor, table-ID lookup, source-address derivation, policy marks, IPv4 and IPv6, gateway rewrite, VLAN output, MAC output, MTU output, and route metric output.
- MTU and redirect-neighbor tests for `BPF_MTU_CHK_SEGS`, fragmentation-needed, GSO segments-too-big, IPv4/IPv6 nexthops, and absent/stale neighbor state.
- Flow dissector tests for IPv4, IPv6, fragmented packets, first and later fragments, encapsulation, IPv6 flow labels, and correct `nhoff`/`thoff`/address/port/flag population.
- Tracing and perf tests for raw tracepoint argument indexing, task FD type reporting, kprobe/uprobe variants, and perf event `counter`/`enabled`/`running` accounting.
- BTF and CO-RE tests for function info, line info, bitfields, anonymous structs, array access strings, type-existence/type-size/type-match relocations, enum relocations, and loading across kernels with intentionally different target layouts.
- Verifier selftests for spin locks, timers, task work, workqueues, dynptrs, linked lists, red-black trees, refcounts, and instruction-array offset rewriting.

## Cross-Chunk Notes

The first line in this range is inside the final comment and field block of `struct bpf_sock_ops`; the structure begins earlier in `tools/include/uapi/linux/bpf.h`. The merge lane should combine this document with the preceding chunk for the same source file before producing the final per-file report.

This tools copy substantially mirrors the non-tools `include/uapi/linux/bpf.h` chunk for the same line range. Reconciliation should still keep the paths distinct because drift between the kernel UAPI copy and the tools UAPI copy is itself an important integration signal.
