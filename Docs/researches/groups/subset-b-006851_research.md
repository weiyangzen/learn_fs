# subset-b-006851 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/liveupdate/liveupdate.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/liveupdate/liveupdate.c

Purpose: kselftest harness coverage for the Live Update Orchestrator character device at `/dev/liveupdate`. It validates ordinary device access, exclusive open behavior, LUO session creation/retrieval constraints, and preservation of supported file descriptors, especially memfds.

Important APIs/types/functions: uses `linux/liveupdate.h` ioctl structs and commands: `liveupdate_ioctl_create_session`, `LIVEUPDATE_IOCTL_CREATE_SESSION`, `liveupdate_session_preserve_fd`, and `LIVEUPDATE_SESSION_PRESERVE_FD`. Local helpers `create_session()` and `preserve_fd()` convert ioctl failures to negative errno values for assertions. Tests are expressed through `kselftest_harness.h` `FIXTURE`, `TEST_F`, `ASSERT_*`, `EXPECT_*`, and `SKIP`.

Control flow: a fixture initializes two device FDs and closes them in teardown. Early tests open `/dev/liveupdate`, skip on `ENOENT`, and check exclusive access returns `EBUSY`. Session tests create duplicate and distinct named sessions. Preservation tests allocate memfds, write known strings, preserve them by token, then seek/read to confirm visible content remains intact. Complex coverage spans two sessions, empty memfds, non-empty memfds, unsupported `/dev/null`, and double-preservation rejection with `EBUSY`.

State and persistence: state is mostly kernel-side LUO session/file tracking. The test keeps session and memfd FDs alive long enough to verify immediate post-ioctl visibility; it does not exercise reboot persistence.

Dependencies and integration points: requires a kernel/device exposing `/dev/liveupdate`, memfd support, and the liveupdate uapi header. Integrates with kselftest result semantics.

Risks: tests assume `/dev/null` has no LUO preservation handler and that LUO enforces process-wide exclusive device open. Some failure paths may leak FDs after a fatal assertion, acceptable for short kselftest runs.

Test signals: pass/fail is assertion-driven; missing device is reported as skip. Key expected errno signals are `ENOENT`, `EBUSY`, and `EEXIST`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/liveupdate/liveupdate.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/liveupdate/luo_kexec_simple.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/liveupdate/luo_kexec_simple.c

Purpose: manual two-stage kexec selftest for LUO persistence of one named session containing one memfd across a kexec reboot.

Important APIs/types/functions: imports `luo_test_utils.h`. Defines session/token/data constants and implements `run_stage_1()` and `run_stage_2()` callbacks consumed by `luo_test()`.

Control flow: stage 1 creates a state-tracking LUO session with token `999` containing next-stage value `2`, creates the main test session, preserves a memfd with token `0x1A`, closes the LUO device, and daemonizes so FDs remain pinned while the operator performs kexec. Stage 2 verifies the state memfd contains stage `2`, retrieves the named test session, restores and verifies the memfd payload, then finishes both the test and state sessions.

State and persistence: relies on LUO preserving sessions and memfd payloads across kexec. State progression is stored inside a preserved memfd, not in the filesystem. A daemonized child intentionally holds session references after stage 1.

Dependencies and integration points: requires `/dev/liveupdate`, kexec-capable environment, the LUO kernel module/device, memfd support, and manual or external reboot orchestration.

Risks: stage mismatch fails hard; stale state sessions from a previous interrupted run can make the system appear to be in stage 2. The daemonized holder must be cleaned through test completion or process management.

Test signals: emits kselftest messages; success requires exact payload recovery and successful `LIVEUPDATE_SESSION_FINISH` for both sessions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/liveupdate/luo_kexec_simple.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/liveupdate/luo_multi_session.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/liveupdate/luo_multi_session.c

Purpose: kexec lifecycle selftest for multiple LUO sessions, including empty sessions and sessions with one or more preserved memfds.

Important APIs/types/functions: uses `luo_create_session()`, `create_and_preserve_memfd()`, `luo_retrieve_session()`, `restore_and_verify_memfd()`, `luo_session_finish()`, and the generic `luo_test()` stage dispatcher.

Control flow: stage 1 writes state stage `2`, creates two empty sessions and two populated sessions, preserving one memfd in `SESSION_FILES_1` and two memfds in `SESSION_FILES_2`. It then daemonizes to pin resources for kexec. Stage 2 reads the state memfd, retrieves all four sessions, verifies all three payloads by token, finishes every test session, finishes the state session, and reports success.

State and persistence: the test asserts that LUO preserves both session namespace and per-token file payloads across kexec. Empty sessions are significant because they validate metadata preservation independent of files.

Dependencies and integration points: same LUO/kexec/manual orchestration dependencies as `luo_kexec_simple.c`. Integrates through shared helper callbacks.

Risks: a partial prior run can leave named sessions that affect detected stage or duplicate-name behavior. Empty-session finalization is an important cleanup step because otherwise persistent metadata may remain.

Test signals: exact data matches for three restored memfds, successful retrieval of two empty sessions, and successful finish calls are the key pass signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/liveupdate/luo_multi_session.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/liveupdate/luo_test_utils.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/liveupdate/luo_test_utils.c

Purpose: shared utility implementation for LUO kexec selftests. It abstracts LUO device open, session ioctls, memfd preservation/restoration, state-file handling, daemonization, and stage selection.

Important APIs/types/functions: wraps `LIVEUPDATE_IOCTL_CREATE_SESSION`, `LIVEUPDATE_IOCTL_RETRIEVE_SESSION`, `LIVEUPDATE_SESSION_PRESERVE_FD`, `LIVEUPDATE_SESSION_RETRIEVE_FD`, and `LIVEUPDATE_SESSION_FINISH`. Uses `memfd_create`, `ftruncate`, `mmap`, `read`, `fork`, `setsid`, `getopt_long`, and kselftest exit helpers.

Control flow: `luo_test()` parses `--stage`, opens `/dev/liveupdate`, probes for the named state session to detect stage 1 versus 2, enforces requested/detected stage agreement, and dispatches to caller-provided stage callbacks. `create_and_preserve_memfd()` creates a one-page memfd, maps and writes the payload, then preserves it under a token. `restore_and_verify_memfd()` retrieves by token, maps the file read-only, and optionally compares payload. `create_state_file()` creates a state session and deliberately leaves its FD open. `daemonize_and_wait()` forks, exits the parent, detaches the child, closes stdio, changes to `/`, and sleeps forever.

State and persistence: state is encoded in preserved memfds; the state session FD is intentionally retained to prevent unpreservation. Process persistence through the daemon child is part of the test contract.

Dependencies and integration points: central integration point for LUO stage tests. Depends on liveupdate uapi, kselftest, memfd, kexec workflow, and process/session semantics.

Risks: `fail_exit` reports current `errno`, so callers should preserve errno before unrelated operations. Infinite daemon children need operator awareness. `create_and_preserve_memfd()` closes the original memfd after preservation, assuming the kernel-side LUO reference is sufficient.

