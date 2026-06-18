# sources/distributed-fs/ceph-client/tools/testing/selftests/filesystems/file_stressor.c

## Purpose

`file_stressor.c` is a long-running stress test for file reference lifetime behavior under `SLAB_TYPESAFE_BY_RCU`. It tries to provoke races between rapid file allocation/freeing and `/proc/<pid>/fd` directory iteration.

## Important APIs, Types, and Functions

It wraps `fsopen`, `fsconfig`, `fsmount`, and `move_mount`, defines `MOVE_MOUNT_F_EMPTY_PATH` if needed, and uses a `file_stressor` fixture containing tmpfs mount fd, process counts, child pid arrays, proc fd directory fds, and `max_fds`. The test uses `fork`, `open`, `close_range`, `getdents64`, `lseek`, `clock_nanosleep`, `kill`, and wait logic.

## Control Flow, State, and Persistence

Setup unshares a mount namespace, mounts a detached tmpfs at `/slab_typesafe_by_rcu`, allocates arrays sized by online CPU count, and sets a 500-fd churn limit. The test forks one opener process per CPU; each repeatedly creates many files and closes all descriptors. The parent opens each opener's `/proc/<pid>/fd/`, then forks one getdents process per CPU; each continuously reads and rewinds that proc fd directory. After fifteen minutes the parent kills all children. Teardown waits for killed children, frees arrays, closes the tmpfs fd, unmounts, and removes the directory.

## Dependencies, Integration Points, Risks, and Test Signals

It depends on procfs, new mount API, tmpfs, `close_range`, `getdents64`, namespaces, and enough process/file limits. It integrates with VFS file lifetime and proc fd iteration regression testing. Risks include long runtime, high CPU/file churn, a likely typo using `self->pids_openers[i]` inside the child loop path format, resource exhaustion, and tests passing only by absence of kernel warnings. Signals are no assertion failures, no hangs before timeout, child cleanup success, and external kernel logs remaining free of file refcount warnings.
