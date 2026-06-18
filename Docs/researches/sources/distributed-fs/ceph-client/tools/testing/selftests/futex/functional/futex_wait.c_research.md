<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/futex/functional/futex_wait.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/futex/functional/futex_wait.c

## Purpose
This test validates basic `FUTEX_WAIT`/`FUTEX_WAKE` behavior for private, SysV shared-memory, and file-backed shared futexes.

## Important APIs, Types, And Functions
It defines shared global `void *futex`, helper `waiterfn()`, and tests `private_futex`, `anon_page`, and `file_backed`. It uses `futex_wait()`, `futex_wake()`, `shmget()`, `shmat()`, `mmap(MAP_SHARED)`, and a temporary `futex_shm_file`.

## Control Flow
Each test places a zero-valued futex in the target backing type, starts a waiter with a short timeout, sleeps to let it block, then wakes one waiter and expects return count `1`.

## State And Persistence
It creates transient pthreads, SysV shared memory attachment, and a temporary file-backed mapping. The file is removed at the end of the file-backed test.

## Dependencies And Integration Points
It depends on System V shared memory support, filesystem-backed shared mappings, pthreads, and futex wrappers.

## Risks
Waiter synchronization uses `usleep`, so extreme scheduling delay can race. The SysV segment is detached but not explicitly marked for removal with `shmctl(IPC_RMID)`, which is a cleanup concern.

## Test Signals
Each backing type should report a pass when `futex_wake()` returns exactly one woken waiter; `shmget ENOSYS` skips the shared-memory case.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/futex/functional/futex_wait.c -->
