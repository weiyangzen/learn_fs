# subset-b-009296 research

Grouped research report for LTP syscall tests under `sources/test-tools/ltp/testcases/kernel/syscalls`. Each section title preserves the exact source path and is wrapped for reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fanotify/fanotify16.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/fanotify/fanotify16.c

Purpose: validates fanotify directory-entry modification reporting across `FAN_REPORT_DFID_NAME`, `FAN_REPORT_DIR_FID`, `FAN_REPORT_DFID_FID`, `FAN_REPORT_DFID_NAME_FID`, and `FAN_REPORT_DFID_NAME_TARGET`. It covers create, delete, move, rename, open, close, self events, child events, and ignored rename masks on filesystem and inode marks.

Important APIs/types/functions: `fanotify_init`, `fanotify_mark`, `fanotify_event_metadata`, `fanotify_event_info_fid`, `file_handle`, `fanotify_save_fid`, `SAFE_FANOTIFY_INIT`, `SAFE_FANOTIFY_MARK`, `SAFE_MOUNT`, `SAFE_UMOUNT`, and `name_to_handle_at` availability via `HAVE_NAME_TO_HANDLE_AT`. Local `event_t` captures expected masks, parent fid, child fid, names, and old/new rename names.

Control flow: `setup()` probes required fanotify capabilities, prepares mount-relative paths, and creates a temp directory. `do_test()` selects a case, initializes a group, marks either the mounted filesystem or watched directories, creates and bind-mounts a subdirectory, records expected fids, generates file and directory operations, reads the event buffer, then walks events while checking mask merging, info record type, fid bytes, fsid, filename, pid, and optional child fid records.

State/persistence behavior: the test mutates a mounted scratch filesystem, creates and removes files/directories, bind-mounts a subdirectory, and relies on fanotify queue state accumulated between operations and reads. Expected state is held in `event_set`; the actual persistent filesystem state is cleaned by unlink, rmdir, unmount, and closing the notification fd.

Dependencies/integration: integrates the LTP fanotify compatibility header, filesystem test matrix, root-only mounting, file-handle support, and kernel feature probes for filesystem marks, target fid reporting, and `FAN_RENAME`.

Risks/test signals: high sensitivity to filesystem event ordering and kernel merge rules. Failures are precise `TFAIL` diagnostics for extra/missing events, wrong info type, wrong handle, wrong name, wrong pid, or unexpected child-fid cardinality; unsupported kernel features are reported as `TCONF`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fanotify/fanotify16.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fanotify/fanotify17.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/fanotify/fanotify17.c

Purpose: checks enforcement of fanotify group and mark limits globally and inside user namespaces. It verifies `EMFILE` when group limits are hit and `ENOSPC` when mark limits are hit, including per-user-namespace limit overrides when supported.

Important APIs/types/functions: `fanotify_init`, `fanotify_mark`, `unshare(CLONE_NEWUSER)`, proc/sys files such as `PATH_FS_MAX_USER_GROUPS`, `PATH_FS_MAX_USER_MARKS`, `PATH_USER_MAX_FANOTIFY_GROUPS`, `PATH_USER_MAX_FANOTIFY_MARKS`, `PATH_USER_MAX_USER_NAMESPACES`, `SAFE_FILE_SCANF`, `SAFE_FILE_PRINTF`, and `setrlimit(RLIMIT_NOFILE)`.

Control flow: `setup()` creates the watched file, verifies fanotify support, records and temporarily raises `max_user_namespaces`, reads current global fanotify limits if available, and raises the open-file limit. Each test forks a child; the child optionally unshares a user namespace and maps uid 0, optionally lowers namespace-local group or mark limits, then loops creating groups and marks until the expected limit error occurs.

State/persistence behavior: modifies proc/sys namespace knobs and restores `max_user_namespaces` in cleanup. It intentionally leaks fanotify fds inside the child because process exit releases them, making limit accounting the state under test rather than long-lived resources.

Dependencies/integration: root is required for namespace/sysctl manipulation. Older kernels without per-user fanotify limits or namespace fanotify support are handled by fallback defaults and `TCONF`.

Risks/test signals: depends on writable proc/sys limit files and enough `RLIMIT_NOFILE`. Passing signals are limit-specific `TPASS` messages; unexpected `EPERM`, unexpected errno, or ability to create beyond the configured limit indicates a kernel or environment mismatch.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fanotify/fanotify17.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fanotify/fanotify18.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/fanotify/fanotify18.c

Purpose: validates unprivileged fanotify listener restrictions. It ensures disallowed init flags, disallowed mark scopes, and permission-event masks fail for an unprivileged process, while permitted unprivileged inode notification setup succeeds.

Important APIs/types/functions: `fanotify_init`, `fanotify_mark`, `FANOTIFY_REQUIRED_USER_INIT_FLAGS`, `FAN_UNLIMITED_QUEUE`, `FAN_UNLIMITED_MARKS`, `FAN_CLASS_CONTENT`, `FAN_CLASS_PRE_CONTENT`, `FAN_REPORT_TID`, `FAN_MARK_MOUNT`, `FAN_MARK_FILESYSTEM`, `FAN_ALL_EVENTS`, `FAN_ALL_PERM_EVENTS`, `SAFE_SETUID`, and `SAFE_GETPWNAM`.

Control flow: `setup()` creates a file on a mounted scratch filesystem, verifies fanotify fid support, drops from root to `nobody`, and confirms unprivileged fanotify is available. Each table case calls `fanotify_init`; expected `EPERM` on forbidden init flags passes. If initialization succeeds, it attempts `fanotify_mark` and expects `EPERM` for forbidden mount/filesystem marks or permission event masks, otherwise success is the expected result.

State/persistence behavior: only one test file and one notification fd are maintained. The process permanently drops uid during setup, so test state is mainly process credentials and the fanotify group lifetime until close.

Dependencies/integration: requires root initially to mount and then drop privileges, kernel support for unprivileged fanotify, and LTP fanotify constants that model required user init flags.

Risks/test signals: failure modes distinguish unsupported unprivileged fanotify (`TCONF`) from incorrect permission enforcement (`TFAIL` or `TBROK`). The test is sensitive to kernel policy changes around unprivileged fanotify.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fanotify/fanotify18.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fanotify/fanotify19.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/fanotify/fanotify19.c

Purpose: verifies the limited event records delivered to unprivileged fanotify listeners. It checks self-generated and child-generated open/access/modify/close events, both before and after temporarily restoring privileged effective uid before reading.

Important APIs/types/functions: `fanotify_init`, `fanotify_mark`, `FANOTIFY_REQUIRED_USER_INIT_FLAGS`, `FAN_ALL_EVENTS`, `fanotify_event_metadata`, `FAN_EVENT_OK`, `FAN_EVENT_NEXT`, `SAFE_FORK`, `SAFE_WAITPID`, `SAFE_SETEUID`, and `SAFE_GETPWNAM`.

Control flow: `setup()` creates the watched file, makes it writable by unprivileged users, verifies fanotify fid support, and stores the original euid. Each case drops to `nobody`, initializes an unprivileged listener, marks the file, generates events either in the current process or a child, optionally restores root before reading, then scans merged event masks against the expected sequence.

State/persistence behavior: the test mutates the file by reading and writing one byte. Fanotify queue state is consumed once per case. For unprivileged listeners, expected event fds are `FAN_NOFD`; child-originated event pid is expected to be zero.

Dependencies/integration: requires a mounted filesystem, root for setup and credential switching, and the kernel behavior from the tagged unprivileged fanotify change. Child synchronization is simple wait-based rather than checkpoint-based.

Risks/test signals: non-permission events may merge, so the scanner subtracts expected bits from one event. Failures include wrong mask bit, wrong pid visibility, unexpected real fd, premature loop exit, or unsupported unprivileged fanotify.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fanotify/fanotify19.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fanotify/fanotify20.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/fanotify/fanotify20.c

Purpose: validates `FAN_REPORT_PIDFD` initialization rules. It checks that combining pidfd reporting with `FAN_REPORT_TID` fails with `EINVAL`, while combining pidfd reporting with fid/dfid-name reporting remains valid.

Important APIs/types/functions: `fanotify_init`, `FAN_REPORT_PIDFD`, `FAN_REPORT_TID`, `FAN_REPORT_FID`, `FAN_REPORT_DFID_NAME`, `REQUIRE_FANOTIFY_INIT_FLAGS_SUPPORTED_ON_FS`, and `TST_EXP_FD_OR_FAIL`.