Test signals: skip on missing LUO device; failure on stage mismatch, ioctl errors, or payload mismatch.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/liveupdate/luo_test_utils.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/liveupdate/luo_test_utils.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/liveupdate/luo_test_utils.h

Purpose: public interface for LUO kexec selftest utilities.

Important APIs/types/functions: defines `LUO_DEVICE`, the variadic `fail_exit()` macro using `ksft_exit_fail_msg`, prototypes for LUO device/session helpers, memfd preserve/restore helpers, state helpers, daemonization, and the `luo_test_stage1_fn`/`luo_test_stage2_fn` callback types.

Control flow: no executable control flow; it establishes the callback contract used by the simple and multi-session kexec tests.

State and persistence: exposes functions that create persistent LUO state sessions and daemonized process pinning, but holds no state itself.

Dependencies and integration points: includes `<linux/liveupdate.h>` and `../kselftest.h`; all users must be built in the kernel selftests tree with generated/uapi headers available.

Risks: `fail_exit()` always includes `strerror(errno)`, which can be misleading if called after helper code that changed errno. The header exports low-level integer return conventions where negative errno and positive FDs share the same type.

Test signals: this header shapes how callers convert errors into kselftest failures or skips.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/liveupdate/luo_test_utils.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/lkdtm/Makefile -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/lkdtm/Makefile

Purpose: build/install rule for LKDTM kselftests.

Important APIs/types/functions: includes `../lib.mk`, declares `TEST_FILES := tests.txt`, `TEST_PROGS := stack-entropy.sh`, and generates one shell wrapper per test name parsed from `tests.txt`.

Control flow: `TEST_GEN_PROGS` is computed by reading the first column of `tests.txt`, stripping leading `#`, and appending `.sh` under `$(OUTPUT)`. The pattern rule installs `run.sh` as each generated test wrapper.

State and persistence: no runtime state; it packages generic `run.sh` under many test-specific names.

Dependencies and integration points: depends on `tests.txt`, `run.sh`, `stack-entropy.sh`, and kselftest `lib.mk`. The generated script name is how `run.sh` selects the LKDTM trigger.

Risks: the generated list is only as accurate as `tests.txt`; commented-out tests still get wrappers and are skipped at runtime.

Test signals: kselftest discovers generated wrappers and the entropy script through `TEST_GEN_PROGS`/`TEST_PROGS`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/lkdtm/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/lkdtm/config -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/lkdtm/config

Purpose: kernel configuration fragment for LKDTM hardening/regression selftests.

Important APIs/types/functions: requests `CONFIG_LKDTM`, debug list checks, slab freelist hardening, fortify, kernel stack erase/randomization, hardened usercopy, init-on-free/alloc, UBSAN bounds, strong stack protector, and SLUB debug.

Control flow: none; consumed by kselftest/kconfig tooling.

State and persistence: no runtime state. It influences kernel build-time and boot-time hardening features that LKDTM probes.

Dependencies and integration points: ties the `lkdtm` tests to kernel debug/hardening options and `/sys/kernel/debug/provoke-crash`.

Risks: enabling these options can change performance and debugging behavior; missing options often cause runtime skips rather than failures.

Test signals: a kernel matching this fragment should expose the trigger and expected hardening behaviors used by `run.sh` and `stack-entropy.sh`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/lkdtm/config -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/lkdtm/run.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/lkdtm/run.sh

Purpose: generic runtime wrapper for individual LKDTM crash/protection tests.

Important APIs/types/functions: uses debugfs files `/sys/kernel/debug/provoke-crash/DIRECT` and `/sys/kernel/debug/clear_warn_once`, reads `tests.txt`, captures `dmesg`, and reports kselftest skip code `4`.

Control flow: verifies the LKDTM trigger, attempts `modprobe lkdtm`, derives the test name from the script basename, finds the corresponding `tests.txt` line, verifies kernel support, detects commented-out tests, parses expected output and optional `repeat:N`, snapshots dmesg, writes test names to the trigger using `cat` so the shell survives expected crashes, diffs new dmesg output, and greps for success text or `XFAIL`.

State and persistence: temporarily creates log files and may clear WARN_ONCE state. It reads and writes debugfs trigger state and consumes kernel log state.

Dependencies and integration points: root/debugfs/module availability, `tests.txt`, `dmesg`, `comm`, `grep`, `modprobe`, and LKDTM debugfs ABI.

Risks: tests intentionally trigger kernel warnings/oops-like behavior; success detection depends on dmesg wording. Kernel log wraparound can affect matching.

Test signals: success is expected regex present in new dmesg; `XFAIL` converts to skip; missing trigger/test/config produces skip.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/lkdtm/run.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/lkdtm/stack-entropy.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/lkdtm/stack-entropy.sh

Purpose: estimates kernel stack offset entropy using LKDTM `REPORT_STACK`.

Important APIs/types/functions: writes `REPORT_STACK` repeatedly to `/sys/kernel/debug/provoke-crash/DIRECT`, follows `dmesg`, parses recent `Stack offset` values, computes a rough bit count with `bc`, and applies kselftest skip code `4`.

Control flow: accepts optional sample count, verifies/modprobes LKDTM, starts `dmesg --follow`, triggers the report loop, kills the follower, counts unique offsets from the last sample window, removes the temporary log, and fails if the observed entropy is below five bits.

State and persistence: creates a temporary log and consumes live kernel log output. It does not restore any kernel state.

Dependencies and integration points: debugfs/LKDTM, root access, `dmesg`, `tac`, `grep`, `awk`, `sort`, `uniq`, `bc`.

Risks: kernel log truncation or concurrent LKDTM messages can skew the sample. The heuristic threshold is coarse and environment-sensitive.

Test signals: skip on missing trigger, fail on fewer than five observed entropy bits, pass otherwise.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/lkdtm/stack-entropy.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/locking/Makefile -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/locking/Makefile

Purpose: kselftest Makefile for locking selftests in this subset.

Important APIs/types/functions: declares an empty `all` target to avoid accidentally invoking runtime tests during a plain build, sets `TEST_PROGS := ww_mutex.sh`, and includes `../lib.mk`.

Control flow: build-time only; no binaries are generated.

State and persistence: none.

Dependencies and integration points: delegates runtime behavior to `ww_mutex.sh` and kselftest `lib.mk`.

Risks: if more locking tests are added, they must be explicitly listed or they will not run.

Test signals: kselftest discovers the shell program via `TEST_PROGS`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/locking/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/locking/ww_mutex.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/locking/ww_mutex.sh

Purpose: loads the kernel `test-ww_mutex` module to run in-kernel wait/wound mutex API tests.

Important APIs/types/functions: uses `/sbin/modprobe -q -n test-ww_mutex` for availability probing, `modprobe test-ww_mutex` to execute module init tests, and `modprobe -r` for cleanup.

Control flow: if the module is unavailable, prints skip and exits `4`. If load succeeds, unloads it and reports ok. If load fails, reports failure and exits `1`.

