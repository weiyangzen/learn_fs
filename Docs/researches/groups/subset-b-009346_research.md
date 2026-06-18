# subset-b-009346 research

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/strace.spec.in -->
## sources/test-tools/strace/strace.spec.in

Purpose: RPM spec template for building, testing, installing, and documenting strace releases across Fedora, RHEL/CentOS, and SUSE-style RPM environments. It carries a large conditional license expression, distro-specific dependencies, build macros, `%check` behavior, file manifest, and upstream changelog.

Important APIs/types/functions: Uses RPM sections and macros (`%prep`, `%build`, `%install`, `%check`, `%files`, `%changelog`, `%configure`, `%make_build`, `%make_install`, `%if`, `%define`, `%global`). Template substitutions include `@PACKAGE_VERSION@`, `@COPYRIGHT_YEAR@`, `@STRACE_MANPAGE_DATE@`, `@SLM_MANPAGE_DATE@`, `@RPM_CHANGELOGTIME@`, and `@PACKAGE_BUGREPORT@`.

Control flow: The spec chooses modern SPDX-rich `License:` metadata for newer Fedora/RHEL family builds, older `LGPL-2.1+ and GPL-2.0+` metadata elsewhere, conditionally adds `Group`, source format, xz support, Bluetooth headers, stacktrace/symbol-demangle dependencies, and SELinux dependencies. `%prep` seeds generated version/date files, `%build` prints environment diagnostics then configures with mpers checking and bundled headers, `%install` installs into `%buildroot` and compresses changelogs, and `%check` runs installed `strace -V` plus the automake test suite except on selected 32-bit cases.

State and persistence: Persists packaging metadata into generated files (`.tarball-version`, `.year`, manpage date files), installs binaries/manpages/docs into the RPM buildroot, and emits test logs for `%check`. It does not maintain runtime state outside RPM build directories.

Dependencies and integration: Integrates autotools outputs, GCC/make, distro RPM macro sets, optional `pkgconfig(bluez)`, elfutils/libdw or binutils, libselinux, kernel headers, and the strace test suite. The `%files` section binds packaging to installed `strace`, `strace-log-merge`, manpages, and documentation.

Risks: The license field is intentionally distro-sensitive and can become stale when bundled kernel headers or generated autotools files change. `%check` depends on kernel behavior, architecture width, and availability of optional test dependencies; failing to skip incompatible 32-bit lanes can cause packaging failures unrelated to source correctness.

Test signals: Useful verification is `rpmbuild` expansion on target distro macros, successful configure/build with `--enable-mpers=check --enable-bundled=yes`, `%check` logs including `tests*/test-suite.log` and `ksysent.gen.log`, and package file-list validation.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/strace.spec.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/Makefile.am -->
## sources/test-tools/strace/tests/Makefile.am

Purpose: Automake input that defines the strace test harness, helper library, generated decoder tests, standalone test binaries, scripts, data files, installable test payloads, and cleanup/prerequisite rules.

Important APIs/types/functions: Defines `AM_CPPFLAGS`, `AM_CFLAGS`, `AM_LDFLAGS`, `libtests_a_SOURCES`, `check_PROGRAMS`, `DECODER_TESTS`, `MISC_TESTS`, `STACKTRACE_TESTS`, `TESTS`, `check_SCRIPTS`, `check_DATA`, `EXTRA_DIST`, `TEST_LOG_COMPILER`, and `AM_TEST_LOG_FLAGS`. Includes `pure_executables.am`, `secontext.am`, `gen_tests.am`, and `../src/scno.am`.

Control flow: Configure-time substitutions set architecture, kernel long size, native architecture, bundled header include paths, and optional SELinux/stacktrace settings. Automake builds `libtests.a`, compiles hundreds of check programs including the files in this group, expands generated tests, runs each `.test` through `run.sh` with architecture environment, and optionally installs tests under `$(libexecdir)/strace/tests$(MPERS_NAME)`.

State and persistence: Build artifacts include `libtests.a`, many test executables, generated `ksysent.h`, per-test `.dir` directories, logs, and optional installed test assets. Cleanup removes generated directories and `ksysent.h`.

Dependencies and integration: Connects test C files to helper sources (`tests.h`, socket, print, pid namespace, secontext, xlat utilities), optional `clock_LIBS`, `mq_LIBS`, `dl_LIBS`, `m_LIBS`, pthread, valgrind rules, bundled Linux UAPI headers, and stacktrace libraries.

Risks: The file is a central registry; missing a wrapper executable or `.test` entry silently reduces coverage. Per-target flags and link libraries must track source requirements, especially BPF clock helpers, pthread attach/thread tests, large-file `_FILE_OFFSET_BITS=64`, and optional stacktrace XFAIL behavior.

Test signals: `make check`, `make check-prerequisites-local`, generated `ksysent.h` correctness, installed-test layout under `ENABLE_INSTALL_TESTS`, and absence of stale test directories after `clean-local-check`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/PTRACE_SEIZE.sh -->
## sources/test-tools/strace/tests/PTRACE_SEIZE.sh

Purpose: Shell prerequisite helper that skips tests when the running kernel/tracer combination cannot use `PTRACE_SEIZE`.

Important APIs/types/functions: Uses `$STRACE -d -enone /`, redirects diagnostics to `$LOG`, searches with `grep -x`, and invokes the harness `skip_` function.

Control flow: Runs strace against `/` while ignoring command failure, then scans the debug log for the exact unsupported `PTRACE_SEIZE doesn't work` diagnostic. A match causes a skip; otherwise the caller continues.

State and persistence: Writes only the harness log file named by `$LOG`; no persistent state.

Dependencies and integration: Requires `init.sh`-style harness variables/functions and is listed as `check_SCRIPTS` in `Makefile.am`. It protects attach/ptrace-heavy tests from unsupported kernels.

Risks: The skip decision depends on a stable diagnostic string and debug output format. Localization or message changes would cause false negatives.

