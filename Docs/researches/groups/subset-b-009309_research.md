# subset-b-009309 research

Grouped research report for LTP syscall tests, pjdfstest shell helpers, and pynfs RPC/NFSv4 support files. Each section preserves the exact source path and is wrapped for reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/utils/inotify.h -->
# sources/test-tools/ltp/testcases/kernel/syscalls/utils/inotify.h

Purpose: vendored Linux inotify interface header used by older LTP syscall tests that need stable inotify constants and structures independent of host libc/kernel headers. It defines the userspace `struct inotify_event`, event masks, helper masks, and, behind `__KERNEL__`, the historical kernel producer/consumer API surface.

Important APIs/types/functions: `struct inotify_event` carries watch descriptor, mask, cookie, name length, and trailing name bytes. Public masks include `IN_ACCESS`, `IN_MODIFY`, `IN_ATTRIB`, close/open/move/create/delete/self events, `IN_UNMOUNT`, `IN_Q_OVERFLOW`, `IN_IGNORED`, flag bits such as `IN_ONLYDIR`, `IN_DONT_FOLLOW`, `IN_MASK_ADD`, `IN_ISDIR`, and `IN_ONESHOT`, plus aggregate `IN_CLOSE`, `IN_MOVE`, and `IN_ALL_EVENTS`. Kernel-only declarations cover `struct inotify_watch`, `struct inotify_operations`, queueing helpers, watch add/remove/find APIs, and CONFIG_INOTIFY stubs returning `-EOPNOTSUPP` where appropriate.

Control flow/state: the userspace portion is declarative. Kernel-only code models reference-counted watch state in `inotify_watch`, with comments documenting handle-list and inode-list locking. When CONFIG_INOTIFY is disabled, inline no-op/error stubs preserve buildability while preventing runtime use.

Dependencies/integration: includes `<linux/types.h>` for fixed-width kernel-style types and, for kernel builds, dcache/fs/list/atomic infrastructure. LTP consumers can compile against exact mask values when probing inotify syscalls.

Risks/test signals: this is a compatibility snapshot; divergence from modern kernel headers can hide newer flags or ABI changes. Its value is constant stability, so audits should compare masks and `struct inotify_event` layout against target kernel UAPI when diagnosing inotify test mismatches.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/utils/inotify.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/utils/mq.h -->
# sources/test-tools/ltp/testcases/kernel/syscalls/utils/mq.h

Purpose: common POSIX message queue setup/cleanup helper for LTP mqueue syscall tests. It creates unique blocking and nonblocking queue names, initializes shared message buffers, installs a SIGINT handler, and drains/unlinks queues during cleanup.

Important APIs/types/functions: globals `queue_name`, `queue_name_nonblock`, `smsg`, and `act` are shared with including tests, which are expected to define descriptors such as `fd_root`, `fd`, and `fd_nonblock`. `setup_common()` creates `/test_mqueue_<pid>` queues via `SAFE_MQ_OPEN`, opens `/` into `fd_root`, and fills `smsg` with deterministic bytes. `cleanup_common()` closes positive descriptors and `mq_unlink()`s both names. `cleanup_queue()` uses `mq_getattr()` and repeated `mq_receive()` to drain queued messages.

Control flow/state: setup is idempotent for the generated names because it calls cleanup before creating queues. Persistent state is kernel POSIX mqueue objects under names derived from PID; cleanup removes them even if prior test iterations left residue.

Dependencies/integration: depends on LTP safe wrappers, `tst_sig_proc.h`, and `tst_safe_posix_ipc.h`. Including tests must link against POSIX realtime/mqueue support as required by the LTP build rules.

Risks/test signals: descriptor-close guards use `> 0`, so descriptor 0 would not be closed, though these opens normally return higher values. Draining logs every message and treats `mq_getattr()` failure as `TBROK`; tests using this helper should verify queue attributes and cleanup noise when failures occur.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/utils/mq.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/utils/mq_timed.h -->
# sources/test-tools/ltp/testcases/kernel/syscalls/utils/mq_timed.h

Purpose: extension helper for LTP timed POSIX mqueue tests, adding libc, legacy syscall, and time64 syscall variants plus common timeout/signal test-case metadata.

Important APIs/types/functions: `variants[]` maps each available ABI to `clock_gettime`, `mqt_send`, `mqt_receive`, a `tst_ts` representation, and a human-readable description. `struct test_case` describes descriptor, length, priority, requested timestamp, invalid message/timespec address flags, signal/timeout behavior, expected return, and expected errno. `set_sig()` arms a future absolute timeout and starts a signal-sending helper. `set_timeout()` sets a near-future absolute timeout. `kill_pid()` terminates and waits for the signal helper.

Control flow/state: including tests iterate `variants` through `tst_variant` and use the helper to construct absolute `CLOCK_REALTIME` deadlines. `set_sig()` creates a child process that repeatedly sends `SIGINT`; cleanup must call `kill_pid()` to prevent leaked helpers.

Dependencies/integration: includes `mq.h`, `time64_variants.h`, and `tst_timer.h`, so it bridges POSIX mqueue tests with LTP time64 syscall coverage. Compile-time syscall availability gates the legacy and time64 entries.

Risks/test signals: timing margins are intentionally small for timeout tests and larger for signal interruption; slow systems can turn expected timeout/signal behavior into flakes. Variant-specific failures identify libc wrapper, old kernel timespec, or time64 ABI regressions.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/utils/mq_timed.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/utils/newer_64.mk -->
# sources/test-tools/ltp/testcases/kernel/syscalls/utils/newer_64.mk

Purpose: LTP make fragment that builds normal syscall tests and optional `_64` variants for syscalls with newer 64-bit interfaces. It mirrors the older compat make pattern while adding a `TST_USE_NEWER64_SYSCALL` preprocessor flag for generated suffixed targets.

Important APIs/types/functions: appends include paths for the source dir and `../utils`, discovers `SRCS` from `*.c`, builds `MAKE_TARGETS` from source basenames, and conditionally adds `_64` targets unless `TST_NEWER_64_SYSCALL=no`. `DEF_64` is `TST_USE_NEWER64_SYSCALL`; `%_64` adds `-D$(DEF_64)=1`, and `%_64.o: %.c` compiles the same source under the suffixed object name.

Control flow/state: make-time logic checks for `../utils/newer_64.h` and sets `HAS_NEWER_64`, but the comments note this block is questionable because not all users have the matching header/define. No runtime state exists.

Dependencies/integration: consumed by syscall test directories that need paired native/newer-64 builds. It depends on LTP's common pattern rules and source-tree variables such as `abs_srcdir` and `COMPILE.c`.

Risks/test signals: the fragment can silently create extra targets that fail if source code does not honor `TST_USE_NEWER64_SYSCALL`. Build logs for unexpected `_64` target failures are the primary signal; setting `TST_NEWER_64_SYSCALL=no` suppresses the variant path.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/utils/newer_64.mk -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/utime/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/utime/Makefile

Purpose: LTP leaf build file for the `utime` syscall test directory. It anchors this directory under the LTP kernel syscall test hierarchy and delegates target discovery, compilation rules, install layout, and harness metadata to the shared make infrastructure.

Important APIs/types/functions: defines `top_srcdir ?= ../../../..`, includes `include/mk/testcases.mk`, and includes `include/mk/generic_leaf_target.mk`. There are no local targets except where noted by the directory-specific report.

Control flow: GNU make resolves `top_srcdir`, loads the common testcase rules, then the generic leaf target builds the C test programs in this directory. State is build-time only: object files, binaries, and dependency tracking are handled by the common LTP rules rather than by this file.

Dependencies/integration: integrates the directory with the LTP build system and assumes the surrounding source tree provides the common mk fragments, compiler settings, and install/test metadata. Risks are mostly build-integration risks: changing includes or `top_srcdir` would orphan the tests from standard LTP discovery.

Test signals: successful make traversal should produce the directory's syscall test binaries; failures here indicate harness/build plumbing issues rather than runtime syscall behavior.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/utime/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/utime/utime01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/utime/utime01.c

Purpose: verifies root-owned execution of `utime(path, NULL)` updates a file's access and modification times to the current filesystem timestamp window after first proving explicit `utimbuf` values are honored.

Important APIs/types/functions: `setup()` creates `mntpoint/tmp_file` with mode `0444`; `run()` uses `utime()`, `SAFE_STAT()`, `tst_fs_timestamp_start/end()`, `TST_EXP_PASS`, and `TST_EXP_EQ_LI`. The `tst_test` metadata requires root, a mounted test device, all filesystem coverage, and skips `vfat`/`exfat`.

Control flow/state: the test first sets deterministic old atime/mtime, validates them, then calls `utime(TEMP_FILE, NULL)` and compares both timestamps against the pre/post window. Persistent state is one mounted test file whose timestamps are mutated.

Dependencies/integration: uses LTP clock helpers to handle filesystem timestamp granularity and common mount orchestration for cross-filesystem testing.

Risks/test signals: failures are timestamp range mismatches or syscall errors. Filesystems with weak timestamp semantics are skipped; remaining flakes usually indicate granularity, clock, or permission behavior differences.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/utime/utime01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/utime/utime02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/utime/utime02.c

Purpose: verifies an unprivileged effective user can call `utime(path, NULL)` on a file that it owns, even when the file mode is read-only.

Important APIs/types/functions: `setup()` gets `nobody`, creates `mntpoint/tmp_file`, chowns it to that UID/GID, then switches effective UID. `run()` uses explicit `utimbuf` setup followed by the `NULL` timestamp update, `SAFE_STAT()`, and LTP timestamp bounds.

Control flow/state: after ownership and euid setup, the test confirms explicit atime/mtime assignment works, then verifies `NULL` updates both times to current filesystem time. State changes are confined to ownership and timestamps of the temporary file.

Dependencies/integration: requires root to prepare ownership and switch credentials, plus the LTP mounted filesystem matrix. It skips `vfat`/`exfat` where ownership/timestamp semantics do not match the test.

Risks/test signals: failures distinguish permission errors from timestamp-range errors. A missing `nobody` account or unusual UID mapping would break setup rather than the syscall assertion.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/utime/utime02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/utime/utime03.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/utime/utime03.c

Purpose: verifies an unprivileged non-owner with write permission can call `utime(path, NULL)` to set atime and mtime to current time.

Important APIs/types/functions: `setup()` selects two non-root UIDs using `SAFE_GETPWNAM("nobody")` and `tst_get_uids()`, creates `mntpoint/tmp_file` with mode `0766`, and chowns it to `nobody`. `run()` establishes initial explicit timestamps, switches euid to the second user, calls `utime(NULL)`, restores root euid, and validates the timestamps.

Control flow/state: the key branch is credential switching around the `utime()` call. The file remains owned by `nobody`, while the caller is a different user that relies on write access.

Dependencies/integration: depends on LTP UID discovery and mounted filesystem timestamp helpers. It is root-only because it changes ownership and effective UID.

Risks/test signals: meaningful failures are `utime()` permission denial or atime/mtime outside the measured window. Systems with insufficient distinct test UIDs or unusual ownership semantics can fail setup.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/utime/utime03.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/utime/utime04.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/utime/utime04.c

Purpose: verifies privileged `utime(path, &times)` can set exact access and modification timestamps on a read-only file.

Important APIs/types/functions: global `times` contains `actime=20000` and `modtime=10000`. `setup()` creates `mntpoint/tmp_file` with mode `0444`; `run()` calls `utime()` and validates `st_mtime` and `st_atime` through `SAFE_STAT()` and `TST_EXP_EQ_LI`.

Control flow/state: single positive syscall path after setup. Persistent state is the timestamp pair on the temporary mounted file.

Dependencies/integration: requires root and LTP mounted filesystem coverage, with `vfat`/`exfat` skipped due to timestamp/permission differences.

Risks/test signals: failures are exact timestamp mismatches or permission/syscall errors. Because it checks second-resolution `st_atime/st_mtime`, filesystems with nonstandard rounding are the main portability risk.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/utime/utime04.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/utime/utime05.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/utime/utime05.c

Purpose: verifies an unprivileged owner can set explicit atime and mtime with `utime(path, &times)`.

Important APIs/types/functions: `setup()` chmods the mount point to `0777`, switches euid to `nobody`, and creates `mntpoint/tmp_file`; `times` holds fixed values `20000` and `10000`. `run()` calls `utime()` and validates both stat fields.

Control flow/state: after root prepares a writable mount point, all file creation and timestamp mutation happen as `nobody`. The test checks ownership-based permission rather than privilege.

Dependencies/integration: uses LTP safe account lookup, euid switching, mounted filesystem orchestration, and skips `vfat`/`exfat`.

Risks/test signals: the primary risks are mountpoint permission setup and filesystems that do not preserve exact test timestamps. Runtime failures directly indicate `utime()` permission or timestamp-setting regressions.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/utime/utime05.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/utime/utime06.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/utime/utime06.c

Purpose: negative coverage for `utime()` error handling: `EACCES` without write permission and `times == NULL`, `ENOENT` for a missing path, `EPERM` for explicit times by a non-owner, and `EROFS` on a read-only filesystem.