Control flow: `do_setup()` verifies `FAN_REPORT_PIDFD` support on the mounted test path. `do_test()` runs the two table cases, calling `fanotify_init` with the specified flags and asserting either the expected `EINVAL` or a valid fd that is then closed.

State/persistence behavior: no filesystem events are generated. State is limited to feature probing and the transient fanotify group fd.

Dependencies/integration: needs root and LTP's all-filesystems mount harness. It depends on Linux pidfd fanotify support introduced in v5.15-rc1 and gracefully skips if unsupported.

Risks/test signals: narrow API contract test. Passing is either the precise expected errno for invalid flag combinations or successful fd creation for compatible reporting flags; any other init failure is a regression or unsupported environment.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fanotify/fanotify20.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fanotify/fanotify21.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/fanotify/fanotify21.c

Purpose: checks the `fanotify_event_info_pidfd` record returned in `FAN_REPORT_PIDFD` mode, including valid pidfds, terminated-child pidfd errors, and read-only mount event-fd behavior with and without `FAN_REPORT_FD_ERROR`.

Important APIs/types/functions: `fanotify_init`, `fanotify_mark`, `fanotify_event_info_pidfd`, `pidfd_open`, `/proc/self/fdinfo`, `SAFE_FILE_LINES_SCANF`, `FAN_REPORT_FD_ERROR`, `FAN_NOPIDFD`, `FAN_EVENT_INFO_TYPE_PIDFD`, bind remounts with `MS_RDONLY`, and LTP `test_variants`.

Control flow: setup bind-mounts the test mount, optionally enables `FAN_REPORT_FD_ERROR`, creates the watched file, initializes a pidfd-reporting group, marks `FAN_OPEN`, and records fdinfo for a pidfd to self. Each case remounts rw or ro, generates an event in self or a child, reads queued events, validates pidfd info header fields, checks event fd error reporting, checks expected pidfd error for terminated children, and compares fdinfo for valid pidfds.

State/persistence behavior: state includes a bind mount toggled read-only/read-write, one fanotify queue, and dynamically allocated fdinfo snapshots. Event fd and pidfd descriptors are closed after inspection.

Dependencies/integration: requires root, mounted filesystem support for pidfd fanotify, `pidfd_open`, proc fdinfo fields, and optional `FAN_REPORT_FD_ERROR` support for variant 1.

Risks/test signals: sensitive to pid lifetime races and mount writeability semantics. Strong signals include header length/type checks, pid identity checks, fd error values, and fdinfo equality with the self pidfd baseline.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fanotify/fanotify21.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fanotify/fanotify22.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/fanotify/fanotify22.c

Purpose: verifies `FAN_FS_ERROR` events from corrupted ext4 filesystems. It triggers filesystem aborts and bad inode/link lookups, then checks error records, error counts, and fid records.

Important APIs/types/functions: `fanotify_init`, `fanotify_mark` with `FAN_MARK_FILESYSTEM`, `FAN_FS_ERROR`, `fanotify_event_info_error`, `fanotify_event_info_fid`, `get_event_info_error`, `get_event_info_fid`, `debugfs -w -R`, `fanotify_save_fid`, `poll`, and ext4-only LTP filesystem selection.

Control flow: `pre_corrupt_fs()` creates baseline directories, saves expected fids, unmounts the filesystem, corrupts inode mode and creates a bad link with `debugfs`, then remounts. Each test marks the filesystem for `FAN_FS_ERROR`, triggers one or more errors, polls and reads until enough error counts accumulate, consolidates multiple events, validates metadata, validates generic error info, validates fid identity, removes the mark, and remounts to reset error state.

State/persistence behavior: deliberately corrupts an ext4 test device and repeatedly unmounts/remounts to enter and recover from error states. `null_fid`, `bad_file_fid`, and `bad_link_fid` are persistent expected state within the process.

Dependencies/integration: requires root, ext4, `debugfs`, file-handle support, and specific kernel support tagged in the file. It is tightly coupled to LTP block-device mount orchestration.

Risks/test signals: destructive to the scratch test filesystem by design. Failures show as missing events, wrong errno, wrong aggregate count, missing fid/error records, or mismatched fsid/file handle.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fanotify/fanotify22.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fanotify/fanotify23.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/fanotify/fanotify23.c

Purpose: tests evictable fanotify inode marks. It verifies upgrade from evictable to non-evictable, refusal to downgrade, ignored-mask behavior, eviction-driven mark removal, and restoration of events after cache eviction removes an evictable ignored mark.

Important APIs/types/functions: `fanotify_init`, `fanotify_mark`, `FAN_MARK_EVICTABLE`, `FAN_MARK_IGNORED_MASK`, `FAN_MARK_IGNORED_SURV_MODIFY`, `FAN_MARK_FILESYSTEM`, `FAN_ATTRIB`, `/proc/sys/vm/drop_caches`, `/proc/sys/vm/vfs_cache_pressure`, `fsync`, and `FAN_NONBLOCK`.

Control flow: setup creates the file, probes evictable mark and filesystem `FAN_ATTRIB` support, and raises vfs cache pressure. The test adds an evictable mark, upgrades it, expects `EEXIST` when trying to downgrade, verifies removal after empty mask, installs a filesystem `FAN_ATTRIB` watch, confirms chmod generates an event, adds an evictable ignored mask on the file, confirms chmod is ignored, drops caches twice, verifies mark removal with `ENOENT`, then confirms chmod events return.

State/persistence behavior: mutates file modes, kernel mark state, inode cache state, and global vfs cache pressure, which LTP save/restore handles. A mount cycle flushes pending mark destruction.

Dependencies/integration: restricted to ext2 because shrinker behavior is predictable enough for eviction. Requires root, mounted scratch device, and writable VM sysctls.

Risks/test signals: cache eviction is inherently environment-sensitive. Passing requires expected `EEXIST`, expected no event while ignored, expected `ENOENT` after eviction, and exactly the expected `FAN_ATTRIB` events.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fanotify/fanotify23.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fanotify/fanotify24.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/fanotify/fanotify24.c

Purpose: tests fanotify pre-content and permission events, including custom denial errno responses and range information for mmap/read/write access. It also covers open-exec permission behavior and a regression for correct mmap offset propagation.

Important APIs/types/functions: `FAN_CLASS_PRE_CONTENT`, `FAN_PRE_ACCESS`, `FAN_OPEN_PERM`, `FAN_OPEN_EXEC_PERM`, `FAN_RESPONSE_ERRNO`, `fanotify_response`, `fanotify_event_info_range`, `SAFE_MMAP`, `pread`, `pwrite`, `execve`, mark types `INODE`, `MOUNT`, `FILESYSTEM`, and `PARENT`, plus the resource helper `fanotify_child`.

Control flow: setup creates and truncates a watched data file, verifies `FAN_PRE_ACCESS` support, and copies `fanotify_child` into the mounted filesystem. Each case initializes a pre-content fanotify group, marks files or parent/mount/filesystem, forks a child to perform open, mmap, write, read, close, and exec attempts, then the parent reads permission events, validates mask, pid, range count/offset for pre-access events, writes the configured allow/deny response, checks that reading event fds does not recursively generate events, and waits for child status.

State/persistence behavior: the child mutates and maps a test file and attempts to execute a copied helper. Parent-held fanotify queue state controls whether child syscalls proceed and what errno they observe. `fd_notify` is closed from a SIGCHLD handler to stop blocking reads when the child exits.

Dependencies/integration: root and mounted filesystems are required. It depends on kernel support for pre-content events and the resource file `fanotify_child`.

Risks/test signals: timing and blocking behavior are central. Failures show as wrong event masks, pid mismatch, missing range info, wrong count/offset, wrong child errno, failed response write, or bad child exit.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fanotify/fanotify24.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fanotify/fanotify25.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/fanotify/fanotify25.c

Purpose: verifies that fanotify mount monitoring works on tracefs and delivers `FAN_MODIFY` events for writes to tracing control files.

Important APIs/types/functions: `tst_fs_type`, tracefs magic `TST_TRACEFS_MAGIC`, `SAFE_MOUNT("tracefs")`, `fanotify_init`, `fanotify_mark` with `FAN_MARK_MOUNT`, `FAN_MODIFY`, `read` on the fanotify fd, and tracefs files such as `/sys/kernel/tracing/kprobe_events`.

