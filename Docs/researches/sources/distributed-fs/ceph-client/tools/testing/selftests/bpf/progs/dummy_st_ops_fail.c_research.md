<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/dummy_st_ops_fail.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/dummy_st_ops_fail.c

## Purpose
`dummy_st_ops_fail.c` is a small eBPF selftest object used to validate verifier, helper, map, attach, or BTF behavior. It belongs to the Linux BPF selftest program corpus vendored under the Ceph client source tree, so its purpose is verifier/runtime coverage rather than Ceph production filesystem logic. The file was read completely for this note; size is 751 bytes across 27 lines.

## Important APIs, Types, and Functions
- Dependencies: `"vmlinux.h"`, `<bpf/bpf_helpers.h>`, `<bpf/bpf_tracing.h>`, `"bpf_misc.h"`.
- BPF API surface: section attach ABI, BTF metadata, return values, or declarations rather than many explicit helper calls.
Attach sections and exported entry points:
- line 10 `SEC("license")` -> int BPF_PROG(test_unsupported_field_sleepable,
- line 12 `SEC("struct_ops.s/test_2")` -> int BPF_PROG(test_unsupported_field_sleepable,
- line 22 `SEC(".struct_ops")` -> struct bpf_dummy_ops dummy_1 = {
Key functions/subprograms:
- line 13 `__msg`: `__failure __msg("attach to unsupported member test_2 of struct bpf_dummy_ops")`
- line 14 `BPF_PROG`: `int BPF_PROG(test_unsupported_field_sleepable,`

## Control Flow
User-space loads the object and attaches programs by `SEC` name. The primary runtime entry sections are `license`, `struct_ops.s/test_2`, `.struct_ops`. Each entry uses the attach-specific context, performs bounded checks or helper/kfunc calls, records result state in globals/maps when needed, and returns the expected verifier/runtime verdict for that attach type.
Local flow is organized through `__msg`, `BPF_PROG`. Error returns are generally checked immediately because verifier tests rely on precise path state and reference lifetime accounting.

## State and Persistence Behavior
No obvious mutable scalar globals were found; state is stack-local, attach-context-local, or represented as type metadata.

## Dependencies and Integration Points
- Linux BPF selftest skeleton/loading code selects programs by section/function name and reads BSS/map state after triggering the relevant kernel path.
- Kernel verifier, BTF IDs, helper/kfunc availability, and program-type-specific context rules are part of the API contract.

## Risks and Edge Cases
- Expected verifier failures/messages are part of the test contract; diagnostic text and annotation drift can break the harness.

## Test Signals
- Uses `__failure` annotations; a passing test is verifier rejection with expected diagnostics.
- Expected verifier messages include `attach to unsupported member test_2 of struct bpf_dummy_ops`.
- Runtime signal comes from attaching the listed sections, triggering the relevant syscall/socket/packet/LSM/testmod path, and reading globals/maps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/dummy_st_ops_fail.c -->
