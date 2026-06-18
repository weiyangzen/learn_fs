<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/connect4_prog.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/connect4_prog.c

## Purpose
`connect4_prog.c` is a cgroup socket-address selftest that rewrites, denies, binds, or probes connect-time socket fields. It belongs to the Linux BPF selftest program corpus vendored under the Ceph client source tree, so its purpose is verifier/runtime coverage rather than Ceph production filesystem logic. The file was read completely for this note; size is 4577 bytes across 203 lines.

## Important APIs, Types, and Functions
- Dependencies: `<string.h>`, `<linux/stddef.h>`, `<linux/bpf.h>`, `<linux/in.h>`, `<linux/in6.h>`, `<linux/tcp.h>`, `<linux/if.h>`, `<errno.h>`, `<bpf/bpf_helpers.h>`, `<bpf/bpf_endian.h>`.
- Important macros/constants: `SRC_REWRITE_IP4`, `DST_REWRITE_IP4`, `DST_REWRITE_PORT4`, `TCP_CA_NAME_MAX`, `TCP_NOTSENT_LOWAT`, `IFNAMSIZ`, `SOL_TCP`.
- BPF API surface: section attach ABI, BTF metadata, return values, or declarations rather than many explicit helper calls.
- Helper/kfunc calls: `bpf_bind`, `bpf_getsockopt`, `bpf_htonl`, `bpf_htons`, `bpf_setsockopt`, `bpf_sk_lookup_tcp`, `bpf_sk_lookup_udp`, `bpf_sk_release`, `bpf_strncmp`.
Attach sections and exported entry points:
- line 143 `SEC("cgroup/connect4")` -> int connect_v4_prog(struct bpf_sock_addr *ctx)
- line 197 `SEC("cgroup/connect4")` -> int connect_v4_deny_prog(struct bpf_sock_addr *ctx)
- line 203 `SEC("license")` -> next declaration
Key functions/subprograms:
- line 41 `do_bind`: `int do_bind(struct bpf_sock_addr *ctx)`
- line 55 `verify_cc`: `static __inline int verify_cc(struct bpf_sock_addr *ctx,`
- line 69 `set_cc`: `static __inline int set_cc(struct bpf_sock_addr *ctx)`
- line 84 `bind_to_device`: `static __inline int bind_to_device(struct bpf_sock_addr *ctx)`
- line 107 `set_keepalive`: `static __inline int set_keepalive(struct bpf_sock_addr *ctx)`
- line 131 `set_notsent_lowat`: `static __inline int set_notsent_lowat(struct bpf_sock_addr *ctx)`
- line 144 `connect_v4_prog`: `int connect_v4_prog(struct bpf_sock_addr *ctx)`
- line 198 `connect_v4_deny_prog`: `int connect_v4_deny_prog(struct bpf_sock_addr *ctx)`

## Control Flow
User-space loads the object and attaches programs by `SEC` name. The primary runtime entry sections are `cgroup/connect4`, `cgroup/connect4`, `license`. Each entry uses the attach-specific context, performs bounded checks or helper/kfunc calls, records result state in globals/maps when needed, and returns the expected verifier/runtime verdict for that attach type.
Local flow is organized through `do_bind`, `verify_cc`, `set_cc`, `bind_to_device`, `set_keepalive`, `set_notsent_lowat`, `connect_v4_prog`, `connect_v4_deny_prog`. Error returns are generally checked immediately because verifier tests rely on precise path state and reference lifetime accounting.

## State and Persistence Behavior
Object-local globals/BSS provide harness-visible state:
- line 58 `char buf[TCP_CA_NAME_MAX];`
- line 86 `char veth1[IFNAMSIZ] = "test_sock_addr1";`
- line 87 `char veth2[IFNAMSIZ] = "test_sock_addr2";`
- line 88 `char missing[IFNAMSIZ] = "nonexistent_dev";`
- line 89 `char del_bind[IFNAMSIZ] = "";`
- line 109 `int zero = 0, one = 1;`
- line 133 `int lowat = 65535;`

## Dependencies and Integration Points
- Linux BPF selftest skeleton/loading code selects programs by section/function name and reads BSS/map state after triggering the relevant kernel path.
- Kernel verifier, BTF IDs, helper/kfunc availability, and program-type-specific context rules are part of the API contract.
- Cgroup attach points require a prepared cgroup and are observed through socket or packet operations.

## Risks and Edge Cases
- Socket address rewrites must preserve network byte order and only touch fields valid for the attach type and family.

## Test Signals
- Runtime signal comes from attaching the listed sections, triggering the relevant syscall/socket/packet/LSM/testmod path, and reading globals/maps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/connect4_prog.c -->
