<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/unpriv_helpers.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/unpriv_helpers.h

## Purpose
`unpriv_helpers.h` exposes the unprivileged-BPF disablement check used by verifier-style tests.

## Important APIs, Types, And Functions
- `UNPRIV_SYSCTL` names `kernel/unprivileged_bpf_disabled`.
- `get_unpriv_disabled()` returns whether unprivileged tests should be treated as disabled.

## Control Flow
No flow exists in the header.

## State And Persistence
No state is defined.

## Dependencies And Integration Points
It includes `<stdbool.h>` and is consumed by `test_verifier.c`.

## Risks And Edge Cases
The sysctl macro omits `/proc/sys/` by design; callers that need a full path must prepend it.

## Test Signals
Compile-time consumers rely on this declaration; runtime behavior is in `unpriv_helpers.c`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/unpriv_helpers.h -->
