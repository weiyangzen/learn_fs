# subset-b-009300 research

Grouped research report for LTP syscall tests under SysV IPC, kcmp, keyctl, kill, Landlock, lchown, xattr, link, listen, and listmount. Each section title preserves the exact source path and is wrapped for reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ipc/semctl/semctl09.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/ipc/semctl/semctl09.c

Purpose: validates `semctl(SEM_INFO)` and `SEM_STAT_ANY` reporting for System V semaphore sets, including consistency with `/proc/sysvipc/sem`. Important APIs include `semctl`, direct `__NR_semctl` via `tst_syscall`, `SAFE_SEMGET`, `SAFE_SEMCTL`, `SAFE_SETEUID`, and `union semun`; the direct syscall variant exists to detect the historical glibc buffer-passing bug. Control flow creates one private semaphore set, checks support, then runs as both `nobody` and root, verifying the returned max index, counting valid indexes, and parsing procfs totals. State is kernel IPC state plus effective UID changes; cleanup restores root euid and removes the semaphore. Risks are procfs races with concurrent IPC tests and libc/kernel version differences; test signals are `TPASS/TFAIL/TCONF` for valid index, counted `semusz`, `semaem`, and glibc bug detection.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ipc/semctl/semctl09.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ipc/semget/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/ipc/semget/Makefile

Purpose: builds the `semget` LTP syscall tests as a generic leaf directory. It sets `top_srcdir`, declares `LTPLIBS = newipc`, includes the common `testcases.mk`, links the directory against `-lltpnewipc`, and delegates targets to `generic_leaf_target.mk`. The dependency on `newipc` is essential because the C tests use helper macros such as `GETIPCKEY`, `PSEMS`, and `/proc/sys/kernel/sem` paths from LTP's IPC support. There is no runtime control flow or persistence in the Makefile itself; its state is build configuration only. Integration risk is missing or mislinked `libltpnewipc`, which would fail compile/link before runtime. Test signal is successful construction of all local `semget*.c` test binaries with the shared LTP harness.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ipc/semget/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ipc/semget/semget01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/ipc/semget/semget01.c

Purpose: basic positive test that `semget()` creates a semaphore set with expected metadata. It uses `GETIPCKEY`, `semget`, `SAFE_SEMCTL(IPC_STAT)`, `union semun`, and LTP expectation macros to compare `sem_nsems` with `PSEMS` and creator UID with `geteuid()`. Control flow allocates a unique key in setup, creates the set with `IPC_CREAT | IPC_EXCL | SEM_RA`, reads `semid_ds`, reports pass on matching fields, and removes the set. Persistent state is one SysV semaphore array that must be removed by test or cleanup. Dependencies are `tse_newipc.h`, `lapi/sem.h`, and `tst_safe_sysv_ipc.h`. Risks are leaked IPC objects on abnormal exit; test signals are creation success and metadata equality.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ipc/semget/semget01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ipc/semget/semget02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/ipc/semget/semget02.c

Purpose: negative coverage for `semget()` errno behavior: `EACCES`, `EEXIST`, `ENOENT`, and multiple `EINVAL` cases. The test table varies key, semaphore count, flags, expected errno, and whether to execute as root or `nobody`. Setup creates one existing semaphore set and stores a second unused key; `do_test()` forks for the permission case, changes UID, then calls `TST_EXP_FAIL2(semget(...))`. State is a root-created semaphore array plus temporary UID changes isolated in children. Dependencies include root privilege, LTP IPC key generation, and `SAFE_FORK`/`tst_reap_children`. Risks are environment-specific SEMMSL limits and user availability; signals are expected errno matches per test case and cleanup removal of the existing set.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ipc/semget/semget02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ipc/semget/semget05.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/ipc/semget/semget05.c

Purpose: drives `semget()` to `ENOSPC` by exhausting the maximum number of semaphore arrays (`SEMMNI`). Setup reads `PATH_KERN_SEM`, subtracts `GET_USED_ARRAYS()`, dynamically adjusts runtime, allocates an array of IDs, and creates semaphore sets until the system limit is reached. The test then attempts one more set with a distinct key and expects `ENOSPC`. State is deliberately large kernel IPC allocation; cleanup iterates all recorded IDs and removes them. Dependencies include writable/readable `/proc/sys/kernel/sem`, enough runtime for the local SEMMNI value, and non-concurrent IPC mutation. Risks are high limits causing long execution or external IPC users changing counts; test signal is a final `semget()` failure with `ENOSPC`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ipc/semget/semget05.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ipc/semop/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/ipc/semop/Makefile

Purpose: builds the `semop` and `semtimedop` syscall tests. It includes LTP common testcase rules, sets `LTPLIBS = newipc`, links `semop01`, `semop02`, and `semop03` against `-lltpnewipc`, and adds `-lpthread` for `semop05`. There is no runtime logic here, but the Makefile defines integration boundaries: most tests depend on the new IPC helper library, while the legacy pthread SEM_UNDO test needs POSIX threads. Build state is limited to target-specific library flags. Risks are omitted target-specific libraries causing unresolved references. Test signal is successful compilation/linking of each semop test binary through `generic_leaf_target.mk`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ipc/semop/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ipc/semop/semop.h -->
# sources/test-tools/ltp/testcases/kernel/syscalls/ipc/semop/semop.h

Purpose: shared variant layer for `semop` tests, allowing the same test bodies to exercise libc `semop`, old-kernel `semtimedop`, and time64 `semtimedop_time64` where available. It defines syscall wrappers with `tst_syscall`, a `time64_variants` array carrying function pointers, timestamp type, and description, plus `call_semop()` and `semop_supported_by_kernel()`. State is compile-time feature gating via syscall numbers and runtime ENOSYS detection. Dependencies are `time64_variants.h`, `tst_timer.h`, `lapi/syscalls.h`, and System V semaphore headers. Integration points are all `semop01`-`semop03` tests using `tst_variant`. Risks are architecture-specific syscall availability and timestamp ABI differences; test signal is TCONF on unsupported kernels rather than false failures.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ipc/semop/semop.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ipc/semop/semop01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/ipc/semop/semop01.c

Purpose: positive functionality test for `semop`/`semtimedop` variants, ensuring an array of operations updates semaphore values correctly. Setup selects the time ABI variant, prepares a short timeout, creates a semaphore set, and fills four `sembuf` operations with `SEM_UNDO` and values `i*i`. Each run calls `call_semop()`, reads all values with `semctl(GETALL)`, checks expected values, then resets them to zero. State is one semaphore set and per-variant timeout representation. Dependencies are `semop.h`, LTP IPC key helpers, and kernel support for the selected variant. Risks are variant-specific timeout handling and cleanup if a reset fails. Test signals are pass/fail on operation success and exact semaphore values.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ipc/semop/semop01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ipc/semop/semop02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/ipc/semop/semop02.c

Purpose: negative errno matrix for `semop` and `semtimedop`, covering `E2BIG`, `EACCES`, `EFAULT`, `EINVAL`, `ERANGE`, `EFBIG`, and `EAGAIN`. Setup runs as `nobody`, creates a permitted and non-permitted semaphore set, reads `semvmx` via `IPC_INFO`, and prepares bad buffer and timeout addresses. Each table row optionally sets a semaphore value, selects invalid IDs, invalid `sembuf`, operation count, or timeout, then checks the expected errno through `call_semop()`. State includes two semaphore arrays and a non-root effective UID. Dependencies are root setup, `nobody`, the time64 variant layer, and bad-address helpers. Risks include libc skipping EFAULT cases and semtimedop-only cases not applicable to libc semop; test signals are expected errno matches or TCONF.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ipc/semop/semop02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ipc/semop/semop03.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/ipc/semop/semop03.c

Purpose: verifies blocking semaphore operations fail with `EIDRM` when the semaphore set is removed and with `EINTR` when interrupted by signal. It uses `call_semop()` variants, `SAFE_FORK`, `TST_PROCESS_STATE_WAIT`, `semctl(SETVAL)`, `SAFE_KILL`, and a `SIGHUP` handler. For each case, the parent sets the target semaphore value, forks a child blocked in `semop`/`semtimedop`, waits until sleeping, then either removes the set or sends `SIGHUP`. Removed sets are recreated for later EIDRM cases. State is one semaphore array and child blocking state. Dependencies include reliable process-state wait and signal delivery. Risks are timing sensitivity around blocking detection; signals are child-reported expected errno and successful recreation/cleanup.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ipc/semop/semop03.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ipc/semop/semop04.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/ipc/semop/semop04.c