State and persistence: temporarily loads a kernel test module and removes it on success.

Dependencies and integration points: kernel built with `test-ww_mutex` module, root/module-loading permissions, modprobe path.

Risks: module init contains the actual assertions; this shell wrapper cannot distinguish individual subtest failures. Cleanup only happens on successful load.

Test signals: module availability skip, successful load/unload pass, load failure fail.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/locking/ww_mutex.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/lsm/Makefile -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/lsm/Makefile

Purpose: builds LSM syscall kselftests.

Important APIs/types/functions: sets `CFLAGS += -Wall -O2 $(KHDR_INCLUDES)`, includes `common.h` as a local header, builds `lsm_get_self_attr_test`, `lsm_list_modules_test`, and `lsm_set_self_attr_test`, and links each with `common.c`.

Control flow: standard kselftest build using `../lib.mk`; target-specific prerequisites ensure common helper code is compiled into each test.

State and persistence: no runtime state.

Dependencies and integration points: requires installed/generated kernel headers containing `linux/lsm.h` and syscall numbers.

Risks: comments note headers should be installed first; stale or missing headers can break builds or test the wrong ABI shape.

Test signals: generated C programs are discovered through `TEST_GEN_PROGS`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/lsm/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/lsm/common.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/lsm/common.c

Purpose: shared helpers for LSM syscall tests.

Important APIs/types/functions: `read_proc_attr()` reads `/proc/self/attr/<attr>` into a caller buffer and strips newline. `read_sysfs_lsms()` reads `/sys/kernel/security/lsm`. `attr_lsm_count()` counts active label-producing LSMs among SELinux, Smack, and AppArmor.

Control flow: helper functions allocate path/name buffers, open/read/probe procfs or securityfs, validate buffer termination, and return `0` or `-1`.

State and persistence: read-only inspection of process attributes and securityfs state. `attr_lsm_count()` allocates a page-sized buffer and, on read failure, returns zero.

Dependencies and integration points: `/proc/self/attr`, `/sys/kernel/security/lsm`, active LSM configuration, `linux/lsm.h` constants used by callers.

Risks: `attr_lsm_count()` leaks `names` on successful `read_sysfs_lsms()` path in this snapshot because it does not free before return. It uses substring matching, so unexpected names containing known strings could overcount.

Test signals: callers use these helpers to decide expected syscall counts and compare syscall results against legacy procfs/sysfs interfaces.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/lsm/common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/lsm/common.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/lsm/common.h

Purpose: compatibility header for LSM syscall tests.

Important APIs/types/functions: defines inline wrappers for `lsm_get_self_attr`, `lsm_set_self_attr`, and `lsm_list_modules` when libc/kernel headers do not provide symbols. Declares common helper functions.

Control flow: no runtime control flow except direct `syscall(__NR_...)` wrappers.

State and persistence: none.

Dependencies and integration points: relies on syscall numbers and `struct lsm_ctx` from installed kernel headers.

Risks: build will fail if headers lack syscall numbers or `linux/lsm.h` support. Inline wrappers return raw syscall results and set `errno`.

Test signals: gives all LSM tests a uniform syscall invocation layer.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/lsm/common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/lsm/config -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/lsm/config

Purpose: minimal kernel config fragment for LSM tests.

Important APIs/types/functions: requests `CONFIG_SYSFS`, `CONFIG_SECURITY`, and `CONFIG_SECURITYFS`.

Control flow: none.

State and persistence: build/runtime environment declaration only.

Dependencies and integration points: supports `/sys/kernel/security/lsm`, securityfs, and LSM infrastructure needed by the syscall tests.

Risks: individual LSMs are not forced on by this fragment, so tests must handle no label-producing LSMs.

Test signals: with these options available, LSM syscall tests should at least execute or report ABI errors rather than missing filesystems.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/lsm/config -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/lsm/lsm_get_self_attr_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/lsm/lsm_get_self_attr_test.c

Purpose: validates `lsm_get_self_attr()` ABI behavior for current and other process security attributes.

Important APIs/types/functions: uses `struct lsm_ctx`, `LSM_ATTR_*`, `LSM_FLAG_SINGLE`, `lsm_get_self_attr()`, `lsm_list_modules()`, helper `next_ctx()`, and procfs comparison via `read_proc_attr()`.

Control flow: negative tests cover NULL size, NULL ctx, undersized buffer, invalid flag combinations, and unsupported attribute bit combinations. The basic test enumerates active LSM IDs, predicts which attributes should be returned for SELinux/Smack/AppArmor, calls `lsm_get_self_attr()` for current/exec/fscreate/keycreate/prev/sockcreate, walks variable-length `lsm_ctx` records using `next_ctx()`, and compares first returned context with matching `/proc/self/attr/*` content where available.

State and persistence: read-only process LSM attribute inspection.

Dependencies and integration points: `linux/lsm.h`, LSM syscalls, `/proc/self/attr`, `/sys/kernel/security/lsm`, and active LSM modules.

Risks: expected counts are hard-coded for known label-capable LSMs, so new LSM behavior may require updates. Tests assume ordering sufficiently matches procfs first context.

Test signals: expected errno includes `EINVAL`, `E2BIG`, and `EOPNOTSUPP`; basic pass requires count and string comparisons to match.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/lsm/lsm_get_self_attr_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/lsm/lsm_list_modules_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/lsm/lsm_list_modules_test.c

Purpose: validates `lsm_list_modules()` syscall argument checks and returned module ordering/names against securityfs.

Important APIs/types/functions: uses `lsm_list_modules()`, `read_sysfs_lsms()`, `LSM_ID_*` constants, and kselftest harness assertions.

Control flow: negative tests verify NULL size (`EFAULT`), NULL ids (`EFAULT`), too-small size (`E2BIG`), and invalid flags (`EINVAL`). The positive test reads `/sys/kernel/security/lsm`, calls the syscall into a page-sized `__u64` array, then maps each returned ID to an expected name and compares it with the comma-separated sysfs list by advancing through the string.

State and persistence: read-only securityfs/syscall inspection.

Dependencies and integration points: active securityfs mount, LSM syscall ABI, current `LSM_ID_*` enum coverage.

Risks: the ID-to-name switch must be updated for new LSM IDs. The string comparison assumes sysfs ordering exactly matches syscall ordering.

Test signals: pass requires matching module count/order/name prefixes and correct errno for invalid invocations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/lsm/lsm_list_modules_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/lsm/lsm_set_self_attr_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/lsm/lsm_set_self_attr_test.c

Purpose: negative ABI tests for `lsm_set_self_attr()`.

Important APIs/types/functions: uses `lsm_set_self_attr()`, `lsm_get_self_attr()` to prepare a context when label-capable LSMs are active, `LSM_ATTR_CURRENT`, `LSM_ATTR_PREV`, and kselftest harness assertions.

Control flow: tests reject NULL context, too-small size, nonzero flags, and overset attribute bits. Where active LSM label contexts exist, the test first fetches a valid current context to make the subsequent set failure target meaningful.

