<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/connect6_prog.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/connect6_prog.c

## Purpose
`connect6_prog.c` is a cgroup socket-address selftest that rewrites, denies, binds, or probes connect-time socket fields. It belongs to the Linux BPF selftest program corpus vendored under the Ceph client source tree, so its purpose is verifier/runtime coverage rather than Ceph production filesystem logic. The file was read completely for this note; size is 2563 bytes across 99 lines.

## Important APIs, Types, and Functions
- Dependencies: `<string.h>`, `<linux/stddef.h>`, `<linux/bpf.h>`, `<linux/in.h>`, `<linux/in6.h>`, `<sys/socket.h>`, `<bpf/bpf_helpers.h>`, `<bpf/bpf_endian.h>`.
- Important macros/constants: `SRC_REWRITE_IP6_0`, `SRC_REWRITE_IP6_1`, `SRC_REWRITE_IP6_2`, `SRC_REWRITE_IP6_3`, `DST_REWRITE_IP6_0`, `DST_REWRITE_IP6_1`, `DST_REWRITE_IP6_2`, `DST_REWRITE_IP6_3`, `DST_REWRITE_PORT6`.
- BPF API surface: section attach ABI, BTF metadata, return values, or declarations rather than many explicit helper calls.
- Helper/kfunc calls: `bpf_bind`, `bpf_htonl`, `bpf_htons`, `bpf_sk_lookup_tcp`, `bpf_sk_lookup_udp`, `bpf_sk_release`.
Attach sections and exported entry points:
- line 27 `SEC("cgroup/connect6")` -> int connect_v6_prog(struct bpf_sock_addr *ctx)
- line 93 `SEC("cgroup/connect6")` -> int connect_v6_deny_prog(struct bpf_sock_addr *ctx)
- line 99 `SEC("license")` -> next declaration
Key functions/subprograms:
- line 28 `connect_v6_prog`: `int connect_v6_prog(struct bpf_sock_addr *ctx)`
- line 94 `connect_v6_deny_prog`: `int connect_v6_deny_prog(struct bpf_sock_addr *ctx)`

## Control Flow
User-space loads the object and attaches programs by `SEC` name. The primary runtime entry sections are `cgroup/connect6`, `cgroup/connect6`, `license`. Each entry uses the attach-specific context, performs bounded checks or helper/kfunc calls, records result state in globals/maps when needed, and returns the expected verifier/runtime verdict for that attach type.
Local flow is organized through `connect_v6_prog`, `connect_v6_deny_prog`. Error returns are generally checked immediately because verifier tests rely on precise path state and reference lifetime accounting.

## State and Persistence Behavior
No obvious mutable scalar globals were found; state is stack-local, attach-context-local, or represented as type metadata.

## Dependencies and Integration Points
- Linux BPF selftest skeleton/loading code selects programs by section/function name and reads BSS/map state after triggering the relevant kernel path.
- Kernel verifier, BTF IDs, helper/kfunc availability, and program-type-specific context rules are part of the API contract.
- Cgroup attach points require a prepared cgroup and are observed through socket or packet operations.

## Risks and Edge Cases
- Socket address rewrites must preserve network byte order and only touch fields valid for the attach type and family.

## Test Signals
- Runtime signal comes from attaching the listed sections, triggering the relevant syscall/socket/packet/LSM/testmod path, and reading globals/maps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/connect6_prog.c -->