Important APIs/types/functions: `tcases[]` defines pathname, expected errno, optional `utimbuf`, and description. `setup()` creates `tmp_file`, switches to `nobody`, and the `tst_test` metadata requests a tmpdir plus read-only filesystem mount.

Control flow/state: each test case calls `utime()` once through `TST_EXP_FAIL`. State is a root-owned writable-mode file, an empty path for missing-file testing, and a read-only mount point.

Dependencies/integration: relies on LTP `needs_rofs` infrastructure and root credential setup. It does not mount the all-filesystem matrix; it targets permission and read-only behavior.

Risks/test signals: failures expose wrong errno mapping or unexpected success. The empty-string `ENOENT` case depends on Linux path handling; read-only behavior depends on the LTP rofs fixture being active.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/utime/utime06.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/utime/utime07.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/utime/utime07.c

Purpose: verifies `utime()` follows symbolic links for timestamp updates and reports correct errors for dangling and self-referential symlinks.

Important APIs/types/functions: `create_symlink()` wraps `SAFE_SYMLINK()` and verifies `S_IFLNK` with `SAFE_LSTAT()`. `test_utime()` symlinks to the tmpdir and expects target atime/mtime deltas of `TIME_DIFF`; `test_utime_no_path()` expects `ENOENT`; `test_utime_loop()` expects `ELOOP`.

Control flow/state: `run()` executes three independent subtests, each creating and unlinking its own symlink. The positive case uses `SAFE_STAT()` rather than `lstat()`, intentionally checking the target path after symlink resolution.

Dependencies/integration: uses only an LTP tmpdir and standard symlink support; no root or mount matrix is required.

Risks/test signals: exact timestamp-delta checks can be sensitive to filesystem timestamp resolution. Error cases are strong signals for path resolution behavior: dangling target must not be created, and a symlink loop must fail with `ELOOP`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/utime/utime07.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/utimensat/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/utimensat/Makefile

Purpose: LTP leaf build file for the `utimensat` syscall test directory. It anchors this directory under the LTP kernel syscall test hierarchy and delegates target discovery, compilation rules, install layout, and harness metadata to the shared make infrastructure.

Important APIs/types/functions: defines `top_srcdir ?= ../../../..`, includes `include/mk/testcases.mk`, and includes `include/mk/generic_leaf_target.mk`. There are no local targets except where noted by the directory-specific report.

Control flow: GNU make resolves `top_srcdir`, loads the common testcase rules, then the generic leaf target builds the C test programs in this directory. State is build-time only: object files, binaries, and dependency tracking are handled by the common LTP rules rather than by this file.

Dependencies/integration: integrates the directory with the LTP build system and assumes the surrounding source tree provides the common mk fragments, compiler settings, and install/test metadata. Risks are mostly build-integration risks: changing includes or `top_srcdir` would orphan the tests from standard LTP discovery.

Test signals: successful make traversal should produce the directory's syscall test binaries; failures here indicate harness/build plumbing issues rather than runtime syscall behavior.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/utimensat/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/utimensat/utimensat01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/utimensat/utimensat01.c

Purpose: broad `utimensat()` ABI and permission test covering read-only/writable files, append-only and immutable inode flags, `UTIME_NOW`, `UTIME_OMIT`, explicit timestamps, bad addresses, bad dirfd/path combinations, and old/time64 syscall variants.

Important APIs/types/functions: `tcase[]` encodes dirfd, pathname, synthetic time tuple, flags, open flags, inode attributes, mode, and expected errno. `variants[]` selects `__NR_utimensat` or `__NR_utimensat_time64`. `multi_set_time()` fills libc/old-kernel/time64 timespec unions. `update_error()` normalizes immutable-file errno across kernel versions. `change_attr()` uses `FS_IOC_GETFLAGS/SETFLAGS`. `reset_time()` resets timestamps before each case. `run()` orchestrates per-case setup, syscall, attribute cleanup, and stat validation.

Control flow/state: every case opens/creates the target if needed, resets times to zero, applies requested inode flags, calls the selected ABI, removes flags, then either checks errno or verifies atime/mtime changed exactly according to `mytime` flags. Persistent state includes `mntpoint/test_file`, `mntpoint/test_dir`, and transient inode flags.

Dependencies/integration: depends on LTP time64 helpers, `lapi/fs.h`, `lapi/utime.h`, root, and a mounted filesystem that supports tested attributes. `ENOTTY` on flag ioctls is treated as `TCONF`.

Risks/test signals: this test is sensitive to kernel version errno changes, filesystem support for immutable/append flags, and timestamp truthiness because success validation expects zero/nonzero changes after reset. Variant-specific failures isolate old-timespec versus time64 ABI regressions.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/utimensat/utimensat01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/utimes/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/utimes/Makefile

Purpose: LTP leaf build file for the `utimes` syscall test directory. It anchors this directory under the LTP kernel syscall test hierarchy and delegates target discovery, compilation rules, install layout, and harness metadata to the shared make infrastructure.

Important APIs/types/functions: defines `top_srcdir ?= ../../../..`, includes `include/mk/testcases.mk`, and includes `include/mk/generic_leaf_target.mk`. There are no local targets except where noted by the directory-specific report.

Control flow: GNU make resolves `top_srcdir`, loads the common testcase rules, then the generic leaf target builds the C test programs in this directory. State is build-time only: object files, binaries, and dependency tracking are handled by the common LTP rules rather than by this file.

Dependencies/integration: integrates the directory with the LTP build system and assumes the surrounding source tree provides the common mk fragments, compiler settings, and install/test metadata. Risks are mostly build-integration risks: changing includes or `top_srcdir` would orphan the tests from standard LTP discovery.

Test signals: successful make traversal should produce the directory's syscall test binaries; failures here indicate harness/build plumbing issues rather than runtime syscall behavior.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/utimes/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/utimes/utimes01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/utimes/utimes01.c

Purpose: verifies `utimes()` success for owner timestamp updates and expected failures for `EACCES`, `ENOENT`, `EFAULT`, `EPERM`, and `EROFS`.

Important APIs/types/functions: `tcases[]` pairs pathnames with `struct timeval` arrays and expected errno. `setup()` creates a root-owned inaccessible file, switches to `nobody`, and creates an owned file. `utimes_verify()` snapshots existing times for success cases, calls `utimes()`, checks `TST_ERR`, and restores the original timestamps.

Control flow/state: each case is independent. Success cases mutate `testfile1` timestamps using alternate atime/mtime arrays, then restore the prior values; negative cases exercise missing, NULL, non-owned, and read-only mount paths.

Dependencies/integration: requires root to switch euid and LTP `needs_rofs` for the read-only path. It uses the legacy LTP syscall harness macros rather than time64 variants.

Risks/test signals: the test checks errno through `TST_ERR`; unexpected success or wrong errno are the main signals. The restoration call can turn a success assertion into `TBROK` if timestamp restoration fails.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/utimes/utimes01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/vfork/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/vfork/Makefile

Purpose: LTP leaf build file for the `vfork` syscall test directory. It anchors this directory under the LTP kernel syscall test hierarchy and delegates target discovery, compilation rules, install layout, and harness metadata to the shared make infrastructure.

Important APIs/types/functions: defines `top_srcdir ?= ../../../..`, includes `include/mk/testcases.mk`, and includes `include/mk/generic_leaf_target.mk`. There are no local targets except where noted by the directory-specific report.

Control flow: GNU make resolves `top_srcdir`, loads the common testcase rules, then the generic leaf target builds the C test programs in this directory. State is build-time only: object files, binaries, and dependency tracking are handled by the common LTP rules rather than by this file.

Dependencies/integration: integrates the directory with the LTP build system and assumes the surrounding source tree provides the common mk fragments, compiler settings, and install/test metadata. Risks are mostly build-integration risks: changing includes or `top_srcdir` would orphan the tests from standard LTP discovery.

Test signals: successful make traversal should produce the directory's syscall test binaries; failures here indicate harness/build plumbing issues rather than runtime syscall behavior.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/vfork/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/vfork/vfork01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/vfork/vfork01.c

Purpose: verifies a `vfork()` child observes the same process attributes as its parent for effective/real/saved UID and GID, umask, current working directory, and root/current directory inode/device numbers.

Important APIs/types/functions: `run()` captures parent `umask`, `getcwd()`, `SAFE_GETRESUID/GID`, `SAFE_STAT()` for cwd and `/`, then a `vfork()` child compares those values using LTP equality macros and `tst_check_resuid/resgid()`. The child exits with `_exit(0)`.

Control flow/state: parent state is sampled before `vfork`; child performs only comparisons and must not return through parent stack. Parent reaps children and frees the allocated cwd string.

Dependencies/integration: uses LTP UID helpers and marks `.forks_child = 1`. No persistent files are created.

Risks/test signals: `vfork()` shares address space until `_exit`, so adding non-async-safe complex behavior in the child would be risky. Current failures signal attribute inheritance regressions or unexpected cwd/root namespace differences.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/vfork/vfork01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/vfork/vfork02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/vfork/vfork02.c

Purpose: verifies a signal pending in the parent is not pending in a `vfork()` child.

Important APIs/types/functions: `setup()` installs a `SIGUSR1` handler, blocks `SIGUSR1`, sends it to the parent, and verifies it is pending. `run()` uses `vfork()` and the child checks `sigpending()` plus `sigismember(SIGUSR1) == 0`. `cleanup()` unblocks the signal.

Control flow/state: parent accumulates a blocked pending signal before the test. The child inspects its own pending set and exits without disturbing parent cleanup.

Dependencies/integration: standard POSIX signal APIs via LTP safe wrappers; `.forks_child = 1` ensures child reaping.

Risks/test signals: signal-mask inheritance and pending-signal semantics are subtle; this specifically asserts pending signals are per-process and not inherited. Failures are either setup inability to create the pending signal or child observation of inherited pending state.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/vfork/vfork02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/vhangup/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/vhangup/Makefile

Purpose: LTP leaf build file for the `vhangup` syscall test directory. It anchors this directory under the LTP kernel syscall test hierarchy and delegates target discovery, compilation rules, install layout, and harness metadata to the shared make infrastructure.

Important APIs/types/functions: defines `top_srcdir ?= ../../../..`, includes `include/mk/testcases.mk`, and includes `include/mk/generic_leaf_target.mk`. There are no local targets except where noted by the directory-specific report.

Control flow: GNU make resolves `top_srcdir`, loads the common testcase rules, then the generic leaf target builds the C test programs in this directory. State is build-time only: object files, binaries, and dependency tracking are handled by the common LTP rules rather than by this file.

Dependencies/integration: integrates the directory with the LTP build system and assumes the surrounding source tree provides the common mk fragments, compiler settings, and install/test metadata. Risks are mostly build-integration risks: changing includes or `top_srcdir` would orphan the tests from standard LTP discovery.

Test signals: successful make traversal should produce the directory's syscall test binaries; failures here indicate harness/build plumbing issues rather than runtime syscall behavior.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/vhangup/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/vhangup/vhangup01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/vhangup/vhangup01.c

Purpose: verifies `vhangup()` fails with `EPERM` when called by a non-root user.

Important APIs/types/functions: `setup()` resolves the `nobody` UID. `run()` forks; the child calls `setreuid(nobody, nobody)`, invokes `tst_syscall(__NR_vhangup)`, and checks return `-1` with `TST_ERR == EPERM`.

Control flow/state: privilege drop happens only in the child, while the root parent waits. No persistent state is created.

Dependencies/integration: requires root and LTP raw syscall wrapper because libc exposure can vary. `.forks_child = 1` isolates credential changes.

Risks/test signals: systems without a `nobody` account fail setup. Runtime failures indicate changed privilege checks or wrong errno for unprivileged virtual terminal hangup.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/vhangup/vhangup01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/vhangup/vhangup02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/vhangup/vhangup02.c

Purpose: verifies privileged `vhangup()` can succeed from a child process that has created a new session.

Important APIs/types/functions: `run()` forks; the child calls `setsid()` and then `tst_syscall(__NR_vhangup)`, reporting pass if the syscall does not return `-1`.

Control flow/state: the parent waits while the child isolates itself as a session leader before invoking the syscall. There is no file or terminal fixture beyond the process session state.

Dependencies/integration: root is required. The test uses the LTP raw syscall path and child forking metadata.

Risks/test signals: behavior can depend on available controlling terminal/session context in the test environment. A failure with errno is a direct signal that privileged `vhangup()` was rejected or unsupported.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/vhangup/vhangup02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/vmsplice/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/vmsplice/Makefile

Purpose: LTP leaf build file for the `vmsplice` syscall test directory. It anchors this directory under the LTP kernel syscall test hierarchy and delegates target discovery, compilation rules, install layout, and harness metadata to the shared make infrastructure.

Important APIs/types/functions: defines `top_srcdir ?= ../../../..`, includes `include/mk/testcases.mk`, and includes `include/mk/generic_leaf_target.mk`. There are no local targets except where noted by the directory-specific report.