State and persistence: attempts to set self attributes but only tests failing invocations, so no intended process security state mutation.

Dependencies and integration points: LSM syscalls and active LSMs. Shares helper behavior with the get/list tests.

Risks: assertions only check failure, not exact errno, so regressions that still fail with the wrong reason may pass.

Test signals: all listed invalid `lsm_set_self_attr()` calls must return `-1`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/lsm/lsm_set_self_attr_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/media_tests/Makefile -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/media_tests/Makefile

Purpose: builds media controller and video device manual stress tools.

Important APIs/types/functions: adds `-I../ $(KHDR_INCLUDES)`, declares `TEST_GEN_PROGS := media_device_test media_device_open video_device_test`, and includes `../lib.mk`.

Control flow: build-only; the generated programs require explicit device arguments at runtime.

State and persistence: none.

Dependencies and integration points: Linux media and V4L2 uapi headers.

Risks: shell helper scripts in the folder are not listed as `TEST_PROGS` here, so they are auxiliary/manual unless invoked externally.

Test signals: successful compilation of three tools.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/media_tests/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/media_tests/bind_unbind_sample.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/media_tests/bind_unbind_sample.sh

Purpose: commented sample for repeatedly unbinding and binding a USB media driver interface, illustrated for `uvcvideo`.

Important APIs/types/functions: demonstrates writes to `/sys/bus/usb/drivers/<driver>/unbind` and `bind`.

Control flow: no active commands except shebang/comments; the intended loop is commented out for manual editing.

State and persistence: if uncommented, mutates USB driver binding state.

Dependencies and integration points: root access, correct USB device interface name, target driver sysfs path.

Risks: intentionally device-specific and dangerous if copied without adjusting device numbers; can disrupt active hardware.

Test signals: none as shipped; serves as operator guidance for concurrent media open/ioctl stress tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/media_tests/bind_unbind_sample.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/media_tests/media_dev_allocator.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/media_tests/media_dev_allocator.sh

Purpose: manual script to exercise media device allocator behavior while unbinding and rebinding related media/audio USB drivers.

Important APIs/types/functions: uses `/sys/bus/usb/drivers/$1` and `$2`, discovers devices via `ls -d *-*` and `*-*.1`, writes to driver `unbind`/`bind`, and inspects `/dev/media*`.

Control flow: accepts media driver and audio driver names, unbinds media then audio, checks media node presence/deletion, rebinds both, then runs another interleaved unbind/bind sequence.

State and persistence: mutates live USB driver binding and device nodes. Uses sleeps to let device state settle.

Dependencies and integration points: specific USB hardware, driver names, root, sysfs, media device allocator.

Risks: no argument validation, no cleanup trap, and `cd`/glob failures can affect the wrong path or abort unpredictably. It is intended for supervised hardware testing.

Test signals: human-readable `ls -l /dev/media*` observations; no formal pass/fail exit checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/media_tests/media_dev_allocator.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/media_tests/media_device_open.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/media_tests/media_device_open.c

Purpose: opens a specified media controller device once and queries device information.

Important APIs/types/functions: parses `-d /dev/mediaX`, uses `open(O_RDWR)`, `ioctl(MEDIA_IOC_DEVICE_INFO)`, and `struct media_device_info`.

Control flow: validates an argument is present, requires root via `getuid()`, opens the media device, prints ioctl error or model/driver, and exits. The device FD is intentionally left to process teardown.

State and persistence: read-only media device query; no persistent state.

Dependencies and integration points: `/dev/mediaX`, media controller API, root, kselftest skip helper.

Risks: `media_device` is uninitialized if `-d` is omitted but argc is still high enough through unrelated args; normal usage avoids this. Exit status on ioctl failure remains success-like because it only prints.

Test signals: skip if not root; open failure exits negative; device info print is the main signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/media_tests/media_device_open.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/media_tests/media_device_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/media_tests/media_device_test.c

Purpose: long-running media controller ioctl loop intended to be run while hardware is removed, unbound, or rebound.

Important APIs/types/functions: parses `-d`, uses `MEDIA_IOC_DEVICE_INFO`, `struct media_device_info`, random iteration count from `rand()`, and kselftest skip for non-root.

Control flow: requires root, opens the device once, prints operator instructions, then loops `count` times, issuing `MEDIA_IOC_DEVICE_INFO` every ten seconds and printing either errors or model/driver.

State and persistence: holds one media device FD open while external hot-unplug/unbind operations mutate device state.

Dependencies and integration points: hardware media controller, root, manual operator actions, optional KASAN/dmesg monitoring.

Risks: random iteration count may be extremely large; no signal cleanup needed but test duration is unpredictable. It does not fail on ioctl errors, because errors during removal may be expected.

Test signals: absence of kernel UAF/oops during external disruption is the real signal; program output is diagnostic.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/media_tests/media_device_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/media_tests/open_loop_test.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/media_tests/open_loop_test.sh

Purpose: repeatedly invokes `media_device_open` for `/dev/mediaN`.

Important APIs/types/functions: constructs `file=/dev/media$1`, increments a loop counter, captures `./media_device_open -d $file` output, and prints it.

Control flow: infinite loop with no sleep, intended for manual stress during bind/unbind tests.

State and persistence: repeatedly opens and closes media devices through subprocesses.

Dependencies and integration points: built `media_device_open` in current directory, device number argument, root if the C tool enforces it.

Risks: unbounded loop can spam logs/terminal and consume CPU. No exit condition or argument validation.

Test signals: diagnostic loop output; kernel stability under concurrent device churn is the target.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/media_tests/open_loop_test.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/media_tests/video_device_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/media_tests/video_device_test.c

Purpose: V4L2 device stress tool that verifies priority ioctl behavior and loops over capability/tuner ioctls during manual device removal/unbind.

Important APIs/types/functions: uses `VIDIOC_G_PRIORITY`, `VIDIOC_S_PRIORITY`, `VIDIOC_QUERYCAP`, `VIDIOC_G_TUNER`, `struct v4l2_capability`, and `struct v4l2_tuner`.

Control flow: parses `-d /dev/videoX`, opens the device, runs `priority_test()` to change priority and restore the old value, prints pass/fail, then `loop_test()` runs random-count iterations issuing querycap and tuner ioctls every ten seconds.

State and persistence: temporarily changes V4L2 file priority and restores it; holds device FD during external hardware churn.

Dependencies and integration points: V4L2 device node and driver supporting the tested ioctls; intended to be paired with dmesg/KASAN observation.

Risks: no root check but some devices require permissions. Random loop length can be long. `VIDIOC_G_TUNER` may be unsupported for non-tuner devices and is treated diagnostically.

Test signals: priority round-trip pass/fail plus absence of kernel errors while ioctls run during removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/media_tests/video_device_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/membarrier/Makefile -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/membarrier/Makefile

Purpose: builds membarrier syscall tests.

Important APIs/types/functions: sets debug CFLAGS with kernel header includes, links pthreads, and declares generated programs `membarrier_test_single_thread` and `membarrier_test_multi_thread`.