Control flow: setup mounts tracefs if needed, checks kprobe events support, creates a nonblocking fanotify group, and marks the tracefs mount for modify events. `run()` forks a child; the child writes a kprobe create command, enables it, disables it, removes it, and after each write drains fanotify events, counting only events from its own pid with `FAN_MODIFY`.

State/persistence behavior: temporarily creates and removes a kprobe event under tracefs. The child is used so tracefs is not kept busy by the main process during cleanup. Cleanup closes the fanotify fd and unmounts tracefs only if this test mounted it.

Dependencies/integration: requires root, `CONFIG_TRACING`, tracefs/kprobe support, and LTP taint checking for warning/die taints.

Risks/test signals: environmental support is the main risk. Passing requires exactly one modify event per tracefs write from the child; wrong masks, read errors other than `EAGAIN`, or missing events fail the test.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fanotify/fanotify25.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fanotify/fanotify_child.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/fanotify/fanotify_child.c

Purpose: tiny helper executable for fanotify tests that need a real file to execute. In this subset it is used by `fanotify24.c` when testing `FAN_OPEN_EXEC_PERM` and pre-content behavior around executable opens.

Important APIs/types/functions: only `main(void)` is defined and returns zero. There are no headers, globals, or external dependencies beyond the C runtime entry point.

Control flow: program startup enters `main()` and immediately returns success.

State/persistence behavior: no state is read or written by the helper itself. Its relevance is as a copied executable artifact on the mounted test filesystem.

Dependencies/integration: listed as a resource file by fanotify tests and copied to a mount path before execution.

Risks/test signals: failures would be indirect: inability to copy or execute this helper breaks the parent fanotify test, not this file's own logic.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fanotify/fanotify_child.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fchdir/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/fchdir/Makefile

Purpose: builds the `fchdir` syscall tests as a standard LTP leaf testcase directory.

Important APIs/types/functions: GNU make variables `top_srcdir`, `include $(top_srcdir)/include/mk/testcases.mk`, and `include $(top_srcdir)/include/mk/generic_leaf_target.mk`.

Control flow: the file sets a default relative top source directory, imports common testcase build rules, then imports generic leaf targets that compile the C files in the directory.

State/persistence behavior: no runtime state. Build state is delegated to the LTP make infrastructure and generated object/binary outputs.

Dependencies/integration: depends on LTP's common make fragments for compiler flags, testcase discovery, install rules, and cleanup.

Risks/test signals: risk is low; build failure would indicate missing make infrastructure or incompatible directory layout rather than syscall test behavior.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fchdir/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fchdir/fchdir01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/fchdir/fchdir01.c

Purpose: positive `fchdir(2)` test that creates a directory, opens it, and verifies changing current working directory by file descriptor succeeds.

Important APIs/types/functions: `fchdir`, `SAFE_MKDIR`, `SAFE_OPEN`, `SAFE_CLOSE`, `TST_EXP_PASS`, and `struct tst_test`.

Control flow: `setup()` creates `alpha` in an LTP temp directory and opens it read-only. `verify_fchdir()` calls `fchdir(fd)` and records pass/fail through the LTP expectation macro. `cleanup()` closes the descriptor.

State/persistence behavior: creates one temporary directory and keeps an open directory fd across the test. The process cwd is changed during the test, but the LTP tempdir harness owns surrounding cleanup.

Dependencies/integration: uses the modern `tst_test.h` API with `.needs_tmpdir = 1`.

Risks/test signals: narrow success-path coverage. Failure indicates the directory fd was invalid, filesystem behavior is unexpected, or `fchdir` failed on a valid directory descriptor.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fchdir/fchdir01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fchdir/fchdir02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/fchdir/fchdir02.c

Purpose: negative `fchdir(2)` test for invalid file descriptors.

Important APIs/types/functions: `fchdir`, `TST_EXP_FAIL`, `EBADF`, and `struct tst_test`.

Control flow: `verify_fchdir()` uses a hard-coded invalid descriptor `-5` and asserts that `fchdir` fails with `EBADF`. There is no setup or cleanup because no files are created.

State/persistence behavior: no filesystem or process state should change. The test only observes errno behavior for an invalid fd argument.

Dependencies/integration: minimal modern LTP test with `.test_all`.

Risks/test signals: simple API contract check. Any success or errno other than `EBADF` is reported as failure.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fchdir/fchdir02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fchdir/fchdir03.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/fchdir/fchdir03.c

Purpose: verifies `fchdir(2)` fails with `EACCES` when an unprivileged effective user lacks execute/search permission on the target directory.

Important APIs/types/functions: `SAFE_GETPWNAM`, `SAFE_SETEUID`, `SAFE_MKDIR`, `SAFE_OPEN`, `fchdir`, `TEST`, `TST_RET`, `TST_ERR`, and `tst_res`.

Control flow: setup looks up `nobody`, switches effective uid to that user, creates `fchdir03_dir` with mode `0400`, and opens it. The test calls `fchdir(fd)`, expects `-1`, then specifically requires `TST_ERR == EACCES`.

State/persistence behavior: creates a temporary directory with no execute permission and permanently changes effective uid within the test process. The open fd remains global.

Dependencies/integration: requires root for `seteuid` and an LTP temp directory. It depends on the presence of the `nobody` account.

Risks/test signals: filesystem permission semantics are central. Incorrect privilege setup could turn this into a false pass/fail; success of `fchdir` or errno mismatch fails.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fchdir/fchdir03.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fchmod/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/fchmod/Makefile

Purpose: builds the `fchmod` syscall tests as a standard LTP leaf directory.

Important APIs/types/functions: `top_srcdir`, `testcases.mk`, and `generic_leaf_target.mk`.

Control flow: declares the default top source location and includes LTP common testcase and generic leaf build rules.

State/persistence behavior: no runtime state; build outputs are managed by the included make fragments.

Dependencies/integration: integrates all local `fchmod*.c` files and `fchmod.h` with the LTP build framework.

Risks/test signals: low logic risk. Failures are build-system or environment failures.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fchmod/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fchmod/fchmod.h -->
# sources/test-tools/ltp/testcases/kernel/syscalls/fchmod/fchmod.h

Purpose: shared constants for the `fchmod` test cases.

Important APIs/types/functions: preprocessor definitions `FILE_MODE`, `DIR_MODE`, `PERMS`, `TESTFILE`, and `TESTDIR`.

Control flow: header guard `FCHMOD_H` prevents double inclusion. No functions or executable code are defined.

State/persistence behavior: no state. It centralizes file and directory names and mode masks used by multiple tests.

Dependencies/integration: included by the `fchmod*.c` tests to keep permission constants consistent.

Risks/test signals: risk is limited to shared constant drift. A wrong mode macro affects several tests' expectations.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fchmod/fchmod.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fchmod/fchmod01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/fchmod/fchmod01.c

Purpose: positive coverage for changing regular-file mode through `fchmod(2)` across several permission and special-bit combinations.

Important APIs/types/functions: `fchmod`, `SAFE_OPEN`, `SAFE_FSTAT`, `SAFE_CLOSE`, `TEST`, `TST_RET`, `tst_res`, and constants from `fchmod.h`.

Control flow: setup creates `testfile`. `verify_fchmod()` iterates over modes `0`, execute-only groups, `0777`, and setuid/setgid/sticky combinations, calls `fchmod(fd, mode)`, stats the fd, and compares mode bits after removing `S_IFREG`.

State/persistence behavior: one open file's mode is repeatedly mutated. Each iteration overwrites the previous mode; no content is written.

Dependencies/integration: modern LTP tempdir test. It assumes the filesystem preserves the tested permission and special bits according to normal Linux rules for the current user.

Risks/test signals: failure can come from syscall failure or mode mismatch. The test's comparison masks only the regular-file type bit, so unexpected extra mode bits are visible.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fchmod/fchmod01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fchmod/fchmod02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/fchmod/fchmod02.c

Purpose: verifies root can use `fchmod(2)` to set broad permissions including sticky/setuid/setgid bits on a file not owned by root when the process group matches the file group.

Important APIs/types/functions: `SAFE_GETPWNAM`, `SAFE_GETGRNAM_FALLBACK`, `SAFE_OPEN`, `SAFE_CHOWN`, `SAFE_SETGID`, `fchmod`, `SAFE_FSTAT`, and `PERMS` from `fchmod.h`.