Test signals: Exercise on kernels with and without usable `PTRACE_SEIZE`, verifying that unsupported cases call `skip_` and supported cases leave the test active.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/PTRACE_SEIZE.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/_newselect-P.c -->
## sources/test-tools/strace/tests/_newselect-P.c

Purpose: Thin compile-time variant of the `_newselect` decoder test that enables path/file-descriptor tracing behavior for fd 9.

Important APIs/types/functions: Defines `PATH_TRACING_FD 9` and includes `_newselect.c`.

Control flow: There is no local runtime logic; compilation flows directly into `_newselect.c`, which then includes the generic `xselect.c` test body with the fd-tracing macro visible.

State and persistence: No state of its own.

Dependencies and integration: Built as `_newselect-P` by `Makefile.am`; depends entirely on `_newselect.c` and `xselect.c` respecting `PATH_TRACING_FD`.

Risks: As a wrapper, its correctness is easy to break by renaming macros or changing `xselect.c` expectations without updating this file.

Test signals: The resulting executable should produce the same `_newselect` coverage as `_newselect.c` plus fd/path tracing expectations for descriptor 9.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/_newselect-P.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/_newselect.c -->
## sources/test-tools/strace/tests/_newselect.c

Purpose: Select-family decoder entry point for the Linux `_newselect` syscall.

Important APIs/types/functions: Includes `tests.h`, `scno.h`, guards on `__NR__newselect`, defines `TEST_SYSCALL_NR` and `TEST_SYSCALL_STR`, and includes shared `xselect.c`.

Control flow: If `_newselect` exists, the generic select test body is compiled for that syscall number/name. Otherwise `SKIP_MAIN_UNDEFINED("__NR__newselect")` provides a skip main.

State and persistence: No persistent state; runtime state is provided by `xselect.c` allocations and fd sets.

Dependencies and integration: Integrates the architecture syscall table, shared select decoder tests, and wrapper variants like `_newselect-P.c`.

Risks: Coverage depends on `xselect.c` accurately handling syscall-specific ABI differences. Architectures without `__NR__newselect` intentionally skip.

Test signals: Build should compile either a runnable `_newselect` test or a skip binary; traced output should show `_newselect` argument decoding.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/_newselect.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/accept.c -->
## sources/test-tools/strace/tests/accept.c

Purpose: Tests decoding of `accept`-style socket syscalls, including direct `__NR_accept` and legacy `socketcall` routing.

Important APIs/types/functions: Defines `TEST_SYSCALL_NAME`, `TEST_SYSCALL_STR`, `do_accept`, `TEST_SYSCALL_PREPARE`, `connect_un`, and includes `sockname.c`. Uses Unix-domain sockets, `bind`, `listen`, `connect`, and `test_sockname_syscall`.

Control flow: Selects direct `accept` or socketcall implementation, creates a listening Unix socket, prepares a client connection in `connect_un`, delegates the actual bad/good sockaddr decoding cases to `sockname.c`, then cleans up the test socket.

State and persistence: Creates and unlinks `TEST_SOCKET` and `TEST_SOCKET.connect`; no state remains after cleanup.

Dependencies and integration: Reused by `accept4.c` through `TEST_SYSCALL_NAME`/suffix macros. Depends on `sockname.c` for common accept/getsockname-style assertions.

Risks: Unix socket filesystem cleanup and connection timing can fail in restricted environments. Legacy socketcall coverage depends on architecture availability.

Test signals: Expected output includes decoded `accept` calls, sockaddr/socklen handling, return status, and final clean exit; missing syscalls should produce a skip binary.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/accept.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/accept4.c -->
## sources/test-tools/strace/tests/accept4.c

Purpose: Tests `accept4` decoding by reusing the common accept test body with an extra flags argument.

Important APIs/types/functions: Includes `kernel_fcntl.h`, guards on `HAVE_ACCEPT4`, defines `TEST_SYSCALL_NAME accept4`, `SUFFIX_ARGS , O_CLOEXEC`, and `SUFFIX_STR ", SOCK_CLOEXEC"`, then includes `accept.c`.

Control flow: If `accept4` is available, compilation specializes `accept.c` so calls include `O_CLOEXEC` and expected output includes `SOCK_CLOEXEC`. Otherwise it emits a skip main.

State and persistence: Same Unix socket lifecycle as `accept.c`; no additional state.

Dependencies and integration: Wrapper integrated by `Makefile.am` as its own executable; depends on accept test macro hooks.

Risks: Macro coupling is tight: changes in `accept.c` suffix hooks can break this variant. Availability is configure/kernel dependent.

Test signals: Traced output should show `accept4(..., SOCK_CLOEXEC)` decoding and normal socket cleanup.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/accept4.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/access.c -->
## sources/test-tools/strace/tests/access.c

Purpose: Tests pathname and mode decoding for the `access` syscall, including SELinux context decoration when enabled.

Important APIs/types/functions: Uses `__NR_access`, `create_and_enter_subdir`, `SECONTEXT_PID_MY`, `SECONTEXT_FILE`, `open`, `unlink`, and `leave_and_remove_subdir`.

Control flow: Enters a subdirectory so tracer and tracee cwd differ, creates `access_sample`, calls `access(sample, F_OK)`, removes it, then calls `access(sample, R_OK|W_OK|X_OK)` and prints expected decoded lines.

State and persistence: Temporarily creates `access_subdir/access_sample` and removes both.

Dependencies and integration: Depends on `secontext.h` and common test helpers. Its output interacts with path decoding and SELinux-aware expected formatting.

Risks: File permission semantics and SELinux context availability vary by environment. Cleanup failures can affect later tests in the same directory.

Test signals: Expected output should include `F_OK`, combined `R_OK|W_OK|X_OK`, optional file contexts, and a clean exit.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/access.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/acct.c -->
## sources/test-tools/strace/tests/acct.c

Purpose: Minimal decoder test for the `acct` syscall path argument.

Important APIs/types/functions: Calls `syscall(__NR_acct, sample)`, prints `sprintrc(rc)`.

Control flow: Uses a constant filename `acct_sample`, invokes `acct`, prints the decoded path and result, exits.