Purpose: stress/basic synchronization test where two processes repeatedly contend for one SysV semaphore. Helper functions `semup()` and `semdown()` wrap `SAFE_SEMOP` with `SEM_UNDO`; `mainloop()` performs 1000 down/sleep/up cycles with deterministic `srand(SEED)`. The run creates a semaphore with fixed key `9142`, initializes it to one, forks a child, runs the same contention loop in both processes, reaps the child, and removes the semaphore. State is a single semaphore used as a lock. Dependencies are SysV semaphore support and LTP safe IPC wrappers. Risks include fixed key collision and long runtime from sleep loops. Test signal is survival without `SAFE_SEMOP` failure and a positive `IPC_RMID` result.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ipc/semop/semop04.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ipc/semop/semop05.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/ipc/semop/semop05.c

Purpose: legacy pthread test for `SEM_UNDO` semantics, ensuring undo adjustments are process-scoped rather than applied when an individual thread exits. Main creates one private semaphore initialized to one, starts a waiter thread and a poster thread, then sleeps and checks global `err_ret`. The poster performs `semop(+1, SEM_UNDO)` and exits; the waiter sleeps ten seconds then performs `semop(-1, SEM_UNDO)`. If the poster's undo were applied at thread exit, the waiter would block; success is the waiter completing and clearing `err_ret`. State is a process-shared semaphore and two pthreads. Dependencies are old LTP `test.h`, pthreads, and SysV semaphores. Risks are long fixed sleeps and minimal return checking; test signal is `TPASS` only if waiter completes.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ipc/semop/semop05.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ipc/shmat/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/ipc/shmat/Makefile

Purpose: builds the `shmat` shared-memory attach tests. It declares `LTPLIBS = newipc`, includes common LTP testcase rules, links all targets in the directory with `-lltpnewipc`, and uses the generic leaf target include. The Makefile has no runtime control flow; its role is to wire test binaries to IPC helper functions and constants such as `GETIPCKEY`, `INT_SIZE`, and `PROBE_FREE_ADDR`. Persistent state is only build metadata. Integration risk is missing `libltpnewipc` or wrong `top_srcdir`. Test signal is successful build of the shmat test set.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ipc/shmat/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ipc/shmat/shmat01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/ipc/shmat/shmat01.c

Purpose: positive `shmat()` behavior test for NULL attachment, aligned address attachment, `SHM_RND` unaligned rounding, and `SHM_RDONLY`. Setup probes a free aligned address, derives an unaligned address, and creates one shared-memory segment. Each case attaches, checks `shm_nattch`, `shm_segsz`, expected address rounding, then forks a child to write to the mapping; readonly attachment expects `SIGSEGV`, others expect normal exit. State is one segment plus transient mappings and child status. Dependencies include root privilege, `PROBE_FREE_ADDR`, `SHMLBA`, and safe SysV IPC helpers. Risks are architecture address-layout differences and signal semantics for readonly writes. Test signals are correct metadata, address, and child exit/signal status.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ipc/shmat/shmat01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ipc/shmat/shmat02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/ipc/shmat/shmat02.c

Purpose: negative `shmat()` errno test for invalid shmid, unaligned address without `SHM_RND`, and permission denial. Setup probes aligned/unaligned addresses, creates a shared-memory segment with read/write permissions, and resolves `nobody`. Cases run directly as root for `EINVAL` checks or in a forked `nobody` child for `EACCES`. Important APIs are `shmat`, `SAFE_SHMGET`, `SAFE_SETUID`, `TST_EXP_FAIL_PTR_VOID`, and `SAFE_FORK`. State is one segment and child UID transition. Dependencies are root privilege and a valid `nobody` account. Risks are environment-specific permission behavior if capabilities are retained unexpectedly; test signal is expected pointer failure and errno per row.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ipc/shmat/shmat02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ipc/shmat/shmat03.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/ipc/shmat/shmat03.c

Purpose: regression for low-address `shmat()` behavior with `SHM_RND | SHM_REMAP`, tied to Linux commits around nil-page protection and Xorg compatibility. Setup creates a one-page private shared-memory segment. The run calls `shmat(shm_id, (void *)1, SHM_RND | SHM_REMAP)`: `EINVAL` is accepted, while a successful map must not land in the first 64 KiB and must tolerate a write. State is one segment and optional mapping. Dependencies include root permission to avoid `security_mmap_addr()` interference. Risks are architecture-specific low-address policy and kernel ABI differences. Test signals are `TPASS` for `EINVAL` or safe non-low mapping, `TFAIL` for mapping in protected low memory.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ipc/shmat/shmat03.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ipc/shmat/shmat04.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/ipc/shmat/shmat04.c

Purpose: regression test for a SysV shared-memory attach-count leak caused by VMA merge/removal paths after `mprotect()`. The test creates a three-page segment, attaches it, records `shm_nattch`, applies `mprotect(PROT_NONE)` to the middle page, then restores write permission over two pages to trigger merge behavior. After `shmdt`, it checks `shm_nattch` is zero and removes the segment. Important APIs are `SAFE_SHMGET`, `SAFE_SHMAT`, `SAFE_MPROTECT`, `SAFE_SHMCTL(IPC_STAT/IPC_RMID)`, and `TST_EXP_EQ_LU`. State is one segment and mutable VMAs. Dependencies include page size and SysV IPC. Risk is kernel-version-specific VMA behavior; test signal is final `shm_nattch == 0`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ipc/shmat/shmat04.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ipc/shmctl/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/ipc/shmctl/Makefile

Purpose: builds the `shmctl` tests and declares target-specific dependencies. It sets `LTPLIBS = newipc`, adds `-pthread` and `-lrt` for `shmctl05`, includes common testcase rules, and links `shmctl01`, `shmctl02`, `shmctl04`, and `shmctl06` with `-lltpnewipc`. The file has no runtime state; it encodes which tests need IPC helpers and which need threading/timing libraries. Integration points are the LTP build system and `generic_leaf_target.mk`. Risks are missing target-specific flags, especially for fuzzy sync/threaded regression coverage. Test signal is successful build of all local shared-memory control tests.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ipc/shmctl/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ipc/shmctl/shmctl01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/ipc/shmctl/shmctl01.c

Purpose: validates `shmctl(IPC_STAT)` and `SHM_STAT` metadata, especially `shm_nattch` across child attach/detach and inherited mappings. Setup creates one private segment, records creation timestamp bounds, maps shm ID to kernel index with `SHM_INFO`/`SHM_STAT`, and installs `SIGUSR1` handler. Test cases check segment size, creator PID, ctime range, then fork 20 children to attach/detach or inherit/detach a parent mapping. State includes one segment, many child processes, and shared attach counts. Dependencies are process-state waits, signal coordination, and kernel `SHM_STAT`. Risks are timing around child pauses and attach-count races. Test signals are matching `IPC_STAT` and `SHM_STAT` nattch values and expected counts.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ipc/shmctl/shmctl01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ipc/shmctl/shmctl02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/ipc/shmctl/shmctl02.c

Purpose: negative `shmctl()` errno coverage for permission, invalid buffer, invalid command/id, removed segment, and root-owned segment operations. It runs both libc `shmctl` and raw `__NR_shmctl` variants, skipping libc EFAULT cases because the wrapper may preclude direct bad-address testing. Setup creates a root-owned segment, drops effective UID to `nobody`, creates accessible/inaccessible segments, and creates/removes a segment for stale-ID checks. State is three segment IDs and euid transitions. Dependencies include root, `nobody`, syscall-number availability, and safe IPC cleanup. Risks are privilege/capability behavior and libc wrapper differences. Test signals are expected errno matches across variants, with cleanup restoring root before removing root-owned shm.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ipc/shmctl/shmctl02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ipc/shmctl/shmctl03.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/ipc/shmctl/shmctl03.c

Purpose: checks `shmctl(IPC_INFO)` global shared-memory limits against procfs kernel tunables. The test calls `shmctl(0, IPC_INFO, (struct shmid_ds *)&info)`, validates `shmmin == 1`, then compares `shmmax`, `shmmni`, and `shmall` with `PATH_KERN_SHMMAX`, `PATH_KERN_SHMMNI`, and `PATH_KERN_SHMALL` through LTP assertion helpers. No shared-memory segment is created; state is read-only kernel IPC configuration. Dependencies are procfs/sysctl visibility and the Linux `struct shminfo` ABI. Risks are concurrent sysctl changes or missing proc paths in constrained environments. Test signals are pass/fail for each tunable equality and syscall success.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ipc/shmctl/shmctl03.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ipc/shmctl/shmctl04.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/ipc/shmctl/shmctl04.c

Purpose: validates `shmctl(SHM_INFO)` and `SHM_STAT_ANY`, including consistency with `/proc/sysvipc/shm`. Setup creates one segment to guarantee at least one entry, checks `SHM_STAT_ANY` support, and records root and `nobody` UIDs. Each test switches euid, calls `SHM_INFO`, verifies the returned max index maps to a valid shm ID, counts valid indexes, and parses procfs to compare `used_ids`, `shm_rss`, `shm_swp`, and page-rounded `shm_tot`. State is one segment plus effective UID changes. Dependencies are root, procfs, page size, and no concurrent IPC mutation. Risks are procfs races and ABI support; test signals are expected counts/totals and valid index mapping.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ipc/shmctl/shmctl04.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ipc/shmctl/shmctl05.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/ipc/shmctl/shmctl05.c

