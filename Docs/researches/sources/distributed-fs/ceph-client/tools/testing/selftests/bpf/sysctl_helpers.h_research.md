<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/sysctl_helpers.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/sysctl_helpers.h

## Purpose
This header exposes the sysctl helper API for BPF userspace selftests.

## Important APIs, Types, and Functions
It declares `int sysctl_set(const char *sysctl_path, char *old_val, const char *new_val);` and `int sysctl_set_or_fail(const char *sysctl_path, char *old_val, const char *new_val);`.

## Control Flow
The header has only include guards and declarations; behavior is implemented in `sysctl_helpers.c`.

## State and Persistence
No state is defined in the header. Callers use the API to mutate sysctl filesystem state.

## Dependencies and Integration Points
It is included by userspace selftests that need temporary sysctl changes and links with `sysctl_helpers.c`.

## Risks
ABI is a simple C declaration contract; mismatched implementation signatures would break builds. Callers must understand that `old_val` is an output buffer.

## Test Signals
Compilation and linkage against the helper implementation are the relevant signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/sysctl_helpers.h -->