State and persistence: Does not create the accounting file; only passes a path string to the kernel.

Dependencies and integration: Depends on `tests.h`, `scno.h`, and generic syscall result formatting.

Risks: `acct` commonly requires privilege and may fail; the test treats failure as expected output, so the risk is syscall-number availability or unexpected errno formatting.

Test signals: Output line should be `acct("acct_sample") = ...` followed by clean exit.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/acct.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/add_key.c -->
## sources/test-tools/strace/tests/add_key.c

Purpose: Exhaustive combinatorial decoder test for `add_key` string, payload, length, and keyring arguments.

Important APIs/types/functions: Defines `print_val_str`, `do_add_key`, uses `tail_memdup`, `ARG_STR`, `STRINGIFY`, `KEY_SPEC_THREAD_KEYRING`, and `syscall(__NR_add_key, ...)`.

Control flow: Builds arrays of type strings, descriptions, payload pointers/lengths, and keyring ids, including NULL, invalid tail pointers, unterminated buffers, escaped strings, long strings, and known keyring constants. Nested loops invoke `do_add_key` for every combination and print the expected decoder representation.

State and persistence: Allocates tail buffers for bogus unterminated data; does not persist keys because most calls are invalid or unprivileged.

Dependencies and integration: Exercises strace string quoting, payload truncation, pointer fallback, keyring xlat decoding, and syscall result formatting.

Risks: Large Cartesian output must stay aligned with test expectations; changing string abbreviation limits or keyring xlat names affects many lines.

Test signals: Expected output covers NULLs, bad pointers, escaped binary strings, truncated payload/description, unknown numeric keyrings, and `KEY_SPEC_THREAD_KEYRING`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/add_key.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/adjtimex.c -->
## sources/test-tools/strace/tests/adjtimex.c

Purpose: Tests decoding of `adjtimex` input/output `timex` structures and return-state names.

Important APIs/types/functions: Uses `k_adjtimex`, `kernel_old_timex_t`, `TAIL_ALLOC_OBJECT_CONST_PTR`, `printflags(adjtimex_status)`, `printxval(adjtimex_state)`, and `zero_extend_signed_to_ull`.

Control flow: Calls `adjtimex(NULL)`, then allocates and zeroes a kernel timex struct, calls `adjtimex(tx)`, skips if the real syscall is unavailable/fails, and prints all decoded fields plus the returned clock state xlat.

State and persistence: Reads kernel clock discipline state into a temporary buffer; no persistent modification because modes are zero.

Dependencies and integration: Depends on `kernel_old_timex.h` and xlat tables for status and state names.

Risks: Kernel struct layout, signedness, and architecture time ABI can differ. The test avoids setting clock state but still depends on permitted read behavior.

Test signals: Output should show `adjtimex(NULL)`, a full `{modes=0,... tai=...}` structure, named status flags or `0`, and named return state.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/adjtimex.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/aio.c -->
## sources/test-tools/strace/tests/aio.c

Purpose: Broad decoder test for legacy Linux AIO syscalls: `io_setup`, `io_submit`, `io_getevents`, `io_cancel`, and `io_destroy`.

Important APIs/types/functions: Uses `<linux/aio_abi.h>`, `struct iocb`, `struct io_event`, `kernel_old_timespec_t`, `tail_alloc`, `tail_memdup`, `IOCB_CMD_PREAD/PREADV/PWRITE/PWRITEV`, optional `HAVE_STRUCT_IOCB_AIO_FLAGS`, and raw syscall numbers.

Control flow: Allocates read buffers and IOCB arrays, opens `/dev/zero` on fd 0, probes invalid `io_setup` arguments, creates an AIO context, submits read and vector-read requests, probes invalid pointers/counts, fetches events with invalid and valid timeouts, cancels invalid/constructed requests, submits synthetic IOCBs to cover opcode, priority, buffer, iovec, string, NULL, and bad-pointer decoding, destroys invalid and valid contexts, and exits.

State and persistence: Temporarily owns a kernel AIO context and fd 0 redirected to `/dev/zero`; destroys the context before exit.

Dependencies and integration: Exercises strace AIO structure decoders, iovec/string printers, old timespec decoding, IOCB flag decoding, and architecture-specific integer formatting macros.

Risks: Legacy AIO syscall availability, `/dev/zero`, and kernel limits can skip/fail. Some outputs depend on optional kernel headers and struct fields.

Test signals: Expected output includes successful context setup, decoded IOCB arrays, event result arrays, timeout structures, invalid pointer fallbacks, ioprio formatting, optional `aio_flags/aio_resfd`, and context destruction.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/aio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/aio_pgetevents.c -->
## sources/test-tools/strace/tests/aio_pgetevents.c

Purpose: Tests `io_pgetevents` decoding, especially timeout and signal-mask argument structures.

Important APIs/types/functions: Defines fallback `struct __aio_sigset`, helper `sys_io_pgetevents`, uses `NSIG_BYTES`, `sigset_t`, `sigemptyset`, `sigaddset`, `kernel_old_timespec_t`, and AIO setup/submit helpers.

Control flow: Opens `/dev/zero`, creates an AIO context, submits two reads, probes bogus context/min/max with bad events, timeout, and sigset pointers, then prints structured sigmask cases for invalid size, all-signals mask, and `[SYS]` mask with large timeout values.

State and persistence: Temporarily owns an AIO context and allocated buffers; the shown source does not explicitly destroy context before process exit, so kernel cleanup occurs on exit.

Dependencies and integration: Exercises strace decoding for six-argument `io_pgetevents`, old timespecs, signal set rendering, and AIO event pointers.

Risks: Availability is kernel/architecture dependent. Signal set size and names must match the harness `nsig.h` assumptions.

Test signals: Output should show NULL vs pointer decoding for `events`, `timeout`, and `sigmask`, `~[]` for full mask, `[SYS]` for SIGSYS, and clean exit or skip when unsupported.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/aio_pgetevents.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/alarm.c -->
## sources/test-tools/strace/tests/alarm.c