Purpose: race regression for use-after-free of a SysV shm file via `remap_file_pages()` while a shm ID is removed and reallocated. It uses `tst_fuzzy_sync_pair`, a worker thread repeatedly doing `shmctl(IPC_RMID)` and `shmget()` on key `0xF00F`, and the main side repeatedly attaching and invoking raw `__NR_remap_file_pages` until the ID disappears. State is a rapidly reused SysV shm ID, one mapping, and fuzzy-sync race windows. Dependencies are `remap_file_pages`, `__NR_shmctl`, pthread/fuzzy-sync helpers, and a minimum runtime of 40 seconds. Risks are intentional race non-determinism and syscall availability. Test signal is no crash plus acceptable `EIDRM` or `EINVAL` from remap.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ipc/shmctl/shmctl05.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ipc/shmctl/shmctl06.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/ipc/shmctl/shmctl06.c

Purpose: verifies that kernel `shmctl(IPC_STAT)` clears high timestamp fields in `struct shmid64_ds` when those fields exist. The test is compiled only under `HAVE_SHMID64_DS_TIME_HIGH`; otherwise it reports TCONF. It initializes `shm_atime_high`, `shm_dtime_high`, and `shm_ctime_high` to nonzero, creates a shared-memory segment, calls `shmctl`, then checks all high fields are zero before removing the segment. State is one segment and a compatibility structure cast to `struct shmid_ds *`. Dependencies are LTP `lapi/shmbuf.h`, newipc key helpers, and architecture headers exposing the high fields. Risks are ABI-layout sensitivity. Test signal is all high fields cleared.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ipc/shmctl/shmctl06.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ipc/shmctl/shmctl07.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/ipc/shmctl/shmctl07.c

Purpose: positive test for `shmctl(SHM_LOCK)` and `SHM_UNLOCK`. Setup creates one private shared-memory segment. The test locks it, reads `IPC_STAT`, expects the `SHM_LOCKED` bit in `shm_perm.mode`, unlocks it, and expects the bit to be clear. Important APIs are `shmctl`, `SAFE_SHMGET`, `SAFE_SHMCTL`, and mode-bit inspection. State is one segment whose locked flag changes. Dependencies include kernel support and sufficient privilege/resource limits for locking. Risks are environment-specific `RLIMIT_MEMLOCK` or privilege restrictions causing lock failure. Test signals are syscall return values and exact mode-bit transitions, followed by cleanup removal.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ipc/shmctl/shmctl07.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ipc/shmctl/shmctl08.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/ipc/shmctl/shmctl08.c

Purpose: tests `shmctl(IPC_SET)` mode changes and ctime update behavior. Setup creates a segment with mode `0666`. The run reads `IPC_STAT`, records old mode and ctime, sleeps one second, clears group/other permission bits, calls `IPC_SET`, re-reads metadata to verify mode and that `shm_ctime` advanced within a ten-second window, then restores the old mode and checks it masked by `MODE_MASK`. State is one segment with mutable permission metadata. Dependencies include wall-clock timestamp granularity and SysV shm metadata semantics. Risks are timing flake if system time behaves unexpectedly. Test signals are successful `IPC_SET`, expected mode values, and ctime advancement.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ipc/shmctl/shmctl08.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ipc/shmdt/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/ipc/shmdt/Makefile

Purpose: builds the `shmdt` detach tests. It sets `LTPLIBS = newipc`, includes LTP testcase rules, links all local targets with `-lltpnewipc`, and uses the generic leaf target. There is no runtime behavior in the Makefile; it provides build-time integration with IPC helpers for keys, sizes, safe shm wrappers, and probe-address utilities used by the C files. Persistent state is only target configuration. Risks are missing LTP IPC library linkage or an incorrect relative `top_srcdir`. Test signal is successful compilation/linking of the shared-memory detach tests.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ipc/shmdt/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ipc/shmdt/shmdt01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/ipc/shmdt/shmdt01.c

Purpose: verifies that `shmdt()` detaches a mapping and subsequent access faults. Setup creates and attaches a shared-memory segment, installs a `SIGSEGV` handler using `sigsetjmp/siglongjmp`, and stores the mapping in `shared`. The test calls `shmdt`, checks `shm_nattch == 0`, attempts to write through the detached pointer, and passes only if the handler runs; it then reattaches for repeatability. State is one segment, one mapping pointer, and a signal-driven `pass` flag. Dependencies include root, LTP IPC helpers, and normal SIGSEGV delivery. Risks are signal-handler complexity and reattachment after failure. Test signals are successful detach, zero attach count, and SIGSEGV on stale pointer access.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ipc/shmdt/shmdt01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ipc/shmdt/shmdt02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/ipc/shmdt/shmdt02.c

Purpose: negative `shmdt()` test for invalid addresses. Setup uses `PROBE_FREE_ADDR()` for a non-attached page-aligned address and derives an unaligned address by adding `SHMLBA - 1`. Two table cases call `shmdt()` on those pointers and expect `EINVAL`. No SysV shared-memory object is created; state is only address values in the process. Dependencies are `tse_newipc.h`, `SHMLBA`, and LTP expectation macros. Risks are platform alignment rules or address-probe behavior. Test signal is `TST_EXP_FAIL(shmdt(...), EINVAL)` for both non-attached and unaligned addresses.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ipc/shmdt/shmdt02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ipc/shmget/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/ipc/shmget/Makefile

Purpose: builds the `shmget` tests with the LTP new IPC support library. It defines `LTPLIBS = newipc`, includes `testcases.mk`, sets `LTPLDLIBS = -lltpnewipc`, and includes `generic_leaf_target.mk`. Runtime behavior is entirely in the C files; this Makefile's state is target/library configuration. Integration points are shared-memory constants and helpers from `tse_newipc.h` and `tst_safe_sysv_ipc.h`. Risks are build failures if the newipc library is unavailable or if `top_srcdir` is wrong. Test signal is successful compilation and linkage of all listed shmget tests.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ipc/shmget/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ipc/shmget/shmget02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/ipc/shmget/shmget02.c

Purpose: broad negative `shmget()` errno coverage for `ENOENT`, `EEXIST`, `EINVAL`, `EACCES`, `EPERM`, and `ENOMEM`/feature-specific hugepage outcomes. Setup sets `RLIMIT_MEMLOCK` to zero, creates one existing segment, resolves `nobody`, probes `CONFIG_HUGETLBFS` and `/proc/meminfo`, and adjusts expected errors for unsupported huge pages. Cases may fork and drop UID/GID before calling `shmget`. State is one shared-memory segment, process credentials in children, kernel SHMMAX temporarily saved/restored to 8192, and no hugepages requested from LTP. Dependencies include root, kconfig access, procfs, and writable sysctls. Risks are hugepage hardware/config differences and privilege handling. Test signals are exact errno matches per scenario.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ipc/shmget/shmget02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ipc/shmget/shmget03.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/ipc/shmget/shmget03.c

Purpose: drives `shmget()` to `ENOSPC` by exhausting `SHMMNI`, the maximum number of shared-memory segments. Setup reads current used segments with `GET_USED_SEGMENTS()`, reads `PATH_KERN_SHMMNI`, allocates an ID array, and creates segments until the limit is reached. The test then attempts one more segment and expects `ENOSPC`. State is deliberately large SysV shm allocation recorded in `queues`; cleanup removes each segment and frees the array. Dependencies are procfs/sysctl visibility and lack of concurrent shared-memory changes. Risks are high limits causing expensive setup and environmental races. Test signal is the final extra `shmget()` failing with `ENOSPC` and successful cleanup.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ipc/shmget/shmget03.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ipc/shmget/shmget04.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/ipc/shmget/shmget04.c

Purpose: verifies `shmget()` returns `EACCES` when an unprivileged user accesses an existing segment without permissions using `SHM_RD`, `SHM_WR`, or `SHM_RW`. Setup resolves `nobody`, switches real UID, generates a key, and creates a segment with no permission bits beyond `IPC_CREAT | IPC_EXCL`. The test table iterates access flags and expects `EACCES`. State is one segment owned by the unprivileged user but without read/write permissions. Dependencies include root startup for UID change and LTP shared-memory flags from `lapi/shm.h`. Risks are capability retention or filesystem namespace not relevant. Test signal is expected errno for all three access modes and cleanup removal.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ipc/shmget/shmget04.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ipc/shmget/shmget05.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/ipc/shmget/shmget05.c