Control flow: setup creates `testfile`, changes ownership to `nobody` and a fallback group, then sets the process gid to that group. The test calls `fchmod(fd, 01777)` and verifies the resulting file mode matches `PERMS` after masking `S_IFREG`.

State/persistence behavior: mutates file ownership, process gid, and file mode. The fd remains open until cleanup.

Dependencies/integration: requires root and known users/groups. It relies on LTP account lookup and tempdir isolation.

Risks/test signals: group/user availability and filesystem special-bit handling can affect results. A syscall failure or incorrect mode is a failure.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fchmod/fchmod02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fchmod/fchmod03.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/fchmod/fchmod03.c

Purpose: verifies a non-root owner can successfully change mode on its own regular file and set the sticky/setuid/setgid bits requested by `PERMS`.

Important APIs/types/functions: `SAFE_GETPWNAM`, `SAFE_SETEUID`, `SAFE_OPEN`, `fchmod`, `fstat`, `TST_EXP_PASS_SILENT`, and constants from `fchmod.h`.

Control flow: setup looks up `nobody`, switches effective uid, and creates `testfile`. The test calls `fchmod(fd, PERMS)`, stats the fd, and verifies all requested `PERMS` bits are present.

State/persistence behavior: process effective uid is changed and a temp file's mode is modified. Cleanup closes the fd but does not restore euid explicitly, relying on process exit.

Dependencies/integration: requires root to switch to `nobody`, tempdir setup, and normal Linux owner permission semantics.

Risks/test signals: the check uses `(file_mode & PERMS) == PERMS`, so extra file-type bits are tolerated. Failure indicates either syscall rejection or missing requested permission bits.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fchmod/fchmod03.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fchmod/fchmod04.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/fchmod/fchmod04.c

Purpose: verifies `fchmod(2)` succeeds on a directory and can set sticky/setuid/setgid-style permission bits when invoked by the directory owner.

Important APIs/types/functions: `SAFE_GETPWNAM`, `SAFE_MKDIR`, `SAFE_OPEN`, `fchmod`, `fstat`, `TST_EXP_PASS_SILENT`, and constants `TESTDIR`, `DIR_MODE`, `PERMS`.

Control flow: setup looks up `nobody`, creates `testdir`, and opens it read-only. The test calls `fchmod(fd, PERMS)` and verifies the resulting directory mode contains all requested permission bits.

State/persistence behavior: creates a temp directory and changes its mode through an open directory fd. Unlike the comment, setup does not switch uid in the current version, so root privileges remain unless inherited behavior changes.

Dependencies/integration: requires root and a tempdir. It depends on directory fds being accepted by `fchmod`.

Risks/test signals: possible mismatch between comment intent and implementation credential state. Failure is syscall failure or missing requested mode bits.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fchmod/fchmod04.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fchmod/fchmod05.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/fchmod/fchmod05.c

Purpose: verifies a non-root directory owner cannot set the setgid bit when its effective/supplementary groups do not match the directory group, while the rest of the requested mode is applied.

Important APIs/types/functions: `tst_get_free_gid`, `SAFE_SETGROUPS`, `SAFE_CHOWN`, `SAFE_SETEGID`, `SAFE_SETEUID`, `fchmod`, `SAFE_FSTAT`, and `PERMS_DIR`.

Control flow: setup creates `testdir`, assigns it to uid `nobody` and a free gid not equal to the user's group, sets supplementary/effective group and uid to `nobody`, and opens the directory. The test calls `fchmod(fd, 043777)` and expects the resulting mode to equal the requested mode with `S_ISGID` cleared.

State/persistence behavior: mutates process uid/gid/groups and directory ownership/mode. Cleanup restores effective uid/gid to root and closes the fd.

Dependencies/integration: root, account database, and a free gid are required.

Risks/test signals: sensitive to Linux setgid clearing rules. The comparison is strict and can expose unexpected special-bit behavior.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fchmod/fchmod05.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fchmod/fchmod06.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/fchmod/fchmod06.c

Purpose: negative `fchmod(2)` errno matrix covering permission denial, bad descriptor, and read-only filesystem behavior.

Important APIs/types/functions: `SAFE_OPEN`, `SAFE_CLOSE`, `SAFE_SETEUID`, `SAFE_GETPWNAM`, `TST_EXP_FAIL`, `.needs_rofs`, and `fchmod`.

Control flow: setup opens a file on the read-only mount, creates two temp files, closes one descriptor to make it invalid, and switches euid to `nobody`. The test table expects `EPERM` on a file not owned by the unprivileged user, `EBADF` on the closed fd, and `EROFS` on the read-only mount fd.

State/persistence behavior: maintains three fds with distinct validity/ownership/filesystem states and changes process euid. The read-only mount is provisioned by LTP.

Dependencies/integration: requires root, read-only filesystem support, and tempdir/mountpoint management.

Risks/test signals: ordering of permission checks can be filesystem-dependent, especially for read-only mounts. The expected errno must match exactly.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fchmod/fchmod06.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fchmodat/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/fchmodat/Makefile

Purpose: builds the `fchmodat` syscall tests with standard LTP leaf rules.

Important APIs/types/functions: `top_srcdir`, `testcases.mk`, and `generic_leaf_target.mk`.

Control flow: defines the relative source root and includes shared testcase and leaf target makefiles.

State/persistence behavior: no runtime state; build products are generated by inherited rules.

Dependencies/integration: ties the local C tests into the LTP build.

Risks/test signals: only build-configuration risk.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fchmodat/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fchmodat/fchmodat01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/fchmodat/fchmodat01.c

Purpose: positive functionality test for `fchmodat(2)` with relative paths under a directory fd, absolute paths where dirfd is ignored, and `AT_FDCWD` relative paths.

Important APIs/types/functions: `fchmodat`, `SAFE_MKDIR`, `SAFE_OPEN`, `SAFE_LSTAT`, `tst_tmpdir_genpath`, LTP buffer allocation, and `AT_FDCWD`.

Control flow: setup creates `fchmodatdir/fchmodatfile`, opens the directory and file, and computes an absolute path. Each table case calls `fchmodat(*fd, *pathname, 0600, 0)`, then `lstat`s the full path and verifies the regular-file mode is `0600`.

State/persistence behavior: one file's mode is repeatedly set through different path resolution modes. Open directory and file fds are closed in cleanup.

Dependencies/integration: tempdir and dynamically managed strings from `tst_buffers`.

Risks/test signals: verifies path resolution plus mode mutation. Failures are syscall failure or mode mismatch after `lstat`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fchmodat/fchmodat01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fchmodat/fchmodat02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/fchmodat/fchmodat02.c

Purpose: negative `fchmodat(2)` errno coverage for invalid dirfd/path/flag combinations.

Important APIs/types/functions: `fchmodat`, `tst_get_bad_addr`, `PATH_MAX`, `TST_EXP_FAIL`, `SAFE_OPEN`, LTP buffers, and errno constants `ENOTDIR`, `EBADF`, `EFAULT`, `ENAMETOOLONG`, `ENOENT`, `EINVAL`.

Control flow: setup creates and opens a regular file, assigns a bad user pointer, and fills an overlong pathname buffer. Each table case calls `fchmodat` with the configured fd, pathname pointer, and flags, expecting the specific errno.

State/persistence behavior: maintains one open regular-file fd and fixed path buffers. No successful chmod should occur.

Dependencies/integration: tempdir and LTP bad-address helper.

Risks/test signals: errno precedence may be kernel-sensitive when several arguments are invalid. The table is designed so each case isolates one error path.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fchmodat/fchmodat02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fchmodat2/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/fchmodat2/Makefile

Purpose: builds the `fchmodat2` tests through the LTP testcase make framework.

Important APIs/types/functions: `top_srcdir`, `testcases.mk`, and `generic_leaf_target.mk`.

Control flow: sets the source root and includes common build fragments.

State/persistence behavior: no runtime state.

Dependencies/integration: covers newer `fchmodat2` tests and their LAPI syscall wrappers.

Risks/test signals: build-only risk, especially around availability of syscall numbers and LAPI headers.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fchmodat2/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fchmodat2/fchmodat2_01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/fchmodat2/fchmodat2_01.c

Purpose: validates `fchmodat2(2)` on regular files, symlinks, and directories, including `AT_SYMLINK_NOFOLLOW` and `AT_EMPTY_PATH` behavior.