Purpose: Simple decoder test for `alarm` argument truncation/printing.

Important APIs/types/functions: Calls `syscall(__NR_alarm, arg)` with a 64-bit-looking value whose low 32 bits are 42, and prints `sprintrc`.

Control flow: Guarded by `__NR_alarm`; if available, invokes alarm once and prints expected `alarm(42)` representation; otherwise emits skip main.

State and persistence: Arms a process alarm but exits immediately, leaving no external state.

Dependencies and integration: Uses `tests.h`, `scno.h`, and generic result formatting.

Risks: The active alarm could theoretically interfere if execution were delayed, but the test exits right away. Architectures without `alarm` skip.

Test signals: Output should show the normalized unsigned argument `42` and clean exit.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/alarm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/answer.c -->
## sources/test-tools/strace/tests/answer.c

Purpose: Test program for injected or traced `exit_group` handling using a recognizable low-byte exit status.

Important APIs/types/functions: Calls raw `__NR_exit_group` and fallback `__NR_exit` with `kernel_ulong_t answer = 0xbadc0ded0000002aULL`.

Control flow: Invokes `exit_group(answer)` first; if that does not terminate, invokes `exit(answer)`, then returns 1 as an error path.

State and persistence: Terminates the process; no persistent state.

Dependencies and integration: Used by fault-injection/exit tests that expect the visible exit code to be 42 while preserving high-bit argument decoding.

Risks: Depends on syscall availability and process termination semantics. Normal execution never reaches clean `+++ exited` printing.

Test signals: Harness should observe exit status 42 or injected/fault behavior around `exit_group`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/answer.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/arch_prctl-Xabbrev.c -->
## sources/test-tools/strace/tests/arch_prctl-Xabbrev.c

Purpose: Compile-time xlat abbreviation variant of the `arch_prctl` decoder test.

Important APIs/types/functions: Defines `XLAT_ABBREV 1` and includes `arch_prctl.c`.

Control flow: No local runtime logic; all behavior comes from `arch_prctl.c` with abbreviated xlat formatting enabled.

State and persistence: No state of its own.

Dependencies and integration: Built as a separate executable to compare `-X abbrev` decoding of arch_prctl commands and xfeature values.

Risks: Wrapper correctness depends on `arch_prctl.c` honoring `XLAT_ABBREV`.

Test signals: Expected output should show known constants in abbreviated symbolic form rather than raw or verbose forms.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/arch_prctl-Xabbrev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/arch_prctl-Xraw.c -->
## sources/test-tools/strace/tests/arch_prctl-Xraw.c

Purpose: Raw numeric xlat variant of the `arch_prctl` decoder test.

Important APIs/types/functions: Defines `XLAT_RAW 1` and includes `arch_prctl.c`.

Control flow: Compiles the common arch_prctl test so expected output uses raw numeric values for xlat-controlled fields.

State and persistence: No wrapper-local state.

Dependencies and integration: Part of the xlat mode matrix in `Makefile.am`.

Risks: A change in `arch_prctl.c` output macros can desynchronize this variant.

Test signals: Output should prefer numeric command/xfeature values where xlat mode applies.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/arch_prctl-Xraw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/arch_prctl-Xverbose.c -->
## sources/test-tools/strace/tests/arch_prctl-Xverbose.c

Purpose: Verbose xlat variant of the `arch_prctl` decoder test.

Important APIs/types/functions: Defines `XLAT_VERBOSE 1` and includes `arch_prctl.c`.

Control flow: Uses common arch_prctl test logic with verbose xlat formatting.

State and persistence: No wrapper-local state.

Dependencies and integration: Builds a distinct test executable for `-X verbose` expectations.

Risks: Depends on shared macros in `arch_prctl.c` and xlat table names.

Test signals: Output should include raw values with symbolic comments for known and unknown arch/xfeature values.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/arch_prctl-Xverbose.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/arch_prctl-success-Xabbrev.c -->
## sources/test-tools/strace/tests/arch_prctl-success-Xabbrev.c

Purpose: Abbreviated xlat variant of the injected-success `arch_prctl` test.

Important APIs/types/functions: Defines `XLAT_ABBREV 1` and includes `arch_prctl-success.c`, which defines `INJECT_RETVAL` before including `arch_prctl.c`.

Control flow: Runtime is inherited from `arch_prctl.c` with injected return handling and abbreviated xlat output.

State and persistence: No state beyond the included test's temporary buffers and real arch_prctl effects.

Dependencies and integration: Exercises successful-return decoder paths that may be hard to trigger on the host kernel.

Risks: Requires the harness invocation to pass injection skip/retval arguments expected by the included code path.

Test signals: Expected lines include ` (INJECTED)` and abbreviated symbolic constants.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/arch_prctl-success-Xabbrev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/arch_prctl-success-Xraw.c -->
## sources/test-tools/strace/tests/arch_prctl-success-Xraw.c

Purpose: Raw xlat variant of the injected-success `arch_prctl` test.

Important APIs/types/functions: Defines `XLAT_RAW 1` and includes `arch_prctl-success.c`.

Control flow: Compiles injected return behavior with raw numeric formatting for xlat-controlled fields.

State and persistence: No wrapper-local state.

Dependencies and integration: Completes the raw xlat lane for arch_prctl success handling.

Risks: Same injection argument and macro-coupling risks as `arch_prctl-success.c`.

Test signals: Expected output combines injected result annotations with numeric command/xfeature rendering.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/arch_prctl-success-Xraw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/arch_prctl-success-Xverbose.c -->
## sources/test-tools/strace/tests/arch_prctl-success-Xverbose.c

Purpose: Verbose xlat variant of the injected-success `arch_prctl` test.

Important APIs/types/functions: Defines `XLAT_VERBOSE 1` and includes `arch_prctl-success.c`.

Control flow: Runs shared arch_prctl cases with injected successful returns and verbose xlat rendering.

State and persistence: No wrapper-local state.

Dependencies and integration: Provides coverage for successful pointer-output formatting in verbose mode.