Control flow: GNU make resolves `top_srcdir`, loads the common testcase rules, then the generic leaf target builds the C test programs in this directory. State is build-time only: object files, binaries, and dependency tracking are handled by the common LTP rules rather than by this file.

Dependencies/integration: integrates the directory with the LTP build system and assumes the surrounding source tree provides the common mk fragments, compiler settings, and install/test metadata. Risks are mostly build-integration risks: changing includes or `top_srcdir` would orphan the tests from standard LTP discovery.

Test signals: successful make traversal should produce the directory's syscall test binaries; failures here indicate harness/build plumbing issues rather than runtime syscall behavior.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/vmsplice/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/vmsplice/vmsplice01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/vmsplice/vmsplice01.c

Purpose: positive data-integrity test for splicing a 128 KiB user buffer into a pipe with `vmsplice()`, then from pipe to file with `splice()`, and reading the file back.

Important APIs/types/functions: `setup()` fills `buffer` with byte pattern. `vmsplice_test()` opens `vmsplice_test_file`, creates a pipe, polls for writable space, repeatedly calls `vmsplice()` on a moving `iovec`, and `SAFE_SPLICE()`s written bytes to the file. `check_file()` reads back the full block and compares byte-by-byte.

Control flow/state: the iovec advances until all bytes are moved or `vmsplice()` returns zero. Persistent state is one temporary file containing the spliced buffer.

Dependencies/integration: depends on `lapi/splice.h`, `lapi/vmsplice.h`, poll, pipes, and LTP tmpdir. NFS is skipped because splice/file semantics may differ.

Risks/test signals: partial writes are expected and handled; data mismatch identifies pipe/splice corruption. A hang would imply poll/write progress issues, while syscall errors are `TBROK`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/vmsplice/vmsplice01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/vmsplice/vmsplice02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/vmsplice/vmsplice02.c

Purpose: negative `vmsplice()` errno coverage for invalid fd, non-pipe fd, and too many iovec segments.

Important APIs/types/functions: `tcases[]` maps descriptor pointer, `iovec`, segment count, and expected errno: `EBADF` for `-1`, `EBADF` for a regular file, and `EINVAL` for `IOV_MAX + 1`. `setup()` opens a temp file, creates a pipe, and initializes the iovec.

Control flow/state: each test case calls `vmsplice()` once and checks return `-1` plus errno. State consists of one regular fd, one pipe, and a static buffer.

Dependencies/integration: uses LTP tmpdir and Linux `vmsplice` lapi wrapper; skips NFS for the regular file fixture.

Risks/test signals: errno expectations are the signal. If a kernel accepts a non-pipe fd or overlarge iov count, the test fails as a syscall contract regression.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/vmsplice/vmsplice02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/vmsplice/vmsplice03.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/vmsplice/vmsplice03.c

Purpose: verifies `vmsplice()` can move data from a pipe into user memory using a read-end pipe descriptor and an output iovec.

Important APIs/types/functions: `setup()` fills a 64 KiB `buffer`. LTP `.bufs` allocates an iovec of the same size. `vmsplice_test()` clears the destination, writes the source buffer into a pipe, calls `vmsplice(pipes[0], iov, 1, 0)`, then compares destination bytes to the source.

Control flow/state: the pipe is created and closed within the test. Successful writes may be partial, but the loop compares up to `TEST_BLOCK_SIZE` and reports pass when all written bytes match.

Dependencies/integration: depends on LTP buffer allocation and `lapi/vmsplice.h`; no tmpdir is needed.

Risks/test signals: partial transfer handling is somewhat loose because the comparison loop iterates over the full block but pass condition uses `i == written`. Failures signal unsupported pipe-to-user transfer or data corruption.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/vmsplice/vmsplice03.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/vmsplice/vmsplice04.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/vmsplice/vmsplice04.c

Purpose: tests `vmsplice()` behavior on a full pipe: nonblocking mode must fail with `EAGAIN`, while blocking mode should sleep rather than write.

Important APIs/types/functions: `setup()` creates a pipe, obtains `F_GETPIPE_SZ`, allocates a buffer of that size, fills the pipe using `vmsplice()`, and stores the iovec. `vmsplice_test()` first calls with `SPLICE_F_NONBLOCK`, then forks a child that calls blocking `vmsplice()`. The parent uses `TST_PROCESS_STATE_WAIT(pid, 'S', 1000)` to confirm sleep and then kills the child.

Control flow/state: pipe fullness is established once in setup and consumed only by attempted writes. The child is expected to block until killed.

Dependencies/integration: requires Linux pipe-size fcntl, `SPLICE_F_NONBLOCK`, LTP process-state polling, and `.forks_child = 1`.

Risks/test signals: scheduler timing can affect the blocked-state check. Nonblocking success or wrong errno indicates pipe capacity/accounting regression; blocking child returning indicates incorrect full-pipe behavior.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/vmsplice/vmsplice04.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/wait/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/wait/Makefile

Purpose: LTP leaf build file for the `wait` syscall test directory. It anchors this directory under the LTP kernel syscall test hierarchy and delegates target discovery, compilation rules, install layout, and harness metadata to the shared make infrastructure.

Important APIs/types/functions: defines `top_srcdir ?= ../../../..`, includes `include/mk/testcases.mk`, and includes `include/mk/generic_leaf_target.mk`. There are no local targets except where noted by the directory-specific report.

Control flow: GNU make resolves `top_srcdir`, loads the common testcase rules, then the generic leaf target builds the C test programs in this directory. State is build-time only: object files, binaries, and dependency tracking are handled by the common LTP rules rather than by this file.

Dependencies/integration: integrates the directory with the LTP build system and assumes the surrounding source tree provides the common mk fragments, compiler settings, and install/test metadata. Risks are mostly build-integration risks: changing includes or `top_srcdir` would orphan the tests from standard LTP discovery.

Test signals: successful make traversal should produce the directory's syscall test binaries; failures here indicate harness/build plumbing issues rather than runtime syscall behavior.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/wait/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/wait/wait01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/wait/wait01.c

Purpose: verifies `wait(NULL)` fails with `ECHILD` when the calling process has no unwaited-for children.

Important APIs/types/functions: `verify_wait()` is a single `TST_EXP_FAIL2(wait(NULL), ECHILD)` assertion.

Control flow/state: no setup or child creation is performed; the process table state of interest is the absence of child processes.

Dependencies/integration: minimal LTP harness only. The test must run in isolation from stray children created by the harness.

Risks/test signals: any returned pid or errno other than `ECHILD` fails the basic wait contract. The test is intentionally narrow and low-flake.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/wait/wait01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/wait/wait02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/wait/wait02.c

Purpose: verifies `wait()` returns the pid and exit status of a terminated child.

Important APIs/types/functions: `verify_wait()` forks a child that exits with status 1, calls `wait(&status)`, checks returned pid, `WIFEXITED(status)`, and `WEXITSTATUS(status)`.

Control flow/state: one child exits immediately; the parent reaps exactly that child and inspects the wait status word.

Dependencies/integration: LTP `.forks_child = 1` and safe fork wrappers.

Risks/test signals: failures identify wrong child selection, broken status encoding, or wait errors. The explicit exit code makes the signal unambiguous.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/wait/wait02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/wait4/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/wait4/Makefile

Purpose: LTP leaf build file for the `wait4` syscall test directory. It anchors this directory under the LTP kernel syscall test hierarchy and delegates target discovery, compilation rules, install layout, and harness metadata to the shared make infrastructure.

Important APIs/types/functions: defines `top_srcdir ?= ../../../..`, includes `include/mk/testcases.mk`, and includes `include/mk/generic_leaf_target.mk`. There are no local targets except where noted by the directory-specific report.

Control flow: GNU make resolves `top_srcdir`, loads the common testcase rules, then the generic leaf target builds the C test programs in this directory. State is build-time only: object files, binaries, and dependency tracking are handled by the common LTP rules rather than by this file.

Dependencies/integration: integrates the directory with the LTP build system and assumes the surrounding source tree provides the common mk fragments, compiler settings, and install/test metadata. Risks are mostly build-integration risks: changing includes or `top_srcdir` would orphan the tests from standard LTP discovery.

Test signals: successful make traversal should produce the directory's syscall test binaries; failures here indicate harness/build plumbing issues rather than runtime syscall behavior.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/wait4/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/wait4/wait401.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/wait4/wait401.c

Purpose: verifies `wait4(pid, &status, 0, &rusage)` waits for a specific child and reports normal zero exit status.

Important APIs/types/functions: child waits until parent is sleeping via `TST_PROCESS_STATE_WAIT(getppid(), 'S', 0)` then exits. Parent calls `wait4()`, checks pid, `WIFEXITED`, and `WEXITSTATUS == 0`; `struct rusage` is supplied but not inspected.

Control flow/state: the child synchronization increases confidence the parent actually blocks in `wait4()`. State is only process lifecycle and returned status.

Dependencies/integration: uses BSD `wait4` interface, LTP fork metadata, and process state polling.

Risks/test signals: status and pid mismatches are direct. The rusage pointer path is covered for ABI validity, but resource contents are not validated.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/wait4/wait401.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/wait4/wait402.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/wait4/wait402.c

Purpose: verifies `wait4()` returns `ECHILD` when asked to wait for an invalid pid larger than the kernel `pid_max`.

Important APIs/types/functions: `setup()` reads `PATH_KERN_PID_MAX`; `run()` calls `wait4(pid_max + 1, &status, 0, &rusage)` through `TST_EXP_FAIL2`.

Control flow/state: no children are created. The test depends on current kernel pid namespace limits from procfs.

Dependencies/integration: LTP `SAFE_FILE_SCANF` and `PATH_KERN_PID_MAX` constants.

Risks/test signals: a stale or namespaced pid_max read would affect the invalid-pid choice. Expected failure is `ECHILD`, not `ESRCH`, for this out-of-range positive pid.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/wait4/wait402.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/wait4/wait403.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/wait4/wait403.c

Purpose: regression test that `wait4(INT_MIN, ...)` is rejected safely with `ESRCH` rather than triggering signed negation undefined behavior in process-group lookup.

Important APIs/types/functions: `run()` calls `wait4(INT_MIN, &status, 0, &rusage)` and expects `ESRCH`. Metadata enables kernel taint checks and tags Linux commit `dd83c161fbcc`.

Control flow/state: single negative syscall call with no children. The special value exercises the pid-negation edge case.

Dependencies/integration: relies on LTP taint detection for warning/oops side effects and standard `wait4` ABI.

Risks/test signals: wrong errno or kernel taint indicates the regression path. On kernels without the fix but without UBSAN, behavior may still be `ECHILD`, which this test treats as failure.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/wait4/wait403.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/waitid/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/waitid/Makefile

Purpose: LTP leaf build file for the `waitid` syscall test directory. It anchors this directory under the LTP kernel syscall test hierarchy and delegates target discovery, compilation rules, install layout, and harness metadata to the shared make infrastructure.

Important APIs/types/functions: defines `top_srcdir ?= ../../../..`, includes `include/mk/testcases.mk`, and includes `include/mk/generic_leaf_target.mk`. There are no local targets except where noted by the directory-specific report.

Control flow: GNU make resolves `top_srcdir`, loads the common testcase rules, then the generic leaf target builds the C test programs in this directory. State is build-time only: object files, binaries, and dependency tracking are handled by the common LTP rules rather than by this file.

Dependencies/integration: integrates the directory with the LTP build system and assumes the surrounding source tree provides the common mk fragments, compiler settings, and install/test metadata. Risks are mostly build-integration risks: changing includes or `top_srcdir` would orphan the tests from standard LTP discovery.

Test signals: successful make traversal should produce the directory's syscall test binaries; failures here indicate harness/build plumbing issues rather than runtime syscall behavior.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/waitid/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/waitid/waitid01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/waitid/waitid01.c

Purpose: focused `waitid()` test that waits for an exited child with `WEXITED` and validates `si_pid`, exit status 123, `SIGCHLD`, and `CLD_EXITED`.

Important APIs/types/functions: each test allocates `siginfo_t *infop` through LTP `.bufs` where needed and uses `SAFE_FORK()`, `waitid()`, `TST_EXP_PASS` or `TST_EXP_FAIL`, and `TST_EXP_EQ_LI` on `siginfo_t` fields. Tests involving stopped children use checkpoints and `SAFE_KILL()` to order signal delivery.

Control flow/state: process state is the core fixture: exited, running, stopped, continued, non-child, signal-killed, or core-dumping child depending on the file. Successful cases inspect `si_pid`, `si_status`, `si_signo`, and `si_code`; negative cases assert exact errno.

Dependencies/integration: integrates with LTP child reaping, checkpoint synchronization, temporary directory/core-limit setup for the SIGFPE case, and signal helpers. Files with `.forks_child` rely on the harness to clean remaining children.

Risks/test signals: timing-sensitive tests are those involving `SIGSTOP`/`SIGCONT` and `WNOHANG`; checkpoint barriers reduce races. Failures point to wait-class filtering, `siginfo_t` population, signal-state reporting, or errno regressions.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/waitid/waitid01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/waitid/waitid02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/waitid/waitid02.c

