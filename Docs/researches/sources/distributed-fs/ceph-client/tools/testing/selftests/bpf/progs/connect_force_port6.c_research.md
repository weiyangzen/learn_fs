<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/connect_force_port6.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/connect_force_port6.c

## Purpose
`connect_force_port6.c` is a cgroup socket-address selftest that rewrites, denies, binds, or probes connect-time socket fields. It belongs to the Linux BPF selftest program corpus vendored under the Ceph client source tree, so its purpose is verifier/runtime coverage rather than Ceph production filesystem logic. The file was read completely for this note; size is 2356 bytes across 103 lines.

## Important APIs, Types, and Functions
- Dependencies: `<string.h>`, `<linux/bpf.h>`, `<linux/in.h>`, `<linux/in6.h>`, `<sys/socket.h>`, `<bpf/bpf_helpers.h>`, `<bpf/bpf_endian.h>`, `<bpf_sockopt_helpers.h>`.
- BPF API surface: section attach ABI, BTF metadata, return values, or declarations rather than many explicit helper calls.
- Helper/kfunc calls: `bpf_bind`, `bpf_htonl`, `bpf_htons`, `bpf_sk_storage_get`.
Map/type declarations observed:
- line 24 declares map type `BPF_MAP_TYPE_SK_STORAGE`
Attach sections and exported entry points:
- line 14 `SEC("license")` -> struct svc_addr {
- line 28 `SEC(".maps")` -> int connect6(struct bpf_sock_addr *ctx)
- line 30 `SEC("cgroup/connect6")` -> int connect6(struct bpf_sock_addr *ctx)
- line 66 `SEC("cgroup/getsockname6")` -> int getsockname6(struct bpf_sock_addr *ctx)
- line 83 `SEC("cgroup/getpeername6")` -> int getpeername6(struct bpf_sock_addr *ctx)
Key functions/subprograms:
- line 31 `connect6`: `int connect6(struct bpf_sock_addr *ctx)`
- line 67 `getsockname6`: `int getsockname6(struct bpf_sock_addr *ctx)`
- line 84 `getpeername6`: `int getpeername6(struct bpf_sock_addr *ctx)`

## Control Flow
User-space loads the object and attaches programs by `SEC` name. The primary runtime entry sections are `license`, `.maps`, `cgroup/connect6`, `cgroup/getsockname6`, `cgroup/getpeername6`. Each entry uses the attach-specific context, performs bounded checks or helper/kfunc calls, records result state in globals/maps when needed, and returns the expected verifier/runtime verdict for that attach type.
Local flow is organized through `connect6`, `getsockname6`, `getpeername6`. Error returns are generally checked immediately because verifier tests rely on precise path state and reference lifetime accounting.

## State and Persistence Behavior
Object-local globals/BSS provide harness-visible state:
- line 16 `__u16 port = 0;`
BPF maps persist while the object is loaded and carry fixture data, counters, callback state, program arrays, object references, or map-in-map handles between the BPF side and the user-space harness.

## Dependencies and Integration Points
- Linux BPF selftest skeleton/loading code selects programs by section/function name and reads BSS/map state after triggering the relevant kernel path.
- Kernel verifier, BTF IDs, helper/kfunc availability, and program-type-specific context rules are part of the API contract.
- Cgroup attach points require a prepared cgroup and are observed through socket or packet operations.

## Risks and Edge Cases
- Socket address rewrites must preserve network byte order and only touch fields valid for the attach type and family.

## Test Signals
- Runtime signal comes from attaching the listed sections, triggering the relevant syscall/socket/packet/LSM/testmod path, and reading globals/maps.
- Map contents are part of the observable state for callbacks, references, counters, or fixture data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/connect_force_port6.c -->