Important APIs/types/functions: `SAFE_FCHMODAT2`, raw `tst_syscall(__NR_fchmodat2)`, `SAFE_FSTATAT`, `AT_SYMLINK_NOFOLLOW`, `AT_EMPTY_PATH`, `O_PATH`, `SAFE_SYMLINKAT`, and all-filesystems LTP mount support.

Control flow: setup opens the mount directory with `O_PATH`, creates a directory, regular file, and symlink. `run()` tests regular-file chmod with and without nofollow, chmod via symlink target with flags zero, expected `EOPNOTSUPP` for nofollow symlink chmod, and `AT_EMPTY_PATH` chmod on an open directory fd.

State/persistence behavior: repeatedly changes file and directory modes and creates/removes a symlink and directory on each filesystem under test.

Dependencies/integration: root, formatted mounted device, all-filesystems matrix, LAPI fcntl/stat wrappers, and kernel behavior tagged to VFS blocking symlink nofollow chmod.

Risks/test signals: symlink mode behavior varies by filesystem/kernel support. The test expects symlink itself to remain `0777` and nofollow chmod to fail with `EOPNOTSUPP`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fchmodat2/fchmodat2_01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fchmodat2/fchmodat2_02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/fchmodat2/fchmodat2_02.c

Purpose: negative `fchmodat2(2)` argument validation for bad fd, missing file, and invalid flags.

Important APIs/types/functions: `tst_syscall(__NR_fchmodat2)`, `SAFE_TOUCH`, `SAFE_OPEN`, `tst_tmpdir_path`, `O_PATH | O_DIRECTORY`, `TST_EXP_FAIL`, and errno constants `EBADF`, `ENOENT`, `EINVAL`.

Control flow: setup records the tempdir path, creates `file.bin`, and opens the temp directory as an `O_PATH` directory fd. Each table case invokes raw `fchmodat2` and checks the expected errno.

State/persistence behavior: creates one file and one directory fd; no successful chmod should occur.

Dependencies/integration: uses LTP syscall-number wrappers and tempdir helpers.

Risks/test signals: narrow errno test. If a libc wrapper or kernel changes validation order, expected errno may need review.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fchmodat2/fchmodat2_02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fchown/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/fchown/Makefile

Purpose: builds the `fchown` syscall tests and enables compatibility support for 16-bit uid/gid variants.

Important APIs/types/functions: `testcases.mk`, `../utils/compat_16.mk`, and `generic_leaf_target.mk`.

Control flow: includes common testcase rules, then the compatibility make fragment before the generic leaf target.

State/persistence behavior: no runtime state. Build configuration may produce compatibility variants depending on the LTP framework.

Dependencies/integration: local tests include `compat_tst_16.h`; this Makefile connects those wrappers to the build.

Risks/test signals: build failures are likely from missing compatibility support or include path issues.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fchown/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fchown/fchown01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/fchown/fchown01.c

Purpose: basic positive `fchown(2)` test on a file descriptor using the process effective uid and gid.

Important APIs/types/functions: `FCHOWN` compatibility macro, `UID16_CHECK`, `GID16_CHECK`, `SAFE_OPEN`, `SAFE_CLOSE`, `TST_EXP_PASS`, and `compat_tst_16.h`.

Control flow: setup validates current uid/gid for compatibility variants and opens `fchown01_testfile`. The test calls `FCHOWN(fd, uid, gid)` and expects success.

State/persistence behavior: creates a temp file and may update ownership to the same uid/gid. The descriptor is held globally and closed in cleanup.

Dependencies/integration: tempdir and 16-bit uid/gid compatibility layer.

Risks/test signals: minimal functionality check. Failure indicates `fchown` rejected a valid fd or the compatibility uid/gid is not usable.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fchown/fchown01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fchown/fchown02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/fchown/fchown02.c

Purpose: verifies superuser `fchown(2)` side effects on setuid/setgid bits: executable files lose both bits, while setgid on a non-group-executable file is preserved.

Important APIs/types/functions: `FCHOWN`, `SAFE_CHMOD`, `SAFE_STAT`, `SAFE_OPEN`, `UID16_CHECK`, `GID16_CHECK`, and mode constants `NEW_PERMS1`, `NEW_PERMS2`, `EXP_PERMS`.

Control flow: setup opens two files. Each test case chmods the file to a special-bit mode, calls `FCHOWN` to current root uid/gid, stats the path, and checks both ownership and resulting mode against the expected clearing/preservation rule.

State/persistence behavior: mutates two files' modes and ownership while root. File descriptors remain open.

Dependencies/integration: requires root and tempdir, plus uid/gid compatibility checks.

Risks/test signals: kernel special-bit clearing semantics are the core. Failures are wrong owner/group or wrong mode after `fchown`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fchown/fchown02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fchown/fchown03.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/fchown/fchown03.c

Purpose: verifies a non-root file owner can change the group of a file to its effective group and that `fchown` clears setuid/setgid bits.

Important APIs/types/functions: `SAFE_GETPWNAM`, `SAFE_SETEGID`, `SAFE_SETEUID`, `SAFE_FCHOWN`, `SAFE_FCHMOD`, `FCHOWN`, `UID16_CHECK`, `GID16_CHECK`, `SAFE_STAT`, and helper checks `check_owner`/`check_mode`.

Control flow: setup switches effective gid/uid to `nobody` and creates the file. The test temporarily returns to root, sets file group to 0 and special bits, switches back to `nobody`, verifies initial state, calls `FCHOWN(fd, -1, gid)`, then verifies group changed and setuid/setgid bits cleared.

State/persistence behavior: toggles credentials, file group, and mode. Cleanup restores effective uid/gid to root and closes the fd.

Dependencies/integration: root and `nobody` account required. Uses compatibility wrappers for uid/gid width.

Risks/test signals: sensitive to supplementary group and privilege semantics. Wrong ownership or mode clearing fails.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fchown/fchown03.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fchown/fchown04.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/fchown/fchown04.c

Purpose: negative `fchown(2)` errno coverage for unprivileged ownership change, invalid fd, and read-only filesystem.

Important APIs/types/functions: `FCHOWN`, `UID16_CHECK`, `GID16_CHECK`, `SAFE_OPEN`, `SAFE_SETEUID`, `SAFE_GETPWNAM`, `TST_EXP_FAIL`, `.needs_rofs`, and errno constants `EPERM`, `EBADF`, `EROFS`.

Control flow: setup opens a normal file, opens the read-only mountpoint, then drops euid to `nobody`. Each test case calls `FCHOWN` using current effective uid/gid and expects the table errno.

State/persistence behavior: maintains one valid writable fd, one invalid fd initialized to `-1`, one rofs fd, and unprivileged credentials.

Dependencies/integration: root, read-only filesystem provisioning, tempdir, and uid/gid compatibility layer.

Risks/test signals: errno precedence is important for rofs and permission cases. Any unexpected success or errno mismatch fails.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fchown/fchown04.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fchown/fchown05.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/fchown/fchown05.c

Purpose: verifies root can set arbitrary numeric uid/gid combinations with `fchown(2)`, including owner-only, group-only, and no-op cases.

Important APIs/types/functions: `FCHOWN`, `SAFE_OPEN`, `SAFE_FSTAT`, `TST_EXP_PASS`, and compatibility header `compat_tst_16.h`.

Control flow: setup opens `testfile`. Each table case calls `FCHOWN(fd, uid, gid)` with values or `-1`, computes expected uid/gid from the previous effective state when an argument is `-1`, and verifies `fstat` ownership.

State/persistence behavior: ownership changes accumulate across table cases; expected values intentionally depend on prior case state.

Dependencies/integration: root and tempdir required. Numeric ids may not correspond to local accounts, which is valid for root `chown` semantics.

Risks/test signals: the expected-value logic depends on case order, especially the first non-`-1` state. Failure indicates ownership did not match requested numeric ids.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fchown/fchown05.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fchownat/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/fchownat/Makefile

Purpose: builds the `fchownat` syscall tests as an LTP leaf directory.

Important APIs/types/functions: `testcases.mk`, `../utils/compat_16.mk`, and `generic_leaf_target.mk`.

Control flow: includes common testcase rules, uid/gid compatibility rules, and generic leaf targets.

State/persistence behavior: no runtime state.

Dependencies/integration: supports tests that exercise both native and compatibility ownership syscalls.