Purpose: focused `waitid()` test that passes invalid option flags (`WNOHANG` without a waitable class) and expects `EINVAL`.

Important APIs/types/functions: each test allocates `siginfo_t *infop` through LTP `.bufs` where needed and uses `SAFE_FORK()`, `waitid()`, `TST_EXP_PASS` or `TST_EXP_FAIL`, and `TST_EXP_EQ_LI` on `siginfo_t` fields. Tests involving stopped children use checkpoints and `SAFE_KILL()` to order signal delivery.

Control flow/state: process state is the core fixture: exited, running, stopped, continued, non-child, signal-killed, or core-dumping child depending on the file. Successful cases inspect `si_pid`, `si_status`, `si_signo`, and `si_code`; negative cases assert exact errno.

Dependencies/integration: integrates with LTP child reaping, checkpoint synchronization, temporary directory/core-limit setup for the SIGFPE case, and signal helpers. Files with `.forks_child` rely on the harness to clean remaining children.

Risks/test signals: timing-sensitive tests are those involving `SIGSTOP`/`SIGCONT` and `WNOHANG`; checkpoint barriers reduce races. Failures point to wait-class filtering, `siginfo_t` population, signal-state reporting, or errno regressions.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/waitid/waitid02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/waitid/waitid03.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/waitid/waitid03.c

Purpose: focused `waitid()` test that calls `waitid(P_ALL, 0, ..., WNOHANG|WEXITED)` without children and expects `ECHILD`.

Important APIs/types/functions: each test allocates `siginfo_t *infop` through LTP `.bufs` where needed and uses `SAFE_FORK()`, `waitid()`, `TST_EXP_PASS` or `TST_EXP_FAIL`, and `TST_EXP_EQ_LI` on `siginfo_t` fields. Tests involving stopped children use checkpoints and `SAFE_KILL()` to order signal delivery.

Control flow/state: process state is the core fixture: exited, running, stopped, continued, non-child, signal-killed, or core-dumping child depending on the file. Successful cases inspect `si_pid`, `si_status`, `si_signo`, and `si_code`; negative cases assert exact errno.

Dependencies/integration: integrates with LTP child reaping, checkpoint synchronization, temporary directory/core-limit setup for the SIGFPE case, and signal helpers. Files with `.forks_child` rely on the harness to clean remaining children.

Risks/test signals: timing-sensitive tests are those involving `SIGSTOP`/`SIGCONT` and `WNOHANG`; checkpoint barriers reduce races. Failures point to wait-class filtering, `siginfo_t` population, signal-state reporting, or errno regressions.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/waitid/waitid03.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/waitid/waitid04.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/waitid/waitid04.c

Purpose: focused `waitid()` test that uses a live checkpoint-blocked child and `WNOHANG|WEXITED` to verify `si_pid` remains zero when nothing was reaped.

Important APIs/types/functions: each test allocates `siginfo_t *infop` through LTP `.bufs` where needed and uses `SAFE_FORK()`, `waitid()`, `TST_EXP_PASS` or `TST_EXP_FAIL`, and `TST_EXP_EQ_LI` on `siginfo_t` fields. Tests involving stopped children use checkpoints and `SAFE_KILL()` to order signal delivery.

Control flow/state: process state is the core fixture: exited, running, stopped, continued, non-child, signal-killed, or core-dumping child depending on the file. Successful cases inspect `si_pid`, `si_status`, `si_signo`, and `si_code`; negative cases assert exact errno.

Dependencies/integration: integrates with LTP child reaping, checkpoint synchronization, temporary directory/core-limit setup for the SIGFPE case, and signal helpers. Files with `.forks_child` rely on the harness to clean remaining children.

Risks/test signals: timing-sensitive tests are those involving `SIGSTOP`/`SIGCONT` and `WNOHANG`; checkpoint barriers reduce races. Failures point to wait-class filtering, `siginfo_t` population, signal-state reporting, or errno regressions.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/waitid/waitid04.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/waitid/waitid05.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/waitid/waitid05.c

Purpose: focused `waitid()` test that filters by process group, expecting `ECHILD` for `pgid+1` and correct `siginfo_t` for the real group.

Important APIs/types/functions: each test allocates `siginfo_t *infop` through LTP `.bufs` where needed and uses `SAFE_FORK()`, `waitid()`, `TST_EXP_PASS` or `TST_EXP_FAIL`, and `TST_EXP_EQ_LI` on `siginfo_t` fields. Tests involving stopped children use checkpoints and `SAFE_KILL()` to order signal delivery.

Control flow/state: process state is the core fixture: exited, running, stopped, continued, non-child, signal-killed, or core-dumping child depending on the file. Successful cases inspect `si_pid`, `si_status`, `si_signo`, and `si_code`; negative cases assert exact errno.

Dependencies/integration: integrates with LTP child reaping, checkpoint synchronization, temporary directory/core-limit setup for the SIGFPE case, and signal helpers. Files with `.forks_child` rely on the harness to clean remaining children.

Risks/test signals: timing-sensitive tests are those involving `SIGSTOP`/`SIGCONT` and `WNOHANG`; checkpoint barriers reduce races. Failures point to wait-class filtering, `siginfo_t` population, signal-state reporting, or errno regressions.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/waitid/waitid05.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/waitid/waitid06.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/waitid/waitid06.c

Purpose: focused `waitid()` test that filters by child pid, expecting `ECHILD` for `pid+1` and correct `siginfo_t` for the real pid.

Important APIs/types/functions: each test allocates `siginfo_t *infop` through LTP `.bufs` where needed and uses `SAFE_FORK()`, `waitid()`, `TST_EXP_PASS` or `TST_EXP_FAIL`, and `TST_EXP_EQ_LI` on `siginfo_t` fields. Tests involving stopped children use checkpoints and `SAFE_KILL()` to order signal delivery.

Control flow/state: process state is the core fixture: exited, running, stopped, continued, non-child, signal-killed, or core-dumping child depending on the file. Successful cases inspect `si_pid`, `si_status`, `si_signo`, and `si_code`; negative cases assert exact errno.

Dependencies/integration: integrates with LTP child reaping, checkpoint synchronization, temporary directory/core-limit setup for the SIGFPE case, and signal helpers. Files with `.forks_child` rely on the harness to clean remaining children.

Risks/test signals: timing-sensitive tests are those involving `SIGSTOP`/`SIGCONT` and `WNOHANG`; checkpoint barriers reduce races. Failures point to wait-class filtering, `siginfo_t` population, signal-state reporting, or errno regressions.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/waitid/waitid06.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/waitid/waitid07.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/waitid/waitid07.c

Purpose: focused `waitid()` test that observes a `SIGSTOP`ped child with `WSTOPPED|WNOWAIT`, validates `CLD_STOPPED`, then continues the child.

Important APIs/types/functions: each test allocates `siginfo_t *infop` through LTP `.bufs` where needed and uses `SAFE_FORK()`, `waitid()`, `TST_EXP_PASS` or `TST_EXP_FAIL`, and `TST_EXP_EQ_LI` on `siginfo_t` fields. Tests involving stopped children use checkpoints and `SAFE_KILL()` to order signal delivery.

Control flow/state: process state is the core fixture: exited, running, stopped, continued, non-child, signal-killed, or core-dumping child depending on the file. Successful cases inspect `si_pid`, `si_status`, `si_signo`, and `si_code`; negative cases assert exact errno.

Dependencies/integration: integrates with LTP child reaping, checkpoint synchronization, temporary directory/core-limit setup for the SIGFPE case, and signal helpers. Files with `.forks_child` rely on the harness to clean remaining children.

Risks/test signals: timing-sensitive tests are those involving `SIGSTOP`/`SIGCONT` and `WNOHANG`; checkpoint barriers reduce races. Failures point to wait-class filtering, `siginfo_t` population, signal-state reporting, or errno regressions.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/waitid/waitid07.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/waitid/waitid08.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/waitid/waitid08.c

Purpose: focused `waitid()` test that observes both stopped and continued states, validating `CLD_STOPPED` after `SIGSTOP` and `CLD_CONTINUED` after `SIGCONT`.

Important APIs/types/functions: each test allocates `siginfo_t *infop` through LTP `.bufs` where needed and uses `SAFE_FORK()`, `waitid()`, `TST_EXP_PASS` or `TST_EXP_FAIL`, and `TST_EXP_EQ_LI` on `siginfo_t` fields. Tests involving stopped children use checkpoints and `SAFE_KILL()` to order signal delivery.

Control flow/state: process state is the core fixture: exited, running, stopped, continued, non-child, signal-killed, or core-dumping child depending on the file. Successful cases inspect `si_pid`, `si_status`, `si_signo`, and `si_code`; negative cases assert exact errno.

Dependencies/integration: integrates with LTP child reaping, checkpoint synchronization, temporary directory/core-limit setup for the SIGFPE case, and signal helpers. Files with `.forks_child` rely on the harness to clean remaining children.

Risks/test signals: timing-sensitive tests are those involving `SIGSTOP`/`SIGCONT` and `WNOHANG`; checkpoint barriers reduce races. Failures point to wait-class filtering, `siginfo_t` population, signal-state reporting, or errno regressions.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/waitid/waitid08.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/waitid/waitid09.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/waitid/waitid09.c

Purpose: focused `waitid()` test that verifies waiting on pid 1 fails with `ECHILD` even while another unwaited child exists.

Important APIs/types/functions: each test allocates `siginfo_t *infop` through LTP `.bufs` where needed and uses `SAFE_FORK()`, `waitid()`, `TST_EXP_PASS` or `TST_EXP_FAIL`, and `TST_EXP_EQ_LI` on `siginfo_t` fields. Tests involving stopped children use checkpoints and `SAFE_KILL()` to order signal delivery.

Control flow/state: process state is the core fixture: exited, running, stopped, continued, non-child, signal-killed, or core-dumping child depending on the file. Successful cases inspect `si_pid`, `si_status`, `si_signo`, and `si_code`; negative cases assert exact errno.

Dependencies/integration: integrates with LTP child reaping, checkpoint synchronization, temporary directory/core-limit setup for the SIGFPE case, and signal helpers. Files with `.forks_child` rely on the harness to clean remaining children.

Risks/test signals: timing-sensitive tests are those involving `SIGSTOP`/`SIGCONT` and `WNOHANG`; checkpoint barriers reduce races. Failures point to wait-class filtering, `siginfo_t` population, signal-state reporting, or errno regressions.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/waitid/waitid09.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/waitid/waitid10.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/waitid/waitid10.c

Purpose: focused `waitid()` test that verifies a child that raises `SIGFPE` is reported as `CLD_DUMPED` or `CLD_KILLED` depending on core-dump availability.

Important APIs/types/functions: each test allocates `siginfo_t *infop` through LTP `.bufs` where needed and uses `SAFE_FORK()`, `waitid()`, `TST_EXP_PASS` or `TST_EXP_FAIL`, and `TST_EXP_EQ_LI` on `siginfo_t` fields. Tests involving stopped children use checkpoints and `SAFE_KILL()` to order signal delivery.

Control flow/state: process state is the core fixture: exited, running, stopped, continued, non-child, signal-killed, or core-dumping child depending on the file. Successful cases inspect `si_pid`, `si_status`, `si_signo`, and `si_code`; negative cases assert exact errno.

Dependencies/integration: integrates with LTP child reaping, checkpoint synchronization, temporary directory/core-limit setup for the SIGFPE case, and signal helpers. Files with `.forks_child` rely on the harness to clean remaining children.

Risks/test signals: timing-sensitive tests are those involving `SIGSTOP`/`SIGCONT` and `WNOHANG`; checkpoint barriers reduce races. Failures point to wait-class filtering, `siginfo_t` population, signal-state reporting, or errno regressions.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/waitid/waitid10.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/waitid/waitid11.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/waitid/waitid11.c

Purpose: focused `waitid()` test that verifies a paused child killed with `SIGKILL` is reported with `si_status=SIGKILL` and `CLD_KILLED`.

Important APIs/types/functions: each test allocates `siginfo_t *infop` through LTP `.bufs` where needed and uses `SAFE_FORK()`, `waitid()`, `TST_EXP_PASS` or `TST_EXP_FAIL`, and `TST_EXP_EQ_LI` on `siginfo_t` fields. Tests involving stopped children use checkpoints and `SAFE_KILL()` to order signal delivery.

Control flow/state: process state is the core fixture: exited, running, stopped, continued, non-child, signal-killed, or core-dumping child depending on the file. Successful cases inspect `si_pid`, `si_status`, `si_signo`, and `si_code`; negative cases assert exact errno.

Dependencies/integration: integrates with LTP child reaping, checkpoint synchronization, temporary directory/core-limit setup for the SIGFPE case, and signal helpers. Files with `.forks_child` rely on the harness to clean remaining children.