Purpose: positive test for checkpoint/restore `shm_next_id`, the sysctl that requests the next shared-memory ID. Setup stores a key and current PID. Each run writes the PID to `PATH_KERN_SHM_NEXT_ID`, creates a segment, expects the returned shm ID equals that PID, asserts the sysctl resets to `-1`, removes the segment, and increments PID for a repeat. State is kernel shm next-ID configuration and one short-lived segment. Dependencies include root, `CONFIG_CHECKPOINT_RESTORE=y`, and writable `/proc/sys/kernel/ns_last_pid`-style IPC path exposed by LTP. Risks are ID collisions or concurrent IPC allocation. Test signals are returned ID equality and sysctl reset.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ipc/shmget/shmget05.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ipc/shmget/shmget06.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/ipc/shmget/shmget06.c

Purpose: verifies `shm_next_id` does not force reuse of an already allocated shared-memory ID. Setup writes the process PID as next ID, creates the first segment, and stores two keys. The test writes the first segment's ID back into `PATH_KERN_SHM_NEXT_ID`, creates a second segment with a different key, and passes if the second ID differs from the existing one. State is two potential shared-memory segments and kernel next-ID configuration. Dependencies include root and `CONFIG_CHECKPOINT_RESTORE=y`. Risks are concurrent shm allocations and cleanup double-removal if IDs are reset outside the test. Test signal is non-equality of the second ID plus cleanup of both segments.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ipc/shmget/shmget06.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/kcmp/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/kcmp/Makefile

Purpose: builds the `kcmp` syscall tests. It includes standard LTP testcase rules, adds `CFLAGS += -Wl,-z,now`, and delegates targets to `generic_leaf_target.mk`. There are no target-specific libraries or runtime state; the linker flag forces immediate symbol binding, likely to keep tests deterministic under the old harness. Integration points are LTP headers and Linux `kcmp` wrappers in the C files. Risks are platform/toolchain support for `-z now`. Test signal is successful build of `kcmp01`, `kcmp02`, and `kcmp03`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/kcmp/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/kcmp/kcmp01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/kcmp/kcmp01.c

Purpose: positive/negative comparison of open-file identity with `kcmp(KCMP_FILE)`. Setup opens `test_file` in the parent; child opens a second file and duplicates the inherited first FD. The test matrix compares same process/same FD, child duplicate FDs, parent/child references to the same open file, and a distinct file descriptor, expecting zero for shared open-file descriptions and nonzero for different files. State is inherited file descriptors across fork plus a child-created FD. Dependencies are `lapi/kcmp.h`, LTP safe open/fork, and tmpdir isolation. Risks are pid/fd pointer indirection in child context and permission restrictions on kcmp. Test signals are successful syscall and expected zero/nonzero result.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/kcmp/kcmp01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/kcmp/kcmp02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/kcmp/kcmp02.c

Purpose: negative errno test for `kcmp()`, covering nonexistent PID (`ESRCH`), invalid comparison types (`EINVAL`), and invalid file descriptor (`EBADF`). Setup stores current PID, gets an unused PID, and opens two files. The table feeds `kcmp(pid1, pid2, type, fd1, fd2)` through `TST_EXP_FAIL`, including `KCMP_TYPES + 1`, `-1`, `INT_MIN`, and `INT_MAX`. State is only two open file descriptors and pid values. Dependencies are Linux `kcmp` syscall wrapper and tmpdir files. Risks include ptrace/security restrictions that can alter kcmp failures in hardened environments. Test signal is exact errno for each invalid case.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/kcmp/kcmp02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/kcmp/kcmp03.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/kcmp/kcmp03.c

Purpose: validates `kcmp()` reports shared kernel resources as equal for clone-created children. The table maps clone flags `CLONE_VM`, `CLONE_FS`, `CLONE_IO`, and `CLONE_SYSVSEM` to `KCMP_VM`, `KCMP_FS`, `KCMP_IO`, and `KCMP_SYSVSEM`. Setup allocates a 1 MiB clone stack. Each run calls `ltp_clone(flag | SIGCHLD, do_child, &kcmp_type, ...)`; the child compares parent PID and child PID for the requested resource and expects success. State is a clone stack and kernel resource sharing relationships. Dependencies are clone flag support, `lapi/sched.h`, and `lapi/kcmp.h`. Risks are kernel/security restrictions and no explicit wait in the test body beyond LTP child handling. Test signal is `TST_EXP_PASS(kcmp(...))`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/kcmp/kcmp03.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/keyctl/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/keyctl/Makefile

Purpose: builds the key management syscall tests. It includes LTP testcase rules, adds `$(KEYUTILS_LIBS)` globally, and links `keyctl02` with `-lpthread` for its read/revoke race. Runtime behavior is in the C files; build state is library linkage for keyutils wrappers such as `add_key`, `request_key`, and `keyctl_join_session_keyring`. Integration risk is missing keyutils development libraries or pthread linkage. Test signal is successful compilation/linking of all `keyctl*.c` tests through `generic_leaf_target.mk`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/keyctl/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/keyctl/keyctl01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/keyctl/keyctl01.c

Purpose: basic keyctl syscall exercise for keyring lookup and negative key operations. It first calls `KEYCTL_GET_KEYRING_ID` for `KEY_SPEC_USER_SESSION_KEYRING` and expects success. It then scans downward from `INT32_MAX` until `KEYCTL_READ` returns `ENOKEY`, using that nonexistent key serial to test `KEYCTL_REVOKE` also fails with `ENOKEY`. State is the caller's keyring namespace but no persistent keys are intentionally created. Dependencies are `lapi/keyctl.h` and kernel keyrings support. Risks include the scan cost and unusual key ID allocation density. Test signals are pass for session keyring lookup and expected `ENOKEY` on revoking a missing key.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/keyctl/keyctl01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/keyctl/keyctl02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/keyctl/keyctl02.c

Purpose: race regression for CVE-2015-7550 / commit `b4a1b4f5047e`, where `keyctl_read()` could race `keyctl_revoke()` on user keys. Setup raises `/proc/sys/kernel/keys/root_maxkeys` and detects PREEMPT_RT for throttling. The test loops up to 20,000 times or 60 seconds, creating a process-keyring user key and launching four pthreads that read and revoke it. It then creates/invalidates an extra key to encourage GC and waits until the last test key returns `ENOKEY`. State includes many transient keys, root key quota sysctl, pthreads, and GC timing. Dependencies are root, keyutils, pthreads, and kconfig reading. Risks are race non-determinism and quota restoration. Test signal is no crash and final pass after GC.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/keyctl/keyctl02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/keyctl/keyctl03.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/keyctl/keyctl03.c

Purpose: regression for uninstantiated keyring garbage collection crash fixed by `f05819df10d7`. The test adds a user key to the session keyring, calls `request_key("keyring", "foo", "bar", KEY_SPEC_THREAD_KEYRING)` to create/request an uninstantiated keyring path, then unlinks the user key from the session keyring. State is the session and thread keyrings plus one user key and one failed/requested keyring object. Dependencies are keyrings support and `lapi/keyctl.h`. Risks are environment-specific request-key helper behavior, though the test does not assert the request result. Test signal is `KEYCTL_UNLINK` success and no kernel crash during GC-triggering state transitions.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/keyctl/keyctl03.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/keyctl/keyctl04.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/keyctl/keyctl04.c

Purpose: regression for CVE-2017-7472, ensuring `KEYCTL_SET_REQKEY_KEYRING` does not replace and leak an existing thread keyring. The test creates/gets the thread keyring with `KEYCTL_GET_KEYRING_ID(..., create=1)`, stores the serial, sets default request-key destination to `KEY_REQKEY_DEFL_THREAD_KEYRING`, then retrieves the thread keyring without creating. State is the current thread keyring and request-key default setting. Dependencies are keyrings support and keyctl constants. Risks are per-thread keyring side effects persisting for the test process only. Test signal is the second keyring ID equaling the original; a different ID indicates leak/regression.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/keyctl/keyctl04.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/keyctl/keyctl05.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/keyctl/keyctl05.c

Purpose: regression for key update freeing uninitialized memory, covering non-updatable key types and a write-permission race. It optionally loads `dns_resolver`, detects FIPS, joins fresh session keyrings, tries adding/updating `asymmetric` and `dns_resolver` keys expecting `EOPNOTSUPP`, and races `KEYCTL_UPDATE` on a user key against a child toggling `KEYCTL_SETPERM`. State includes session keyrings, x509 payload parsing, module availability, permissions, and a forked child. Dependencies include root, optional kernel key types, crypto/x509 config, and request-key/keyutils APIs. Risks are many TCONF branches depending on kernel configuration and FIPS policy. Test signals are expected update failures and no crash while racing user-key update.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/keyctl/keyctl05.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/keyctl/keyctl06.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/keyctl/keyctl06.c

Purpose: regression for keyring read buffer sizing bugs fixed by `e645016abc80` and `3239b6f29bdf`. The test adds two user keys to the process keyring, then calls `KEYCTL_READ` on the keyring with a buffer only large enough for one `key_serial_t` but backed by a two-element array. It verifies the second element remains zero and the return value is the full required size for both key IDs. State is the process keyring with two transient user keys and a stack buffer. Dependencies are keyrings support and `add_key`. Risks are unspecified contents inside the too-small part of the buffer, which the test intentionally avoids checking. Test signal is no overrun and full-count return.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/keyctl/keyctl06.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/keyctl/keyctl07.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/keyctl/keyctl07.c