Risks/test signals: build-only risk from make include availability.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fchownat/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fchownat/fchownat01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/fchownat/fchownat01.c

Purpose: positive `fchownat(2)` functionality test for `AT_FDCWD` and directory-fd relative path resolution.

Important APIs/types/functions: `fchownat`, `SAFE_OPEN` with `O_DIRECTORY`, `SAFE_TOUCH`, `SAFE_STAT`, `TST_EXP_PASS`, and `TST_EXP_EQ_LI`.

Control flow: setup opens the current temp directory and creates two files. The test first calls `fchownat(AT_FDCWD, TESTFILE1, 1000, 1000, 0)` and verifies ownership, then calls `fchownat(dir_fd, TESTFILE2, 1000, 1000, 0)` and verifies ownership.

State/persistence behavior: mutates ownership of two temp files to numeric uid/gid 1000.

Dependencies/integration: requires root and tempdir. It assumes numeric uid/gid values are accepted even if no matching accounts exist.

Risks/test signals: failures isolate either `AT_FDCWD` or directory-fd path resolution. Wrong uid/gid after stat fails.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fchownat/fchownat01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fchownat/fchownat02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/fchownat/fchownat02.c

Purpose: verifies `fchownat(2)` with `AT_SYMLINK_NOFOLLOW` changes symlink ownership rather than target ownership.

Important APIs/types/functions: `fchownat`, `SAFE_TOUCH`, `SAFE_SYMLINK`, `SAFE_STAT`, `SAFE_LSTAT`, `AT_SYMLINK_NOFOLLOW`, and `TST_EXP_EXPR`.

Control flow: setup creates a file and symlink, stats both target and link, and aborts if the link already has the target uid/gid expected for the test. The test calls `fchownat(AT_FDCWD, link, 1000, 1000, AT_SYMLINK_NOFOLLOW)`, then checks the target did not change while the link did.

State/persistence behavior: mutates symlink metadata only. The target file should retain original ownership.

Dependencies/integration: root, tempdir, and filesystem support for symlink ownership changes.

Risks/test signals: filesystems may have limited symlink ownership semantics. Failure is target ownership changed or link ownership not changed.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fchownat/fchownat02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fchownat/fchownat03.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/fchownat/fchownat03.c

Purpose: negative `fchownat(2)` errno matrix covering access denial, bad fd, bad address, invalid flags, symlink loop, long path, missing path, non-directory fd, permission denial, and read-only filesystem.

Important APIs/types/functions: `fchownat`, `SAFE_TOUCH`, `SAFE_MKDIR`, `SAFE_OPEN`, `SAFE_SYMLINK`, `SAFE_SETEUID`, `tst_get_bad_addr`, LTP buffers, `.needs_rofs`, and errno constants `EACCES`, `EBADF`, `EFAULT`, `EINVAL`, `ELOOP`, `ENAMETOOLONG`, `ENOENT`, `ENOTDIR`, `EPERM`, `EROFS`.

Control flow: setup creates baseline files, opens the current directory, creates an inaccessible directory/file as root, drops to `nobody`, creates bad-address, regular-file fd, symlink loop, and long path state. Each table case calls `fchownat` with current euid/egid and expects the configured errno.

State/persistence behavior: combines credential state, rofs mount state, symlink loop state, and buffer-managed path strings. No ownership change should succeed.

Dependencies/integration: root, tempdir, read-only mount, and `nobody` account.

Risks/test signals: errno precedence is the main risk. The table isolates cases to make mismatches meaningful.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fchownat/fchownat03.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fcntl/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/fcntl/Makefile

Purpose: builds the `fcntl` syscall test suite with additional libraries, large-file variants, and GNU/largefile feature defines.

Important APIs/types/functions: per-target `LDLIBS` additions for `fcntl33`, `fcntl34`, and `fcntl36`, include `testcases.mk`, include `../utils/newer_64.mk`, pattern rule `%_64: CPPFLAGS += -D_FILE_OFFSET_BITS=64`, global `CPPFLAGS += -D_GNU_SOURCE -D_LARGEFILE64_SOURCE`, and `generic_leaf_target.mk`.

Control flow: target-specific library flags are declared first, then common rules and 64-bit variant support are loaded, then compile flags and generic targets are applied.

State/persistence behavior: no runtime state. Build state includes extra 64-bit test binaries and linked realtime/pthread dependencies for selected tests.

Dependencies/integration: integrates legacy and modern fcntl tests with LTP large-file build infrastructure.

Risks/test signals: incorrect flags could hide GNU constants or large-file APIs. Build failures are the primary signal.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fcntl/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fcntl/fcntl01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/fcntl/fcntl01.c

Purpose: legacy broad smoke test for `fcntl(2)` commands `F_DUPFD`, `F_SETFL`, `F_GETFL`, `F_GETFD`, and `F_SETFD`.

Important APIs/types/functions: legacy LTP `test.h`, `tst_parse_opts`, `TEST_LOOPING`, `tst_tmpdir`, `fcntl`, `open`, `close`, `unlink`, `F_DUPFD`, `F_SETFL`, `O_NDELAY`, `O_APPEND`, `F_GETFD`, and `F_SETFD`.

Control flow: each loop creates eight temp files, closes selected fds to create holes, duplicates `fd[1]` with minimum fd values, validates returned fd positions, tests setting and clearing file status flags, then sets close-on-exec fd flag and checks `F_GETFD`.

State/persistence behavior: creates per-pid temp files, mutates descriptor table holes and duplicated descriptors, mutates file status flags on a shared open file description, and deletes files at loop end.

Dependencies/integration: uses old LTP harness and tempdir support rather than `tst_test.h`.

Risks/test signals: several checks only test bit presence, not exact flag values. Failures are unexpected duplicate fd numbers, flag mutation failures, or cleanup errors.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fcntl/fcntl01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fcntl/fcntl02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/fcntl/fcntl02.c

Purpose: basic `F_DUPFD` test verifying duplicated descriptors are at least the requested minimum fd.

Important APIs/types/functions: `fcntl(fd, F_DUPFD, min_fd)`, `SAFE_OPEN`, `SAFE_CLOSE`, `TEST`, `TST_RET`, and modern `struct tst_test`.

Control flow: setup opens a temp file. The test iterates minimum fd values `0, 1, 2, 3, 10, 100`, duplicates the open fd, checks success and returned value `>= min_fd`, then closes each duplicate.

State/persistence behavior: one original fd persists for the test; duplicate fds are transient descriptor-table state.

Dependencies/integration: tempdir and modern LTP API.

Risks/test signals: simple contract. Failure indicates `F_DUPFD` returned below the minimum or failed unexpectedly.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fcntl/fcntl02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fcntl/fcntl03.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/fcntl/fcntl03.c

Purpose: basic `F_GETFD` test verifying descriptor flags can be queried on a valid fd.

Important APIs/types/functions: `fcntl(fd, F_GETFD, 0)`, `SAFE_OPEN`, `SAFE_CLOSE`, `TEST`, and `tst_res`.

Control flow: setup opens a temp file. The test calls `fcntl` and reports pass on any nonnegative return.

State/persistence behavior: one open file descriptor persists until cleanup. No descriptor flags are changed.

Dependencies/integration: modern LTP tempdir test.

Risks/test signals: minimal API liveness check. It does not assert an exact default flag value.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fcntl/fcntl03.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fcntl/fcntl04.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/fcntl/fcntl04.c

Purpose: basic `F_GETFL` test verifying file status flags can be queried and preserve the `O_RDWR` access mode.

Important APIs/types/functions: `fcntl(fd, F_GETFL, 0)`, `O_ACCMODE`, `O_RDWR`, `SAFE_OPEN`, `SAFE_CLOSE`, and LTP `TEST`.

Control flow: setup opens a temp file `O_RDWR | O_CREAT`. The test calls `F_GETFL`, fails on `-1`, then masks `O_ACCMODE` and requires `O_RDWR`.

State/persistence behavior: one open fd; no file status flags are changed.

Dependencies/integration: modern LTP tempdir harness.

Risks/test signals: passing requires only access-mode correctness. Other status flags are tolerated.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fcntl/fcntl04.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fcntl/fcntl05.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/fcntl/fcntl05.c

Purpose: verifies `F_GETLK` reports `F_UNLCK` and preserves other `struct flock` fields when the requested lock would be placeable.

