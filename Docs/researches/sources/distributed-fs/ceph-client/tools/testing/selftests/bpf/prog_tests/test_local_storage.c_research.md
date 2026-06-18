<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/test_local_storage.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/test_local_storage.c

Purpose: validates task, inode, and socket local-storage maps through both direct syscalls and BPF LSM-triggered runtime behavior.

Important APIs/types/functions: `run_self_unlink()` forks a copied `rm` binary that attempts to delete itself; `check_syscall_operations()` performs lookup/update/lookup/delete/lookup on a local-storage map keyed by fd; `test_test_local_storage()` loads and attaches `local_storage`.

Control flow: load/attach skeleton, open current pidfd and validate task storage syscalls, create a temp directory and copy `/bin/rm`, validate inode storage syscalls on the copied executable, execute self-unlink and expect `EPERM`, rename the file to exercise null-inode LSM path, start an IPv6 server socket, validate socket storage syscalls, then cleanup.

State and persistence: creates `/tmp/local_storageXXXXXX`, copies/removes an executable, opens task/inode/socket fds, sets `skel->bss->monitored_pid`, and observes result fields in skeleton data. Temp directory removal is best-effort.

Dependencies and integration: depends on generated `local_storage.skel.h`, task local storage helpers, `pidfd_open`, LSM attachment, `/bin/rm`, shell `cp`/`mv`/`rm`, and network helper `start_server`.

Risks: requires privileges and kernel support for local-storage maps and BPF LSM. Shell commands and hard-coded `/bin/rm` path are environment-sensitive. Early failures may leave temp files until the cleanup label is reached.

Test signals: syscall operation assertions check `-ENOENT`, update success, value round-trip, delete success, and post-delete miss; runtime signals check task/inode/socket BPF result fields and expected self-unlink `EPERM`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/test_local_storage.c -->