Control flow: standard kselftest `lib.mk` build; both C programs include the shared implementation header.

State and persistence: none.

Dependencies and integration points: membarrier uapi header, syscall availability, pthread library.

Risks: because implementation is in a header, changes there affect both runners.

Test signals: generated binaries are kselftest-discoverable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/membarrier/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/membarrier/membarrier_test_impl.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/membarrier/membarrier_test_impl.h

Purpose: shared membarrier syscall test implementation for single-threaded and multi-threaded runners.

Important APIs/types/functions: `sys_membarrier()` wraps `syscall(__NR_membarrier)`. Test helpers cover query, invalid command/flags, global barrier, private expedited registration/use, sync-core variants when supported, global expedited registration/use, and registration tracking with `MEMBARRIER_CMD_GET_REGISTRATIONS`.

Control flow: `test_membarrier_query()` skips if syscall is disabled or lacks `MEMBARRIER_CMD_GLOBAL`. `test_membarrier_fail()` verifies invalid invocations and unregistered private expedited commands fail with `EINVAL`/`EPERM`. `test_membarrier_success()` performs global, registration, and expedited commands, conditionally including sync-core based on query bits. `test_membarrier_get_registrations()` maintains a process-local `registrations` bitmask and compares syscall output to expected cumulative registrations.

State and persistence: state is per-process membarrier registrations plus the local expected `registrations` variable. No persistent system state.

Dependencies and integration points: kernel membarrier support, syscall numbers, kselftest result APIs.

Risks: the helper named `test_membarrier_private_expedited_sync_core_success()` uses `MEMBARRIER_CMD_PRIVATE_EXPEDITED` as command while its test name says sync core; that may reflect an intentional compatibility check or a coverage bug. Registration expectations are order-dependent.

Test signals: pass lines for each command; skip on disabled/unsupported membarrier; fatal failure on unexpected errno/result.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/membarrier/membarrier_test_impl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/membarrier/membarrier_test_multi_thread.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/membarrier/membarrier_test_multi_thread.c

Purpose: runs membarrier tests while another pthread exists, exercising multi-threaded process semantics.

Important APIs/types/functions: uses pthread mutex/condition variables, `pthread_create`, `pthread_join`, and shared helpers from `membarrier_test_impl.h`.

Control flow: starts a worker thread that signals readiness and waits until `thread_quit`. The main thread waits for readiness, runs failure and success membarrier suites, signals quit, joins the thread, and exits through kselftest.

State and persistence: process-local synchronization flags `thread_ready` and `thread_quit`; membarrier registration state belongs to the process.

Dependencies and integration points: pthreads and membarrier syscall support.

Risks: no error checks on pthread calls in this snapshot. Test plan is fixed at 16, matching expected helper result count for the multi-thread flow.

Test signals: kselftest plan/pass output, skip/fail inherited from shared helpers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/membarrier/membarrier_test_multi_thread.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/membarrier/membarrier_test_single_thread.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/membarrier/membarrier_test_single_thread.c

Purpose: runs membarrier syscall tests in a single-threaded process.

Important APIs/types/functions: includes `membarrier_test_impl.h` and calls `test_membarrier_get_registrations()`, `test_membarrier_query()`, `test_membarrier_fail()`, and `test_membarrier_success()`.

Control flow: prints kselftest header, sets plan `18`, checks initial registrations with command `0`, verifies query/support, runs negative and positive suites, checks registrations again, and exits pass.

State and persistence: only process-local membarrier registration state.

Dependencies and integration points: membarrier syscall and kselftest framework.

Risks: test count depends on query-supported optional commands and helper behavior; stale assumptions can desynchronize plan output.

Test signals: expected kselftest pass lines and registration bitmask consistency.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/membarrier/membarrier_test_single_thread.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/memfd/Makefile -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/memfd/Makefile

Purpose: builds memfd core, FUSE race, and hugetlbfs wrapper tests.

Important APIs/types/functions: builds `memfd_test`, scripts `run_fuse_test.sh` and `run_hugetlbfs_test.sh`, generated files `fuse_test` and `fuse_mnt`, and detects FUSE cflags/libs through `pkg-config` with fallback include/library flags.

Control flow: compiles common code into `memfd_test` and `fuse_test`; applies FUSE cflags to `fuse_mnt.o` and FUSE libs to the `fuse_mnt` link.

State and persistence: build metadata only.

Dependencies and integration points: FUSE development headers/libs, memfd uapi headers, kselftest `lib.mk`.

Risks: fallback FUSE flags may not match all distributions. Missing FUSE support affects only FUSE-specific generated tools.

Test signals: generated binaries and scripts are kselftest-visible.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/memfd/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/memfd/common.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/memfd/common.c

Purpose: shared memfd helpers and hugetlbfs mode toggle.

Important APIs/types/functions: global `hugetlbfs_test`, `default_huge_page_size()` parsing `/proc/meminfo`, and `sys_memfd_create()` wrapping `syscall(__NR_memfd_create)` while adding `MFD_HUGETLB` when hugetlbfs mode is active.

Control flow: huge page size helper reads lines until `Hugepagesize:` is found, converts kB to bytes, and returns zero on failure. The syscall wrapper mutates flags based on global mode.

State and persistence: process-global `hugetlbfs_test` controls memfd creation behavior.

Dependencies and integration points: `/proc/meminfo`, memfd uapi, syscall numbers.

Risks: global mode affects all callers in the process. Parser assumes the meminfo field spelling/spacing used by Linux.

Test signals: callers skip/fail when huge page size cannot be determined or memfd creation fails.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/memfd/common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/memfd/common.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/memfd/common.h

Purpose: declarations for shared memfd helpers.

Important APIs/types/functions: declares `extern int hugetlbfs_test`, `default_huge_page_size()`, and `sys_memfd_create()`.

Control flow: none.

State and persistence: exposes the process-global hugetlbfs mode.

Dependencies and integration points: included by `memfd_test.c` and `fuse_test.c`.

Risks: direct global access can make mode changes implicit across helper users.

Test signals: none directly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/memfd/common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/memfd/config -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/memfd/config

Purpose: kernel config fragment for memfd FUSE tests.

Important APIs/types/functions: requests `CONFIG_FUSE_FS=m`.

Control flow: none.

State and persistence: build configuration only.

Dependencies and integration points: supports the FUSE mount helper used by memfd GUP race tests.

Risks: module form requires load permission at runtime.

Test signals: FUSE tests can run when the module and userspace FUSE tooling are available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/memfd/config -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/memfd/fuse_mnt.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/memfd/fuse_mnt.c

Purpose: tiny read-only FUSE filesystem exposing `/memfd` with slow direct I/O to force GUP-pinned user pages during reads.

Important APIs/types/functions: implements FUSE callbacks `getattr`, `readdir`, `open`, and `read` through `struct fuse_operations`. Uses `fi->direct_io = 1` and sleeps one second in `read`.

Control flow: only `/` and `/memfd` exist. `/memfd` must be opened read-only. Reads copy from static content after a delay and honor offsets.

