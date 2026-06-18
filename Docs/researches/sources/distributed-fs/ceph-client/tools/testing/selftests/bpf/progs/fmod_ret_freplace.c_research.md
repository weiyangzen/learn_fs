<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/fmod_ret_freplace.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/fmod_ret_freplace.c

## Purpose
`fmod_ret_freplace.c` is a BPF-to-BPF function replacement or modify-return selftest checking target signature and attach behavior. It belongs to the Linux BPF selftest program corpus vendored under the Ceph client source tree, so its purpose is verifier/runtime coverage rather than Ceph production filesystem logic. The file was read completely for this note; size is 319 bytes across 14 lines.

## Important APIs, Types, and Functions
- Dependencies: `<linux/bpf.h>`, `<bpf/bpf_helpers.h>`, `<bpf/bpf_tracing.h>`.
- BPF API surface: section attach ABI, BTF metadata, return values, or declarations rather than many explicit helper calls.
Attach sections and exported entry points:
- line 7 `SEC("fmod_ret/security_new_get_constant")` -> int BPF_PROG(fmod_ret_test, long val, int ret)
- line 14 `SEC("license")` -> next declaration
Key functions/subprograms:
- line 8 `BPF_PROG`: `int BPF_PROG(fmod_ret_test, long val, int ret)`

## Control Flow
User-space loads the object and attaches programs by `SEC` name. The primary runtime entry sections are `fmod_ret/security_new_get_constant`, `license`. Each entry uses the attach-specific context, performs bounded checks or helper/kfunc calls, records result state in globals/maps when needed, and returns the expected verifier/runtime verdict for that attach type.
Local flow is organized through `BPF_PROG`. Error returns are generally checked immediately because verifier tests rely on precise path state and reference lifetime accounting.

## State and Persistence Behavior
Object-local globals/BSS provide harness-visible state:
- line 6 `volatile __u64 test_fmod_ret = 0;`

## Dependencies and Integration Points
- Linux BPF selftest skeleton/loading code selects programs by section/function name and reads BSS/map state after triggering the relevant kernel path.
- Kernel verifier, BTF IDs, helper/kfunc availability, and program-type-specific context rules are part of the API contract.

## Risks and Edge Cases
- The main drift risk is mismatch with the user-space selftest harness for section names, globals, maps, return codes, or expected side effects.

## Test Signals
- Runtime signal comes from attaching the listed sections, triggering the relevant syscall/socket/packet/LSM/testmod path, and reading globals/maps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/fmod_ret_freplace.c -->