Risks/test signals: timing-sensitive tests are those involving `SIGSTOP`/`SIGCONT` and `WNOHANG`; checkpoint barriers reduce races. Failures point to wait-class filtering, `siginfo_t` population, signal-state reporting, or errno regressions.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/waitid/waitid11.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/waitpid/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/waitpid/Makefile

Purpose: LTP leaf build file for the `waitpid` syscall test directory. It anchors this directory under the LTP kernel syscall test hierarchy and delegates target discovery, compilation rules, install layout, and harness metadata to the shared make infrastructure.

Important APIs/types/functions: defines `top_srcdir ?= ../../../..`, includes `include/mk/testcases.mk`, and includes `include/mk/generic_leaf_target.mk`. There are no local targets except where noted by the directory-specific report.

Control flow: GNU make resolves `top_srcdir`, loads the common testcase rules, then the generic leaf target builds the C test programs in this directory. State is build-time only: object files, binaries, and dependency tracking are handled by the common LTP rules rather than by this file.

Dependencies/integration: integrates the directory with the LTP build system and assumes the surrounding source tree provides the common mk fragments, compiler settings, and install/test metadata. Risks are mostly build-integration risks: changing includes or `top_srcdir` would orphan the tests from standard LTP discovery.

Test signals: successful make traversal should produce the directory's syscall test binaries; failures here indicate harness/build plumbing issues rather than runtime syscall behavior.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/waitpid/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/waitpid/waitpid01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/waitpid/waitpid01.c

Purpose: verifies `waitpid()` reports signal-terminated children correctly for a broad set of standard signals and for both `raise(sig)` and `kill(getpid(), sig)` child paths.

Important APIs/types/functions: `testcase_list[]` maps signals to expected core-dump behavior; `variant_list[]` selects child trigger function. `setup()` adjusts `RLIMIT_CORE` to allow minimal core dumps when possible. `run()` resets signal disposition, forks, waits with `waitpid(pid, &status, 0)`, and checks `WIFSIGNALED`, `WTERMSIG`, and optionally `WCOREDUMP`.

Control flow/state: each signal/variant pair is independent. Child terminates by signal; parent inspects the status word. Temporary directory support exists for core files.

Dependencies/integration: LTP variants multiply coverage across trigger mechanisms. Core-dump checks are conditional on rlimit capacity.

Risks/test signals: signal defaults and platform core-dump policy affect `WCOREDUMP`; the primary contract is pid and terminating signal. `SIGKILL` cannot have its handler reset and is handled specially.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/waitpid/waitpid01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/waitpid/waitpid03.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/waitpid/waitpid03.c

Purpose: verifies waiting for a specific child pid succeeds once and then fails with `ECHILD` after that child has been reaped.

Important APIs/types/functions: `MAX_CHILDREN` is 25. `run()` forks all children, selects the midpoint pid, and calls `check_waitpid(pid, reaped)` twice. `check_waitpid()` validates either returned pid or `-1/ECHILD` depending on expected reaped state.

Control flow/state: many children exit immediately; parent reaps one chosen child explicitly, then proves repeated wait on the same pid fails. `tst_reap_children()` cleans the rest.

Dependencies/integration: LTP fork metadata handles child cleanup. No checkpoints are needed because children exit immediately.

Risks/test signals: a wrong pid return, non-`ECHILD` errno, or repeated successful reap indicates waitpid bookkeeping regression.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/waitpid/waitpid03.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/waitpid/waitpid04.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/waitpid/waitpid04.c

Purpose: negative `waitpid()` errno test for no children, non-child pid, invalid flags, and `INT_MIN` process-group edge case.

Important APIs/types/functions: `testcase_list[]` holds pid, flags, and expected errno: `ECHILD`, `ECHILD`, `EINVAL`, and `ESRCH`. `run()` calls `TST_EXP_FAIL2(waitpid(...))` for each row.

Control flow/state: no child processes are created; every call should fail from syscall validation or child lookup.

Dependencies/integration: minimal LTP harness with `<sys/wait.h>` and signal constants.

Risks/test signals: the `INT_MIN` case protects the same negation edge as wait4. Wrong errno mapping is the principal failure mode.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/waitpid/waitpid04.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/waitpid/waitpid06.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/waitpid/waitpid06.c

Purpose: waitpid process-selection regression test that forks `MAXKIDS` children, moves half into a new process group, releases them via checkpoint, and reaps all children with `waitpid(-1, 0)`.

Important APIs/types/functions: this file is built around `waitpid_common.h`, especially `waitpid_setup()`, `waitpid_test()`, `do_exit()`, `waitpid_ret_test()`, and `reap_children()`. Its local `do_child_1()` constructs the exact child/process-group/signal scenario for the case.

Control flow/state: the top-level harness forks a coordinator child; that child forks `MAXKIDS` children, stores pids in shared mmap, uses LTP checkpoints to hold or release them, then calls the common reaper. State includes child pid arrays, process groups, stop/continue state, and expected exit status 3 for helper children unless the file documents a direct special case.

Dependencies/integration: requires LTP checkpoints, shared anonymous mmap, and `.forks_child = 1`. The common cleanup kills any leftover child pids to avoid leaking blocked or stopped children.

Risks/test signals: these tests are race-prone without checkpoints; failures usually show as unexpected pid, unreaped child, wrong `ECHILD`, wrong exit status, or mishandled stopped child. Process-group cases are sensitive to `setpgid()` ordering.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/waitpid/waitpid06.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/waitpid/waitpid07.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/waitpid/waitpid07.c

Purpose: waitpid process-selection regression test that checks `waitpid(-1, WNOHANG)` returns 0 while children are checkpoint-blocked, then releases and reaps them with `WNOHANG`.

Important APIs/types/functions: this file is built around `waitpid_common.h`, especially `waitpid_setup()`, `waitpid_test()`, `do_exit()`, `waitpid_ret_test()`, and `reap_children()`. Its local `do_child_1()` constructs the exact child/process-group/signal scenario for the case.

Control flow/state: the top-level harness forks a coordinator child; that child forks `MAXKIDS` children, stores pids in shared mmap, uses LTP checkpoints to hold or release them, then calls the common reaper. State includes child pid arrays, process groups, stop/continue state, and expected exit status 3 for helper children unless the file documents a direct special case.

Dependencies/integration: requires LTP checkpoints, shared anonymous mmap, and `.forks_child = 1`. The common cleanup kills any leftover child pids to avoid leaking blocked or stopped children.

Risks/test signals: these tests are race-prone without checkpoints; failures usually show as unexpected pid, unreaped child, wrong `ECHILD`, wrong exit status, or mishandled stopped child. Process-group cases are sensitive to `setpgid()` ordering.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/waitpid/waitpid07.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/waitpid/waitpid08.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/waitpid/waitpid08.c

Purpose: waitpid process-selection regression test that creates stopped children and reaps them with `waitpid(-1, WUNTRACED)`, continuing `SIGSTOP`ped children through the common helper.

Important APIs/types/functions: this file is built around `waitpid_common.h`, especially `waitpid_setup()`, `waitpid_test()`, `do_exit()`, `waitpid_ret_test()`, and `reap_children()`. Its local `do_child_1()` constructs the exact child/process-group/signal scenario for the case.

Control flow/state: the top-level harness forks a coordinator child; that child forks `MAXKIDS` children, stores pids in shared mmap, uses LTP checkpoints to hold or release them, then calls the common reaper. State includes child pid arrays, process groups, stop/continue state, and expected exit status 3 for helper children unless the file documents a direct special case.

Dependencies/integration: requires LTP checkpoints, shared anonymous mmap, and `.forks_child = 1`. The common cleanup kills any leftover child pids to avoid leaking blocked or stopped children.

Risks/test signals: these tests are race-prone without checkpoints; failures usually show as unexpected pid, unreaped child, wrong `ECHILD`, wrong exit status, or mishandled stopped child. Process-group cases are sensitive to `setpgid()` ordering.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/waitpid/waitpid08.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/waitpid/waitpid09.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/waitpid/waitpid09.c

Purpose: waitpid process-selection regression test that implements four direct cases for `WNOHANG`: running child returns 0, exited child returns pid, and no-child calls return `ECHILD` with and without `WNOHANG`.

Important APIs/types/functions: this file is built around `waitpid_common.h`, especially `waitpid_setup()`, `waitpid_test()`, `do_exit()`, `waitpid_ret_test()`, and `reap_children()`. Its local `do_child_1()` constructs the exact child/process-group/signal scenario for the case.

Control flow/state: the top-level harness forks a coordinator child; that child forks `MAXKIDS` children, stores pids in shared mmap, uses LTP checkpoints to hold or release them, then calls the common reaper. State includes child pid arrays, process groups, stop/continue state, and expected exit status 3 for helper children unless the file documents a direct special case.

Dependencies/integration: requires LTP checkpoints, shared anonymous mmap, and `.forks_child = 1`. The common cleanup kills any leftover child pids to avoid leaking blocked or stopped children.

Risks/test signals: these tests are race-prone without checkpoints; failures usually show as unexpected pid, unreaped child, wrong `ECHILD`, wrong exit status, or mishandled stopped child. Process-group cases are sensitive to `setpgid()` ordering.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/waitpid/waitpid09.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/waitpid/waitpid10.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/waitpid/waitpid10.c

Purpose: waitpid process-selection regression test that forks eight children with mixed behavior: immediate exit, CPU loops, repeated fork/reap, and sleeps, then reaps all expected pids.

Important APIs/types/functions: this file is built around `waitpid_common.h`, especially `waitpid_setup()`, `waitpid_test()`, `do_exit()`, `waitpid_ret_test()`, and `reap_children()`. Its local `do_child_1()` constructs the exact child/process-group/signal scenario for the case.

Control flow/state: the top-level harness forks a coordinator child; that child forks `MAXKIDS` children, stores pids in shared mmap, uses LTP checkpoints to hold or release them, then calls the common reaper. State includes child pid arrays, process groups, stop/continue state, and expected exit status 3 for helper children unless the file documents a direct special case.

Dependencies/integration: requires LTP checkpoints, shared anonymous mmap, and `.forks_child = 1`. The common cleanup kills any leftover child pids to avoid leaking blocked or stopped children.

Risks/test signals: these tests are race-prone without checkpoints; failures usually show as unexpected pid, unreaped child, wrong `ECHILD`, wrong exit status, or mishandled stopped child. Process-group cases are sensitive to `setpgid()` ordering.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/waitpid/waitpid10.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/waitpid/waitpid11.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/waitpid/waitpid11.c

Purpose: waitpid process-selection regression test that tests process-group selection with `pid=0` for current group and negative pgid for a different group.

Important APIs/types/functions: this file is built around `waitpid_common.h`, especially `waitpid_setup()`, `waitpid_test()`, `do_exit()`, `waitpid_ret_test()`, and `reap_children()`. Its local `do_child_1()` constructs the exact child/process-group/signal scenario for the case.

Control flow/state: the top-level harness forks a coordinator child; that child forks `MAXKIDS` children, stores pids in shared mmap, uses LTP checkpoints to hold or release them, then calls the common reaper. State includes child pid arrays, process groups, stop/continue state, and expected exit status 3 for helper children unless the file documents a direct special case.

Dependencies/integration: requires LTP checkpoints, shared anonymous mmap, and `.forks_child = 1`. The common cleanup kills any leftover child pids to avoid leaking blocked or stopped children.

Risks/test signals: these tests are race-prone without checkpoints; failures usually show as unexpected pid, unreaped child, wrong `ECHILD`, wrong exit status, or mishandled stopped child. Process-group cases are sensitive to `setpgid()` ordering.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/waitpid/waitpid11.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/waitpid/waitpid12.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/waitpid/waitpid12.c

Purpose: waitpid process-selection regression test that combines process-group selection with `WNOHANG`, first expecting 0 while children are blocked, then reaping current and alternate groups.

Important APIs/types/functions: this file is built around `waitpid_common.h`, especially `waitpid_setup()`, `waitpid_test()`, `do_exit()`, `waitpid_ret_test()`, and `reap_children()`. Its local `do_child_1()` constructs the exact child/process-group/signal scenario for the case.

Control flow/state: the top-level harness forks a coordinator child; that child forks `MAXKIDS` children, stores pids in shared mmap, uses LTP checkpoints to hold or release them, then calls the common reaper. State includes child pid arrays, process groups, stop/continue state, and expected exit status 3 for helper children unless the file documents a direct special case.

Dependencies/integration: requires LTP checkpoints, shared anonymous mmap, and `.forks_child = 1`. The common cleanup kills any leftover child pids to avoid leaking blocked or stopped children.

Risks/test signals: these tests are race-prone without checkpoints; failures usually show as unexpected pid, unreaped child, wrong `ECHILD`, wrong exit status, or mishandled stopped child. Process-group cases are sensitive to `setpgid()` ordering.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/waitpid/waitpid12.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/waitpid/waitpid13.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/waitpid/waitpid13.c

Purpose: waitpid process-selection regression test that combines process-group selection with `WUNTRACED`, validating stopped-child reporting and continuation across groups.

