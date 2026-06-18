<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_vfs_reject.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_vfs_reject.c

## Purpose
This companion LSM verifier rejection suite validates that VFS kfuncs reject null, untrusted, wrongly typed, unreleased, unacquired, oversized, or disallowed-context arguments.

## Important APIs, Types, and Functions
It uses the same kfunc family as the acceptance file: `bpf_get_task_exe_file`, `bpf_put_file`, and `bpf_path_d_path`. It also uses `PATH_MAX` for an intentionally oversized buffer-size test and `BPF_PROG` for typed LSM/fentry signatures.

## Control Flow
Programs pass null or stack-cast task pointers to `bpf_get_task_exe_file`, walk from a trusted task to an untrusted parent, leak an acquired file reference, release an unacquired `struct file *`, pass null/untrusted/type-mismatched paths to `bpf_path_d_path`, supply a size larger than the static buffer, call an LSM-only kfunc from fentry, and dereference a nullable `d_inode` without a null check.

## State and Persistence
There is no map persistence. Reference ownership and trusted pointer provenance are the central verifier states.

## Dependencies and Integration Points
The file integrates with the verifier harness through exact `__failure` and `__msg` annotations. It relies on BTF type checking, kfunc argument annotations, and LSM hook restrictions.

## Risks
Changes in kfunc availability or verifier wording can cause expected-message failures. Type mismatch diagnostics are especially tied to BTF type names and argument numbering.

## Test Signals
Expected failures include null trusted-arg rejection, untrusted pointer rejection, unreleased reference, release of unacquired pointer, invalid map-value buffer access size, non-LSM kfunc rejection, and nullable trusted pointer dereference rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_vfs_reject.c -->