Important APIs/types/functions: `fcntl(fd, F_GETLK, &flocks)`, `struct flock`, `F_RDLCK`, `F_UNLCK`, `SEEK_CUR`, `SAFE_OPEN`, and `TST_EXP_EQ_LI`.

Control flow: setup opens a temp file and initializes `flocks` with `l_whence = SEEK_CUR`, zero start/len, and current pid. Each run resets `l_type` to `F_RDLCK`, calls `F_GETLK`, and checks `l_type` became `F_UNLCK` while whence/start/len/pid remain as initialized.

State/persistence behavior: no locks are placed. The only mutation is the kernel's update to the user `struct flock`.

Dependencies/integration: modern LTP tempdir test.

Risks/test signals: exact field-preservation expectations are the key. A kernel/libc ABI change to `F_GETLK` output fields would fail this test.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fcntl/fcntl05.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fcntl/fcntl07.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/fcntl/fcntl07.c

Purpose: verifies `FD_CLOEXEC` closes descriptors across `exec` for regular files, both ends of a pipe, and a FIFO.

Important APIs/types/functions: legacy LTP `test.h`, `option_t`, `fcntl(F_SETFD, FD_CLOEXEC)`, `fcntl(F_GETFD)`, `execlp`, `tst_fork`, `SAFE_PIPE`, `SAFE_MKFIFO`, and child mode option `-T`.

Control flow: normal mode opens a file, pipe, and FIFO. For each fd, `verify_cloexec()` sets `FD_CLOEXEC`, forks, and execs the same test binary with `-T fd`. Test mode calls `F_GETFD` on that numeric fd and returns zero only if it fails with `EBADF`, proving the fd was closed during exec.

State/persistence behavior: descriptor flags are changed on several fd types. The same executable is used as both parent test and child verifier.

Dependencies/integration: requires executable lookup by `TCID` in the test environment and legacy LTP safe macros.

Risks/test signals: environment path issues can look like test breakage. Functional failures are child reporting the fd remains open after exec.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fcntl/fcntl07.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fcntl/fcntl08.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/fcntl/fcntl08.c

Purpose: basic `F_SETFL` test using `O_NDELAY | O_APPEND | O_NONBLOCK`.

Important APIs/types/functions: `fcntl(fd, F_SETFL, flags)`, `SAFE_OPEN`, `SAFE_CLOSE`, `TST_EXP_PASS`, and `lapi/fcntl.h`.

Control flow: setup opens a temp file. The single test calls `fcntl` to set the combined status flags and expects success.

State/persistence behavior: mutates file status flags on one open file description. It does not read back the flags.

Dependencies/integration: modern LTP tempdir test with GNU fcntl constants via LAPI.

Risks/test signals: narrow success-only check. It detects rejection of the flag set but not silent partial flag changes.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fcntl/fcntl08.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fcntl/fcntl09.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/fcntl/fcntl09.c

Purpose: legacy smoke test for nonblocking POSIX record locks with `F_SETLK`, covering both write and read lock placement followed by unlock.

Important APIs/types/functions: `fcntl(F_SETLK)`, `struct flock`, `F_WRLCK`, `F_RDLCK`, `F_UNLCK`, legacy `test.h`, `TEST`, `TEST_RETURN`, and temp file setup with `creat`/`open`.

Control flow: setup creates and opens a temp file and initializes flock whence/start/len/pid. Each loop sets `l_type` to write then read lock, calls `F_SETLK`, reports pass/fail, then sets `F_UNLCK` and unlocks before the next type.

State/persistence behavior: places and removes byte-range locks on one file. Lock region is whole file from current position because `l_len = 0`.

Dependencies/integration: legacy LTP harness and tempdir. No child process validates conflicts.

Risks/test signals: basic liveness only. It detects inability to set/unset locks but not cross-process semantics.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fcntl/fcntl09.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fcntl/fcntl10.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/fcntl/fcntl10.c

Purpose: legacy smoke test for blocking POSIX record locks with `F_SETLKW`, covering write/read lock placement and unlock on an uncontended file.

Important APIs/types/functions: `fcntl(F_SETLKW)`, `struct flock`, `F_WRLCK`, `F_RDLCK`, `F_UNLCK`, legacy LTP `TEST`, and temp file setup.

Control flow: setup creates a temp file and initializes flock fields. Each loop tries a write lock and unlock, then a read lock and unlock using `F_SETLKW`, reporting success for each call.

State/persistence behavior: places and removes whole-file locks on one fd. Since there is no competing process, `F_SETLKW` should not block.

Dependencies/integration: legacy LTP tempdir and signal pause handling.

Risks/test signals: only validates uncontended blocking command path. It will not detect incorrect wakeup/deadlock behavior.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fcntl/fcntl10.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fcntl/fcntl11.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/fcntl/fcntl11.c

Purpose: detailed record-lock splitting/coalescing test for adding read locks around existing write locks. It verifies `F_GETLK` reports the correct blocking subrange after parent lock transformations.

Important APIs/types/functions: `fcntl(F_SETLK)`, `fcntl(F_GETLK)`, `struct flock`, `F_WRLCK`, `F_RDLCK`, `F_UNLCK`, pipes for parent/child requests, `mkstemp`, `SAFE_PIPE`, `SAFE_WRITE`, `SAFE_READ`, and helper functions `do_lock`, `do_test`, `compare_lock`, `unlock_file`.

Control flow: setup creates a temp file with known content and pipes. Parent forks a child that repeatedly receives a `struct flock`, calls `F_GETLK`, and returns the result. The parent runs nine blocks that place write/read locks at adjacent, overlapping, nested, and separated byte ranges, asks the child to query conflicts, compares type/whence/start/len/pid, then unlocks all.

State/persistence behavior: uses process-associated POSIX locks on one file, with the child as an external observer so parent-owned locks are visible. Pipe messages are the synchronization state.

Dependencies/integration: legacy LTP harness, fork, pipes, and signal handling for unexpected child death.

Risks/test signals: complex range math and POSIX lock merging semantics. Failures pinpoint wrong lock type, range start/length, or pid after transformations.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fcntl/fcntl11.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fcntl/fcntl12.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/fcntl/fcntl12.c

Purpose: verifies `F_DUPFD` fails with `EMFILE` when the process file descriptor table is exhausted.

Important APIs/types/functions: `getdtablesize`, `open`, `fcntl(F_DUPFD)`, `TST_EXP_FAIL2`, `SAFE_FORK`, and `tst_reap_children`.

Control flow: setup records the descriptor-table size. The test forks a child; the child opens the same file repeatedly until open fails, then calls `fcntl(1, F_DUPFD, 1)` and expects `EMFILE`. The parent reaps the child.

State/persistence behavior: descriptor exhaustion occurs only in the child and is released on child exit. The shared temp filename is unlinked in cleanup.

Dependencies/integration: modern LTP fork/tempdir test.

Risks/test signals: relies on being able to consume all fd slots. External rlimits or inherited descriptors affect the exact loop count but not the expected final errno.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fcntl/fcntl12.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fcntl/fcntl13.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/fcntl/fcntl13.c

Purpose: negative `fcntl(2)` argument validation for lock pointer faults, invalid commands, invalid `l_whence`, and invalid file descriptors.

Important APIs/types/functions: `fcntl`, `F_SETLK`, `F_GETLK`, `tst_get_bad_addr`, `struct flock`, `TST_EXP_FAIL2`, and errno constants `EFAULT`, `EINVAL`, `EBADF`.

Control flow: setup initializes a `struct flock` with invalid `l_whence = -1`. Each table case calls `fcntl` with the configured fd, command, and flock pointer; the null pointer case is replaced by an LTP bad address at runtime.

State/persistence behavior: no files are opened. Tests use fd `1` for argument validation and `-1` for bad-fd validation.

Dependencies/integration: modern LTP bad-address helper.

Risks/test signals: errno precedence depends on command validation order. Cases are separated to target one invalid condition each.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fcntl/fcntl13.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fcntl/fcntl14.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/fcntl/fcntl14.c

Purpose: randomized two-process record-lock test that checks whether child locks block exactly when their byte ranges conflict with parent locks, across normal and mandatory-locking variants.

Important APIs/types/functions: `fcntl(F_SETLK)`, `fcntl(F_GETLK)`, `struct flock`, `SAFE_FORK`, shared `mmap` results, `lseek`, `rand`, `tst_parse_int`, and option `-n` controlling operation count.