Purpose: CVE-2017-12192 regression ensuring `KEYCTL_READ` on a negative key fails safely with `ENOKEY`. A child calls `request_key("user", ...)` expecting `ENOKEY` or `ENOENT`, reads the process keyring to obtain the negative key serial, then attempts `KEYCTL_READ` on that serial. The parent waits and treats normal exit as pass, while `SIGKILL` indicates a likely kernel oops. State is a process keyring containing a negative key with a short lifetime. Dependencies include request-key behavior and keyring read support. Risks are local `/sbin/request-key` policy unexpectedly instantiating the key. Test signals are child `ENOKEY` plus parent survival/no crash.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/keyctl/keyctl07.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/keyctl/keyctl08.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/keyctl/keyctl08.c

Purpose: CVE-2016-9604 regression checking that session keyrings beginning with `.` cannot be joined. The test calls `keyctl_join_session_keyring(".builtin_trusted_keys")` as root and expects failure with `EPERM`; success is reported as a security failure. State is only the process session keyring request. Dependencies are keyutils helper wrappers and root execution. Risks are typo in diagnostic text only; behavior is direct. Test signal is `EPERM` denial for the dot-prefixed builtin trusted keyring name.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/keyctl/keyctl08.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/keyctl/keyctl09.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/keyctl/keyctl09.c

Purpose: tests encrypted key instantiation using user-provided decrypted data encoded as hex ASCII. It first adds a `user:masterkey` to the process keyring, then adds an `encrypted` key with a valid payload, reads it with `KEYCTL_READ`, and finally expects `EINVAL` when adding another encrypted key with non-hex plaintext characters. State is the process keyring containing user and encrypted keys, cleared at the end. Dependencies include `CONFIG_USER_DECRYPTED_DATA=y`, encrypted key type support, and keyutils APIs. Risks are kernel key type availability and payload-format coupling. Test signals are positive `add_key`/`read` for valid data and `EINVAL` for invalid data.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/keyctl/keyctl09.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/kill/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/kill/Makefile

Purpose: builds the kill syscall test directory. It declares `LTPLIBS = newipc`, includes common LTP testcase rules, links `kill05` with `-lltpnewipc` for its shared-memory synchronization helper use, and delegates to the generic leaf target. The Makefile has no runtime state; it records build dependencies for both legacy `test.h` tests and newer `tst_test.h` tests. Integration risk is missing the newipc library for `kill05`. Test signal is successful build of all kill test binaries.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/kill/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/kill/kill02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/kill/kill02.c

Purpose: legacy process-group semantics test for `kill(0, SIGUSR1)`. It builds a parent process group containing child 1 and grandchild A, plus child 2 and grandchild B in separate process groups, then sends signal to pid zero and checks only same-process-group members report receipt. Important APIs are `tst_fork`, `setpgrp`, `kill`, `signal`, nonblocking pipes, alarms, `pause`, and `wait`. State is four child processes, four pipes, process-group membership, signal handlers, and cleanup signaling. Dependencies are old LTP `test.h` and reliable signal/pipe timing. Risks are long sleeps, global state, and legacy async-signal behavior. Test signals are pipe bytes from expected recipients and absence from excluded process groups.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/kill/kill02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/kill/kill03.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/kill/kill03.c

Purpose: negative `kill()` errno test for invalid signal and nonexistent PIDs, including `INT_MIN`. Setup records current PID, an unused PID from LTP, and `INT_MIN`. The table calls `kill(real_pid, 2000)` expecting `EINVAL`, and `kill(fake_pid, SIGKILL)` plus `kill(INT_MIN, SIGKILL)` expecting `ESRCH`. State is only pid values; no child processes are created. Dependencies are Linux signal validation order and `tst_get_unused_pid`. Risks are signal-number range differences, though 2000 is intentionally invalid. Test signal is `kill()` returning `-1` with the expected errno in each row.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/kill/kill03.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/kill/kill05.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/kill/kill05.c

Purpose: verifies `kill()` returns `EPERM` when a process owned by one unprivileged UID signals a process owned by another. Setup creates a SysV shared-memory page used as a flag and obtains two test UIDs. A master child forks a target child that switches to user 0, then the master switches to user 1, waits for readiness through shared memory, calls `kill(pid1, SIGKILL)`, signals the target to exit, and checks `EPERM`. State is a shared flag segment, two forked children, and real/effective UID transitions. Dependencies are root, at least two test users, and newipc helpers. Risks are capability leakage or user namespace policy. Test signal is expected `EPERM`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/kill/kill05.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/kill/kill06.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/kill/kill06.c

Purpose: basic functionality test for killing an entire process group with a negative PID. A child creates a new process group, forks five paused children, then calls `kill(-getpgrp(), SIGKILL)` to kill its group. The parent waits for a child and verifies the termination signal is `SIGKILL`. State is a process group with six processes. Dependencies are POSIX process groups, `SAFE_FORK`, and wait status macros. Risks are the parent waiting for any child and assuming the observed status is representative; however the group kill should terminate the group consistently. Test signal is `WTERMSIG(status) == SIGKILL`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/kill/kill06.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/kill/kill08.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/kill/kill08.c

Purpose: checks `kill(0, SIGKILL)` sends to the caller's current process group. The child creates a new process group, forks five paused children, calls `SAFE_KILL(0, SIGKILL)`, and pauses. The parent waits for the manager child and checks it died from `SIGKILL`. State is one isolated process group and paused child processes. Dependencies are `setpgrp`, signal broadcast semantics for PID zero, and LTP child cleanup. Risks are that descendant cleanup is implicit in the group kill; if a child escapes the group, it could leak until harness cleanup. Test signal is parent observing expected `SIGKILL` termination.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/kill/kill08.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/kill/kill10.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/kill/kill10.c

Purpose: legacy signal-flooding stress test using multiple process groups. The master forks `-g` manager processes, each in its own process group, and each manager forks `-n` child processes. The master broadcasts `SIGUSR1` to each manager group; children repeatedly signal managers with `SIGUSR2`, managers acknowledge and stop children, then signal the master when all children reported. Important APIs are `fork`, `setpgid`, negative-pid `kill`, `sigaction(SA_SIGINFO)`, alarms, `pause`, `qsort/bsearch` PID checklists, and old LTP looping. State is a three-level process tree and per-process checklist flags. Dependencies are reliable signal delivery under load. Risks are timing sensitivity and complex cleanup. Test signal is all process groups reporting completion each iteration.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/kill/kill10.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/kill/kill11.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/kill/kill11.c

Purpose: verifies wait status for children killed by many signals, including whether the core-dump bit is set for signals that dump core by default. Setup raises `RLIMIT_CORE` to at least 512 KiB if possible. Each test forks a paused child, sends one signal, waits, checks `WTERMSIG(status)` and `WCOREDUMP(status)` against the table. State is one child per signal and process core-file resource limits in the test process. Dependencies include tmpdir for core output, signal defaults, and permissions to raise limits if needed. Risks are system core handling policy and non-root hard limits causing TCONF. Test signals are exact signal number and expected core bit per row.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/kill/kill11.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/kill/kill12.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/kill/kill12.c

Purpose: legacy test that ignored/caught signals do not terminate a child, except uncatchable `SIGKILL`. For signals 1 through 13, the child installs `SIG_IGN` for the current signal, notifies the parent with `SIGCHLD`, waits, and exits after receiving a second `SIGCHLD`; the parent sends the tested signal then `SIGCHLD`, waits, and validates either normal exit or SIGKILL termination. State is one child per signal, global `sig`, `chflag`, and old `sigset` handlers. Dependencies are old LTP `test.h` and traditional signal numbers. Risks include fragile wait loop logic and obsolete signal APIs. Test signal is aggregate pass when ignored signals exit normally and signal 9 terminates.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/kill/kill12.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/kill/kill13.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/kill/kill13.c

Purpose: CVE-2018-10124 reproducer for signed overflow when negating `INT_MIN` in kill PID handling. The test only runs with `CONFIG_UBSAN_SIGNED_OVERFLOW` and taint checking enabled, because normal `kill(INT_MIN, 0)` returns `ESRCH` whether or not the overflow bug exists. It calls `TST_EXP_FAIL2(kill(INT_MIN, 0), ESRCH)` and relies on UBSAN taint detection to catch the bug. State is none beyond kernel taint state. Dependencies are UBSAN signed-overflow instrumentation. Risks are TCONF on non-UBSAN kernels and no behavioral distinction without taint. Test signal is expected `ESRCH` plus no warning/taint regression.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/kill/kill13.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/landlock/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/landlock/Makefile

