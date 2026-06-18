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