Important APIs/types/functions: this file is built around `waitpid_common.h`, especially `waitpid_setup()`, `waitpid_test()`, `do_exit()`, `waitpid_ret_test()`, and `reap_children()`. Its local `do_child_1()` constructs the exact child/process-group/signal scenario for the case.

Control flow/state: the top-level harness forks a coordinator child; that child forks `MAXKIDS` children, stores pids in shared mmap, uses LTP checkpoints to hold or release them, then calls the common reaper. State includes child pid arrays, process groups, stop/continue state, and expected exit status 3 for helper children unless the file documents a direct special case.

Dependencies/integration: requires LTP checkpoints, shared anonymous mmap, and `.forks_child = 1`. The common cleanup kills any leftover child pids to avoid leaking blocked or stopped children.

Risks/test signals: these tests are race-prone without checkpoints; failures usually show as unexpected pid, unreaped child, wrong `ECHILD`, wrong exit status, or mishandled stopped child. Process-group cases are sensitive to `setpgid()` ordering.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/waitpid/waitpid13.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/waitpid/waitpid_common.h -->
# sources/test-tools/ltp/testcases/kernel/syscalls/waitpid/waitpid_common.h

Purpose: shared harness for the older multi-child `waitpid` tests. It centralizes child pid storage, coordinator process setup, cleanup, checkpoint-based child release, and verification of returned pids/status.

Important APIs/types/functions: `MAXKIDS` is 8. `waitpid_setup()` maps shared pid storage. `waitpid_cleanup()` kills recorded children and the coordinator then unmaps. `waitpid_test()` forks the coordinator and reaps it. `do_exit(stop)` waits on a checkpoint, optionally sends itself `SIGSTOP`, and exits with status 3. `waitpid_ret_test()` checks return value and errno. `reap_children()` loops on `waitpid()`, handles `EINTR`, expects final `ECHILD`, continues stopped children, validates returned pids against the expected array, and checks exit status 3.

Control flow/state: the including C file supplies `do_child_1()`, which creates the concrete child topology. Shared mmap lets the parent cleanup path know child pids created by the coordinator process.

Dependencies/integration: depends on LTP safe mmap/fork/checkpoint wrappers and standard wait status macros. It is header-included into multiple standalone tests, so all globals are `static` except `waitpid_ret_test()`.

Risks/test signals: because cleanup kills all nonzero recorded pids, stale pid reuse would be dangerous if tests ran long after children exit; the reaper zeros pids when consumed to reduce that risk. Failures are reported at the exact invariant: errno, unexpected pid, abnormal exit, wrong exit code, or unreaped child.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/waitpid/waitpid_common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/write/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/write/Makefile

Purpose: LTP leaf build file for the `write` syscall test directory. It anchors this directory under the LTP kernel syscall test hierarchy and delegates target discovery, compilation rules, install layout, and harness metadata to the shared make infrastructure.

Important APIs/types/functions: defines `top_srcdir ?= ../../../..`, includes `include/mk/testcases.mk`, and includes `include/mk/generic_leaf_target.mk`. There are no local targets except where noted by the directory-specific report.

Control flow: GNU make resolves `top_srcdir`, loads the common testcase rules, then the generic leaf target builds the C test programs in this directory. State is build-time only: object files, binaries, and dependency tracking are handled by the common LTP rules rather than by this file.

Dependencies/integration: integrates the directory with the LTP build system and assumes the surrounding source tree provides the common mk fragments, compiler settings, and install/test metadata. Risks are mostly build-integration risks: changing includes or `top_srcdir` would orphan the tests from standard LTP discovery.

Test signals: successful make traversal should produce the directory's syscall test binaries; failures here indicate harness/build plumbing issues rather than runtime syscall behavior.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/write/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/write/write01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/write/write01.c

Purpose: focused `write(2)` syscall test that writes decreasing byte counts from `BUFSIZ` to 1 to an open file and verifies each `write()` returns the requested count.

Important APIs/types/functions: uses LTP safe open/read/write/close/seek wrappers and the modern `tst_test` harness. The exact fixture varies by file: regular temp file, protected mmap page, FIFO, pipe, signal handler, or append-mode file.

Control flow/state: setup creates the required descriptor state, `verify_write()` performs the single syscall scenario, and cleanup closes descriptors/unlinks files. Persistent state is confined to the LTP tmpdir and, for append/corruption tests, file content and offset are part of the assertion.

Dependencies/integration: depends on Linux/POSIX file descriptor semantics, LTP tmpdir isolation, and for negative tests exact errno propagation. The append test uses LTP allocated buffers through `.bufs`.

Risks/test signals: failures identify short writes where full writes are expected, wrong errno, missing SIGPIPE, data corruption after a failed write, FIFO capacity behavior changes, or broken `O_APPEND` offset/size semantics.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/write/write01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/write/write02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/write/write02.c

Purpose: focused `write(2)` syscall test that checks the special `write(fd, NULL, 0)` case returns 0 rather than failing on the NULL buffer.

Important APIs/types/functions: uses LTP safe open/read/write/close/seek wrappers and the modern `tst_test` harness. The exact fixture varies by file: regular temp file, protected mmap page, FIFO, pipe, signal handler, or append-mode file.

Control flow/state: setup creates the required descriptor state, `verify_write()` performs the single syscall scenario, and cleanup closes descriptors/unlinks files. Persistent state is confined to the LTP tmpdir and, for append/corruption tests, file content and offset are part of the assertion.

Dependencies/integration: depends on Linux/POSIX file descriptor semantics, LTP tmpdir isolation, and for negative tests exact errno propagation. The append test uses LTP allocated buffers through `.bufs`.

Risks/test signals: failures identify short writes where full writes are expected, wrong errno, missing SIGPIPE, data corruption after a failed write, FIFO capacity behavior changes, or broken `O_APPEND` offset/size semantics.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/write/write02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/write/write03.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/write/write03.c

Purpose: focused `write(2)` syscall test that writes 100 bytes, attempts a failing write from a `PROT_NONE` buffer, then reopens and verifies the original file data was not corrupted.

Important APIs/types/functions: uses LTP safe open/read/write/close/seek wrappers and the modern `tst_test` harness. The exact fixture varies by file: regular temp file, protected mmap page, FIFO, pipe, signal handler, or append-mode file.

Control flow/state: setup creates the required descriptor state, `verify_write()` performs the single syscall scenario, and cleanup closes descriptors/unlinks files. Persistent state is confined to the LTP tmpdir and, for append/corruption tests, file content and offset are part of the assertion.

Dependencies/integration: depends on Linux/POSIX file descriptor semantics, LTP tmpdir isolation, and for negative tests exact errno propagation. The append test uses LTP allocated buffers through `.bufs`.

Risks/test signals: failures identify short writes where full writes are expected, wrong errno, missing SIGPIPE, data corruption after a failed write, FIFO capacity behavior changes, or broken `O_APPEND` offset/size semantics.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/write/write03.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/write/write04.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/write/write04.c

Purpose: focused `write(2)` syscall test that fills a nonblocking FIFO and verifies another write fails with `EAGAIN`.

Important APIs/types/functions: uses LTP safe open/read/write/close/seek wrappers and the modern `tst_test` harness. The exact fixture varies by file: regular temp file, protected mmap page, FIFO, pipe, signal handler, or append-mode file.

Control flow/state: setup creates the required descriptor state, `verify_write()` performs the single syscall scenario, and cleanup closes descriptors/unlinks files. Persistent state is confined to the LTP tmpdir and, for append/corruption tests, file content and offset are part of the assertion.

Dependencies/integration: depends on Linux/POSIX file descriptor semantics, LTP tmpdir isolation, and for negative tests exact errno propagation. The append test uses LTP allocated buffers through `.bufs`.

Risks/test signals: failures identify short writes where full writes are expected, wrong errno, missing SIGPIPE, data corruption after a failed write, FIFO capacity behavior changes, or broken `O_APPEND` offset/size semantics.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/write/write04.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/write/write05.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/write/write05.c

Purpose: focused `write(2)` syscall test that covers `EBADF`, `EFAULT`, and `EPIPE`, also checking that the closed-pipe case delivers exactly one `SIGPIPE`.

Important APIs/types/functions: uses LTP safe open/read/write/close/seek wrappers and the modern `tst_test` harness. The exact fixture varies by file: regular temp file, protected mmap page, FIFO, pipe, signal handler, or append-mode file.

Control flow/state: setup creates the required descriptor state, `verify_write()` performs the single syscall scenario, and cleanup closes descriptors/unlinks files. Persistent state is confined to the LTP tmpdir and, for append/corruption tests, file content and offset are part of the assertion.

Dependencies/integration: depends on Linux/POSIX file descriptor semantics, LTP tmpdir isolation, and for negative tests exact errno propagation. The append test uses LTP allocated buffers through `.bufs`.

Risks/test signals: failures identify short writes where full writes are expected, wrong errno, missing SIGPIPE, data corruption after a failed write, FIFO capacity behavior changes, or broken `O_APPEND` offset/size semantics.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/write/write05.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/write/write06.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/write/write06.c

Purpose: focused `write(2)` syscall test that verifies `O_APPEND` atomically appends at EOF even after seeking to an earlier offset, producing 3 KiB size and offset.

Important APIs/types/functions: uses LTP safe open/read/write/close/seek wrappers and the modern `tst_test` harness. The exact fixture varies by file: regular temp file, protected mmap page, FIFO, pipe, signal handler, or append-mode file.

Control flow/state: setup creates the required descriptor state, `verify_write()` performs the single syscall scenario, and cleanup closes descriptors/unlinks files. Persistent state is confined to the LTP tmpdir and, for append/corruption tests, file content and offset are part of the assertion.

Dependencies/integration: depends on Linux/POSIX file descriptor semantics, LTP tmpdir isolation, and for negative tests exact errno propagation. The append test uses LTP allocated buffers through `.bufs`.

Risks/test signals: failures identify short writes where full writes are expected, wrong errno, missing SIGPIPE, data corruption after a failed write, FIFO capacity behavior changes, or broken `O_APPEND` offset/size semantics.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/write/write06.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/writev/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/writev/Makefile

Purpose: LTP leaf build file for the `writev` syscall test directory. It anchors this directory under the LTP kernel syscall test hierarchy and delegates target discovery, compilation rules, install layout, and harness metadata to the shared make infrastructure.

Important APIs/types/functions: defines `top_srcdir ?= ../../../..`, includes `include/mk/testcases.mk`, and includes `include/mk/generic_leaf_target.mk`. There are no local targets except where noted by the directory-specific report.

Control flow: GNU make resolves `top_srcdir`, loads the common testcase rules, then the generic leaf target builds the C test programs in this directory. State is build-time only: object files, binaries, and dependency tracking are handled by the common LTP rules rather than by this file.

Dependencies/integration: integrates the directory with the LTP build system and assumes the surrounding source tree provides the common mk fragments, compiler settings, and install/test metadata. Risks are mostly build-integration risks: changing includes or `top_srcdir` would orphan the tests from standard LTP discovery.

Test signals: successful make traversal should produce the directory's syscall test binaries; failures here indicate harness/build plumbing issues rather than runtime syscall behavior.

Directory-specific integration: `writev03` adds `-pthread` and `-lrt` because that regression test uses LTP fuzzy synchronization, atomics, and threaded racing around page-faulted iovecs. Other `writev` tests use the generic leaf rules.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/writev/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/writev/writev01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/writev/writev01.c

Purpose: basic and negative `writev()` coverage for invalid iovec length, invalid fd, invalid iovcnt, zero iovcnt, NULL zero-length iovecs, and closed-pipe `EPIPE`.

Important APIs/types/functions: `iovec_badlen`, `iovec_simple`, and `iovec_zero_null` define vector shapes. `testcases[]` encodes expected return and errno. `setup()` blocks `SIGPIPE`, opens a regular file, creates a pipe, and closes the read end.

Control flow/state: each row calls `writev()` once and compares return/errno against the table. File and pipe descriptors are shared fixtures.

Dependencies/integration: uses modern LTP harness and tmpdir. Blocking SIGPIPE keeps the closed-pipe case observable as `EPIPE` without terminating the test.

Risks/test signals: architecture/libc handling of negative `iov_len` represented in `size_t` is the main portability edge. Expected successes are exact byte counts; expected failures require exact errno.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/writev/writev01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/writev/writev02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/writev/writev02.c

Purpose: `writev(2)` regression test that legacy harness test for a sparse file with valid data at the 8 KiB offset; an invalid first iovec must return `EFAULT` and leave the existing sparse-file data intact.

Important APIs/types/functions: uses `struct iovec`, `writev()`, file positioning, mmap-protected bad addresses or page-boundary good addresses, and either the legacy `test.h` harness or modern `tst_test` harness depending on the file. Helper routines include signal handlers, `l_seek()` wrappers, fuzzy-sync thread functions, or per-offset validation functions.

Control flow/state: setup builds the file and memory mapping fixture, the main test invokes `writev()` with carefully chosen vectors, and validation checks errno, byte count, file contents, and file offset. Legacy files loop under `TEST_LOOPING`; modern files run once or for a timed fuzzy-sync runtime.

