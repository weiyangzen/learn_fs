<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/getpeername4_prog.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/getpeername4_prog.c

## Purpose
`getpeername4_prog.c` is a cgroup sock_addr selftest that rewrites returned peer addresses. It belongs to the Linux BPF selftest program corpus vendored under the Ceph client source tree, so its purpose is verifier/runtime coverage rather than Ceph production filesystem logic. The file was read completely for this note; size is 558 bytes across 24 lines.

## Important APIs, Types, and Functions
- Dependencies: `"vmlinux.h"`, `<string.h>`, `<bpf/bpf_helpers.h>`, `<bpf/bpf_endian.h>`, `<bpf/bpf_core_read.h>`, `"bpf_kfuncs.h"`.
- Important macros/constants: `REWRITE_ADDRESS_IP4`, `REWRITE_ADDRESS_PORT4`.
- BPF API surface: section attach ABI, BTF metadata, return values, or declarations rather than many explicit helper calls.
- Helper/kfunc calls: `bpf_htonl`, `bpf_htons`.
Attach sections and exported entry points:
- line 15 `SEC("cgroup/getpeername4")` -> int getpeername_v4_prog(struct bpf_sock_addr *ctx)
- line 24 `SEC("license")` -> next declaration
Key functions/subprograms:
- line 16 `getpeername_v4_prog`: `int getpeername_v4_prog(struct bpf_sock_addr *ctx)`

## Control Flow
User-space loads the object and attaches programs by `SEC` name. The primary runtime entry sections are `cgroup/getpeername4`, `license`. Each entry uses the attach-specific context, performs bounded checks or helper/kfunc calls, records result state in globals/maps when needed, and returns the expected verifier/runtime verdict for that attach type.
Local flow is organized through `getpeername_v4_prog`. Error returns are generally checked immediately because verifier tests rely on precise path state and reference lifetime accounting.

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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/getpeername4_prog.c -->
