# Research: sources/distributed-fs/ceph-client/tools/include/uapi/linux/bpf.h

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-006579`: lines 1-6943, `Docs/researches/chunks/subset-b-006579_research.md`
- `subset-b-006580`: lines 6944-7704, `Docs/researches/chunks/subset-b-006580_research.md`

## Chunk Research

### subset-b-006579: lines 1-6943

# sources/distributed-fs/ceph-client/tools/include/uapi/linux/bpf.h lines 1-6943

## Scope

This chunk covers the first 6,943 lines of `tools/include/uapi/linux/bpf.h`, a user-kernel ABI header copied into the Ceph client's tools include tree. It is not Ceph filesystem logic; it is the Linux eBPF UAPI contract used by user-space tooling when constructing BPF instructions, issuing the `bpf()` syscall, decoding BPF object metadata, and compiling programs against stable verifier-visible context layouts.

The chunk includes:

- Extended BPF instruction encodings and register numbering.
- Core syscall command, map, program, attach, link, and perf-event enumerations.
- BPF object flags, pseudo-instruction source-register encodings, and map/prog/load/update/query attributes.
- The complete `union bpf_attr` layout through commands present in this copy, including newer token, stream-read, struct-ops association, signature, and exclusive-program-hash fields.
- The large helper-function documentation block and the helper ID mapper up through `bpf_cgrp_storage_delete`.
- Helper flag constants, ring-buffer constants, redirect/action modes, and visible metadata/context structures through the beginning of `struct bpf_sock_ops`.

The chunk ends inside `struct bpf_sock_ops` after `sk`; callback flags, sock-ops operation codes, TCP-state lists, FIB lookup structures, BTF/CO-RE records, and iterator/kfunc tail definitions continue after line 6,943 and should be covered by the next chunk for this source file.

## Purpose

The header defines numeric ABI values shared by the kernel, libbpf-style tooling, selftests, bpftool-adjacent utilities, and any local build that includes `tools/include/uapi/linux/bpf.h` rather than a system header. The values here are consumed in three broad ways:

- BPF bytecode construction: opcodes such as `BPF_ALU64`, `BPF_JMP32`, `BPF_CALL`, `BPF_EXIT`, `BPF_ATOMIC`, sign-extending loads, endian conversions, pseudo calls, map references, BTF references, and kfunc calls are encoded into `struct bpf_insn`.
- BPF syscall marshalling: `enum bpf_cmd` selects the syscall operation, and `union bpf_attr` provides the command-specific input/output memory layout passed to the kernel.
- Verifier-visible ABI: structs such as `__sk_buff`, `xdp_md`, `bpf_sock`, `bpf_tcp_sock`, `bpf_sock_addr`, and `bpf_sock_ops` define the field order and access model that BPF programs can read or write.

Because this is UAPI, the primary design constraint is compatibility. New enum values and struct fields are appended, aliased, or padded rather than reordered. Several comments explicitly say that new fields can only be added at the end of public structs.

## Important APIs, Types, And Constants

The instruction section defines the eBPF extension over classic BPF. `struct bpf_insn` is the packed instruction record: one opcode byte, destination/source register nibbles, signed 16-bit offset, and signed 32-bit immediate. `MAX_BPF_REG` exposes the ten general-purpose 64-bit registers plus frame pointer convention through the `BPF_REG_0` through `BPF_REG_10` numbering. Pseudo encodings such as `BPF_PSEUDO_MAP_FD`, `BPF_PSEUDO_MAP_VALUE`, `BPF_PSEUDO_BTF_ID`, `BPF_PSEUDO_FUNC`, `BPF_PSEUDO_CALL`, and `BPF_PSEUDO_KFUNC_CALL` define how the loader/verifier rewrites special `ldimm64` and call instructions.

The early key and iterator structures include `bpf_lpm_trie_key`, `bpf_lpm_trie_key_hdr`, `bpf_lpm_trie_key_u8`, `bpf_cgroup_storage_key`, `enum bpf_cgroup_iter_order`, and `union bpf_iter_link_info`. These describe user-provided map keys or link creation payloads for LPM trie, cgroup storage, and iterator links.

`enum bpf_cmd` is the syscall command table. In this copy it runs from map element operations and program loading through object pin/get, attach/detach/query, BTF load/get, batch map operations, link create/update/detach, stats enabling, iterator creation, map binding, token creation, program stream reading, and struct-ops association. The command order is ABI-significant because user space passes the numeric command to `bpf()`.

`enum bpf_map_type` covers classic hash/array/prog-array/perf-array maps, percpu variants, LRU maps, LPM trie, map-in-map, devmap/cpumap/xskmap, socket maps and hashes, cgroup storage aliases, queue/stack, local-storage maps, struct-ops, ring buffer, user ring buffer, arena, and instruction-array maps. Deprecated cgroup-storage names are preserved as aliases to maintain source and numeric compatibility.

`enum bpf_prog_type`, `enum bpf_attach_type`, and `enum bpf_link_type` define where programs can run and how they can be attached. Covered program types include socket filter, kprobe, tc, tracepoint, XDP, perf event, cgroup hooks, LWT, sock ops, SK_SKB/SK_MSG, raw tracepoint, sock address and sockopt hooks, tracing, struct_ops, extension, LSM, SK_LOOKUP, syscall, and netfilter. Attach/link types include cgroup, tracing, XDP/devmap/cpumap, perf event, kprobe/uprobe multi, netfilter, TCX, netkit, sockmap, and session-style tracing attach points.

The flag section defines behavior for attach ordering and replacement, verifier/load modes, XDP fragments/device-bound programs, map creation and lookup/update semantics, path-FD object lookup/pin behavior, token-FD delegation, arena fault/user-pointer behavior, ring-buffer overwrite, program query, and test-run execution. Some flags intentionally share bit positions only within command-specific namespaces; callers must use them with the matching `bpf_attr` command branch.

`union bpf_attr` is the central syscall ABI. The covered branches include:

- `BPF_MAP_CREATE`: map type, key/value size, max entries, flags, inner map FD, NUMA node, object name, ifindex, BTF IDs, `map_extra`, BTF object FD, token FD, exclusive program hash, and hash size.
- Map element and batch operations: map FD, aligned user pointers for keys/values, per-element flags, batch cursors, and counts.
- `BPF_PROG_LOAD`: program type, instruction count and pointer, license, verifier log controls, object name, expected attach type, BTF/function/line/CO-RE metadata, attached program or BTF object, FD array binding, true log size, token FD, signature buffer, signature size, and keyring ID.
- Object pin/get: pathname pointer, object FD, file flags, and optional `path_fd` for openat-style semantics.
- Attach/detach/query/test-run: target object or ifindex, program FD, attach type, flags, replacement/relative placement fields, revisions, packet/context buffers, CPU selection, batch size, returned IDs, and per-link flags.
- BTF, task FD query, link create/update/detach, stats, iterator create, program bind map, token create, program stream read, and program-to-struct-ops association.

The helper documentation block is source material for `scripts/bpf_doc.py` and generated helper man pages. It documents helper signatures, descriptions, return values, and error cases from fundamental map helpers through tracing, networking, sockets, cgroup/local storage, ring buffers, dynptrs, timers, kptrs, user ring buffers, and cgroup storage helpers. The executable ABI from that documentation is crystallized by `___BPF_FUNC_MAPPER`, which maps helper names to stable numeric IDs in `enum bpf_func_id` through `BPF_FUNC_cgrp_storage_delete = 211`. The comment says the helper list is effectively frozen and new functionality should prefer kfuncs with weaker stability guarantees.

Helper-specific flags include checksum replacement and skb mutation flags, tunnel key flags, stack capture flags, perf-event output/read selector flags, checksum-level operations, skb adjust-room and encapsulation flags, sysctl name flags, local-storage creation flags, branch record flags, ring-buffer wakeup/query constants, SK_LOOKUP assignment flags, LWT encapsulation modes, binary-loader secureexec flag, and redirect flags.

The context and metadata structs before the chunk boundary include:

- `__sk_buff`, a verifier-visible mirror of `sk_buff` metadata for skb-oriented program types.
- `bpf_tunnel_key` and `bpf_xfrm_state` for tunnel and IPsec state helpers.
- `bpf_ret_code`, `tcx_action_base`, `xdp_action`, `sk_action` return code enums.
- `bpf_sock`, `bpf_tcp_sock`, and `bpf_sock_tuple` for socket and TCP metadata exposure.
- `xdp_md`, `bpf_xdp_sock`, `bpf_devmap_val`, and `bpf_cpumap_val` for XDP and map redirect paths.
- `sk_msg_md` and `sk_reuseport_md` for socket-message and reuseport program contexts.
- `bpf_prog_info`, `bpf_map_info`, `bpf_btf_info`, `bpf_link_info`, and `bpf_token_info` for `BPF_OBJ_GET_INFO_BY_FD` output.
- `bpf_sock_addr` and the initial portion of `bpf_sock_ops` for cgroup socket-address and TCP sock-ops programs.

## Control Flow

This header has no C runtime control flow. It describes control flow that occurs across the kernel/user boundary:

1. User space encodes a program as an array of `struct bpf_insn`, using opcode and pseudo-source constants from this header.
2. User space fills the appropriate `union bpf_attr` branch and calls `bpf(cmd, attr, size)`.
3. The kernel selects the syscall implementation based on `enum bpf_cmd`, copies only the fields valid for the command and provided `size`, and performs verifier, map, link, object, BTF, or query logic.
4. For `BPF_PROG_LOAD`, the verifier interprets instruction opcodes, register numbers, pseudo references, helper IDs, expected attach type, BTF/CO-RE data, map references, and program flags to decide whether the program can run.
5. At runtime, the program type and attach type decide which context struct layout is exposed to BPF bytecode and which helper IDs/flags are accepted.
6. Object lifetime continues through file descriptors, pinned paths, attached links, bound maps, and IDs exposed through info/query commands.

The cgroup attach comments describe effective execution order for inherited cgroup programs. For multi-attach cgroups, descendant programs may run before ancestor programs, and `BPF_F_REPLACE`, relative FD/ID, and expected revision fields provide ordered replacement semantics.

## State And Persistence Behavior

The header itself stores no state. It defines ABI fields used to create and reference persistent kernel BPF objects:

- Maps persist while referenced by FDs, pins, links, programs, or other kernel references. Map values can be updated, deleted, batch-processed, frozen, mmapped, shared across CPUs, or tied to local storage depending on type and flags.
- Programs persist through FDs, pinned object paths, attachments, links, and IDs. `bpf_prog_info` exposes load time, creator UID, tags, JIT/xlated lengths, map IDs, BTF metadata, run counters, runtime, recursion misses, verified instruction count, and attach BTF metadata.
- Links persist attachment state as first-class FDs and IDs. `bpf_link_info` reports attachment-specific state for raw tracepoints, tracing, cgroups, iterators, netns, XDP, struct_ops, netfilter, kprobe/uprobe multi, perf-event, TCX, netkit, and sockmap links.
- BTF objects persist as BPF objects with IDs and can be queried through `bpf_btf_info`.
- Tokens persist as delegated capability objects bound to a bpffs user namespace and report allowed command/map/program/attach masks via `bpf_token_info`.
- Ring-buffer and user-ring-buffer maps maintain producer/consumer positions and records. Flags in this chunk control wakeup behavior, discard/submit state, overwrite mode, and query selectors.

The comments in the syscall preamble state the key lifetime rule: BPF objects can be inherited across `fork`, transferred over Unix sockets, duplicated, pinned to bpffs, and deallocated only after all descriptors, pins, and attachments are gone.

## Dependencies

This header depends on Linux UAPI fixed-width types from `<linux/types.h>` and classic BPF definitions from `<linux/bpf_common.h>`. It uses UAPI annotations such as `__u32`, `__u64`, `__s32`, `__s64`, `__be16`, `__be32`, and `__aligned_u64`; preserving these types is necessary for 32-bit and 64-bit user-space ABI compatibility.

Integration points include:

- Kernel `kernel/bpf/syscall.c`, verifier, map implementations, link implementations, BTF loader, token support, and program-type attach code that consume the enum values and `union bpf_attr` branches.
- libbpf, bpftool, BPF selftests, loaders, and generated skeletons that include this tools UAPI header to compile against specific kernel ABI values.
- `scripts/bpf_doc.py`, which parses the helper documentation comments and helper mapper to generate helper documentation.
- Networking, tracing, cgroup, LSM, perf, XDP, netfilter, socket, and struct_ops subsystems that provide program contexts and helper behavior.
- Ceph-client tooling only indirectly, through the vendored `tools/include/uapi` header set used by build utilities rather than distributed filesystem runtime state.

## Risks And Edge Cases

ABI drift is the largest risk. If this copied tools header diverges from the target runtime kernel, user-space code can compile with enum values, struct fields, helper IDs, or flags that the running kernel does not understand. Older kernels generally reject unknown commands, map/prog/link types, flags, helpers, or oversized attributes, but feature probing is required for portable tooling.

`union bpf_attr` is size- and offset-sensitive. User space must zero-initialize it, fill only the branch matching `cmd`, pass the correct `size`, and use `__aligned_u64` for user pointers. Uninitialized padding or stale fields can cause `EINVAL`, verifier rejection, or unintended behavior. The union is explicitly aligned to 8 bytes for syscall ABI consistency.

Enum numeric order is stable ABI. New values must be appended or explicitly aliased. Reordering `bpf_cmd`, `bpf_map_type`, `bpf_prog_type`, `bpf_attach_type`, `bpf_link_type`, helper IDs, or return-code enums would break already compiled programs and loaders.

Program context structs are append-only. Comments on `__sk_buff`, `xdp_md`, devmap/cpumap values, SK_MSG metadata, and sock-ops metadata warn that fields must only be added at the end. Inserting fields in the middle changes verifier field offsets and breaks compiled BPF bytecode.

Byte order is easy to misuse. Many socket and packet fields are explicitly network byte order while others, such as `local_port` and some TCP metrics, are host byte order. BPF programs and loaders need consistent endian conversions.

Flags are command- or helper-specific. Identical bit positions mean different things in different contexts, such as map creation flags, program load flags, attach flags, helper flags, and ring-buffer flags. Passing a flag into the wrong command/helper namespace should be treated as invalid even if the bit value exists elsewhere.

The helper list is described as effectively frozen. Adding helpers or changing helper IDs would be high-risk; newer extensibility should happen through kfuncs. Existing helper documentation also carries behavioral details and error codes that tests and users may rely on.

The chunk boundary matters: this research stops while `struct bpf_sock_ops` is still open. Any full-file reasoning about sock-ops callback flags, TCP state/operation enums, FIB lookup, flow keys, CO-RE relocation records, or kfunc flags needs the following chunk.

## Test Signals

Useful validation for this header chunk includes:

- Compile coverage for tools that include `tools/include/uapi/linux/bpf.h`, especially code that constructs `struct bpf_insn`, fills `union bpf_attr`, or decodes `bpf_*_info`.
- BPF selftests or libbpf feature probes that exercise map create/update/lookup/delete, batch operations, BTF load, program load, link create/update/detach, token create, and object info queries.
- Static ABI checks comparing enum values, `sizeof(union bpf_attr)`, member offsets, and context struct offsets against the kernel header expected by the target kernel.
- Verifier tests for pseudo map references, BTF IDs, BPF-to-BPF calls, kfunc calls, helper ID selection, load flags, expected attach types, and context field access.
- Networking/XDP tests that validate `__sk_buff`, `xdp_md`, `bpf_sock`, `bpf_tcp_sock`, SK_MSG, reuseport, devmap, cpumap, and return-code semantics.
- Ring-buffer and user-ring-buffer tests for wakeup flags, discard/submit behavior, overwrite mode, producer/consumer position queries, and malformed user-producer error paths.
- Documentation generation using `scripts/bpf_doc.py --filename tools/include/uapi/linux/bpf.h` to catch helper comment or mapper formatting regressions.

### subset-b-006580: lines 6944-7704

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