Dependencies/integration: depends on VM fault behavior, generic write path fault-in semantics, and filesystem write semantics. `writev03` requires pthread/librt build flags from the Makefile and a mounted filesystem matrix; `writev07` carries Linux commit tags for iomap partial-write fixes.

Risks/test signals: these tests are sensitive to kernel short-write semantics around invalid iovecs. They intentionally allow both full failure and bounded short write where Linux semantics permit it, but never allow uninitialized data exposure, offset drift, or writes beyond reported byte count.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/writev/writev02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/writev/writev03.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/writev/writev03.c

Purpose: `writev(2)` regression test that threaded fuzzy-sync regression for `iov_iter_fault_in_readable()`, racing reads of the output file while `writev()` faults in shared mapped pages after a leading zero-length iovec.

Important APIs/types/functions: uses `struct iovec`, `writev()`, file positioning, mmap-protected bad addresses or page-boundary good addresses, and either the legacy `test.h` harness or modern `tst_test` harness depending on the file. Helper routines include signal handlers, `l_seek()` wrappers, fuzzy-sync thread functions, or per-offset validation functions.

Control flow/state: setup builds the file and memory mapping fixture, the main test invokes `writev()` with carefully chosen vectors, and validation checks errno, byte count, file contents, and file offset. Legacy files loop under `TEST_LOOPING`; modern files run once or for a timed fuzzy-sync runtime.

Dependencies/integration: depends on VM fault behavior, generic write path fault-in semantics, and filesystem write semantics. `writev03` requires pthread/librt build flags from the Makefile and a mounted filesystem matrix; `writev07` carries Linux commit tags for iomap partial-write fixes.

Risks/test signals: these tests are sensitive to kernel short-write semantics around invalid iovecs. They intentionally allow both full failure and bounded short write where Linux semantics permit it, but never allow uninitialized data exposure, offset drift, or writes beyond reported byte count.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/writev/writev03.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/writev/writev05.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/writev/writev05.c

Purpose: `writev(2)` regression test that legacy harness variant where valid data is written at the beginning of the file; invalid `writev()` must return `EFAULT` and not create data at the 8 KiB offset.

Important APIs/types/functions: uses `struct iovec`, `writev()`, file positioning, mmap-protected bad addresses or page-boundary good addresses, and either the legacy `test.h` harness or modern `tst_test` harness depending on the file. Helper routines include signal handlers, `l_seek()` wrappers, fuzzy-sync thread functions, or per-offset validation functions.

Control flow/state: setup builds the file and memory mapping fixture, the main test invokes `writev()` with carefully chosen vectors, and validation checks errno, byte count, file contents, and file offset. Legacy files loop under `TEST_LOOPING`; modern files run once or for a timed fuzzy-sync runtime.

Dependencies/integration: depends on VM fault behavior, generic write path fault-in semantics, and filesystem write semantics. `writev03` requires pthread/librt build flags from the Makefile and a mounted filesystem matrix; `writev07` carries Linux commit tags for iomap partial-write fixes.

Risks/test signals: these tests are sensitive to kernel short-write semantics around invalid iovecs. They intentionally allow both full failure and bounded short write where Linux semantics permit it, but never allow uninitialized data exposure, offset drift, or writes beyond reported byte count.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/writev/writev05.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/writev/writev06.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/writev/writev06.c

Purpose: `writev(2)` regression test that legacy harness test that iovecs pointing to the last readable byte of two mapped pages, each surrounded by `PROT_NONE` mappings, still write two bytes successfully.

Important APIs/types/functions: uses `struct iovec`, `writev()`, file positioning, mmap-protected bad addresses or page-boundary good addresses, and either the legacy `test.h` harness or modern `tst_test` harness depending on the file. Helper routines include signal handlers, `l_seek()` wrappers, fuzzy-sync thread functions, or per-offset validation functions.

Control flow/state: setup builds the file and memory mapping fixture, the main test invokes `writev()` with carefully chosen vectors, and validation checks errno, byte count, file contents, and file offset. Legacy files loop under `TEST_LOOPING`; modern files run once or for a timed fuzzy-sync runtime.

Dependencies/integration: depends on VM fault behavior, generic write path fault-in semantics, and filesystem write semantics. `writev03` requires pthread/librt build flags from the Makefile and a mounted filesystem matrix; `writev07` carries Linux commit tags for iomap partial-write fixes.

Risks/test signals: these tests are sensitive to kernel short-write semantics around invalid iovecs. They intentionally allow both full failure and bounded short write where Linux semantics permit it, but never allow uninitialized data exposure, offset drift, or writes beyond reported byte count.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/writev/writev06.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/writev/writev07.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/writev/writev07.c

Purpose: `writev(2)` regression test that modern regression test for partially valid iovec lists: either `EFAULT` with unchanged file/offset or a short write whose file content and offset match the reported byte count.

Important APIs/types/functions: uses `struct iovec`, `writev()`, file positioning, mmap-protected bad addresses or page-boundary good addresses, and either the legacy `test.h` harness or modern `tst_test` harness depending on the file. Helper routines include signal handlers, `l_seek()` wrappers, fuzzy-sync thread functions, or per-offset validation functions.

Control flow/state: setup builds the file and memory mapping fixture, the main test invokes `writev()` with carefully chosen vectors, and validation checks errno, byte count, file contents, and file offset. Legacy files loop under `TEST_LOOPING`; modern files run once or for a timed fuzzy-sync runtime.

Dependencies/integration: depends on VM fault behavior, generic write path fault-in semantics, and filesystem write semantics. `writev03` requires pthread/librt build flags from the Makefile and a mounted filesystem matrix; `writev07` carries Linux commit tags for iomap partial-write fixes.

Risks/test signals: these tests are sensitive to kernel short-write semantics around invalid iovecs. They intentionally allow both full failure and bounded short write where Linux semantics permit it, but never allow uninitialized data exposure, offset drift, or writes beyond reported byte count.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/writev/writev07.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/pjdfstest/tests/misc.sh -->
# sources/test-tools/pjdfstest/tests/misc.sh

Purpose: shared shell library for pjdfstest TAP-style filesystem tests. It locates the project configuration and `pjdfstest` binary, provides expectation helpers, random name/path generators, feature gating, mount-option probes, and fixture creation helpers.

Important APIs/types/functions: `expect()` and `jexpect()` run pjdfstest commands locally or inside a FreeBSD jail and emit `ok/not ok` with incrementing `ntest`. `test_check()` wraps shell predicates. `todo()` marks OS/filesystem-specific expected failures. `namegen*()` and `dirgen_max()` produce random names at requested or filesystem maximum lengths. `supported()` and `require()` gate features such as `lchmod`, `chflags`, `link`, `posix_fallocate`, `rename_ctime`, `stat_st_birthtime`, `utimensat`, and `UTIME_NOW`. FreeBSD-only helpers report mount options, NFSv4 ACL support, `noexec`, and `nosuid`. `create_file()` creates typed filesystem objects and applies optional mode/ownership.

Control flow/state: sourcing the file initializes `ntest`, `confdir`, `maindir`, `fstest`, imports `conf`, and exits early on missing configuration/binary. Runtime state is shell globals such as `todomsg`, `os`, `fs`, and TAP counter.

Dependencies/integration: depends on `/bin/sh`, `dd`, `openssl md5`, `awk`, `grep`, `jail` for jail paths, and pjdfstest command semantics. It is included by many pjdfstest test scripts.

Risks/test signals: unquoted variables can mis-handle spaces in paths; random generators depend on OpenSSL output format. The TAP output itself is the test signal, and `quick_exit()` is used to count unsupported feature tests as skipped/successful according to suite convention.
<!-- END_FILE_RESEARCH: sources/test-tools/pjdfstest/tests/misc.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/pynfs/examples/localhost_helper.sh -->
# sources/test-tools/pynfs/examples/localhost_helper.sh

Purpose: server-helper script for pynfs tests against local Linux knfsd. It lets tests restart the local NFS server, manipulate files on the server side, or expire a specific NFSv4 client.

Important APIs/types/functions: `expire_client()` scans `/proc/fs/nfsd/clients/*/info` for a matching `name: "client"` line and writes `expire` to the sibling `ctl` file. The command dispatch supports `reboot`, `unlink`, `rename`, `link`, `chmod`, and `expire`.

Control flow/state: the first argument is ignored server name, the second is command, and remaining arguments are command operands. `reboot` runs `sudo systemctl restart nfs-server.service`; file operations run locally.

Dependencies/integration: assumes passwordless sudo for nfs-server restart when needed and Linux nfsd procfs client controls. It is used via pynfs `--serverhelper` options.

Risks/test signals: arguments are unquoted, so spaces or shell metacharacters in filenames are unsafe. Failure signals appear as helper command failures observed by the calling pynfs test.
<!-- END_FILE_RESEARCH: sources/test-tools/pynfs/examples/localhost_helper.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/pynfs/examples/server_helper.sh -->
# sources/test-tools/pynfs/examples/server_helper.sh

Purpose: remote-server variant of the pynfs server helper. It performs knfsd restart, file operations, and client expiration over SSH against a named server.

Important APIs/types/functions: defines and exports `expire_client()`, then dispatches `reboot`, `unlink`, `rename`, `link`, `chmod`, and `expire`. Remote operations use `ssh root@$server` for privileged restart/expire and `ssh $server` for normal file operations.

Control flow/state: first CLI argument selects the server, second selects the command, and later arguments are passed into the remote shell snippet.

Dependencies/integration: assumes SSH connectivity, appropriate root access for service restart and `/proc/fs/nfsd/clients` control, and systemd service name `nfs-server.service`.

Risks/test signals: unquoted interpolation makes filenames and client names with spaces unsafe and creates shell-injection risk in untrusted scenarios. In test labs, failures surface as server-helper nonzero exits or unchanged server-side state.
<!-- END_FILE_RESEARCH: sources/test-tools/pynfs/examples/server_helper.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/pynfs/nfs4.0/lib/rpc/__init__.py -->
# sources/test-tools/pynfs/nfs4.0/lib/rpc/__init__.py

Purpose: package convenience initializer for the pynfs RPC library.

Important APIs/types/functions: executes `from rpc import *` and declares `__all__ = ['rpcsec', 'rpc_const.py', 'rpc_type.py']`. It is intended to expose the top-level RPC module names to older pynfs imports.

Control flow/state: import-time only; no persistent state beyond whatever the imported `rpc` module initializes.

Dependencies/integration: depends on Python import path layout where `rpc` resolves to the local package/module set. It supports legacy code that imports from `rpc` directly.

Risks/test signals: the `__all__` entries include `.py` suffixes, which is unusual for Python packages and may not behave as intended with `from rpc import *`. Import errors are the only direct signal.
<!-- END_FILE_RESEARCH: sources/test-tools/pynfs/nfs4.0/lib/rpc/__init__.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/pynfs/nfs4.0/lib/rpc/rpc.py -->
# sources/test-tools/pynfs/nfs4.0/lib/rpc/rpc.py

Purpose: core ONC RPC transport layer for pynfs. It implements record-marked TCP RPC clients, a poll-based RPC server, RPC reply validation, XID tracking, reconnection/resend behavior, and pluggable security flavors.

Important APIs/types/functions: socket monkey patches `_recv_all()`, `_recv_record()`, and `_send_record()` implement RFC record marking. `RPCClient` owns per-thread sockets, packers/unpackers, outstanding XID caches, `send()`, `listen()`, `call()`, `get_call_header()`, and `check_reply()`. `Server` abstracts poll/select event dispatch. `RPCServer` accepts connections, buffers record fragments, dispatches command records, decodes RPC calls, invokes `handle_<proc>()`, applies security unwrapping/wrapping, and packs accepted/denied replies. Exceptions `RPCError`, `RPCAcceptError`, and `RPCDeniedError` expose protocol errors.

Control flow/state: clients create one TCP socket per thread, assign monotonically wrapping XIDs, cache request headers/data until a matching reply arrives, and cache out-of-order replies. Servers keep dictionaries keyed by fd for read buffers, write buffers, partial packets, queued records, and sockets. Security objects mediate credentials, verifiers, and data wrapping.

Dependencies/integration: depends on generated `rpc_const`, `rpc_type`, `rpc_pack`, optional GSS security, Python sockets, poll/select, and threading. `nfs4lib.NFS4Client` subclasses `RPCClient`; callback server subclasses `RPCServer`.

Risks/test signals: monkey-patching `socket.socket` is global. Reconnect resends can duplicate non-idempotent calls if the server processed a request before disconnect. Some `raise` statements lack explicit exception objects. Test signals include RPC mismatch/auth exceptions, duplicate XID errors, truncated record handling, and server fd cleanup on poll errors.
<!-- END_FILE_RESEARCH: sources/test-tools/pynfs/nfs4.0/lib/rpc/rpc.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/pynfs/nfs4.0/lib/rpc/rpcsec/__init__.py -->
# sources/test-tools/pynfs/nfs4.0/lib/rpc/rpcsec/__init__.py