State and persistence: no persistent backing store; all data is static in process memory. Mount state exists while the FUSE process runs.

Dependencies and integration points: libfuse, FUSE kernel support, `run_fuse_test.sh`, and `fuse_test.c`.

Risks: FUSE API version 26 is old but intentional for compatibility. Slow reads are by design and can make tests time-sensitive.

Test signals: successful mount makes `./mnt/memfd` available for the GUP/sealing race test.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/memfd/fuse_mnt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/memfd/fuse_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/memfd/fuse_test.c

Purpose: tests memfd sealing interactions with get_user_pages by racing FUSE direct-IO reads into a mapped memfd against `F_ADD_SEALS`.

Important APIs/types/functions: uses `sys_memfd_create`, `ftruncate`, `mmap`, `read`, `clone(CLONE_FILES|CLONE_FS|CLONE_VM)`, `F_GET_SEALS`, `F_ADD_SEALS`, `F_SEAL_WRITE`, and optional `hugetlbfs` mode.

Control flow: opens the slow FUSE file, creates and maps a sealable memfd, spawns a sealing thread that waits 200ms, unmaps the shared mapping, tries to add `F_SEAL_WRITE` while the parent read should have pages pinned, then retries after the read completes if needed. Parent reads from the FUSE file into the mapped memfd, checks whether sealing happened before/after data transfer, joins the sealing thread, and verifies final seal state and content behavior.

State and persistence: process-global `global_mfd` and `global_p` share state with the clone child. No persistent files except FUSE mount inputs.

Dependencies and integration points: requires `fuse_mnt` mounted path, memfd sealing, GUP behavior, and optionally free huge pages for hugetlbfs mode.

Risks: timing depends on FUSE delay and scheduler. Test intentionally tolerates future kernels that avoid EBUSY by replacing pages.

Test signals: aborts on unexpected syscall/seal/content outcomes; prints `fuse: DONE` on success.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/memfd/fuse_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/memfd/memfd_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/memfd/memfd_test.c

Purpose: comprehensive memfd syscall/sealing/noexec/sysctl/sharing selftest, with optional hugetlbfs mode.

Important APIs/types/functions: wraps memfd creation, seal get/add, read/write/mmap/ftruncate/fallocate/chmod checks, `/proc/self/fd` reopening, `/proc/sys/vm/memfd_noexec`, `clone()` with `CLONE_NEWPID` and shared file-table flags, SysV semaphores for nested PID namespace synchronization, and constants `MFD_EXEC`, `MFD_NOEXEC_SEAL`, `F_SEAL_EXEC`, `F_SEAL_FUTURE_WRITE`, and `F_WX_SEALS`.

Control flow: helper assertions abort on unexpected behavior. `test_create()` validates name/flag constraints. Basic and seal tests verify `F_SEAL_SEAL`, write, future-write, shrink, grow, resize, and read-only mapping behavior. Exec/noexec tests validate file mode and chmod restrictions. Sysctl tests run inside PID namespaces to verify `memfd_noexec` values 0/1/2, inheritance, and child-lowering/no-raising rules. Sharing tests verify seals are shared through dup, mmap constraints, separate `/proc/self/fd` opens, forked children, and repeated under a shared file table.

State and persistence: mutates `/proc/sys/vm/memfd_noexec` inside PID namespaces, creates memfds, maps memory, and uses process/global state only. In hugetlbfs mode, memfd size and name prefix change and write paths skip unsupported operations.

Dependencies and integration points: memfd syscall, sealing support, PID namespaces for sysctl tests, `/proc`, hugetlb pages when requested, and kselftest wrappers.

Risks: abort-based style gives coarse failure localization. Root or namespace permissions may be needed for sysctl/PID namespace behavior. Some checks depend on current memfd noexec policy semantics.

Test signals: prints section banners and finishes with `memfd: DONE`; any failed assertion aborts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/memfd/memfd_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/memfd/run_fuse_test.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/memfd/run_fuse_test.sh

Purpose: mounts the test FUSE filesystem and runs `fuse_test`.

Important APIs/types/functions: uses `fusermount -u`, `mkdir`, `rmdir`, `./fuse_mnt`, and `./fuse_test ./mnt/memfd`.

Control flow: removes a pre-existing `./mnt` mount/directory, enables `set -e`, creates `mnt`, starts `fuse_mnt`, runs `fuse_test` with forwarded args, unmounts, and removes the directory.

State and persistence: creates and removes a local mountpoint; may leave it behind if commands fail after `set -e` and before cleanup.

Dependencies and integration points: built FUSE helper/test, fusermount, FUSE permissions.

Risks: no trap after `set -e`, so failure can leave mounted state. Assumes `fuse_mnt` backgrounds or daemonizes as FUSE normally does.

Test signals: inherits `fuse_test` exit status unless cleanup fails.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/memfd/run_fuse_test.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/memfd/run_hugetlbfs_test.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/memfd/run_hugetlbfs_test.sh

Purpose: prepares enough huge pages and runs memfd tests in hugetlbfs mode.

Important APIs/types/functions: reads `HugePages_Free` from `/proc/meminfo`, adjusts `/proc/sys/vm/nr_hugepages`, drops caches, runs `./memfd_test hugetlbfs` and `./run_fuse_test.sh hugetlbfs`, and restores original huge page count if changed.

Control flow: requires eight free huge pages, attempts to allocate more if root, skips if insufficient, runs both tests, then restores count.

State and persistence: mutates global huge page pool and drops caches. Restoration is at the end, without a shell trap.

Dependencies and integration points: root for allocation, hugetlbfs-capable kernel, memfd/FUSE tests.

Risks: on early failure, huge page count may not be restored. Error message references `$needpgs`, which is undefined in this snapshot.

Test signals: skip on insufficient huge pages/non-root allocation need; success is inherited from child tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/memfd/run_hugetlbfs_test.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/memory-hotplug/Makefile -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/memory-hotplug/Makefile

Purpose: kselftest Makefile for memory hotplug shell testing.

Important APIs/types/functions: empty `all`, includes `../lib.mk`, declares `TEST_PROGS := mem-on-off-test.sh`, and provides `run_full_test` wrapper running `mem-on-off-test.sh -r 10`.

Control flow: runtime is delegated to the shell script; `run_full_test` prints pass/fail based on script status.

State and persistence: none at build level.

Dependencies and integration points: kselftest `lib.mk` and the hotplug script.

Risks: `run_full_test` converts result to printed text rather than kselftest TAP.

Test signals: script registered as a kselftest program.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/memory-hotplug/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/memory-hotplug/config -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/memory-hotplug/config

Purpose: kernel config fragment for memory hotplug tests.

Important APIs/types/functions: requests memory hotplug, hotremove, notifier error injection, and the memory notifier error injection module.

Control flow: none.

State and persistence: build configuration only.

Dependencies and integration points: enables sysfs memory block state changes and debugfs notifier injection used by the script.

Risks: test coverage still requires actual removable memory blocks.