Purpose: builds the Landlock syscall tests. It includes standard LTP testcase rules, adds `$(KEYUTILS_LIBS)` only for `landlock07` because that regression uses `keyctl`, and delegates to `generic_leaf_target.mk`. Runtime state is absent; build state is target-specific library linkage. Integration points are LTP Landlock lapi headers, keyutils for the Houdini credential-transfer regression, and resource file handling for `landlock_exec`. Risks are missing keyutils linkage for `landlock07`. Test signal is successful build of all Landlock tests and helper binary.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/landlock/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/landlock/landlock01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/landlock/landlock01.c

Purpose: negative errno coverage for `landlock_create_ruleset`. Setup verifies Landlock is enabled, computes valid, too-small, and too-big attribute sizes, and allocates a ruleset buffer. Test cases vary handled filesystem access, size, flags, and invalid attr pointer, expecting `EINVAL`, `E2BIG`, `EFAULT`, or `ENOMSG`. State is one userspace ruleset attribute buffer; any unexpectedly created fd is closed. Dependencies are Landlock enabled, root with `CAP_SYS_ADMIN`, and ABI-1 attr layout from LTP lapi. Risks are kernel ABI changes in validation ordering. Test signal is expected errno for unknown access, invalid flags/size/address, and empty access.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/landlock/landlock01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/landlock/landlock02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/landlock/landlock02.c

Purpose: negative errno coverage for `landlock_add_rule`. Setup detects current ABI, allocates ABI-specific ruleset attrs, creates a ruleset fd with filesystem execute handled, and allocates path and network rule buffers. Test cases cover invalid flags, invalid rule type, empty access, invalid ruleset fd, invalid parent fd, bad rule pointer, network rule with filesystem access, and invalid port, gating net cases on ABI >= 4. State is one ruleset fd and mutable rule attribute buffers. Dependencies are Landlock enabled, root/CAP_SYS_ADMIN, ABI 4 for network cases. Risks are validation-order differences across ABI versions. Test signal is expected `EINVAL`, `ENOMSG`, `EBADF`, or `EFAULT`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/landlock/landlock02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/landlock/landlock03.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/landlock/landlock03.c

Purpose: negative errno coverage for `landlock_restrict_self`. Setup creates a ruleset fd and a regular file fd. Each case forks a child to isolate Landlock stacking, then tests invalid flags (`EINVAL`), invalid fd (`EBADF`), non-ruleset fd (`EBADFD`), missing `CAP_SYS_ADMIN` (`EPERM` after dropping cap), and too many stacked rulesets (`E2BIG` after applying 16 layers). State includes one ruleset fd, one file fd, child-local Landlock layers, and capability changes. Dependencies are Landlock enabled, root, CAP_SYS_ADMIN, and tmpdir. Risks are maximum layer count or capability semantics changing. Test signals are expected errno per case without polluting the parent sandbox.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/landlock/landlock03.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/landlock/landlock04.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/landlock/landlock04.c

Purpose: table-driven positive/negative test for Landlock filesystem access rights. Setup detects ABI, creates a ruleset handling all supported FS rights, grants read/execute permissions for shared libraries found in `/proc/self/maps`, mounts a test filesystem at `sandbox`, and adds a rule for one selected access variant. Each run prepares sandbox files, forks, enforces the ruleset, and calls `tester_run_all_fs_rules()` to require allowed operations pass and all other supported operations fail. State includes mounted filesystem content, ruleset fd, helper executable, and child sandbox. Dependencies are root, CAP_SYS_ADMIN/CAP_MKNOD, all-filesystem LTP mount matrix, and `landlock_tester.h`. Risks are filesystem-specific unsupported node types and dynamic library discovery. Test signal is per-operation `TPASS/TFAIL`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/landlock/landlock04.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/landlock/landlock05.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/landlock/landlock05.c

Purpose: tests `LANDLOCK_ACCESS_FS_REFER`, introduced in ABI 2, for cross-directory rename restrictions. Setup creates three directories and a file under a mounted sandbox, creates a ruleset handling read/write/refer, adds `REFER` permission for `DIR1` and `DIR2` only, and enforces it in the process. The forked run expects `rename(FILENAME1, FILENAME2)` to pass, `rename(FILENAME2, FILENAME3)` to fail with `EXDEV`, then moving back to `DIR1` to pass. State is sandbox directory tree and an enforced Landlock layer. Dependencies include ABI >= 2, root/CAP_SYS_ADMIN, and filesystems other than vfat/exfat. Risks are enforced sandbox affecting cleanup if not isolated. Test signals are expected rename pass/fail outcomes.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/landlock/landlock05.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/landlock/landlock06.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/landlock/landlock06.c

Purpose: tests `LANDLOCK_ACCESS_FS_IOCTL_DEV` behavior from ABI 5. Setup requires ABI >= 5, creates a sandbox file, opens it and `/dev/zero`, then enforces a ruleset allowing `IOCTL_DEV` under the mounted sandbox. The forked run checks several `ioctl()` operations: `FIONREAD` on the regular file and `FIOCLEX`, `FIONCLEX`, `FIONBIO`, and `FIOASYNC` on `/dev/zero`, documenting operations that should remain allowed. State is two open file descriptors and a Landlock layer. Dependencies are root/CAP_SYS_ADMIN, mount device, and non-vfat filesystem. Risks are ioctl policy subtleties across device/file types. Test signal is all listed `ioctl()` calls passing.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/landlock/landlock06.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/landlock/landlock07.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/landlock/landlock07.c

Purpose: CVE-2024-42318 regression for the Landlock "Houdini" cred-transfer bug where restrictions could be lost through keyring credential transfer. Setup creates a ruleset handling `LANDLOCK_ACCESS_FS_WRITE_FILE`. The child enforces no-new-privs and the ruleset, verifies opening `/dev/null` for write fails with `EACCES`, then `spawn_houdini()` joins session keyrings in parent and child and calls `KEYCTL_SESSION_TO_PARENT`. After waiting, it verifies `/dev/null` write is still denied. State includes a Landlock layer, session keyring manipulation, and forked helper process. Dependencies are keyutils, root/CAP_SYS_ADMIN, and Landlock enabled. Risks are keyctl support/policy differences. Test signal is `EACCES` before and after credential transfer.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/landlock/landlock07.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/landlock/landlock08.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/landlock/landlock08.c

Purpose: tests Landlock network rules for TCP `bind()` and `connect()` on IPv4 and IPv6. Setup requires ABI >= 4, chooses an unused bind port, and maps shared memory for the server's ephemeral port. For each address family, a server child binds/listens on an ephemeral port; separate children first demonstrate unrestricted bind/connect, then enforce rules allowing only one port and verify that same-port operations pass while offset-port operations fail with `EACCES`. State includes sockets, shared port memory, checkpoints, and child-local Landlock layers. Dependencies include `CONFIG_INET`, CAP_NET_BIND_SERVICE, CAP_SYS_ADMIN, and IPv6 availability. Risks are port conflicts and synchronization. Test signals are expected pass/fail for bind/connect per port.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/landlock/landlock08.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/landlock/landlock09.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/landlock/landlock09.c

Purpose: tests ABI 6 `LANDLOCK_SCOPE_ABSTRACT_UNIX_SOCKET` scoping. The test has three variants: scope client only, server only, or both. A forked wrapper isolates stacked layers; the client and server synchronize with checkpoints around an abstract UNIX socket named `\0test.sock`. If only the client is scoped, connecting to the server's different domain should fail with `EPERM`; otherwise connection should pass. State is abstract UNIX socket namespace, child processes, and scoped Landlock layers. Dependencies are ABI >= 6, root/CAP_SYS_ADMIN, AF_UNIX sockets, and checkpoints. Risks are abstract socket name reuse and domain inheritance subtleties. Test signal is expected `connect()` result per variant.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/landlock/landlock09.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/landlock/landlock10.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/landlock/landlock10.c

Purpose: tests ABI 6 `LANDLOCK_SCOPE_SIGNAL`, which restricts signals across Landlock domains. Variants scope the paused target, the killer, or both. A wrapper child isolates layers, forks a paused process, waits for it to sleep, then forks a killer process that optionally enters a different scoped domain. If only the killer is scoped, `kill(paused_pid, SIGKILL)` should fail with `EPERM`; if both are in the same domain or only the paused process is scoped, it should pass. State is two child processes, checkpoint synchronization, and scoped Landlock layers. Dependencies are ABI >= 6 and CAP_SYS_ADMIN. Risks are cleanup of a still-paused target. Test signal is expected `kill()` result and clean wait.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/landlock/landlock10.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/landlock/landlock_common.h -->
# sources/test-tools/ltp/testcases/kernel/syscalls/landlock/landlock_common.h

