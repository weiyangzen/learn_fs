<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/cgrp_ls_sleepable.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/cgrp_ls_sleepable.c

## Purpose
`cgrp_ls_sleepable.c` is a cgroup iterator/typed tracepoint selftest for cgroup local storage and cgroup1 lookup kfuncs. It belongs to the Linux BPF selftest program corpus vendored under the Ceph client source tree, so its purpose is verifier/runtime coverage rather than Ceph production filesystem logic. The file was read completely for this note; size is 2772 bytes across 125 lines.

## Important APIs, Types, and Functions
- Dependencies: `<vmlinux.h>`, `<bpf/bpf_helpers.h>`, `<bpf/bpf_tracing.h>`, `"bpf_misc.h"`.
- BPF API surface: task/cgroup/time/function metadata helpers; task or cgroup reference kfuncs.
- Helper/kfunc calls: `bpf_cgroup_release`, `bpf_cgrp_storage_get`, `bpf_get_current_task_btf`, `bpf_rcu_read_lock`, `bpf_rcu_read_unlock`, `bpf_task_get_cgroup1`.
Map/type declarations observed:
- line 11 declares map type `BPF_MAP_TYPE_CGRP_STORAGE`
Attach sections and exported entry points:
- line 8 `SEC("license")` -> struct {
- line 15 `SEC(".maps")` -> int target_hid;
- line 27 `SEC("?iter.s/cgroup")` -> int cgroup_iter(struct bpf_iter__cgroup *ctx)
- line 56 `SEC("SEC("?fentry.s/" SYS_PREFIX "sys_getpgid")")` -> int cgrp1_no_rcu_lock(void *ctx)
- line 76 `SEC("SEC("?fentry.s/" SYS_PREFIX "sys_getpgid")")` -> int no_rcu_lock(void *ctx)
- line 90 `SEC("SEC("?fentry.s/" SYS_PREFIX "sys_getpgid")")` -> int yes_rcu_lock(void *ctx)
Key functions/subprograms:
- line 28 `cgroup_iter`: `int cgroup_iter(struct bpf_iter__cgroup *ctx)`
- line 43 `__no_rcu_lock`: `static void __no_rcu_lock(struct cgroup *cgrp)`
- line 57 `cgrp1_no_rcu_lock`: `int cgrp1_no_rcu_lock(void *ctx)`
- line 77 `no_rcu_lock`: `int no_rcu_lock(void *ctx)`
- line 91 `yes_rcu_lock`: `int yes_rcu_lock(void *ctx)`

## Control Flow
User-space loads the object and attaches programs by `SEC` name. The primary runtime entry sections are `license`, `.maps`, `?iter.s/cgroup`, `SEC("?fentry.s/" SYS_PREFIX "sys_getpgid")`, `SEC("?fentry.s/" SYS_PREFIX "sys_getpgid")`, `SEC("?fentry.s/" SYS_PREFIX "sys_getpgid")`. Each entry uses the attach-specific context, performs bounded checks or helper/kfunc calls, records result state in globals/maps when needed, and returns the expected verifier/runtime verdict for that attach type.
Local flow is organized through `cgroup_iter`, `__no_rcu_lock`, `cgrp1_no_rcu_lock`, `no_rcu_lock`, `yes_rcu_lock`. Error returns are generally checked immediately because verifier tests rely on precise path state and reference lifetime accounting.

## State and Persistence Behavior
Object-local globals/BSS provide harness-visible state:
- line 17 `__s32 target_pid;`
- line 18 `__u64 cgroup_id;`
- line 19 `int target_hid;`
- line 20 `bool is_cgroup1;`
- line 31 `long *ptr;`
- line 45 `long *ptr;`
- line 95 `long *ptr;`
BPF maps persist while the object is loaded and carry fixture data, counters, callback state, program arrays, object references, or map-in-map handles between the BPF side and the user-space harness.

## Dependencies and Integration Points
- Linux BPF selftest skeleton/loading code selects programs by section/function name and reads BSS/map state after triggering the relevant kernel path.
- Kernel verifier, BTF IDs, helper/kfunc availability, and program-type-specific context rules are part of the API contract.

## Risks and Edge Cases
- The main drift risk is mismatch with the user-space selftest harness for section names, globals, maps, return codes, or expected side effects.

## Test Signals
- Runtime signal comes from attaching the listed sections, triggering the relevant syscall/socket/packet/LSM/testmod path, and reading globals/maps.
- Map contents are part of the observable state for callbacks, references, counters, or fixture data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/cgrp_ls_sleepable.c -->