Risks: Expected output is sensitive to xlat table content and injected return positioning.

Test signals: Output should show verbose xlat values and ` (INJECTED)` result annotations.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/arch_prctl-success-Xverbose.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/arch_prctl-success.c -->
## sources/test-tools/strace/tests/arch_prctl-success.c

Purpose: Wrapper that forces `arch_prctl.c` through injected successful-return paths.

Important APIs/types/functions: Defines `INJECT_RETVAL` and includes `arch_prctl.c`.

Control flow: The included main parses `NUM_SKIP INJECT_RETVAL`, waits until a marker `arch_prctl(-1, -2)` call returns the injected value, then runs the full command/xfeature matrix with success annotations.

State and persistence: Uses included temporary buffers; may perform real `ARCH_SET_*` attempts under injection control.

Dependencies and integration: Used by success and xlat-success executables and by `arch_prctl.sh` through strace injection arguments.

Risks: If injection setup does not lock onto the marker call, the test fails early. Host arch support still controls syscall availability.

Test signals: Expected output contains injected return text and successful pointer dereference formatting for commands normally failing.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/arch_prctl-success.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/arch_prctl.c -->
## sources/test-tools/strace/tests/arch_prctl.c

Purpose: Comprehensive decoder test for x86 `arch_prctl` commands, unknown ranges, pointer-output commands, CPUID toggles, and xfeature permission/query commands.

Important APIs/types/functions: Defines `sys_arch_prctl`, `arch_prctl_marker`, `ARRAY_END`, `INJ_STR`, uses `struct strval32/64`, `TAIL_ALLOC_OBJECT_CONST_PTR`, xlat tables `archvals`, `x86_xfeature_bits`, `x86_xfeatures`, and `XLAT_*` macros.

Control flow: Emits a marker call for filtering/injection, optionally locks onto injected return values, allocates output buffers, iterates unknown command ranges with zero/dummy/pointer args, iterates known default commands, tests `ARCH_GET_GS`/`ARCH_GET_FS` pointer output after setting related values, tests `ARCH_GET_CPUID`, iterates xfeature mask getters with many masks, and tests xfeature permission request commands where positive return masks are decoded.

State and persistence: Temporary buffers hold returned segment/xfeature values. Some calls attempt to set FS/GS/CPUID/xfeature state, but failures are acceptable and process-local.

Dependencies and integration: Shared by raw/abbrev/verbose and injected-success wrappers; `arch_prctl.sh` filters marker output from strace logs. Requires `__NR_arch_prctl` and x86-specific constants.

Risks: Real arch_prctl effects are architecture- and kernel-dependent. Injected mode changes output paths. Xfeature tables must stay synchronized with kernel definitions.

Test signals: Expected output covers unknown commands, known command names, pointer success/failure formatting, xfeature mask flag expansion, request return masks, xlat mode differences, and clean exit or skip.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/arch_prctl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/arch_prctl.sh -->
## sources/test-tools/strace/tests/arch_prctl.sh

Purpose: Harness script for arch_prctl decoder tests that removes the intentionally emitted marker syscall from strace logs before diffing.

Important APIs/types/functions: Sources `init.sh`, uses `check_prog sed`, `run_prog`, `run_strace -earch_prctl`, `sed` range deletion, and `match_diff`.

Control flow: Verifies `sed`, runs the test program once to generate expected output, runs it under strace, strips log content through the marker `arch_prctl(0xffffffff..., 0xfffffffe)` failure line, then diffs filtered output against expectations.

State and persistence: Writes standard harness `$EXP`, `$LOG`, and `$OUT` files.

Dependencies and integration: Tied to `arch_prctl.c` marker call and expected formatting. Listed as a check script in `Makefile.am`.

Risks: The copyright year has an apparent typo (`20212`). More importantly, sed filtering depends on exact marker formatting across xlat modes.

Test signals: Passing diff after marker removal confirms tracer output matches program-generated expectations.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/arch_prctl.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/at_fdcwd-pathmax.c -->
## sources/test-tools/strace/tests/at_fdcwd-pathmax.c

Purpose: Tests `AT_FDCWD` path annotation behavior when current working directory paths approach or exceed `PATH_MAX`.

Important APIs/types/functions: Uses `create_and_enter_subdir`, `get_fd_path`, `get_dir_fd`, `mkdir`, `chdir`, `rmdir`, `syscall(__NR_openat, AT_FDCWD, ...)`, `PATH_MAX`, and `NAME_MAX`.

Control flow: Creates nested long-name directories until the cwd path exceeds `PATH_MAX`, verifies `openat(AT_FDCWD, ...)` omits resolved cwd annotation, backs up one directory and verifies annotation appears, creates an exact-boundary directory where full resolution still fails, verifies annotation omission again, then removes all directories.

State and persistence: Temporarily creates deep `pathmax_subdir` hierarchy and removes it on completion.

Dependencies and integration: Intended for `-y` or similar fd/path decoding options and depends on filesystem path length behavior.

Risks: Filesystems with different `NAME_MAX`/path constraints or cleanup interruptions can affect behavior. The test is sensitive to exact `PATH_MAX` boundary calculations.

Test signals: Expected output alternates between `AT_FDCWD` without path and `AT_FDCWD<resolved-path>` when resolution is possible.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/at_fdcwd-pathmax.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/attach-f-p-cmd.c -->
## sources/test-tools/strace/tests/attach-f-p-cmd.c

Purpose: Companion command process for the `attach-f-p` test, producing predictable traced output with its pid.

Important APIs/types/functions: Uses `skip_if_unavailable("/proc/self/task/")`, `getpid`, `chdir`, and `sprintrc`.

Control flow: Skips if task information is unavailable, attempts to `chdir` into a known non-existent directory, prints the expected pid-prefixed syscall line and exit line.

State and persistence: No persistent state; only attempted cwd change.

Dependencies and integration: Coordinates with `attach-f-p.c` and the corresponding shell test to validate `strace -f -p` output ordering/format.

Risks: Output formatting uses fixed-width pid fields and must match tracer pid-prefix formatting.