Purpose: common Landlock helper header for all local tests. It defines IPv4/IPv6 loopback constants, `struct socket_data`, ABI detection via `landlock_create_ruleset(...VERSION)`, helpers to add filesystem and network rules, enforce rulesets with `PR_SET_NO_NEW_PRIVS`, apply one-layer FS/network/scoped sandboxes, and create/query sockets for network tests. State is passed through caller-provided attr structures, file descriptors, and socket structs; helpers close path fds after adding rules. Dependencies are LTP `tst_test.h`, `lapi/prctl.h`, `lapi/fcntl.h`, `lapi/landlock.h`, and socket safe macros. Risks are helper calls enforcing restrictions in the current process, so callers often fork to isolate. Test signal support is TCONF/TBROK for disabled Landlock and safe wrapper failures.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/landlock/landlock_common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/landlock/landlock_exec.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/landlock/landlock_exec.c

Purpose: tiny helper executable used by Landlock filesystem execute tests. Its `main()` simply returns zero, providing a deterministic binary that can be copied into the sandbox and run by `_test_exec()` in `landlock_tester.h`. There are no APIs beyond process entry, no state, and no dependencies other than successful compilation. Integration point is `landlock04.c`, which declares this helper in `.resource_files`, copies it to `sandbox/landlock_exec`, and tests whether Landlock allows or denies `execve()` on it. Risks are dynamic-linker/library access, handled in `landlock04.c` by adding rules for shared libraries. Test signal is exit status zero when execution is allowed.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/landlock/landlock_exec.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/landlock/landlock_tester.h -->
# sources/test-tools/ltp/testcases/kernel/syscalls/landlock/landlock_tester.h

Purpose: filesystem-operation test harness for Landlock tests, especially `landlock04.c`. It defines sandbox paths, supported access mask composition with ABI gating, setup/cleanup routines creating files, dirs, symlinks, device numbers, and helper binary, plus operation probes for execute, read, write, readdir, rmdir, unlink/remove, `mknod` of several types, symlink, and truncate. `tester_run_fs_rules()` runs only requested rule probes and handles filesystem limitations for vfat/exfat; `tester_run_all_fs_rules()` computes allowed and denied masks. State is the sandbox filesystem tree and static device numbers. Dependencies include LTP filesystem/device context and Landlock ABI version. Risks are destructive operations requiring per-test re-setup and filesystem-specific unsupported special files. Test signals are LTP expectations per operation.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/landlock/landlock_tester.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/lchown/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/lchown/Makefile

Purpose: builds `lchown` syscall tests, including compatibility variants for 16-bit ownership APIs. It includes common `testcases.mk`, then `../utils/compat_16.mk`, and finally generic leaf targets. There is no runtime state; the Makefile's key integration point is compatibility infrastructure used by `lchown02.c` through `compat_tst_16.h` and UID/GID range checks. Risks are build incompatibilities on architectures without compat variants or missing utility include paths. Test signal is successful build of the lchown test binaries and any generated compat targets.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/lchown/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/lchown/lchown01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/lchown/lchown01.c

Purpose: positive root test for `lchown()` on a symbolic link itself, not the target. Setup creates `testfile` and symlink `slink_file`. Each table row supplies owner/group numeric values or `-1` to leave a field unchanged; the test lstat's the symlink, computes expected UID/GID, calls `SAFE_LCHOWN`, then lstat's again and compares fields. State is one file, one symlink, and symlink metadata. Dependencies are root privilege and filesystem support for symlink ownership. Risks are filesystems that do not preserve symlink ownership or map IDs. Test signals are UID/GID equality for owner-only, group-only, both, and no-op cases.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/lchown/lchown01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/lchown/lchown02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/lchown/lchown02.c

Purpose: negative `lchown()` errno coverage for permission and path-resolution failures: `EPERM`, `EACCES`, `EFAULT`, `ENAMETOOLONG`, `ENOTDIR`, `ENOENT`, `ELOOP`, and `EROFS`. Setup prepares bad address, long path, `nobody` UID/GID with 16-bit compat checks, symlinks including an infinite loop, a no-search directory, a regular-file path component, and a read-only mount point. The test calls `lchown(path, nobody_uid, nobody_gid)` expecting the configured errno. State is tmpdir filesystem objects, credentials switched to `nobody`, and an LTP read-only filesystem. Dependencies are root, compat helpers, and rofs mount support. Risks are path validation order differences. Test signal is expected errno per case.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/lchown/lchown02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/lgetxattr/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/lgetxattr/Makefile

Purpose: builds the `lgetxattr` tests. It includes standard LTP testcase rules and generic leaf targets without additional libraries. Runtime xattr availability is handled in the C files through `HAVE_SYS_XATTR_H` and filesystem support checks. Build state is minimal. Integration risk is platforms without `<sys/xattr.h>`, which compile to TCONF paths rather than functional tests. Test signal is successful build of the xattr test binaries.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/lgetxattr/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/lgetxattr/lgetxattr01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/lgetxattr/lgetxattr01.c

Purpose: positive symlink-specific `lgetxattr()` test. Setup creates a regular file and symlink, sets `security.ltptest1` on the file and `security.ltptest2` on the symlink using `lsetxattr`, treating `ENOTSUP` as TCONF. The test reads `SECURITY_KEY2` from `symlink`, checks size and value, then confirms `SECURITY_KEY1` is not visible through `lgetxattr` on the symlink and fails with `ENODATA`. State is xattrs on both target and link. Dependencies include root, `<sys/xattr.h>`, filesystem xattr support, and permission to set `security.*` attributes. Risks are filesystem/security-policy differences. Test signals are expected value retrieval and `ENODATA` for target-only attr.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/lgetxattr/lgetxattr01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/lgetxattr/lgetxattr02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/lgetxattr/lgetxattr02.c

Purpose: negative `lgetxattr()` errno coverage for missing attribute, too-small buffer, and invalid path pointer. Setup creates a file and symlink and sets `security.ltptest` on the symlink. The table calls `lgetxattr("testfile", key, buf, size)` expecting `ENODATA`, `lgetxattr("symlink", key, one-byte buffer)` expecting `ERANGE`, and `lgetxattr((char *)-1, ...)` expecting `EFAULT`. State is one symlink xattr and stack buffers sized per case. Dependencies are root, xattr header/support, and ability to set `security.*`. Risks include filesystem returning `ENOTSUP` during setup. Test signal is exact errno match per row.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/lgetxattr/lgetxattr02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/link/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/link/Makefile

Purpose: builds the `link` syscall tests with standard LTP infrastructure. It includes `testcases.mk` and `generic_leaf_target.mk` without extra libraries. There is no runtime state in the Makefile. Integration points are the old and new LTP harnesses used by the C files and filesystem test setup such as read-only mount handling. Risks are minimal beyond build-system path correctness. Test signal is successful compilation of `link02`, `link04`, `link05`, `link08`, and any adjacent link tests in the directory.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/link/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/link/link02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/link/link02.c

Purpose: basic positive `link()` test. Setup creates `oldpath`; the test calls `link("oldpath", "newpath")`, then stats both paths and checks the original link count is greater than one and equal to the new link count. It unlinks `newpath` after validation. State is a tmpdir file and its hard link. Dependencies are filesystem support for hard links and LTP safe stat/touch helpers. Risks are filesystems that do not support hard links or unusual link count semantics. Test signals are syscall success and matching `st_nlink` values.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/link/link02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/link/link04.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/link/link04.c

Purpose: negative `link()` cases that should fail regardless of root except explicit permission setups. It tests invalid old/new paths, empty strings, non-directory path components, too-long paths, bad addresses, existing destination, and `EACCES` for write/search permission denial after switching to `nobody`. Setup creates regular files and directories, long path buffer, and replaces NULL test pointers with bad addresses. State is a tmpdir tree with permission changes and euid transitions for `EACCES` cases. Dependencies are root, `nobody`, path-resolution semantics, and LTP bad-address helpers. Risks are typo-driven desc checks and filesystem permission quirks. Test signal is exact expected errno per case.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/link/link04.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/link/link05.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/link/link05.c

Purpose: stress/positive `link()` test creating 999 hard links to one file. Setup creates a pid-derived base file name. The test loops from 1 to 999 creating `fname_N`, stats the original and each link, and verifies link counts are greater than one and match; cleanup unlinks all created links. State is many directory entries pointing to one inode. Dependencies are filesystem hard-link support and a link-count limit above 1000. Risks are filesystems with low max hard links or quota limitations. Test signal is all links created and link counts matching, with partial cleanup on failure.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/link/link05.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/link/link08.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/link/link08.c

Purpose: negative `link()` coverage for directory source (`EPERM`), cross-device link (`EXDEV`), read-only filesystem (`EROFS`), and symlink loop (`ELOOP`). Setup creates a directory source and constructs a deep self-referential symlink path; LTP mounts a read-only filesystem at `mntpoint`. Cases call `link(oldpath, newpath)` and verify errno. State includes a directory, symlink loop tree, and read-only mount. Dependencies are root, rofs mount setup, and path traversal behavior. Risks include filesystem or kernel differences for linking directories and loop depth. Test signal is exact errno for each scenario.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/link/link08.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/linkat/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/linkat/Makefile

