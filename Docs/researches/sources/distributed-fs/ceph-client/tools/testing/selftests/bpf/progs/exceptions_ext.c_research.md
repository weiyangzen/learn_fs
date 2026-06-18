<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/exceptions_ext.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/exceptions_ext.c

## Purpose
`exceptions_ext.c` is a BPF exception selftest for throw, unwind, assertion, callback, and verifier-rejection semantics. It belongs to the Linux BPF selftest program corpus vendored under the Ceph client source tree, so its purpose is verifier/runtime coverage rather than Ceph production filesystem logic. The file was read completely for this note; size is 940 bytes across 72 lines.

## Important APIs, Types, and Functions
- Dependencies: `<vmlinux.h>`, `<bpf/bpf_helpers.h>`, `"bpf_experimental.h"`.
- BPF API surface: exception unwinding.
- Helper/kfunc calls: `bpf_throw`.
Attach sections and exported entry points:
- line 6 `SEC("?fentry")` -> int pfentry(void *ctx)
- line 12 `SEC("?fentry")` -> int throwing_fentry(void *ctx)
- line 24 `SEC("?freplace")` -> int extension(struct __sk_buff *ctx)
- line 30 `SEC("?freplace")` -> int throwing_exception_cb_extension(u64 cookie)
- line 38 `SEC("?freplace")` -> int throwing_extension(struct __sk_buff *ctx)
- line 46 `SEC("?fexit")` -> int pfexit(void *ctx)
- line 52 `SEC("?fexit")` -> int throwing_fexit(void *ctx)
- line 59 `SEC("?fmod_ret")` -> int pfmod_ret(void *ctx)
- line 65 `SEC("?fmod_ret")` -> int throwing_fmod_ret(void *ctx)
- line 72 `SEC("license")` -> next declaration
Key functions/subprograms:
- line 7 `pfentry`: `int pfentry(void *ctx)`
- line 13 `throwing_fentry`: `int throwing_fentry(void *ctx)`
- line 19 `exception_cb`: `__noinline int exception_cb(u64 cookie)`
- line 25 `extension`: `int extension(struct __sk_buff *ctx)`
- line 32 `throwing_exception_cb_extension`: `int throwing_exception_cb_extension(u64 cookie)`
- line 40 `throwing_extension`: `int throwing_extension(struct __sk_buff *ctx)`
- line 47 `pfexit`: `int pfexit(void *ctx)`
- line 53 `throwing_fexit`: `int throwing_fexit(void *ctx)`
- line 60 `pfmod_ret`: `int pfmod_ret(void *ctx)`
- line 66 `throwing_fmod_ret`: `int throwing_fmod_ret(void *ctx)`

## Control Flow
User-space loads the object and attaches programs by `SEC` name. The primary runtime entry sections are `?fentry`, `?fentry`, `?freplace`, `?freplace`, `?freplace`, `?fexit`, `?fexit`, `?fmod_ret` and additional sections. Each entry uses the attach-specific context, performs bounded checks or helper/kfunc calls, records result state in globals/maps when needed, and returns the expected verifier/runtime verdict for that attach type.
Local flow is organized through `pfentry`, `throwing_fentry`, `exception_cb`, `extension`, `throwing_exception_cb_extension`, `throwing_extension`, `pfexit`, `throwing_fexit` and related helper subprograms. Error returns are generally checked immediately because verifier tests rely on precise path state and reference lifetime accounting.
Exception paths deliberately leave normal fall-through through `bpf_throw`, so expected behavior includes unwind/default-return handling as well as rejection in unsafe contexts.

## State and Persistence Behavior
No obvious mutable scalar globals were found; state is stack-local, attach-context-local, or represented as type metadata.

## Dependencies and Integration Points
- Linux BPF selftest skeleton/loading code selects programs by section/function name and reads BSS/map state after triggering the relevant kernel path.
- Kernel verifier, BTF IDs, helper/kfunc availability, and program-type-specific context rules are part of the API contract.
- Packet contexts (`tc`, `xdp`, `lwt`, cgroup skb) make data/meta bounds and return codes verifier-sensitive.

## Risks and Edge Cases
- Exception cases are sensitive to lock, RCU, preemption, IRQ, callback, and reference-lifetime restrictions.

## Test Signals
- Runtime signal comes from attaching the listed sections, triggering the relevant syscall/socket/packet/LSM/testmod path, and reading globals/maps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/exceptions_ext.c -->
