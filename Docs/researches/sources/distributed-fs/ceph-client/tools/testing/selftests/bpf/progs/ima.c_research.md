<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/ima.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/ima.c

## Purpose
`ima.c` is a sleepable BPF LSM/IMA selftest for file hash measurement and optional deny behavior. It belongs to the Linux BPF selftest program corpus vendored under the Ceph client source tree, so its purpose is verifier/runtime coverage rather than Ceph production filesystem logic. The file was read completely for this note; size is 1822 bytes across 103 lines.

## Important APIs, Types, and Functions
- Dependencies: `"vmlinux.h"`, `<errno.h>`, `<bpf/bpf_helpers.h>`, `<bpf/bpf_tracing.h>`.
- BPF API surface: task/cgroup/time/function metadata helpers.
- Helper/kfunc calls: `bpf_get_current_pid_tgid`, `bpf_ima_file_hash`, `bpf_ima_inode_hash`, `bpf_ringbuf_reserve`, `bpf_ringbuf_submit`.
Map/type declarations observed:
- line 15 declares map type `BPF_MAP_TYPE_RINGBUF`
Attach sections and exported entry points:
- line 17 `SEC(".maps")` -> bool use_ima_file_hash;
- line 19 `SEC("license")` -> bool use_ima_file_hash;
- line 66 `SEC("lsm.s/bprm_committed_creds")` -> void BPF_PROG(bprm_committed_creds, struct linux_binprm *bprm)
- line 72 `SEC("lsm.s/bprm_creds_for_exec")` -> int BPF_PROG(bprm_creds_for_exec, struct linux_binprm *bprm)
- line 82 `SEC("lsm.s/kernel_read_file")` -> int BPF_PROG(kernel_read_file, struct file *file, enum kernel_read_file_id id,
Key functions/subprograms:
- line 26 `ima_test_common`: `static void ima_test_common(struct file *file)`
- line 55 `ima_test_deny`: `static int ima_test_deny(void)`
- line 67 `BPF_PROG`: `void BPF_PROG(bprm_committed_creds, struct linux_binprm *bprm)`
- line 73 `BPF_PROG`: `int BPF_PROG(bprm_creds_for_exec, struct linux_binprm *bprm)`
- line 83 `BPF_PROG`: `int BPF_PROG(kernel_read_file, struct file *file, enum kernel_read_file_id id,`

## Control Flow
User-space loads the object and attaches programs by `SEC` name. The primary runtime entry sections are `.maps`, `license`, `lsm.s/bprm_committed_creds`, `lsm.s/bprm_creds_for_exec`, `lsm.s/kernel_read_file`. Each entry uses the attach-specific context, performs bounded checks or helper/kfunc calls, records result state in globals/maps when needed, and returns the expected verifier/runtime verdict for that attach type.
Local flow is organized through `ima_test_common`, `ima_test_deny`, `BPF_PROG`, `BPF_PROG`, `BPF_PROG`. Error returns are generally checked immediately because verifier tests rely on precise path state and reference lifetime accounting.

## State and Persistence Behavior
Object-local globals/BSS provide harness-visible state:
- line 12 `u32 monitored_pid = 0;`
- line 21 `bool use_ima_file_hash;`
- line 22 `bool enable_bprm_creds_for_exec;`
- line 23 `bool enable_kernel_read_file;`
- line 24 `bool test_deny;`
- line 28 `u64 ima_hash = 0;`
- line 29 `u64 *sample;`
- line 30 `int ret;`
- line 31 `u32 pid;`
- line 57 `u32 pid;`
- plus 1 more entries of the same pattern.
BPF maps persist while the object is loaded and carry fixture data, counters, callback state, program arrays, object references, or map-in-map handles between the BPF side and the user-space harness.

## Dependencies and Integration Points
- Linux BPF selftest skeleton/loading code selects programs by section/function name and reads BSS/map state after triggering the relevant kernel path.
- Kernel verifier, BTF IDs, helper/kfunc availability, and program-type-specific context rules are part of the API contract.
- BPF LSM hooks may require sleepable attachment and kernel security/IMA configuration.

## Risks and Edge Cases
- The main drift risk is mismatch with the user-space selftest harness for section names, globals, maps, return codes, or expected side effects.

## Test Signals
- Runtime signal comes from attaching the listed sections, triggering the relevant syscall/socket/packet/LSM/testmod path, and reading globals/maps.
- Map contents are part of the observable state for callbacks, references, counters, or fixture data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/ima.c -->