Test signals: configured kernels should expose memory block `state`/`removable` and notifier error injection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/memory-hotplug/config -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/memory-hotplug/mem-on-off-test.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/memory-hotplug/mem-on-off-test.sh

Purpose: exercises memory block online/offline transitions and notifier error-injection failure paths.

Important APIs/types/functions: discovers sysfs mount, scans `$SYSFS/devices/system/memory/memory*`, reads `removable` and `state`, writes `online`/`offline`, loads `memory-notifier-error-inject`, and writes debugfs action error values for `MEM_GOING_ONLINE` and `MEM_GOING_OFFLINE`.

Control flow: parses `-e`, `-p`, and `-r`; requires root, sysfs, hotpluggable memory, and removable blocks. It onlines all offline memory, attempts to offline a target percentage, onlines all again, loads error-injection module, randomly offlines blocks, verifies online failures under injected error, restores, verifies offline failures under injected error, removes the module, restores all memory online, and exits accumulated status.

State and persistence: mutates real memory block state and module/debugfs settings. It attempts restoration via `online_all_offline_memory` and clearing injected errors.

Dependencies and integration points: root, memory hotplug hardware/config, sysfs, debugfs, `memory-notifier-error-inject`, `bc`.

Risks: operating on live memory blocks is disruptive and can fail due to busy blocks. No trap means interruption can leave memory offline or module loaded.

Test signals: skip for missing prerequisites; pass/fail through `retval` and printed transition diagnostics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/memory-hotplug/mem-on-off-test.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mincore/Makefile -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/mincore/Makefile

Purpose: builds the mincore kselftest.

Important APIs/types/functions: sets `CFLAGS += -Wall`, declares `TEST_GEN_PROGS := mincore_selftest`, and includes `../lib.mk`.

Control flow: build-only.

State and persistence: none.

Dependencies and integration points: libc/kernel support for `mincore`, `mmap`, and kselftest harness.

Risks: minimal Makefile assumes default lib.mk rules suffice.

Test signals: generated `mincore_selftest` binary.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mincore/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mincore/mincore_selftest.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/mincore/mincore_selftest.c

Purpose: validates `mincore()` interface errors and residency reporting for anonymous, huge, file-backed, and tmpfs-backed mappings.

Important APIs/types/functions: uses `mincore`, `mmap`, `mlock`, `munlock`, `madvise(MADV_DONTNEED)`, `MAP_HUGETLB`, `O_TMPFILE`, `fallocate`, kselftest harness macros, and skip handling.

Control flow: `basic_interface` checks zero-length success and documented errors for unmapped address, unaligned address, too-large length, and bad vec. Anonymous test verifies nonresident before touch, resident after touch/lock, and nonresident after unlock plus `MADV_DONTNEED`. Huge-page test skips if huge pages/config unavailable, then repeats touch/residency logic. File-backed test creates an unnamed file in current directory, fallocates 4MB, maps it, expects no initial residency, touches the middle, and validates the touched page plus readahead window. Tmpfs test repeats simpler file residency checks in `/dev/shm`.

State and persistence: temporary unnamed files and mappings only.

Dependencies and integration points: filesystem support for `O_TMPFILE`/`fallocate`, `/dev/shm`, huge page availability for optional coverage.

Risks: readahead expectations are intentionally broad but still environment-sensitive. `mincore(addr, -1, ...)` relies on unsigned length conversion semantics.

Test signals: harness pass/fail/skip per test.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mincore/mincore_selftest.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mm/Makefile -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/mm/Makefile

Purpose: central build/run Makefile for the kernel mm selftest suite.

Important APIs/types/functions: includes local config generation, architecture detection, common CFLAGS/LDLIBS, a large `TEST_GEN_FILES` suite, wrapper `TEST_PROGS`, helper `TEST_FILES`, x86 32/64-bit target generation, target-specific libraries, and warning targets for missing liburing or page_frag prerequisites.

Control flow: disables built-in make rules and deletes failed outputs. It generates `local_config.mk`/`.h` through `check_config.sh`, selects architecture-specific tests, adds optional pkey and VA tests, wires common dependencies like `vm_util.c`/`thp_settings.c`, and emits user-facing warnings instead of hard failures for optional support gaps.

State and persistence: creates local config files and many generated binaries under `$(OUTPUT)`.

Dependencies and integration points: kernel build tree, generated headers, optional liburing/libcap/libnuma, architecture toolchains, `Module.symvers`, and kselftest `lib.mk`.

Risks: broad Makefile means local changes can affect many mm tests. Optional feature detection impacts coverage, especially liburing for COW tests and 32-bit builds on x86_64.

Test signals: build products and wrapper scripts define CI-visible mm coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mm/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mm/charge_reserved_hugetlb.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/mm/charge_reserved_hugetlb.sh

Purpose: validates hugetlb cgroup reservation and fault accounting under cgroup v1 or v2.

Important APIs/types/functions: mounts/finds hugetlb cgroup, writes hugetlb `limit/max`, `rsvd.limit/max`, reads `usage/current` and `rsvd.usage/current`, mounts hugetlbfs at `/mnt/huge`, adjusts `/proc/sys/vm/nr_hugepages`, invokes `write_hugetlb_memory.sh`, and uses `killall write_to_hugetlbfs` for cleanup.

Control flow: requires root and `killall`, stores original huge page count, configures cgroup file names for v1/v2, defines cleanup and wait helpers, then iterates over populate/write methods/private/reserve modes. `run_test()` sets huge pages, creates one cgroup, mounts hugetlbfs, runs writer, measures usage deltas, and asserts final usage zero. `run_multiple_cgroup_test()` does the same for two cgroups and checks isolation. In this snapshot, a `continue` after the normal write case makes the later reservation-limit, cgroup-limit, and multi-cgroup cases unreachable inside the loop.

State and persistence: mutates cgroups, hugetlbfs mount, huge page pool, and files under `/mnt/huge`; cleanup restores many but not all paths on interruption.

Dependencies and integration points: root, hugetlb cgroup controller, hugetlbfs, `write_hugetlb_memory.sh`, huge page availability.

Risks: destructive cleanup writes `0` to `nr_hugepages` repeatedly and only restores original count at the end. The unreachable section reduces actual coverage versus script text.

Test signals: explicit `expect_equal` failures exit `1`; skips on root/tool prerequisites; `PASS` text per reachable case.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mm/charge_reserved_hugetlb.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mm/check_config.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/mm/check_config.sh

Purpose: probes optional build dependencies for mm selftests and emits local config files.

Important APIs/types/functions: creates a temporary C file including `<liburing.h>`, compiles it with `$CC $CFLAGS`, writes `local_config.h` and `local_config.mk` with either liburing support or empty `IOURING_EXTRA_LIBS`.

Control flow: compile success produces `#define LOCAL_CONFIG_HAVE_LIBURING 1` and `IOURING_EXTRA_LIBS = -luring`; failure writes a comment/no-library setting. Temporary files are removed at the end.