Control flow: setup writes a small file, optionally enables mandatory locking in variant 1, and maps shared results. Each generated testcase chooses a file position and random parent/child ranges using `SEEK_CUR`, computes overlap and blocking expectation, parent places its lock, child queries with `F_GETLK`, verifies conflict metadata or `F_UNLCK`, then tries `F_SETLK` expecting either `EWOULDBLOCK` or success.

State/persistence behavior: each iteration opens the same file, sets process locks, forks a child observer, and closes the fd to clear locks. Shared anonymous mapping reports child assertion state.

Dependencies/integration: modern LTP, tempdir, fork, optional mandatory locking support, and skips NFS.

Risks/test signals: randomized coverage can be non-reproducible because it seeds with `time(0)`. Failing debug output includes generated ranges and expected blocking mode.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fcntl/fcntl14.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fcntl/fcntl15.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/fcntl/fcntl15.c

Purpose: checks POSIX file-lock lifetime rules when descriptors are closed, comparing duplicated fds, independently opened fds in the same process, and locks held by another process.

Important APIs/types/functions: `fcntl(F_SETLK)`, `fcntl(F_DUPFD)`, `SAFE_OPEN`, `SAFE_FORK`, `TST_CHECKPOINT_*`, `struct flock`, and predefined `lock_one`/`lock_two`.

Control flow: for each case, parent opens and locks region one, obtains region-two lock either by dup, separate open, or child process, then forks a tester. The tester first verifies both regions are locked, waits while parent closes `fd[0]`, then verifies same-process locks disappeared for dup/open cases while child-held region-two lock remains in the fork case.

State/persistence behavior: creates one file, writes data, holds locks through fd duplication/opening/forking, and uses checkpoints for synchronization. Closing a descriptor is the state transition under test.

Dependencies/integration: modern LTP with fork and checkpoint support.

Risks/test signals: POSIX locks are per-process, not per-fd, so expected behavior differs from open-file-description locks. Failures indicate lock lifetime semantics changed or synchronization failed.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fcntl/fcntl15.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fcntl/fcntl16.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/fcntl/fcntl16.c

Purpose: legacy blocking-lock wakeup test. It verifies children waiting on lock boundaries are notified or remain blocked as expected when the parent changes overlapping locks, across normal, mandatory, and mandatory plus `O_NDELAY` modes.

Important APIs/types/functions: `fcntl(F_SETLK)`, `fcntl(F_SETLKW)`, `struct flock`, signal handlers for `SIGUSR1`, `SIGUSR2`, `SIGALRM`, child process management, `testcases[]` describing parent/child lock sequences, and constants `NOBLOCK`, `WILLBLOCK`, `IGNORED`.

Control flow: each `run_test()` case opens a file, writes data, sets one or two parent locks, forks up to two children that attempt blocking locks, waits for readiness signals, applies parent lock changes, then waits for child exits. Children expected to remain blocked are interrupted by signal and should exit with status 1; nonblocking-success children exit 0.

State/persistence behavior: repeatedly creates locks on one temp file and uses signals plus child exit codes as synchronization state. The file is reopened for each testcase and unlinked after the run.

Dependencies/integration: legacy LTP harness, mandatory locking support, NFS detection, signals, alarms, and fork.

Risks/test signals: timing-sensitive and legacy mandatory locking behavior may be disabled on modern systems. Failures include children not signaling, unexpected child status, lock setup failure, or timeout.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fcntl/fcntl16.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fcntl/fcntl17.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/fcntl/fcntl17.c

Purpose: validates kernel deadlock detection for blocking POSIX record locks. It orchestrates three children so two blocking lock requests form a delayed cycle and expects `EDEADLK`.

Important APIs/types/functions: `fcntl(F_SETLK)`, `fcntl(F_SETLKW)`, `fcntl(F_GETLK)`, `struct flock`, multiple pipes, `fork`, `alarm`, `SIGCHLD`/`SIGALRM` handlers, locks `lock1` through `lock5`, and helper messaging functions `parent_wait`, `child_free`, `stop_children`.

Control flow: setup creates pipes and a temp file. Parent forks three children, commands them to place initial disjoint write locks, verifies those locks with `F_GETLK`, then commands child 2 to block on child 3's range and child 3 to block on a range held by child 1/2. After child 1 releases, a deadlock should be detected and reported through the parent pipe as `EDEADLK`.

State/persistence behavior: child processes own distinct byte-range locks. Parent drives state transitions with pipe messages and uses an alarm to fail if deadlock detection never occurs.

Dependencies/integration: legacy LTP, fork, pipes, signals, and POSIX lock deadlock detection.

Risks/test signals: highly timing/order dependent but explicitly synchronized. Failure means wrong initial lock ownership, missing `EDEADLK`, timeout, or child death.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fcntl/fcntl17.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fcntl/fcntl18.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/fcntl/fcntl18.c

Purpose: legacy negative `fcntl(2)` test for `EFAULT` on bad flock pointers and `EINVAL` on invalid commands, including an unprivileged child path.

Important APIs/types/functions: `fcntl`, `F_GETLK`, invalid pointer cast `(struct flock *)-1`, invalid command `-1`, `tst_fork`, `setreuid`, `getpwnam("nobody")`, and legacy LTP root/tempdir helpers.

Control flow: setup requires root and creates a tempdir. Block 1 opens `temp.dat` and expects `F_GETLK` with an invalid pointer to set `EFAULT`. Block 2 repeats the `EFAULT` check. Block 3 forks a child, drops it to `nobody`, calls `fcntl(fd, -1, &fl)`, and expects `EINVAL`; parent checks child exit status.

State/persistence behavior: opens one temp file and changes child credentials only. The file remains open until cleanup.

Dependencies/integration: requires root and a `nobody` account. Uses legacy LTP APIs.

Risks/test signals: the repeated EFAULT blocks are redundant. The code does not reset errno before every call, so correctness relies on failed calls setting errno as expected.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fcntl/fcntl18.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fcntl/fcntl19.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/fcntl/fcntl19.c

Purpose: detailed record-lock test for unlocking sections around an existing write lock. It verifies the kernel trims or splits write locks correctly after `F_UNLCK` ranges overlap different portions.

Important APIs/types/functions: `fcntl(F_SETLK)`, `fcntl(F_GETLK)`, `struct flock`, parent/child pipes, `mkstemp`, `do_lock`, `do_test`, `compare_lock`, `unlock_file`, `F_WRLCK`, and `F_UNLCK`.

Control flow: setup creates a temp file, writes alphabet data, and starts a child that answers `F_GETLK` queries. Parent runs seven blocks: unlock just before, ending at first byte, overlapping front, middle split, overlapping end, starting at last byte, and starting past end of a write lock. After each unlock, it asks the child to query conflicting write locks and compares the remaining lock regions.

State/persistence behavior: parent-owned write locks are mutated in place; the child observes them as an independent process. Unlock calls can shrink, split, or leave locks untouched depending on overlap.

Dependencies/integration: legacy LTP, fork, pipes, signal handler for child death, tempdir.

Risks/test signals: exact range arithmetic is the test target. Failures report wrong lock type/start/length/pid or unexpected child termination.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fcntl/fcntl19.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fcntl/fcntl20.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/fcntl/fcntl20.c

Purpose: companion to `fcntl19.c` for read locks. It verifies unlocking sections around an existing read lock trims or splits the remaining read-lock regions correctly.

Important APIs/types/functions: `fcntl(F_SETLK)`, `fcntl(F_GETLK)`, `struct flock`, `F_RDLCK`, `F_WRLCK` probe locks, `F_UNLCK`, pipe helpers, `mkstemp`, `do_lock`, `do_test`, `compare_lock`, and `unlock_file`.

Control flow: setup creates the temp file and child query process. Parent runs seven blocks that place a read lock and unlock ranges before, overlapping the front, in the middle, overlapping the end, at the last byte, and past the end. The child queries with a write-lock request so read locks are reported as conflicts, and parent checks the resulting ranges.

State/persistence behavior: manipulates parent-owned read locks while a child process observes them. State is reset with a whole-file unlock after each block.

Dependencies/integration: legacy LTP, fork, pipes, tempdir, signal handling.

Risks/test signals: exact read-lock range splitting is the focus. Failures indicate wrong remaining read-lock extent, unexpected unlocked areas, or synchronization failure.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fcntl/fcntl20.c -->
