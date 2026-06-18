<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/dummy_st_ops_success.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/dummy_st_ops_success.c

## Purpose
`dummy_st_ops_success.c` is a small eBPF selftest object used to validate verifier, helper, map, attach, or BTF behavior. It belongs to the Linux BPF selftest program corpus vendored under the Ceph client source tree, so its purpose is verifier/runtime coverage rather than Ceph production filesystem logic. The file was read completely for this note; size is 1311 bytes across 56 lines.

## Important APIs, Types, and Functions
- Dependencies: `"vmlinux.h"`, `<bpf/bpf_helpers.h>`, `<bpf/bpf_tracing.h>`.
- BPF API surface: section attach ABI, BTF metadata, return values, or declarations rather than many explicit helper calls.
Attach sections and exported entry points:
- line 7 `SEC("license")` -> int BPF_PROG(test_1, struct bpf_dummy_ops_state *state)
- line 9 `SEC("struct_ops/test_1")` -> int BPF_PROG(test_1, struct bpf_dummy_ops_state *state)
- line 33 `SEC("struct_ops/test_2")` -> int BPF_PROG(test_2, struct bpf_dummy_ops_state *state, int a1, unsigned short a2,
- line 45 `SEC("struct_ops.s/test_sleepable")` -> int BPF_PROG(test_sleepable, struct bpf_dummy_ops_state *state)
- line 51 `SEC(".struct_ops")` -> struct bpf_dummy_ops dummy_1 = {
Key functions/subprograms:
- line 10 `BPF_PROG`: `int BPF_PROG(test_1, struct bpf_dummy_ops_state *state)`
- line 20 `volatile`: `asm volatile (`
- line 34 `BPF_PROG`: `int BPF_PROG(test_2, struct bpf_dummy_ops_state *state, int a1, unsigned short a2,`
- line 46 `BPF_PROG`: `int BPF_PROG(test_sleepable, struct bpf_dummy_ops_state *state)`

## Control Flow
User-space loads the object and attaches programs by `SEC` name. The primary runtime entry sections are `license`, `struct_ops/test_1`, `struct_ops/test_2`, `struct_ops.s/test_sleepable`, `.struct_ops`. Each entry uses the attach-specific context, performs bounded checks or helper/kfunc calls, records result state in globals/maps when needed, and returns the expected verifier/runtime verdict for that attach type.
Local flow is organized through `BPF_PROG`, `volatile`, `BPF_PROG`, `BPF_PROG`. Error returns are generally checked immediately because verifier tests rely on precise path state and reference lifetime accounting.

## State and Persistence Behavior
Object-local globals/BSS provide harness-visible state:
- line 12 `int ret;`
- line 31 `__u64 test_2_args[5];`

## Dependencies and Integration Points
- Linux BPF selftest skeleton/loading code selects programs by section/function name and reads BSS/map state after triggering the relevant kernel path.
- Kernel verifier, BTF IDs, helper/kfunc availability, and program-type-specific context rules are part of the API contract.

## Risks and Edge Cases
- The main drift risk is mismatch with the user-space selftest harness for section names, globals, maps, return codes, or expected side effects.

## Test Signals
- Runtime signal comes from attaching the listed sections, triggering the relevant syscall/socket/packet/LSM/testmod path, and reading globals/maps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/dummy_st_ops_success.c -->