State and persistence: creates or overwrites `local_config.h` and `local_config.mk` in the mm selftest directory/output context.

Dependencies and integration points: compiler, CFLAGS, liburing headers/libraries, Makefile include flow.

Risks: no `set -e`; cleanup uses `rm ${tmpname}.*`, which may fail noisily if glob expansion differs. Compile-only probing does not link liburing.

Test signals: affects whether COW/iouring-related code is compiled and whether missing liburing warning appears.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mm/check_config.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mm/compaction_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/mm/compaction_test.c

Purpose: tests whether compaction can produce enough huge pages after fragmenting/locking memory, targeting unevictable page compaction behavior.

Important APIs/types/functions: reads `/proc/meminfo` through `popen`, checks `/proc/sys/vm/compact_unevictable_allowed`, writes `/proc/sys/vm/nr_hugepages`, uses `mmap(MAP_LOCKED)`, `setrlimit(RLIMIT_MEMLOCK)`, and kselftest result APIs.

Control flow: requires root and compaction allowed. It resets huge pages to zero while remembering the original value, raises memlock limit, reads free memory/huge page size, maps and locks chunks covering about 80% of free memory while writing unique page content to avoid KSM merging, unmaps them, requests huge pages for about half of adjusted free memory, checks at least roughly one third of memory can be allocated as huge pages, restores original huge page count, and reports one test result.

State and persistence: mutates huge page pool and consumes/locks large memory temporarily.

Dependencies and integration points: root, `/proc/sys/vm/*`, huge page support, sufficient memory.

Risks: memory pressure is intentional and can affect host stability. Linked-list cleanup advances `entry` twice in the loop, which appears to skip nodes and leak some list allocations, though mappings are mostly short-lived process state.

Test signals: skip on unmet prerequisites; pass if compaction index is acceptable; fail on sysctl/meminfo/allocation errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mm/compaction_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mm/config -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/mm/config

Purpose: kernel config fragment for broad mm selftest coverage.

Important APIs/types/functions: requests SysV IPC, userfaultfd and PTE markers, test vmalloc/HMM/GUP modules, THP, soft-dirty, anon VMA names, tracing/profiling/uprobe support, memory failure/hwpoison injection, and forced `/proc/pid/mem` behavior.

Control flow: none.

State and persistence: build configuration only.

Dependencies and integration points: supports many tests built by `mm/Makefile`, including COW, GUP, THP, HMM, vmalloc, and memory failure cases.

Risks: this fragment is not exhaustive for every optional runtime path; external libraries and hardware still affect coverage.

Test signals: configured kernels expose the features required by most mm selftests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mm/config -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mm/cow.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/mm/cow.c

Purpose: extensive Copy-On-Write correctness tests across anonymous memory, THP, hugetlb, zeropage, memfd/tmpfile-backed private mappings, vmsplice, GUP pins, and optional io_uring fixed buffers.

Important APIs/types/functions: uses pagemap helpers, THP helpers, hugetlb size detection, `fork`, `pipe`, `vmsplice`, `mprotect`, `madvise(MADV_PAGEOUT|MADV_COLLAPSE|MADV_DONTFORK|MADV_DOFORK)`, `mremap`, `memfd_create`, `fallocate`, `ioctl` on `/sys/kernel/debug/gup_test`, optional liburing buffer registration/write-fixed, and kselftest logging helpers.

Control flow: test helpers create synchronized parent/child scenarios to detect leaks across COW boundaries. Anonymous tests cover parent writes, mprotect optimization, vmsplice pins in parent/child, optional io_uring long-term pins, and read-only long-term GUP/GUP-fast pins under shared/previously-shared/exclusive page states. Runners execute each case on base pages, swapped pages, PMD/PTE/single-PTE/partial THP forms, and hugetlb sizes. Additional THP collapse tests verify COW after `MADV_COLLAPSE` on fully or partially shared THPs. Non-anonymous tests cover shared zeropage, huge zeropage, memfd, tmpfile, and memfd-hugetlb mappings.

State and persistence: temporarily changes THP settings and restores them at the end, reads pagemap, opens debugfs `gup_test`, creates mappings/files, and may use swap/pageout.

Dependencies and integration points: mm helper files, `gup_test` debugfs for pin tests, optional liburing, THP/hugetlb/swap availability, pagemap access.

Risks: environment-sensitive skips are common. Some hugetlb vmsplice cases are marked expected failure. Correct THP restoration depends on normal process exit.

Test signals: dynamic kselftest plan from detected sizes/features; failures are content mismatches indicating COW isolation or pin reliability bugs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mm/cow.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mm/droppable.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/mm/droppable.c

Purpose: tests `MAP_DROPPABLE` anonymous mappings by forcing memory pressure until pages are dropped.

Important APIs/types/functions: uses `mmap(PROT_READ|PROT_WRITE, MAP_ANONYMOUS|MAP_DROPPABLE)`, `fork`, `malloc` pressure loop, `kill(SIGTERM)`, and kselftest output.

Control flow: maps 128 MiB droppable memory, fills and verifies it, forks a child that continuously allocates/touches pages, parent scans the droppable mapping until it observes a zeroed page, kills the child, and reports pass.

State and persistence: consumes memory aggressively and relies on kernel reclamation of droppable pages. No persistent files.

Dependencies and integration points: kernel support for `MAP_DROPPABLE` and enough memory pressure to reclaim pages.

Risks: child allocation loop is unbounded until parent detects a drop; on unsupported or misbehaving kernels the test may hang or trigger OOM behavior.

Test signals: pass when any previously filled page reads zero; assertions abort on setup failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mm/droppable.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mm/folio_split_race_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/mm/folio_split_race_test.c

Purpose: stress test for race conditions between shmem folio splitting via `MADV_REMOVE` and concurrent pagecache reads via `filemap_get_entry()`.

Important APIs/types/functions: uses `mmap(MAP_SHARED|MAP_ANONYMOUS)`, `madvise(MADV_HUGEPAGE)`, `madvise(MADV_REMOVE)`, `pthread` reader threads, C11 atomics, barriers, THP settings helpers, `check_huge_shmem()`, and kselftest.

Control flow: main verifies THP/root prerequisites, saves THP settings, sets shmem THP to advise mode, and runs 100 iterations. Each iteration maps five PMD-sized shmem huge pages, fills every base page with a marker containing its page index, verifies shmem THP allocation, starts 16 reader threads, then punches non-hugepage-aligned hole ranges every 50 pages. Readers continuously verify all non-punched pages and record corruption. Any corruption breaks the iteration loop and fails the single planned test; otherwise all iterations pass.

State and persistence: temporarily changes THP shmem settings and restores them through `atexit` and signal handlers. Allocates transient shared memory only.

Dependencies and integration points: root, THP support, PMD page size detection, shmem huge pages, pthreads.

Risks: timing/race stress can be CPU-heavy. If interrupted by unhandled signals, THP settings restoration may not run beyond configured handlers.

Test signals: failure prints corrupted page details; pass requires zero reader failures across all iterations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mm/folio_split_race_test.c -->