Test signals: Expected two pid-prefixed lines for `chdir("attach-f-p.test cmd")` and clean exit.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/attach-f-p-cmd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/attach-f-p.c -->
## sources/test-tools/strace/tests/attach-f-p.c

Purpose: Multithreaded tracee for testing `strace -f -p` attach behavior across threads.

Important APIs/types/functions: Uses pthreads, `pipe`, `read`, `write`, `pthread_create`, `pthread_join`, `syscall(__NR_gettid)`, `fstat`, `sleep`, `chdir`, and fixed pid-prefixed printf formatting.

Control flow: Creates three worker threads blocked on per-thread pipes, writes a newline to signal readiness, waits until the peer has written enough output to stdout, releases each thread one at a time, joins it and prints expected failed `chdir` output with that thread tid, then prints parent `chdir` failure and exit.

State and persistence: Maintains in-process pipes and threads only; no files except stdout coordination.

Dependencies and integration: Linked with pthread by `Makefile.am`; paired with `attach-f-p-cmd.c` and attach test scripts to validate following threads while attached.

Risks: Timing-sensitive coordination uses stdout file size and sleeps to let tracer catch up. Environments where stdout is not seekable/regular can affect `fstat` assumptions.

Test signals: Output should include child thread tids, parent pid, failed `chdir` lines with `ENOENT`, and clean exits in expected order.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/attach-f-p.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/attach-p-cmd-cmd.c -->
## sources/test-tools/strace/tests/attach-p-cmd-cmd.c

Purpose: Command-side tracee for `attach-p-cmd` tests, publishing its pid and waiting for peer coordination before producing output.

Important APIs/types/functions: Defines `write_pidfile`, `wait_for_peer_invocation`, uses `fopen/fprintf/fclose`, `rmdir`, `chdir`, `sprintrc`, and constants from `attach-p-cmd.h`.

Control flow: Writes its pid to `attach-p-cmd.test-pid`, waits until the peer-created lock directory can be removed, attempts the expected `chdir`, prints pid-prefixed syscall and exit lines.

State and persistence: Creates a pid file and removes the lock directory created by the peer; pid file is later removed by the peer.

Dependencies and integration: Coordinates with `attach-p-cmd-p.c` via `lockdir` and `pidfile`. Used by the attach-p command test script.

Risks: Busy waiting on filesystem state can fail if stale lock/pid files exist or if cleanup from prior failures is incomplete.

Test signals: Expected command pid appears in pid file and output contains failed `chdir("attach-p-cmd.test cmd")`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/attach-p-cmd-cmd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/attach-p-cmd-p.c -->
## sources/test-tools/strace/tests/attach-p-cmd-p.c

Purpose: `-p` side companion for `attach-p-cmd`, coordinating with a command process then emitting a delayed trace line.

Important APIs/types/functions: Uses `mkdir/rmdir` lock handoff, pid file reading, `kill(pid, 0)` polling, `unlink`, `nanosleep`, `chdir`, and constants from `attach-p-cmd.h`.

Control flow: Creates lockdir, waits until peer removes it and recreates/removes it for cleanup, reads peer pid, waits for peer termination, sleeps briefly, then attempts `chdir("attach-p-cmd.test -p")` and prints pid-prefixed output.

State and persistence: Creates/removes `attach-p-cmd.test-lock` and removes `attach-p-cmd.test-pid`.

Dependencies and integration: Paired with `attach-p-cmd-cmd.c`; validates strace attaching to an existing process while also running a command.

Risks: Uses busy loops over filesystem and process liveness, so stale files or permission issues can deadlock/fail.

Test signals: Expected output appears only after peer termination and includes failed `chdir("attach-p-cmd.test -p")`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/attach-p-cmd-p.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/attach-p-cmd.h -->
## sources/test-tools/strace/tests/attach-p-cmd.h

Purpose: Shared constants for the `attach-p-cmd` companion programs.

Important APIs/types/functions: Defines `static const char lockdir[] = "attach-p-cmd.test-lock"` and `pidfile[] = "attach-p-cmd.test-pid"`.

Control flow: Header-only; no runtime flow.

State and persistence: Names the lock directory and pid file that companion programs create/remove.

Dependencies and integration: Included by both `attach-p-cmd-cmd.c` and `attach-p-cmd-p.c`.

Risks: Changing names without matching shell harness cleanup would break coordination.

Test signals: Both companion binaries must agree on the same lock and pid file names.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/attach-p-cmd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/block_reset_raise_run.c -->
## sources/test-tools/strace/tests/block_reset_raise_run.c

Purpose: Helper launcher that blocks a signal, resets its handler to default, raises it pending, then execs another command.

Important APIs/types/functions: Uses `sigemptyset`, `sigaddset`, `sigprocmask(SIG_BLOCK)`, `signal(SIG_DFL)`, `raise`, and `execvp`.

Control flow: Parses `signo` and command arguments, blocks the signal, installs default handling, raises the signal while blocked, then execs the requested program.

State and persistence: Signal mask and pending signal are inherited across `execvp`; no filesystem state.

Dependencies and integration: Used by signal/status tests that need a target process with a blocked pending default signal at exec time.

Risks: Invalid signal numbers or exec failures abort with harness error. Signal inheritance semantics are central to expected behavior.

Test signals: The child command should start with the chosen signal blocked and pending, allowing tracer status/term-signal tests to observe it.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/block_reset_raise_run.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/block_reset_run.c -->
## sources/test-tools/strace/tests/block_reset_run.c

Purpose: Helper launcher that blocks a signal, resets its handler to default, and execs another command.

Important APIs/types/functions: Uses `sigemptyset`, `sigaddset`, `sigprocmask(SIG_BLOCK)`, `signal(SIG_DFL)`, and `execvp`.

Control flow: Validates arguments, blocks the requested signal, sets default disposition, then replaces the process image with the target command.

State and persistence: The signal mask is inherited by the executed program; no persistent external state.

Dependencies and integration: Used by signal handling tests that need controlled blocked/default signal state without a pending raised signal.

