<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/connect_unix_prog.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/connect_unix_prog.c

## Purpose
`connect_unix_prog.c` is a cgroup socket-address selftest that rewrites, denies, binds, or probes connect-time socket fields. It belongs to the Linux BPF selftest program corpus vendored under the Ceph client source tree, so its purpose is verifier/runtime coverage rather than Ceph production filesystem logic. The file was read completely for this note; size is 1136 bytes across 45 lines.

## Important APIs, Types, and Functions
- Dependencies: `"vmlinux.h"`, `<string.h>`, `<bpf/bpf_helpers.h>`, `<bpf/bpf_core_read.h>`, `"bpf_kfuncs.h"`.
- BPF API surface: socket option/address helpers.
- Helper/kfunc calls: `bpf_cast_to_kern_ctx`, `bpf_core_cast`, `bpf_sock_addr_set_sun_path`.
Attach sections and exported entry points:
- line 13 `SEC("cgroup/connect_unix")` -> int connect_unix_prog(struct bpf_sock_addr *ctx)
- line 39 `SEC("cgroup/connect_unix")` -> int connect_unix_deny_prog(struct bpf_sock_addr *ctx)
- line 45 `SEC("license")` -> next declaration
Key functions/subprograms:
- line 14 `connect_unix_prog`: `int connect_unix_prog(struct bpf_sock_addr *ctx)`
- line 40 `connect_unix_deny_prog`: `int connect_unix_deny_prog(struct bpf_sock_addr *ctx)`

## Control Flow
User-space loads the object and attaches programs by `SEC` name. The primary runtime entry sections are `cgroup/connect_unix`, `cgroup/connect_unix`, `license`. Each entry uses the attach-specific context, performs bounded checks or helper/kfunc calls, records result state in globals/maps when needed, and returns the expected verifier/runtime verdict for that attach type.
Local flow is organized through `connect_unix_prog`, `connect_unix_deny_prog`. Error returns are generally checked immediately because verifier tests rely on precise path state and reference lifetime accounting.

## State and Persistence Behavior
Object-local globals/BSS provide harness-visible state:
- line 11 `__u8 SERVUN_REWRITE_ADDRESS[] = "\0bpf_cgroup_unix_test_rewrite";`
- line 20 `int ret;`

## Dependencies and Integration Points
- Linux BPF selftest skeleton/loading code selects programs by section/function name and reads BSS/map state after triggering the relevant kernel path.
- Kernel verifier, BTF IDs, helper/kfunc availability, and program-type-specific context rules are part of the API contract.
- Cgroup attach points require a prepared cgroup and are observed through socket or packet operations.

## Risks and Edge Cases
- Socket address rewrites must preserve network byte order and only touch fields valid for the attach type and family.

## Test Signals
- Runtime signal comes from attaching the listed sections, triggering the relevant syscall/socket/packet/LSM/testmod path, and reading globals/maps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/connect_unix_prog.c -->