Purpose: empty package marker for pynfs RPC security flavors.

Important APIs/types/functions: no runtime definitions are present. The package contains `base.py`, `sec_auth_none.py`, `sec_auth_sys.py`, and optional GSS support modules.

Control flow/state: import has no side effects.

Dependencies/integration: enables relative imports such as `.base` and `.sec_auth_gss` from the RPC layer.

Risks/test signals: none beyond package discovery. An empty initializer keeps security flavor modules independently loadable.
<!-- END_FILE_RESEARCH: sources/test-tools/pynfs/nfs4.0/lib/rpc/rpcsec/__init__.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/pynfs/nfs4.0/lib/rpc/rpcsec/base.py -->
# sources/test-tools/pynfs/nfs4.0/lib/rpc/rpcsec/base.py

Purpose: base abstraction for RPC authentication/security flavors used by pynfs RPC clients and servers.

Important APIs/types/functions: `SecError` is the common exception. `SecFlavor` defines `_none = opaque_auth(AUTH_NONE, b'')` and default no-op implementations for `initialize()`, `secure_data()`, `unsecure_data()`, `make_cred()`, `make_verf()`, `make_reply_verf()`, `get_owner()`, `get_group()`, and `check_verf()`.

Control flow/state: the base class is stateless and returns AUTH_NONE credentials/verifiers unless a subclass overrides behavior. Data wrapping and unwrapping are identity functions by default.

Dependencies/integration: imports RPC constants and `opaque_auth` XDR type. `rpc.py` treats concrete security flavor objects through this interface.

Risks/test signals: subclasses must obey the same method contracts because RPC header packing calls `make_cred()` before `make_verf()` and server replies call `make_reply_verf()`. Base behavior is suitable only for no-auth paths.
<!-- END_FILE_RESEARCH: sources/test-tools/pynfs/nfs4.0/lib/rpc/rpcsec/base.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/pynfs/nfs4.0/lib/rpc/rpcsec/sec_auth_gss.py -->
# sources/test-tools/pynfs/nfs4.0/lib/rpc/rpcsec/sec_auth_gss.py

Purpose: RPCSEC_GSS security flavor for pynfs, implementing context initialization, per-call credentials/verifiers, integrity/privacy wrapping, reply unwrapping, and verifier checking for GSS/Kerberos-backed RPC.

Important APIs/types/functions: `show_minor()`, `show_major()`, and `hint_string()` format GSS/Kerberos errors. `SecAuthGss` manages per-thread GSS packers/unpackers, `gss_seq_num`, `gss_handle`, and `gss_context`. `initialize()` performs the RFC 2203 context creation loop by sending NULL RPC calls with tokens. `make_cred()` emits INIT, CONTINUE_INIT, or DATA credentials. `secure_data()` and `unsecure_data()` implement `rpc_gss_svc_none`, integrity, and privacy services. `make_reply_verf()` and `check_verf()` create/verify sequence-number MICs.

Control flow/state: initialization is explicitly not thread-safe; after completion, calls increment `gss_seq_num` under a lock. Integrity wraps opaque `seq+data` plus checksum; privacy wraps encrypted `seq+data`. Server-side `handle_proc()` can accept INIT but other GSS procedures remain stubbed.

Dependencies/integration: imports `gssapi`, generated GSS constants/types/packers, and RPC constants. `rpc.py` adds GSS to supported flavors only if this module imports successfully.

Risks/test signals: several comments mark stubs or API drift risks, including server-side limited procedure handling and sequence overflow. Bugs would surface as `SecError`, GSS exceptions, verifier failures, mismatched sequence numbers, or RPC auth errors.
<!-- END_FILE_RESEARCH: sources/test-tools/pynfs/nfs4.0/lib/rpc/rpcsec/sec_auth_gss.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/pynfs/nfs4.0/lib/rpc/rpcsec/sec_auth_none.py -->
# sources/test-tools/pynfs/nfs4.0/lib/rpc/rpcsec/sec_auth_none.py

Purpose: concrete AUTH_NONE security flavor for pynfs RPC.

Important APIs/types/functions: `SecAuthNone` subclasses `SecFlavor` without overrides, inheriting AUTH_NONE credentials, AUTH_NONE verifiers, identity data wrapping, and no verifier checks.

Control flow/state: stateless. Every RPC call uses an empty AUTH_NONE opaque auth.

Dependencies/integration: used by `rpc.py` as the default security flavor when no `sec_list` is provided.

Risks/test signals: appropriate only for servers that accept unauthenticated RPC. Authentication failures will surface as RPC denied/accepted errors from the client layer, not inside this class.
<!-- END_FILE_RESEARCH: sources/test-tools/pynfs/nfs4.0/lib/rpc/rpcsec/sec_auth_none.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/pynfs/nfs4.0/lib/rpc/rpcsec/sec_auth_sys.py -->
# sources/test-tools/pynfs/nfs4.0/lib/rpc/rpcsec/sec_auth_sys.py

Purpose: AUTH_SYS security flavor implementation for pynfs RPC, packing UNIX-style machine, uid, gid, and supplemental groups into the RPC credential body.

Important APIs/types/functions: `SecAuthSys.__init__()` validates machinename length <=255 and gid array length <=16, then uses `xdrlib`/`xdrlib3.Packer` to pack stamp, machinename, uid, gid, and group array. `make_cred()` returns `opaque_auth(AUTH_SYS, self.cred)`. `get_owner()` and `get_group()` expose uid/gid for server-side ownership checks.

Control flow/state: credential bytes are created once at object construction and reused for each call. No verifier override is provided, so the base AUTH_NONE verifier is used.

Dependencies/integration: consumed by `nfs4lib.AuthSys` as the default NFSv4 client security object. Depends on generated RPC constants/types and XDR packing.

Risks/test signals: the default `gids=[]` is mutable but not modified. Packing errors are wrapped in `SecError`; authentication failures later appear as RPC auth errors from the server.
<!-- END_FILE_RESEARCH: sources/test-tools/pynfs/nfs4.0/lib/rpc/rpcsec/sec_auth_sys.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/pynfs/nfs4.0/lib/testmod.py -->
# sources/test-tools/pynfs/nfs4.0/lib/testmod.py

Purpose: pynfs test-suite runner and reporting framework. It discovers test functions, parses docstring metadata, resolves dependencies/flags/version ranges, runs tests in dependency order, records outcomes, and emits text, JSON, and XML reports.

Important APIs/types/functions: outcome constants model not-run/running/wait/omit/fail/unsupported/warn/pass. `Result` stores outcome, message, traceback, and default marker. `Test` wraps one test function, parses `FLAGS`, `DEPEND`, `CODE`, and `VERS`, formats display output, provides `fail()`, `fail_support()`, `pass_warn()`, and runs environment lifecycle hooks. `Environment` is a base hook class. `runtests()` and `_runtree()` resolve dependencies recursively. `createtests()` imports package modules from `__all__`, finds `test*` functions, validates unique codes, builds flag bitmasks, and resolves dependencies. `printresults()`, `json_printresults()`, and `xml_printresults()` summarize results.

Control flow/state: each `Test` transitions through `TEST_WAIT`, run/omit/fail/pass states, and stores elapsed time. Dependencies can be other tests or callable dependency functions marked `DEP_FUNCT`. Environment startup/shutdown runs around each test, with cleanup of sessions/clients after success.

Dependencies/integration: imports `nfs4lib`, Python import/introspection, traceback formatting, JSON, and DOM XML. It is used by pynfs command-line runners to turn suite modules into executable tests.

Risks/test signals: duplicate `def _run_filter` text appears in the file and would be a syntax error in the shown source if not otherwise patched; this is a critical import-time risk. Docstring metadata is mandatory for codes and fragile under renamed tests. Report outputs are the suite-level test signals.
<!-- END_FILE_RESEARCH: sources/test-tools/pynfs/nfs4.0/lib/testmod.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/pynfs/nfs4.0/nfs4acl.py -->
# sources/test-tools/pynfs/nfs4.0/nfs4acl.py

Purpose: utility module for translating between POSIX-like mode bits and NFSv4 ACL ACE lists, validating ACLs that map to POSIX semantics, and printing ACLs.

Important APIs/types/functions: constants define file and directory read/write/execute masks, owner/all flag sets, default inheritance flags, used bits, ACE types, and mode lookup tables. `mode2acl()` creates six ACEs for OWNER@, GROUP@, and EVERYONE@ allow/deny pairs. `acl2mode()` derives octal mode from first matching allow/deny ACEs. `maps_to_posix()` validates ACL shape and delegates to `chk_owners()`, `chk_groups()`, and `chk_everyone()`. `chk_pair()` and `chk_triple()` enforce complementary allow/deny masks and repeated mask structure. `printableacl()` formats ACEs.

Control flow/state: functions are pure transformations/validators over ACE lists except that validators delete elements from a working copy. No persistent state exists.

Dependencies/integration: imports generated NFSv4 constants and `nfsace4` type. Tests use it to generate expected ACLs and verify server-returned ACL mapping.

Risks/test signals: `acl2mode()` contains a likely typo `perm[keys] = 0`, which would raise if a named ACE is missing. Mapping comments acknowledge incomplete checks for legal access-mask sets and flag combinations. Failures surface as `ACLError` or mismatched mode/ACL expectations.
<!-- END_FILE_RESEARCH: sources/test-tools/pynfs/nfs4.0/nfs4acl.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/pynfs/nfs4.0/nfs4client.py -->
# sources/test-tools/pynfs/nfs4.0/nfs4client.py

Purpose: interactive Python shell for manually driving an NFSv4 server with pynfs operations.

Important APIs/types/functions: `PyShell` subclasses `code.InteractiveConsole`, creates `nfs4lib.NFS4Client("myid", server, homedir=[])`, imports generated NFSv4 types/constants into locals, exposes client operation builders as uppercase commands, and binds readline tab completion. `modify_packers()` improves `entry4.__repr__`. `main()` launches the shell with a prompt hint.

Control flow/state: startup adjusts `sys.path` when run from package root, initializes a live NFS4 client and callback server through `nfs4lib`, then enters an interactive console. Completion evaluates dotted expressions against shell locals.

Dependencies/integration: depends on readline, generated `xdrdef` modules, `nfs4lib`, and an accessible NFS server argument. It is a developer/test operator tool rather than automated test code.

Risks/test signals: completion uses `eval()` on partially typed expressions, acceptable for an interactive trusted shell but unsafe for untrusted input. Runtime signals are interactive RPC responses, exceptions, and printed tracebacks.
<!-- END_FILE_RESEARCH: sources/test-tools/pynfs/nfs4.0/nfs4client.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/pynfs/nfs4.0/nfs4lib.py -->
# sources/test-tools/pynfs/nfs4.0/nfs4lib.py

Purpose: high-level NFSv4 client library for pynfs. It wraps the lower RPC layer with NFSv4 COMPOUND construction/validation, generated XDR packers/unpackers, callback server handling, file/object helpers, stateid/seqid management, ACL/attribute conversion helpers, and URL parsing.

Important APIs/types/functions: exception classes `BadCompoundRes`, `UnexpectedCompoundRes`, and `InvalidCompoundRes` represent NFS protocol failures. `FancyNFS4Packer/Unpacker` convert bitmaps, fattrs, and dirlists into friendlier Python forms. `CBServer` handles callback NULL and CB_COMPOUND with CB_GETATTR and CB_RECALL support. `NFS4Client` extends `rpc.RPCClient` and provides `compound()`, `init_connection()`, `setclientid()`, `open()`, path helpers, getattr/readdir/read/write/create/remove/rename/open-confirm/lock/close/commit helpers, and tree creation. Module functions include `check_result()`, attribute bit-name caches, `dict2fattr()`, `fattr2dict()`, `list2bitmap()`, `bitmap2list()`, and `parse_nfs_url()`.

Control flow/state: client construction starts a callback RPC server thread, opens a callback control socket, initializes RPC security, and tracks `clientid`, callback ids, owner sequence ids, verifier, homedir, and options. `compound()` packs operations, retries `NFS4ERR_DELAY`, unpacks results, and enforces response operation ordering/status invariants. File/open/lock helpers update seqids only when protocol rules allow. Callback recall state is protected by a lock and reset after recall handling.

Dependencies/integration: depends on `rpc.rpc`, generated NFSv4 constants/types/packers, `nfs_ops.NFS4ops`, sockets, threading, inspect, and Python XDR error classes. It is the central integration layer for pynfs automated tests and the interactive client.

Risks/test signals: several code comments mark stubs/FIXMEs around callbacks, retry behavior, and server quirks. Mutable default arguments are used for attrs/sec lists/path defaults. A visible duplicate line in `do_readdir()` suggests source hygiene risk. Test signals are raised NFS exceptions, invalid compound validation failures, callback op counts/results, and helper-returned status fields such as read data, write count, lockid, and stateid.
<!-- END_FILE_RESEARCH: sources/test-tools/pynfs/nfs4.0/nfs4lib.py -->