Purpose: builds `linkat` tests and suppresses format-string warnings with `CPPFLAGS += -Wno-error` because the legacy test sources have messy diagnostics. It includes LTP testcase and generic leaf rules. There is no runtime state. Integration points are old `test.h`, raw `__NR_linkat`, and safe macros in the C files. Risks are warning suppression hiding non-format issues only if warnings are globally promoted. Test signal is successful build despite legacy format strings.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/linkat/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/linkat/linkat01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/linkat/linkat01.c

Purpose: broad functional and errno test for raw `linkat()` with combinations of directory fds, absolute paths, cwd-relative paths, invalid fds, deleted directory fds, cross-device source, directory source, and invalid flags. Setup creates old/new/deleted directories, opens fds, removes one directory while retaining its fd, creates source file and FIFO, and computes absolute paths. Each test recreates destination directory, calls `__NR_linkat`, and for success writes through the reference source then reads through the link to verify same inode content. State is tmpdir directory fds and files. Dependencies are old LTP safe macros and `/proc/cpuinfo` for EXDEV. Risks are legacy cleanup and path/fd validation order. Test signals are expected errno or content equality.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/linkat/linkat01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/linkat/linkat02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/linkat/linkat02.c

Purpose: negative `linkat()` errno test for too-long names, existing destination, symlink loop with `AT_SYMLINK_FOLLOW`, permission denial, read-only filesystem, and hard-link limit (`EMLINK`). Setup requires root, acquires a block device, creates a filesystem/mountpoint, prepares files, symlink loop, permission test paths, and fills a directory to discover max hard links. Cases can run setup/cleanup hooks to drop euid for `EACCES` or remount read-only for `EROFS`. State includes mounted test filesystem, hardlink-saturated directory, and credential changes. Dependencies are device acquisition, mount support, `nobody`, and raw `__NR_linkat`. Risks include `EMLINK` inapplicability and mount cleanup. Test signals are expected errno or TCONF for unsuitable `EMLINK`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/linkat/linkat02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/listen/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/listen/Makefile

Purpose: builds the `listen` syscall tests with standard LTP rules and generic leaf targets. It has no special libraries or runtime configuration. Integration points are old `test.h`, socket safe macros, and libc networking headers used by `listen01.c`. Risks are minimal build-path issues. Test signal is successful compilation of `listen01`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/listen/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/listen/listen01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/listen/listen01.c

Purpose: negative `listen()` errno coverage for bad file descriptor, non-socket fd, and unsupported datagram socket. The old LTP harness table provides setup/cleanup hooks: one uses fd `400` for `EBADF`, one opens `/dev/null` for `ENOTSOCK`, and one creates a `PF_INET/SOCK_DGRAM` socket for `EOPNOTSUPP`. Each iteration calls `listen(s, backlog)` and compares both return value and errno. State is one descriptor per test case. Dependencies are networking/socket support and `/dev/null`. Risks are platform-specific errno for UDP listen, though Linux expects `EOPNOTSUPP`. Test signal is expected failure for each table row.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/listen/listen01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/listmount/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/listmount/Makefile

Purpose: builds `listmount` syscall tests. It includes standard LTP testcase rules and generic leaf target rules without extra libraries. Runtime feature gating appears in the C files through minimum kernel versions and raw syscall wrappers. Integration points are `lapi/mount.h`, `lapi/syscalls.h`, namespace/mount helpers, and statx support. Risks are older kernels lacking `listmount`. Test signal is successful compilation of the listmount test binaries.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/listmount/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/listmount/listmount.h -->
# sources/test-tools/ltp/testcases/kernel/syscalls/listmount/listmount.h

Purpose: shared wrapper for the `listmount` syscall. It defines `_GNU_SOURCE`, includes LTP test, mount, and syscall lapi headers, and provides `static inline ssize_t listmount(...)` that fills `mnt_id_req` with `MNT_ID_REQ_SIZE_VER0`, requested mount ID, and iterator parameter, then calls `tst_syscall(__NR_listmount, ...)`. State is caller-provided mount ID arrays and request values. Dependencies are the Linux mount API lapi and kernel syscall availability. Risks are ABI changes to `mnt_id_req` or versioned size. Test signal support is raw return value/errno consumed by the individual tests.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/listmount/listmount.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/listmount/listmount01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/listmount/listmount01.c

Purpose: verifies `listmount(LSMT_ROOT, ...)` recognizes the root mount in a fresh namespace. Setup unshares the mount namespace, chroots to LTP mountpoint, makes `/` private recursively, and uses `statx(...STATX_MNT_ID_UNIQUE)` to store the root mount ID. The run calls `listmount(LSMT_ROOT, 0, list, LISTSIZE, 0)` and expects exactly one result equal to `root_id`. State is a private mount namespace and chrooted root. Dependencies include kernel >= 6.8, mount device setup, `statx` unique mount IDs, and namespace support. Risks are chroot/namespace side effects isolated by LTP forking. Test signal is return count one and matching mount ID.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/listmount/listmount01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/listmount/listmount02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/listmount/listmount02.c

Purpose: compares one-shot and iterator-style `listmount()` enumeration. Setup unshares a mount namespace, chroots to the mountpoint, and makes `/` shared recursively. The run creates seven recursive bind mounts of `/`, producing `1 << 7` mount IDs, reads all IDs in one call, then repeatedly calls `listmount(LSMT_ROOT, last_id, ..., GROUPS_SIZE)` to page through groups of three, comparing the resulting arrays. State is a synthetic mount tree in a private namespace. Dependencies include kernel >= 6.8, mount namespace support, and bind mounts. Risks are count assumptions if mount propagation differs. Test signal is exact array equality, followed by unmounting each bind.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/listmount/listmount02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/listmount/listmount03.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/listmount/listmount03.c

Purpose: verifies `listmount()` returns `EPERM` when the mount point is not accessible after chroot/credential changes. Setup records `/` unique mount ID via `statx`, resolves `nobody`, then chroots to the temporary directory. The child drops effective GID/UID to `nobody` and calls `listmount(root_id, 0, list, LISTSIZE, 0)` expecting `EPERM`. State is a stored mount ID outside the child's accessible root and child credentials. Dependencies are root, kernel >= 6.8, `nobody`, `statx`, and chroot support. Risks are permission model changes around mount namespace visibility. Test signal is expected `EPERM`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/listmount/listmount03.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/listmount/listmount04.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/listmount/listmount04.c

Purpose: negative `listmount()` errno matrix for invalid request pointer, invalid result pointer, flags, request size, spare/mount namespace fd, param, mount ID zero, and nonexistent mount ID. It allocates a `mnt_id_req` buffer, fills fields per table, and calls raw `__NR_listmount`. Setup classifies kernels before/after 6.17.9 because invalid `mnt_ns_fd` changed expected errno from `EINVAL` to `EBADF`. State is a request buffer and fixed mount ID result array. Dependencies include kernel >= 6.11 and version-aware errno behavior. Risks are backports changing validation order. Test signals are expected `EFAULT`, `EINVAL`, `EBADF`, or `ENOENT`, with TCONF for version-inappropriate rows.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/listmount/listmount04.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/listxattr/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/listxattr/Makefile

Purpose: builds `listxattr` tests. It includes standard LTP testcase rules, adds `$(ACL_LIBS)` only for `listxattr04` outside this subset, and delegates to generic leaf targets. The two files in this work item need no extra libraries but depend on xattr headers at compile time. Runtime feature checks live in the C files. Risks are missing ACL libs affecting adjacent targets and missing xattr headers yielding TCONF code paths. Test signal is successful build.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/listxattr/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/listxattr/listxattr01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/listxattr/listxattr01.c

Purpose: positive `listxattr()` test ensuring a file's extended attribute names can be listed. Setup creates `testfile` and sets `security.ltptest1` to `"test"` with `SAFE_SETXATTR`. The test calls `listxattr(TESTFILE, buf, sizeof(buf))`, then scans the NUL-separated name list with `has_attribute()` for the expected key. State is one file with one xattr. Dependencies include root, `<sys/xattr.h>`, filesystem xattr support, and permission to set `security.*`. Risks include filesystem/security policy rejecting security attributes. Test signal is syscall success and presence of the expected attribute name.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/listxattr/listxattr01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/listxattr/listxattr02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/listxattr/listxattr02.c

Purpose: negative `listxattr()` errno coverage for too-small buffer (`ERANGE`), empty path (`ENOENT`), invalid path pointer (`EFAULT`), and too-long path (`ENAMETOOLONG`). Setup creates `testfile`, sets `security.ltptest`, and fills a `PATH_MAX + 2` long pathname buffer. Each case allocates a stack buffer of the requested size and expects `listxattr()` failure with the configured errno. State is one file with xattr plus path buffers. Dependencies include root, xattr header/support, and path validation semantics. Risks are filesystem xattr policy during setup. Test signal is exact errno match per row.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/listxattr/listxattr02.c -->
