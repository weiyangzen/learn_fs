<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/fexit_sleep.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/fexit_sleep.c

## Purpose
`fexit_sleep.c` is an fexit tracing selftest validating return-value and BPF-to-BPF instrumentation behavior. It belongs to the Linux BPF selftest program corpus vendored under the Ceph client source tree, so its purpose is verifier/runtime coverage rather than Ceph production filesystem logic. The file was read completely for this note; size is 589 bytes across 32 lines.

## Important APIs, Types, and Functions
- Dependencies: `"vmlinux.h"`, `<bpf/bpf_helpers.h>`, `<bpf/bpf_tracing.h>`, `"bpf_misc.h"`.
- BPF API surface: task/cgroup/time/function metadata helpers.
- Helper/kfunc calls: `bpf_get_current_pid_tgid`.
Attach sections and exported entry points:
- line 8 `SEC("license")` -> int pid = 0;
- line 14 `SEC("SEC("fentry/" SYS_PREFIX "sys_nanosleep")")` -> int nanosleep_fentry(void *ctx)
- line 24 `SEC("SEC("fexit/" SYS_PREFIX "sys_nanosleep")")` -> int nanosleep_fexit(void *ctx)
Key functions/subprograms:
- line 15 `nanosleep_fentry`: `int nanosleep_fentry(void *ctx)`
- line 25 `nanosleep_fexit`: `int nanosleep_fexit(void *ctx)`

## Control Flow
User-space loads the object and attaches programs by `SEC` name. The primary runtime entry sections are `license`, `SEC("fentry/" SYS_PREFIX "sys_nanosleep")`, `SEC("fexit/" SYS_PREFIX "sys_nanosleep")`. Each entry uses the attach-specific context, performs bounded checks or helper/kfunc calls, records result state in globals/maps when needed, and returns the expected verifier/runtime verdict for that attach type.
Local flow is organized through `nanosleep_fentry`, `nanosleep_fexit`. Error returns are generally checked immediately because verifier tests rely on precise path state and reference lifetime accounting.

## State and Persistence Behavior
Object-local globals/BSS provide harness-visible state:
- line 10 `int pid = 0;`
- line 11 `int fentry_cnt = 0;`
- line 12 `int fexit_cnt = 0;`

## Dependencies and Integration Points
- Linux BPF selftest skeleton/loading code selects programs by section/function name and reads BSS/map state after triggering the relevant kernel path.
- Kernel verifier, BTF IDs, helper/kfunc availability, and program-type-specific context rules are part of the API contract.

## Risks and Edge Cases
- The main drift risk is mismatch with the user-space selftest harness for section names, globals, maps, return codes, or expected side effects.

## Test Signals
- Runtime signal comes from attaching the listed sections, triggering the relevant syscall/socket/packet/LSM/testmod path, and reading globals/maps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/fexit_sleep.c -->
