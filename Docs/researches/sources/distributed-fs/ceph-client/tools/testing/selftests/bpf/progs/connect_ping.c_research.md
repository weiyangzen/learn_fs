<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/connect_ping.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/connect_ping.c

## Purpose
`connect_ping.c` is a cgroup socket-address selftest that rewrites, denies, binds, or probes connect-time socket fields. It belongs to the Linux BPF selftest program corpus vendored under the Ceph client source tree, so its purpose is verifier/runtime coverage rather than Ceph production filesystem logic. The file was read completely for this note; size is 1056 bytes across 53 lines.

## Important APIs, Types, and Functions
- Dependencies: `<linux/bpf.h>`, `<bpf/bpf_helpers.h>`, `<bpf/bpf_endian.h>`, `<netinet/in.h>`, `<sys/socket.h>`.
- Important macros/constants: `BINDADDR_V6`.
- BPF API surface: section attach ABI, BTF metadata, return values, or declarations rather than many explicit helper calls.
- Helper/kfunc calls: `bpf_bind`, `bpf_htonl`.
Attach sections and exported entry points:
- line 21 `SEC("cgroup/connect4")` -> int connect_v4_prog(struct bpf_sock_addr *ctx)
- line 37 `SEC("cgroup/connect6")` -> int connect_v6_prog(struct bpf_sock_addr *ctx)
- line 53 `SEC("license")` -> next declaration
Key functions/subprograms:
- line 22 `connect_v4_prog`: `int connect_v4_prog(struct bpf_sock_addr *ctx)`
- line 38 `connect_v6_prog`: `int connect_v6_prog(struct bpf_sock_addr *ctx)`

## Control Flow
User-space loads the object and attaches programs by `SEC` name. The primary runtime entry sections are `cgroup/connect4`, `cgroup/connect6`, `license`. Each entry uses the attach-specific context, performs bounded checks or helper/kfunc calls, records result state in globals/maps when needed, and returns the expected verifier/runtime verdict for that attach type.
Local flow is organized through `connect_v4_prog`, `connect_v6_prog`. Error returns are generally checked immediately because verifier tests rely on precise path state and reference lifetime accounting.

## State and Persistence Behavior
Object-local globals/BSS provide harness-visible state:
- line 16 `__u32 do_bind = 0;`
- line 17 `__u32 has_error = 0;`
- line 18 `__u32 invocations_v4 = 0;`
- line 19 `__u32 invocations_v6 = 0;`

## Dependencies and Integration Points
- Linux BPF selftest skeleton/loading code selects programs by section/function name and reads BSS/map state after triggering the relevant kernel path.
- Kernel verifier, BTF IDs, helper/kfunc availability, and program-type-specific context rules are part of the API contract.
- Cgroup attach points require a prepared cgroup and are observed through socket or packet operations.

## Risks and Edge Cases
- Socket address rewrites must preserve network byte order and only touch fields valid for the attach type and family.

## Test Signals
- Runtime signal comes from attaching the listed sections, triggering the relevant syscall/socket/packet/LSM/testmod path, and reading globals/maps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/connect_ping.c -->
