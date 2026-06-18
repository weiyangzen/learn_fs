# Research: sources/distributed-fs/ceph-client/include/uapi/linux/bpf.h

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-005975`: lines 1-6943, `Docs/researches/chunks/subset-b-005975_research.md`
- `subset-b-005976`: lines 6944-7705, `Docs/researches/chunks/subset-b-005976_research.md`

## Chunk Research

### subset-b-005975: lines 1-6943

# sources/distributed-fs/ceph-client/include/uapi/linux/bpf.h lines 1-6943

## Scope

This chunk covers the first 6,943 lines of `include/uapi/linux/bpf.h`, from the header guard through the beginning of `struct bpf_sock_ops`. It is a UAPI header, so the content is almost entirely ABI declarations, numeric constants, command payload layouts, and in-header documentation rather than executable implementation.

The range includes the extended BPF instruction encodings, register and instruction layout definitions, LPM trie and cgroup iterator key structures, the `bpf()` syscall command documentation and `enum bpf_cmd`, map/program/attach/link type enumerations, BPF object and program flags, the full `union bpf_attr` command argument ABI, the helper-function documentation block, the frozen helper ID mapper through helper ID 211, helper flag definitions, and many user-visible BPF context/info structures for skb, XDP, sockets, maps, programs, BTF, links, and tokens. The chunk ends mid-file inside `struct bpf_sock_ops`; later sock-ops constants and remaining context/BTF/CO-RE/kfunc definitions are outside this chunk.

## Purpose

This header is the central Linux eBPF user/kernel ABI contract. It tells user space, BPF loaders, BPF compilers, libbpf-style tooling, and in-tree eBPF programs how to encode BPF instructions, call the `bpf()` syscall, create and manage BPF objects, identify supported program/map/link/attach/helper types, and interpret context structures exposed to BPF programs.

For the Ceph client source tree this is a vendored kernel UAPI dependency, not Ceph-specific filesystem logic. Its practical role is compatibility: code that builds BPF-related pieces against this tree must see the same numeric IDs, struct layout, alignment, and field-order rules that the target kernel expects.

## Important APIs, Types, and Data

Instruction-level definitions extend classic BPF with eBPF classes and opcodes: `BPF_JMP32`, `BPF_ALU64`, `BPF_DW`, `BPF_MEMSX`, `BPF_ATOMIC`, `BPF_XADD`, `BPF_MOV`, `BPF_ARSH`, `BPF_END`, endian flags, signed and unsigned jump encodings, `BPF_JCOND`, `BPF_CALL`, `BPF_EXIT`, and atomic operation modifiers such as `BPF_FETCH`, `BPF_XCHG`, `BPF_CMPXCHG`, `BPF_LOAD_ACQ`, and `BPF_STORE_REL`. `struct bpf_insn` defines the packed instruction ABI: opcode byte, 4-bit destination/source registers, signed 16-bit offset, and signed 32-bit immediate.

Register definitions expose `BPF_REG_0` through `BPF_REG_10` and `MAX_BPF_REG`. The header records the eBPF calling convention shape indirectly: ten general-purpose 64-bit registers plus a stack frame, with `BPF_REG_10` conventionally used as the frame pointer by verifier/JIT code outside this header.

Map key/support types include deprecated `struct bpf_lpm_trie_key`, replacement `struct bpf_lpm_trie_key_hdr`, flexible-array `struct bpf_lpm_trie_key_u8`, and `struct bpf_cgroup_storage_key`. Cgroup iteration is represented by `enum bpf_cgroup_iter_order` and `union bpf_iter_link_info`, which packages iterator-specific link data for map, cgroup, and task iterators.

`enum bpf_cmd` declares the syscall command IDs from map element operations and program load through link management, stats enablement, iterator creation, map binding, token creation, program stream reads, and struct-ops association. The surrounding documentation describes expected return values and object lifetime: maps, programs, BTF objects, links, stats FDs, iterators, and tokens are FD-backed kernel objects whose lifetime can also be extended by bpffs pinning, links, or map/program references.

`enum bpf_map_type` covers hash/array/program/perf-event/per-CPU maps, stack trace, cgroup array/storage, LRU maps, LPM trie, map-in-map, devmap/cpumap/xskmap, sockmap/sockhash, queue/stack, local-storage variants, struct-ops, ring buffers, bloom filter, user ring buffer, cgroup storage, arena, and instruction-array maps. It also preserves deprecated cgroup storage names as ABI aliases.

`enum bpf_prog_type` defines program classes such as socket filter, kprobe, sched cls/act, tracepoint, XDP, perf event, cgroup hooks, LWT, sock ops, SK_SKB/SK_MSG/SK_REUSEPORT/SK_LOOKUP, raw tracepoints, LIRC, flow dissector, tracing, struct ops, extension, LSM, syscall, and netfilter. The header explicitly warns that tracing-related programs are not stable across kernel internals.

`enum bpf_attach_type` and `enum bpf_link_type` enumerate hook positions and FD-based link object types. Attach types span cgroup network/socket/sysctl/sockopt/unix hooks, SK_SKB/SK_MSG/SK_REUSEPORT/SK_LOOKUP, tracing fentry/fexit/modify-return/LSM/iterator/kprobe/uprobe sessions, XDP/devmap/cpumap, perf events, struct ops, netfilter, TCX, and netkit. Link types include raw tracepoint, tracing, cgroup, iterator, netns, XDP, perf event, kprobe/uprobe multi, struct ops, netfilter, TCX, netkit, and sockmap.

Program and map flags define verifier and object creation policy. Important program-load flags include strict/any alignment, high-32-bit randomization tests, state-frequency and register-invariant test flags, sleepable programs, XDP fragments, and device-bound XDP-only loading. Map creation flags include no prealloc/common LRU, NUMA node, syscall/program read/write restrictions, stack build IDs, zero seed, socket clone, mmapable maps, preserved perf elements, inner-map support, link-backed maps, path FD semantics, value-type BTF object FD, BPF token FD, arena fault/user-conversion behavior, and ring buffer overwrite mode.

Pseudo instruction source registers define loader/verifier rewrite contracts for map FDs or indexes, map value pointers, BTF IDs, function addresses, subprogram calls, and kfunc calls: `BPF_PSEUDO_MAP_FD`, `BPF_PSEUDO_MAP_IDX`, `BPF_PSEUDO_MAP_VALUE`, `BPF_PSEUDO_MAP_IDX_VALUE`, `BPF_PSEUDO_BTF_ID`, `BPF_PSEUDO_FUNC`, `BPF_PSEUDO_CALL`, and `BPF_PSEUDO_KFUNC_CALL`.

`union bpf_attr` is the main syscall ABI payload. Its anonymous members cover `BPF_MAP_CREATE`, element lookup/update/delete/freeze and batch operations, `BPF_PROG_LOAD`, object pin/get, attach/detach, test-run, get-by-ID/get-next-ID, object info, program query, raw tracepoint open, BTF load, task FD query, link create/update/detach, stats enablement, iterator creation, program/map binding, token creation, program stream reads, and struct-ops association. It is explicitly aligned to 8 bytes and relies on `__aligned_u64` user pointers to keep 32-bit and 64-bit user-space ABIs consistent.

The helper documentation block describes helper prototypes and semantics for helpers such as map lookup/update/delete, probe reads, time, tracing output, random/CPU/task/UID metadata, packet mutation, checksum repair, tail calls, redirect, perf/ringbuf/user-ringbuf output, stack capture, tunnel metadata, protocol changes, socket and cgroup queries, sockmap/sockhash operations, LWT/SRv6 operations, sysctl access, local storage, timers, dynptrs, BTF printing, kernel symbol/function introspection, raw SYN cookie helpers, and cgroup storage. `___BPF_FUNC_MAPPER` assigns stable helper IDs 0 through 211 and `enum bpf_func_id` derives `BPF_FUNC_*` constants from that mapper. The chunk records that this helper list is effectively frozen and new functionality should prefer kfuncs.

Helper flag enums define shared option bits for checksum helpers, tunnel helpers, stack capture, perf event output, adjust-room, local-storage creation, branch records, ringbuf wakeup/query state, SK lookup assignment, BPF return redirects, and skb timestamp clocks.

Context and object info structures in this range include `struct __sk_buff`, `struct bpf_tunnel_key`, `struct bpf_xfrm_state`, `enum bpf_ret_code`, `struct bpf_sock`, `struct bpf_tcp_sock`, `struct bpf_sock_tuple`, `enum tcx_action_base`, `struct bpf_xdp_sock`, `enum xdp_action`, `struct xdp_md`, `struct bpf_devmap_val`, `struct bpf_cpumap_val`, `enum sk_action`, `struct sk_msg_md`, `struct sk_reuseport_md`, `struct bpf_prog_info`, `struct bpf_map_info`, `struct bpf_btf_info`, `struct bpf_link_info`, `struct bpf_token_info`, `struct bpf_sock_addr`, and the beginning of `struct bpf_sock_ops`.

## Control Flow

The primary runtime flow is user space invoking `bpf(cmd, attr, size)`. The `cmd` value selects one arm of `union bpf_attr`, and the kernel validates `size`, command-specific fields, capability/token requirements, object FDs, BTF metadata, program/map/link types, and pointer arguments. Success usually returns either 0, a new FD, a next object ID, or command-specific output in user-provided buffers. Errors are reported through negative syscall return and `errno`.

Map control flow starts with `BPF_MAP_CREATE`, then element operations use `map_fd`, `key`, `value`/`next_key`, and `flags`. Batch operations carry input/output batch cursors plus arrays of keys and values. Map-in-map, BTF-typed maps, arenas, ring buffers, local storage, struct-ops maps, and token-gated map creation add command-specific fields in the same `BPF_MAP_CREATE` arm.

Program load flow uses the `BPF_PROG_LOAD` arm. User space passes program type, instruction array pointer/count, license, verifier log buffer/level/size, program flags, optional expected attach type, BTF FD, function and line records, attach BTF/program/module target, CO-RE relocation data, FD array, token FD, signature, and keyring metadata. The verifier consumes these fields, rewrites pseudo instructions, validates helper/kfunc/map access, and returns a program FD or an error plus optional verifier log output.

Attach flow has two styles. Older `BPF_PROG_ATTACH`/`BPF_PROG_DETACH` uses a target FD or ifindex plus attach type, flags, replacement FD, relative FD/ID, and expected revision. FD-backed `BPF_LINK_CREATE` packages program or map FD, target FD/ifindex, attach type, flags, and a union of attach-type-specific payloads for iterators, perf events, kprobe/uprobe multi, tracing, netfilter, TCX, netkit, and cgroup links. `BPF_LINK_UPDATE`, `BPF_LINK_DETACH`, get-by-ID, and get-next-ID then manage link objects.

Introspection flow uses get-next-ID commands to enumerate objects, get-by-ID commands to open FDs, and `BPF_OBJ_GET_INFO_BY_FD` to fill `struct bpf_prog_info`, `struct bpf_map_info`, `struct bpf_btf_info`, `struct bpf_link_info`, or `struct bpf_token_info`. Program query flow reports attached program IDs, link IDs, per-program flags, link flags, and revision data for a target hook.

Helper call flow is encoded in BPF bytecode by `BPF_CALL` with `imm = BPF_FUNC_*`. The verifier resolves the numeric helper ID against program type, attach type, argument types, sleepability, privileges, and kernel configuration. Some helpers mutate packet buffers or dynptr backing data and therefore invalidate previously verified direct-access pointers; BPF programs must re-check bounds after such calls.

Context flow depends on program type. Network programs see ABI mirrors such as `__sk_buff` or `xdp_md`; socket hooks see `bpf_sock_addr`, `bpf_sock_ops`, `sk_msg_md`, or `sk_reuseport_md`; introspection/user-space tools receive `bpf_*_info` structures. These structs are append-only ABI surfaces: comments repeatedly require new fields to be added at the end.

## State and Persistence Behavior

This chunk defines no storage itself, but it describes many persistent kernel object lifetimes. Maps, programs, BTF objects, links, tokens, stats handles, and iterators are FD-backed objects. Closing the last FD can free them unless another reference persists through bpffs pinning, attachment, map/program binding, link ownership, map-in-map nesting, or another kernel reference.

Map state persists in kernel map objects according to map type and flags. Hash/array-style maps hold key/value elements; per-CPU maps maintain CPU-local values; LPM trie keys carry prefix lengths; queue/stack maps expose push/pop/peek helpers; ring buffers and user ring buffers persist producer/consumer positions; local-storage maps attach values to sockets, inodes, tasks, or cgroups; arena maps expose memory-mappable regions with fault behavior controlled by flags.

Program state persists as loaded, verifier-approved bytecode plus metadata: type, attach constraints, BTF func/line/CO-RE info, referenced map FDs, bound maps, token provenance, optional signature metadata, and runtime counters. `BPF_ENABLE_STATS` creates reference-counted global runtime statistics state that remains enabled while any returned stats FD is open.

Link state persists an attachment relationship independently of process lifetime while the link FD or pin exists. Link info records target-specific state such as cgroup IDs, iterator target names, netns ifindex, XDP ifindex, struct-ops map IDs, netfilter hook tuple, kprobe/uprobe arrays/cookies, perf event identity, TCX/netkit attach location, and sockmap map ID.

Token state persists delegated permissions. `BPF_TOKEN_CREATE` derives a token from a bpffs instance configured with delegation mount options. `struct bpf_token_info` exposes allowed command, map, program, and attach masks. Token FDs can be passed into map creation, program load, BTF load, and get-by-ID flows when the relevant token flag is set.

Helper-visible state includes transient packet buffers, skb hash/checksum/offload state, tunnel metadata, XDP head/tail/meta pointers, socket cookies and ownership, cgroup IDs, current task identity, perf event counters, stack trace maps, ringbuf samples, dynptr validity, BPF timers, local storage entries, kptr references, TCP sock-ops callback flags, sysctl new/current values, and skb timestamps. Many helpers require callers to handle NULL, negative errors, reference release, or verifier-enforced cleanup.

ABI stability is a central persistence concern. Numeric enum values and struct field layouts are long-lived user/kernel contracts. Deprecated aliases such as cgroup storage map types and older probe-read helpers remain present for compatibility. The helper ID mapper is explicitly treated as frozen, so reordering or removing entries would break existing BPF bytecode.

## Dependencies and Integration Points

The header depends on `<linux/types.h>` and `<linux/bpf_common.h>` for fixed-width integer types, endian annotations, `__aligned_u64`, and classic BPF shared constants. It also refers to many kernel types by ABI name in helper prototypes and comments, including `struct bpf_map`, `struct sk_buff`, `struct xdp_buff`, `struct xdp_md`, `struct bpf_sock`, `struct sock`, `struct tcp_sock`, `struct task_struct`, `struct inode`, `struct file`, `struct path`, `struct seq_file`, `struct cgroup`, `struct btf_ptr`, IP/TCP header structs, and perf event data types.

The primary integration point is the `bpf()` syscall implementation in the kernel. User-space loaders must fill `union bpf_attr` exactly, pass the correct `size`, and maintain zeroed unused fields for forward/backward compatibility. Libbpf, bpftool, clang/LLVM BPF code generation, selftests, tracing tools, container runtimes, and network dataplane tooling all depend on this contract.

Verifier and JIT integration is implicit in instruction encodings, pseudo instruction definitions, helper IDs, program flags, BTF/CO-RE fields, and context structs. The verifier uses these declarations to type-check memory, helper arguments, pointer lifetimes, direct packet access, BTF-based access, sleepable program restrictions, spin-lock regions, dynptr cleanup, and kptr reference ownership.

Networking integration is broad. The chunk exposes TC and XDP return codes, skb/XDP metadata, tunnel keys, XFRM state, sock tuples, redirect helpers, FIB/neighbor helpers via later helper docs in this chunk, skb checksum/hash/timestamp flags, devmap/cpumap values, SK_MSG and reuseport contexts, socket lookup/assignment helpers, and cgroup socket address/ops contexts.

Tracing, observability, and security integration includes kprobe/uprobe/tracepoint/perf-event program/link types, raw tracepoint opening, task FD query, stack helpers, branch record helpers, BTF load/introspection, LSM attach types, bprm options, IMA hash helpers, signal helpers, `bpf_sys_bpf`/`bpf_sys_close` helper exposure for constrained syscall execution, and helper docs for function argument/return inspection.

Object pinning integrates with bpffs through `BPF_OBJ_PIN`, `BPF_OBJ_GET`, `BPF_F_PATH_FD`, and BPF token creation. Attach/query APIs integrate with cgroup v2, net namespaces, netfilter, TCX, netkit, perf events, and struct-ops subsystems.

## Risks

ABI drift is the highest risk. Changing enum order, numeric helper IDs, struct field order, alignment, field width, or union arm layout can break compiled BPF bytecode and user-space loaders. New fields must be appended where comments say so, and deprecated values generally cannot be removed.

`union bpf_attr` is easy to misuse because many commands share overlapping anonymous fields. Incorrectly zeroing unused fields, using the wrong union arm for a command, passing 32-bit pointers without `__aligned_u64` handling, or setting incompatible flag combinations can yield `EINVAL`, verifier rejection, or subtle behavior differences across kernels.

Verifier-visible helper side effects are subtle. Helpers that resize, pull, linearize, write, or otherwise mutate skb/XDP/dynptr backing storage invalidate direct-access pointers. Programs that keep using old `data`/`data_end` or dynptr slices after such helpers can be rejected by the verifier or, if verifier rules drift, risk unsafe memory access.

Reference ownership is a common source of bugs. Socket lookup helpers return references that must be released with `bpf_sk_release`; kptr exchange can return a referenced pointer that must be released or moved; dynptr ringbuf reservation must be submitted or discarded; local storage creation can fail and return NULL; ringbuf reserve can fail; some helper outputs are only momentary snapshots.

Capability and context restrictions are security-sensitive. Helpers such as `bpf_probe_write_user`, override return, kernel symbol lookup, syscall helpers, signal helpers, BPF token delegation, sleepable program helpers, and map/program creation with tokens all depend on kernel-side privilege, token, program-type, and config checks outside this header. Over-broad enablement can expose kernel memory or policy control.

Endianness and byte-order comments matter for network contexts. Fields such as IPv4/IPv6 addresses, remote ports, tunnel IDs, SPI, and socket ports use mixed host and network byte order. BPF programs and user-space decoders that ignore these annotations can silently make wrong routing, filtering, or policy decisions.

Trace helper documentation is not a stable kernel-internal ABI promise. The header explicitly states tracing program contexts depend on the analyzed kernel. Programs using raw tracepoint, kprobe, BTF IDs, kfuncs, or kernel struct pointers need matching kernel BTF/layout expectations.

Helper ID list maintenance is constrained. The file says the helper list is effectively frozen in favor of kfuncs. Adding helpers anyway increases long-term ABI burden; inserting helpers anywhere but the end would be a direct compatibility break.

## Test and Validation Signals

UAPI build validation should compile representative user-space BPF loaders and in-kernel BPF selftests against this header on 32-bit and 64-bit targets, checking `sizeof(union bpf_attr)`, 8-byte alignment, `__aligned_u64` pointer handling, and layout offsets for key structs such as `bpf_insn`, `bpf_prog_info`, `bpf_map_info`, `bpf_link_info`, `__sk_buff`, `xdp_md`, and `bpf_sock_addr`.

ABI compatibility tests should assert stable numeric values for `enum bpf_cmd`, map/program/attach/link types, `BPF_FUNC_*` helper IDs 0 through 211, return codes, XDP actions, TCX actions, map flags, program flags, pseudo instruction source registers, and helper flags. These tests should catch accidental reordering.

Syscall tests should exercise every `union bpf_attr` arm represented in this chunk with valid and invalid inputs: map create/update/lookup/delete/batch/freeze, program load with verifier log and BTF metadata, object pin/get using absolute and path-FD forms, attach/detach/link create/update/detach, get-next/get-by-ID, object info, program query, BTF load, task FD query, stats enable/close, iterator create, map binding, token create, stream read, and struct-ops association.

Verifier tests should cover pseudo instruction rewrites for map FD/index, map value, BTF ID, BPF-to-BPF function calls, and kfunc calls. They should also cover strict versus any alignment, sleepable program restrictions, XDP fragment flags, device-bound XDP flags, token-gated map/program/BTF operations, FD-array binding, signatures, and expected attach type validation.

Helper tests should be grouped by subsystem: map helpers; time/random/task metadata; skb mutation and checksum helpers; XDP adjust/load/store helpers; redirect/devmap/cpumap helpers; perf/ringbuf/user-ringbuf output; stack and branch record capture; socket lookup/assignment/release helpers; sockmap/sockhash/SK_MSG helpers; local storage for socket/inode/task/cgroup; sysctl helpers; timers; dynptr read/write/data and ringbuf dynptr helpers; BTF printing; IMA hash; kptr exchange; raw SYN cookie helpers; and cgroup storage helpers.

Negative verifier tests should confirm pointer invalidation after skb/XDP/dynptr-mutating helpers, missing release of referenced sockets/kptrs, missing ringbuf dynptr submit/discard, out-of-bounds dynptr reads/writes, invalid spin-lock use, unsupported helpers for program type, nonzero reserved flags, invalid CPU numbers for per-CPU lookup, invalid netns IDs, and use of tracing-only helpers in inappropriate contexts.

Networking tests should validate byte-order expectations and return-code behavior for `__sk_buff`, tunnel keys, `bpf_xfrm_state`, `bpf_sock`, `bpf_tcp_sock`, sock tuples, `xdp_md`, devmap/cpumap values, `sk_msg_md`, reuseport metadata, cgroup socket address fields, and the beginning sock-ops metrics in this chunk.

Documentation generation is also a test signal. The helper documentation is intentionally parseable by `scripts/bpf_doc.py` and `rst2man`; whitespace, prototype formatting, and helper block delimiters should be checked because malformed docs can break generated `bpf-helpers(7)` output even if C compilation succeeds.

## Cross-Chunk Notes

This chunk starts at the beginning of `bpf.h` but stops at line 6,943 inside `struct bpf_sock_ops`. The merge lane must combine it with later chunks for the rest of `struct bpf_sock_ops`, sock-ops callback flags and operation enums, TCP state constants, FIB/check-MTU structs, flow keys, BPF line/function info, lock/timer/dynptr container structs, sysctl/sockopt/sk-lookup contexts, BTF/CO-RE relocation definitions, iterator state, kfunc flags, and the final header guard.

Because this is a UAPI header, the final per-file report should emphasize ABI stability and integration contracts rather than looking for local Ceph control flow. Most behavior described here is implemented in the kernel BPF subsystem, verifier, JITs, networking stack, tracing stack, bpffs, and user-space tooling outside this header.

### subset-b-005976: lines 6944-7705

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
