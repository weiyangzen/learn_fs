# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_lsm.c

## Purpose
This file verifies BPF LSM return-value constraints, disabled hook rejection, and nullable/trusted pointer handling for LSM program contexts.

## Important APIs, Types, And Functions
It uses `vmlinux.h`, `bpf_tracing.h`, `BPF_PROG`, and LSM sections such as `lsm/file_permission`, `lsm/file_mprotect`, `lsm/audit_rule_known`, `lsm/file_free_security`, `lsm/getprocattr`, `lsm/setprocattr`, `lsm/ismaclabel`, and `lsm/mmap_file`.

## Control Flow
Naked tests return constants to validate hook-specific return ranges: errno-or-zero, bool, and void. Later C `BPF_PROG` tests dereference `struct file *` from `mmap_file`, one without a null check and one with a null guard before reading `f_inode`.

## State And Persistence
No application state persists. Verifier state is hook metadata, expected return range, nullable trusted-pointer tracking, and BTF-derived field access.

## Dependencies And Integration Points
The tests integrate with BPF LSM attach-point metadata and BTF type information from `vmlinux.h`. The selftest harness checks that disabled hooks are rejected.

## Risks
Wrong return-range enforcement could let LSM programs return invalid allow/deny values. Nullable pointer mishandling could admit unsafe kernel pointer dereferences.

## Test Signals
Signals include success for valid return ranges and failures with messages such as `should have been in [-4095, 0]`, `should have been in [0, 1]`, `points to disabled hook`, and `trusted_ptr_or_null_`.
