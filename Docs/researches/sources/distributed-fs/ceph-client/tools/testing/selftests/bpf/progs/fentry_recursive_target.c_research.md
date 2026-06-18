<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/fentry_recursive_target.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/fentry_recursive_target.c

## Purpose
`fentry_recursive_target.c` is an fentry tracing selftest validating typed argument capture and recursion behavior. It belongs to the Linux BPF selftest program corpus vendored under the Ceph client source tree, so its purpose is verifier/runtime coverage rather than Ceph production filesystem logic. The file was read completely for this note; size is 578 bytes across 25 lines.

## Important APIs, Types, and Functions
- Dependencies: `<linux/bpf.h>`, `<bpf/bpf_helpers.h>`, `<bpf/bpf_tracing.h>`.
- BPF API surface: section attach ABI, BTF metadata, return values, or declarations rather than many explicit helper calls.
Attach sections and exported entry points:
- line 7 `SEC("license")` -> /* Dummy fentry bpf prog for testing fentry attachment chains. It's going to be
- line 12 `SEC("fentry/bpf_testmod_fentry_test1")` -> int BPF_PROG(test1, int a)
- line 21 `SEC("raw_tp/sys_enter")` -> int BPF_PROG(fentry_target, struct pt_regs *regs, long id)
Key functions/subprograms:
- line 13 `BPF_PROG`: `int BPF_PROG(test1, int a)`
- line 22 `BPF_PROG`: `int BPF_PROG(fentry_target, struct pt_regs *regs, long id)`

## Control Flow
User-space loads the object and attaches programs by `SEC` name. The primary runtime entry sections are `license`, `fentry/bpf_testmod_fentry_test1`, `raw_tp/sys_enter`. Each entry uses the attach-specific context, performs bounded checks or helper/kfunc calls, records result state in globals/maps when needed, and returns the expected verifier/runtime verdict for that attach type.
Local flow is organized through `BPF_PROG`, `BPF_PROG`. Error returns are generally checked immediately because verifier tests rely on precise path state and reference lifetime accounting.

## State and Persistence Behavior
No obvious mutable scalar globals were found; state is stack-local, attach-context-local, or represented as type metadata.

## Dependencies and Integration Points
- Linux BPF selftest skeleton/loading code selects programs by section/function name and reads BSS/map state after triggering the relevant kernel path.
- Kernel verifier, BTF IDs, helper/kfunc availability, and program-type-specific context rules are part of the API contract.
- Several symbols or hooks integrate with `bpf_testmod`; the kernel test module must be available for those attach points.

## Risks and Edge Cases
- The main drift risk is mismatch with the user-space selftest harness for section names, globals, maps, return codes, or expected side effects.

## Test Signals
- Runtime signal comes from attaching the listed sections, triggering the relevant syscall/socket/packet/LSM/testmod path, and reading globals/maps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/fentry_recursive_target.c -->
