<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/find_vma_fail1.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/find_vma_fail1.c

## Purpose
`find_vma_fail1.c` is a bpf_find_vma selftest checking callback behavior and verifier rejection paths. It belongs to the Linux BPF selftest program corpus vendored under the Ceph client source tree, so its purpose is verifier/runtime coverage rather than Ceph production filesystem logic. The file was read completely for this note; size is 628 bytes across 30 lines.

## Important APIs, Types, and Functions
- Dependencies: `"vmlinux.h"`, `<bpf/bpf_helpers.h>`.
- Important macros/constants: `vm_flags`.
- BPF API surface: task/cgroup/time/function metadata helpers.
- Helper/kfunc calls: `bpf_find_vma`, `bpf_get_current_task_btf`.
Attach sections and exported entry points:
- line 7 `SEC("license")` -> struct callback_ctx {
- line 22 `SEC("raw_tp/sys_enter")` -> int handle_getpid(void)
Key functions/subprograms:
- line 13 `write_vma`: `static long write_vma(struct task_struct *task, struct vm_area_struct *vma,`
- line 23 `handle_getpid`: `int handle_getpid(void)`

## Control Flow
User-space loads the object and attaches programs by `SEC` name. The primary runtime entry sections are `license`, `raw_tp/sys_enter`. Each entry uses the attach-specific context, performs bounded checks or helper/kfunc calls, records result state in globals/maps when needed, and returns the expected verifier/runtime verdict for that attach type.
Local flow is organized through `write_vma`, `handle_getpid`. Error returns are generally checked immediately because verifier tests rely on precise path state and reference lifetime accounting.

## State and Persistence Behavior
Object-local globals/BSS provide harness-visible state:
- line 10 `int dummy;`

## Dependencies and Integration Points
- Linux BPF selftest skeleton/loading code selects programs by section/function name and reads BSS/map state after triggering the relevant kernel path.
- Kernel verifier, BTF IDs, helper/kfunc availability, and program-type-specific context rules are part of the API contract.

## Risks and Edge Cases
- The main drift risk is mismatch with the user-space selftest harness for section names, globals, maps, return codes, or expected side effects.

## Test Signals
- Runtime signal comes from attaching the listed sections, triggering the relevant syscall/socket/packet/LSM/testmod path, and reading globals/maps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/find_vma_fail1.c -->
