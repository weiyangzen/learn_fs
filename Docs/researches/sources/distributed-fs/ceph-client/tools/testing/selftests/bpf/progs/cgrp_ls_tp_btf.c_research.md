<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/cgrp_ls_tp_btf.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/cgrp_ls_tp_btf.c

## Purpose
`cgrp_ls_tp_btf.c` is a cgroup iterator/typed tracepoint selftest for cgroup local storage and cgroup1 lookup kfuncs. It belongs to the Linux BPF selftest program corpus vendored under the Ceph client source tree, so its purpose is verifier/runtime coverage rather than Ceph production filesystem logic. The file was read completely for this note; size is 2644 bytes across 126 lines.

## Important APIs, Types, and Functions
- Dependencies: `"vmlinux.h"`, `<bpf/bpf_helpers.h>`, `<bpf/bpf_tracing.h>`.
- Important macros/constants: `MAGIC_VALUE`.
- BPF API surface: task/cgroup/time/function metadata helpers; task or cgroup reference kfuncs.
- Helper/kfunc calls: `bpf_cgroup_release`, `bpf_cgrp_storage_delete`, `bpf_cgrp_storage_get`, `bpf_get_current_task_btf`, `bpf_task_get_cgroup1`.
Map/type declarations observed:
- line 11 declares map type `BPF_MAP_TYPE_CGRP_STORAGE`
- line 18 declares map type `BPF_MAP_TYPE_CGRP_STORAGE`
Attach sections and exported entry points:
- line 8 `SEC("license")` -> struct {
- line 15 `SEC(".maps")` -> struct {
- line 22 `SEC(".maps")` -> #define MAGIC_VALUE 0xabcd1234
- line 66 `SEC("tp_btf/sys_enter")` -> int BPF_PROG(on_enter, struct pt_regs *regs, long id)
- line 104 `SEC("tp_btf/sys_exit")` -> int BPF_PROG(on_exit, struct pt_regs *regs, long id)
Key functions/subprograms:
- line 36 `__on_enter`: `static void __on_enter(struct pt_regs *regs, long id, struct cgroup *cgrp)`
- line 67 `BPF_PROG`: `int BPF_PROG(on_enter, struct pt_regs *regs, long id)`
- line 90 `__on_exit`: `static void __on_exit(struct pt_regs *regs, long id, struct cgroup *cgrp)`
- line 105 `BPF_PROG`: `int BPF_PROG(on_exit, struct pt_regs *regs, long id)`

## Control Flow
User-space loads the object and attaches programs by `SEC` name. The primary runtime entry sections are `license`, `.maps`, `.maps`, `tp_btf/sys_enter`, `tp_btf/sys_exit`. Each entry uses the attach-specific context, performs bounded checks or helper/kfunc calls, records result state in globals/maps when needed, and returns the expected verifier/runtime verdict for that attach type.
Local flow is organized through `__on_enter`, `BPF_PROG`, `__on_exit`, `BPF_PROG`. Error returns are generally checked immediately because verifier tests rely on precise path state and reference lifetime accounting.

## State and Persistence Behavior
Object-local globals/BSS provide harness-visible state:
- line 27 `int mismatch_cnt = 0;`
- line 28 `int enter_cnt = 0;`
- line 29 `int exit_cnt = 0;`
- line 30 `int target_hid = 0;`
- line 31 `bool is_cgroup1 = 0;`
- line 38 `long *ptr;`
- line 39 `int err;`
- line 92 `long *ptr;`
BPF maps persist while the object is loaded and carry fixture data, counters, callback state, program arrays, object references, or map-in-map handles between the BPF side and the user-space harness.

## Dependencies and Integration Points
- Linux BPF selftest skeleton/loading code selects programs by section/function name and reads BSS/map state after triggering the relevant kernel path.
- Kernel verifier, BTF IDs, helper/kfunc availability, and program-type-specific context rules are part of the API contract.

## Risks and Edge Cases
- The main drift risk is mismatch with the user-space selftest harness for section names, globals, maps, return codes, or expected side effects.

## Test Signals
- Runtime signal comes from attaching the listed sections, triggering the relevant syscall/socket/packet/LSM/testmod path, and reading globals/maps.
- Map contents are part of the observable state for callbacks, references, counters, or fixture data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/cgrp_ls_tp_btf.c -->
