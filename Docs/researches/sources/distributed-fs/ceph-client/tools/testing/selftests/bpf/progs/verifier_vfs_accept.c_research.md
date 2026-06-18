<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_vfs_accept.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_vfs_accept.c

## Purpose
This LSM verifier acceptance suite checks valid use of VFS-related kfuncs and trusted pointer arguments, including acquiring and releasing task executable files and formatting paths.

## Important APIs, Types, and Functions
The file uses `bpf_get_task_exe_file`, `bpf_get_current_task_btf`, `bpf_put_file`, `bpf_path_d_path`, and `BPF_PROG` tracing wrappers. It declares a static `buf[64]` and uses kernel types `struct file`, `struct path`, `struct task_struct`, `struct inode`, and `struct dentry`.

## Control Flow
Accepted programs acquire a file reference from current task or task argument, null-check it, and release it. Path tests call `bpf_path_d_path` on a trusted path argument or on `&file->f_path`, which remains trusted despite being an embedded member with fixed offset. The inode rename test reads `new_dentry->d_inode`, checks for null, reads `i_ino`, and conditionally denies with `-EACCES`.

## State and Persistence
There is no persistent map state. Reference state is important: acquired `struct file *` references must be released with `bpf_put_file`. The static buffer is used only during helper calls.

## Dependencies and Integration Points
The programs are sleepable and non-sleepable LSM hooks using BTF typed arguments. They depend on `bpf_experimental.h` for kfunc declarations and on verifier trusted-pointer rules.

## Risks
VFS kfunc trust and reference rules are evolving APIs. Changes to which LSM hooks allow specific kfuncs, or to trusted embedded-member recognition, can alter acceptance.

## Test Signals
Every section is annotated `__success`; successful load proves trusted arguments, fixed-offset trusted member access, proper null checking, and reference release are accepted.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_vfs_accept.c -->