Risks: Invalid signal names/numbers and exec failure produce fatal harness output. Behavior depends on POSIX signal inheritance across exec.

Test signals: Executed program should run under the requested blocked signal with default disposition.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/block_reset_run.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/bpf-obj_get_info_by_fd-prog-v.c -->
## sources/test-tools/strace/tests/bpf-obj_get_info_by_fd-prog-v.c

Purpose: Verbose program-info variant of the `BPF_OBJ_GET_INFO_BY_FD` BPF test.

Important APIs/types/functions: Defines `CHECK_OBJ_PROG 1`, `VERBOSE 1`, and includes `bpf-obj_get_info_by_fd.c`.

Control flow: Enables creation/loading of a test BPF program and verbose printing of returned `bpf_prog_info` and map info structures.

State and persistence: Inherited test creates BPF maps/programs and holds fds until process exit; lock file serialization prevents memlock pressure across runs.

Dependencies and integration: Linked with clock libs by `Makefile.am`; depends on BPF syscall support and verbose xlat tables.

Risks: Requires sufficient BPF permissions/kernel support; otherwise the common body skips. Verbose output is sensitive to kernel struct growth.

Test signals: Expected output includes map creation, program load, map info, program info, xlated/map id buffer cases, and verbose symbolic fields.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/bpf-obj_get_info_by_fd-prog-v.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/bpf-obj_get_info_by_fd-prog.c -->
## sources/test-tools/strace/tests/bpf-obj_get_info_by_fd-prog.c

Purpose: Program-info variant of the `BPF_OBJ_GET_INFO_BY_FD` test without verbose field expansion.

Important APIs/types/functions: Defines `CHECK_OBJ_PROG 1` and includes `bpf-obj_get_info_by_fd.c`.

Control flow: Enables test BPF program loading and program info queries; non-verbose mode prints info pointers rather than detailed structures.

State and persistence: Creates BPF maps/programs in the included body, serialized by `lock_file_by_dirname`.

Dependencies and integration: Exercises program-info path while keeping expected output less kernel-field-specific.

Risks: BPF program load may fail under unprivileged or locked-down kernels, causing skip.

Test signals: Output should show successful map/program creation attempts and `BPF_OBJ_GET_INFO_BY_FD` program query lines with pointer-style info.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/bpf-obj_get_info_by_fd-prog.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/bpf-obj_get_info_by_fd-v.c -->
## sources/test-tools/strace/tests/bpf-obj_get_info_by_fd-v.c

Purpose: Verbose map-info-only variant of `BPF_OBJ_GET_INFO_BY_FD`.

Important APIs/types/functions: Defines `VERBOSE 1` and includes `bpf-obj_get_info_by_fd.c`.

Control flow: Runs the common body without program loading but expands returned `bpf_map_info` fields symbolically.

State and persistence: Creates temporary BPF maps, serialized to reduce memlock contention.

Dependencies and integration: Uses map/prog xlat tables and BPF syscall support.

Risks: Map creation may fail due to permissions, kernel config, or memlock limits.

Test signals: Expected output includes detailed map info fields such as type, id, key/value sizes, flags, name, namespace ids, BTF fields, hash/map_extra when available.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/bpf-obj_get_info_by_fd-v.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/bpf-obj_get_info_by_fd.c -->
## sources/test-tools/strace/tests/bpf-obj_get_info_by_fd.c

Purpose: Integration-style BPF decoder test for `BPF_OBJ_GET_INFO_BY_FD`, covering real map info and optionally real program info returned by the kernel.

Important APIs/types/functions: Defines `sys_bpf`, `print_map_create`, optional `socket_prog`, `print_prog_load`, `try_bpf`, and `main`. Uses `BPF_MAP_CREATE_struct`, `BPF_PROG_LOAD_struct`, `BPF_OBJ_GET_INFO_BY_FD_struct`, `bpf_map_info_struct`, `bpf_prog_info_struct`, `print_fields.h`, xlat tables, `lock_file_by_dirname`, `tail_alloc`, `clock_gettime`, and `print_time_t_nsec`.

Control flow: Serializes invocations and sleeps for BPF locked-memory reclamation, tries multiple attr sizes to create two array maps, optionally loads a socket filter program referencing those maps, queries map info into exact and oversized buffers, and in program mode queries program info through several caller-provided buffer configurations for xlated instructions and map id arrays. Verbose mode prints decoded returned structs; non-verbose mode prints pointers.

State and persistence: Creates kernel BPF map/program objects and file descriptors for process lifetime. Uses a lock under the test directory to serialize runs and avoid transient memlock failures.

Dependencies and integration: Wrapper files enable program and verbose modes. Requires Linux BPF syscall/header support, anonymous inode fd path decoding, clock APIs for load-time rendering, and xlat tables for map/prog flags/types.

Risks: Highly kernel- and privilege-sensitive; unprivileged BPF restrictions, memlock limits, old kernels, or struct field changes can alter skips/output. Time conversion for program load time is explicitly approximate.

Test signals: Passing output shows map creation attempts, info_len shrink/expansion behavior, fd annotation as `anon_inode:bpf-map`/`bpf-prog`, verbose map/prog fields, map id array truncation cases, and clean exit.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/bpf-obj_get_info_by_fd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/bpf-success-long-y.c -->
## sources/test-tools/strace/tests/bpf-success-long-y.c

Purpose: Injected-success BPF decoder variant with fd path decoding enabled and `/dev/full` expected for fd 0.

Important APIs/types/functions: Defines `INJECT_RETVAL ((long) 0xbadc0de1e55beefULL)`, `FD0_PATH "</dev/full>"`, `YFLAG`, and includes `bpf.c`.

Control flow: Runs the full `bpf.c` table-driven decoder under injected return behavior, while `YFLAG` makes `AT_FDCWD` print with resolved path and `FD0_PATH` changes fd-zero annotations.

State and persistence: Inherits `bpf.c` tail allocations and syscall probes; no real successful BPF side effects because results are injection-oriented.

