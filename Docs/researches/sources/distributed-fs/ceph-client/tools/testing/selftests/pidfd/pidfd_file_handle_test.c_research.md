# sources/distributed-fs/ceph-client/tools/testing/selftests/pidfd/pidfd_file_handle_test.c

Purpose: tests pidfs file-handle export/import behavior through `name_to_handle_at()` and `open_by_handle_at()` for pidfds across same, child, foreign, exited, and reaped PID namespace scenarios.

Important APIs/types/functions: fixture creates self pidfd and three child pidfds using `create_child()` with user/PID namespace variants. Tests allocate `struct file_handle`, use `MAX_HANDLE_SZ`, `AT_EMPTY_PATH`, `AT_HANDLE_FID`, `FD_PIDFS_ROOT`, valid/invalid open flags, `fstat()` identity checks, `setns()`, and pidfd signal/wait helpers.

Control flow: same/child namespace tests obtain a handle from a child pidfd and reopen it via the parent's pidfd with several valid flags, comparing device/inode. Foreign namespace test creates a handle for the parent, enters a child PID/user namespace, forks, and confirms decode fails outside the caller hierarchy. Exited vs reaped tests show handles remain decodable after exit before reap but fail after reap. Flag tests verify allowed pidfd flags and reject creation/path flags. Lookup tests ensure pidfs does not support path lookup. Final tests validate `AT_HANDLE_FID` and decoding via `FD_PIDFS_ROOT`.

State and persistence: creates paused children, pidfds, namespace changes in a forked child, and signals/reaps children in teardown. No filesystem files.

Dependencies/integration: requires pidfs export operations, file handle syscalls, pidfd_open/send_signal/waitid, user/PID namespace support, and matching UAPI flags.

Risks: `setns()` in the foreign namespace test changes namespace state in the fixture process before forking, so test isolation relies on kselftest process model. Feature availability is new-kernel-specific. Teardown must avoid double-killing child3 when tests consume it.

Test signals: kselftest assertions for each file-handle decode/flag/lookup case; failures indicate pidfs export or namespace visibility regressions.
