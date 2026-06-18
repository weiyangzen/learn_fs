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