Dependencies and integration: Used as a decoder/injection test for long return values and `-y` path output.

Risks: Expected output tightly couples injected return text, fd path setup, and architecture word-size formatting.

Test signals: Lines should show injected BPF return value, fd zero rendered as `</dev/full>`, and `AT_FDCWD<...>` where applicable.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/bpf-success-long-y.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/bpf-success-v.c -->
## sources/test-tools/strace/tests/bpf-success-v.c

Purpose: Verbose injected-success variant of the BPF syscall decoder test.

Important APIs/types/functions: Defines `INJECT_RETVAL 42` and includes `bpf-v.c`, which defines `VERBOSE 1` before including `bpf.c`.

Control flow: Runs the full BPF command matrix with verbose nested data printing and injected successful return formatting.

State and persistence: Inherits `bpf.c` allocations; injection prevents reliance on actual kernel success.

Dependencies and integration: Combines verbose BPF attr decoding with success-path return handling.

Risks: Very large expected output; changes to verbose printers or xlat tables can affect many lines.

Test signals: Output should include expanded extra-data blobs, arrays, strings, flags, and ` (INJECTED)` return annotations.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/bpf-success-v.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/bpf-success.c -->
## sources/test-tools/strace/tests/bpf-success.c

Purpose: Injected-success variant of the table-driven BPF syscall decoder test.

Important APIs/types/functions: Defines `INJECT_RETVAL 42` and includes `bpf.c`.

Control flow: The included `sys_bpf` verifies the kernel/tracer-injected return value equals 42, rewrites `errstr` to include `(INJECTED)`, and all command cases print success-style results.

State and persistence: No intended real BPF object creation; uses test memory buffers.

Dependencies and integration: Used by injection tests to exercise code paths that would otherwise fail due to invalid attrs or privileges.

Risks: Requires correct fault/retval injection setup; without it the helper fails on unexpected return values.

Test signals: Every BPF probe should show `= 42 (INJECTED)` style output.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/bpf-success.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/bpf-v.c -->
## sources/test-tools/strace/tests/bpf-v.c

Purpose: Verbose variant of the BPF syscall decoder test.

Important APIs/types/functions: Defines `VERBOSE 1` and includes `bpf.c`.

Control flow: Compiles the common BPF command matrix so dynamic arrays, buffers, and extra attr bytes are printed in expanded form instead of ellipses or raw pointers.

State and persistence: Same as `bpf.c`; wrapper-local state is absent.

Dependencies and integration: Provides the `-v` expected-output lane and is also included by `bpf-success-v.c`.

Risks: Verbose output is most sensitive to formatting and kernel/uapi table drift.

Test signals: Expected output includes quoted hex data, decoded instruction arrays, iter/kprobe arrays, and explicit extra bytes.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/bpf-v.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/bpf.c -->
## sources/test-tools/strace/tests/bpf.c

Purpose: Large table-driven decoder test for the `bpf` syscall across map, program, object, query, link, BTF, batch, token, stream-read, and struct-ops commands.

Important APIs/types/functions: Defines `union bpf_attr_data`, `struct bpf_attr_check`, `struct bpf_check`, `sys_bpf`, `print_bpf_attr`, `test_bpf`, many `BPF_*_checks` arrays, command-specific init/print callbacks, `attach_type_is_ifindex`, `skip_special_attach_types`, `CHK`, and `main`. Uses `bpf_attr.h`, `print_fields.h`, `xmalloc.h`, BPF xlat tables, `tail_alloc`, `tail_memdup`, `fill_memory_ex`, and optional macros `VERBOSE`, `INJECT_RETVAL`, `YFLAG`, and `FD0_PATH`.

Control flow: `main` computes page-boundary buffers and `AT_FDCWD` text, then iterates a `checks[]` table for each BPF command. `test_bpf` probes NULL attrs, zero size, each declared attr size, short reads, exact union-size reads, non-zero trailing data, page-sized reads, and over-page sizes. Command tables cover evolving UAPI fields including map create BTF/token/hash fields, prog load signature/core relo/fd arrays, object pin/get path fd flags, attach/detach/query flags, raw tracepoints, BTF load, task fd query, batch ops, link create variants for cgroup/perf/kprobe/uprobe/netfilter/tcx/netkit/tracing, link update/detach, enable stats, iter create, prog bind map, token create, prog stream read, and prog assoc struct ops.

State and persistence: Uses process memory at page boundaries to test decoder fault handling and allocates tail buffers for strings/arrays. Real BPF syscalls usually fail because attrs are synthetic; injected variants override returns. No persistent kernel objects are expected from the invalid probes.

Dependencies and integration: This is a central regression test for `src/bpf.c` and related printers/xlat tables. Wrapper files enable verbose output, injected success, long return values, fd path decoding, and fd-zero path annotations.

Risks: Very sensitive to Linux BPF UAPI growth: static assertions on map/prog xlat array sizes intentionally force test updates when tables change. Architecture pointer width and endianness affect expected address rendering. The volume of generated output makes small format changes high blast radius.

Test signals: Passing tests show stable decoding for all command tables, unknown command fallback, short/bad pointer handling, extra_data behavior, flag/xlat expansion, wrapper-specific verbose/injected/path modes, and final clean exit.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/bpf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/brk.c -->
## sources/test-tools/strace/tests/brk.c

Purpose: Minimal decoder test for the `brk` syscall with NULL argument.

Important APIs/types/functions: Calls `syscall(__NR_brk, NULL)` and prints the returned program break as hex.

Control flow: Invokes `brk(NULL)`, prints an escaped regex-style expected line `brk\(NULL\) = %#lx`, then exits without the usual `+++ exited` marker.

State and persistence: Reads current program break without changing it.

Dependencies and integration: Uses `tests.h`, `scno.h`, and raw syscall invocation; included in decoder tests.

Risks: Output intentionally resembles a regex expectation and omits the standard exit marker, so harness expectations must account for that.

Test signals: Expected output is a single `brk(NULL)` line with the current break address.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/brk.c -->
