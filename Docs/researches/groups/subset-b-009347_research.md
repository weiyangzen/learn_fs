# subset-b-009347 research

Grouped research report for strace tests under `sources/test-tools/strace/tests`. Every section preserves the source path, is wrapped for reconciliation, and was generated after a full read of the corresponding source file. The final per-file research documents are also written to source-tree-aligned paths under `Docs/researches/sources/test-tools/strace/tests/`.

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/btrfs.c -->
# sources/test-tools/strace/tests/btrfs.c

Purpose: `btrfs.c` exercises strace decoding for Btrfs ioctl command families, including balance, qgroup, scrub, device, subvolume, send/receive, feature, fiemap, and filesystem info structures.

Important APIs/types/functions: local functions include `sprint_xlat_`, `sprint_makedev`, `prfl_btrfs`, `prxval_btrfs`, `print_uint64`, `print_hex`, `print_uuid`, `max_flags_plus_one`, `btrfs_test_trans_ioctls`, ... (48 total), `btrfs_test_fs_info_ioctl`, `rm_test_dir`, `main`; macros include `XLAT_MACROS_ONLY`, `ioc`, `BTRFS_COMPRESS_TYPES`, `BTRFS_INVALID_COMPRESS`; included headers include `tests.h`, `errno.h`, `fcntl.h`, `inttypes.h`, `limits.h`, `stdint.h`, `stdio.h`, ... (43 total), `linux/fiemap.h`, `xlat/fiemap_flags.h`, `xlat/fiemap_extent_flags.h`. Kernel/user ABI names observed in the full file include `btrfs`, `ioctl`, `fcntl`. Prominent constants include `SPDX`, `GPL`, `XLAT_MACROS_ONLY`, `BTRFS_UUID_SIZE`, `UINT64_MAX`, `BYTE_HEX_CHARS`, `BTRFS_IOC_TRANS_START`, `BTRFS_IOC_TRANS_END`, `NULL`, ... (118 total), `AT_REMOVEDIR`, `BTRFS_SUPER_MAGIC`, `EEXIST`; prominent struct names include `xlat`, `btrfs_qgroup_inherit`, `btrfs_ioctl_vol_args_v2`, `btrfs_ioctl_vol_args`, `btrfs_balance_args`, ... (35 total), `xlat_data`, `btrfs_ioctl_fs_info_args`, `statfs`.

Control flow: `main` builds deterministic arguments, invokes the target syscall or helper sequence, prints the expected strace line with `printf`/test helpers, and exits through the strace test harness. The Btrfs test walks through grouped helper functions for each ioctl family, using failing `ioctl(-1, ...)` calls for pure decoder checks and live filesystem setup where a real Btrfs mount is needed.

State and persistence behavior: runtime state is intentionally temporary and test-local. The test may allocate tail buffers and/or create temporary files, directories, descriptors, sockets, eventfds, epoll instances, or mount/file handles, then relies on process exit or explicit cleanup for disposal. Btrfs live coverage can depend on an externally provided Btrfs test root, writable permissions, and filesystem feature support; otherwise decoder-only EBADF paths still validate formatting.

Dependencies: strace test harness headers such as `tests.h`, `scno.h`, `print_utils.h`, `pidns.h`, `secontext.h`, local xlat tables, libc headers, and Linux UAPI headers provide syscall numbers, fallback structs, constants, and output helpers. This file directly includes `tests.h`, `errno.h`, `fcntl.h`, `inttypes.h`, `limits.h`, `stdint.h`, `stdio.h`, ... (43 total), `linux/fiemap.h`, `xlat/fiemap_flags.h`, `xlat/fiemap_extent_flags.h`.

Integration points: the file participates in strace's testsuite as a compiled C test, AWK normalizer, header, or generator input. It integrates with generated xlat tables, syscall-number selection, test-driver `.test` scripts, and expected-output comparison.

Risks: Btrfs ioctls have many variable-size structs and kernel-version-dependent flags, so stale xlat tables, wrong structure sizing, or assuming a writable Btrfs filesystem can make expected output drift.

Test signals: useful validation is the corresponding strace testsuite target under the same basename, comparison of stdout against expected decoder lines, successful compilation under the configured personality/time ABI, and skip behavior when the kernel lacks the syscall or permission. The source was read in full for this report: 2182 lines, 61801 bytes, sha256 prefix `494021e88926`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/btrfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/cachestat-P.c -->
# sources/test-tools/strace/tests/cachestat-P.c

Purpose: `cachestat-P.c` covers the cachestat syscall decoder, its range/stat structures, fd/path qualification variants, and success/error output formatting.

Important APIs/types/functions: local functions include none detected; macros include `TRACE_PATH`; included headers include `cachestat.c`. Kernel/user ABI names observed in the full file include `cachestat`. Prominent constants include `TRACE_PATH`; prominent struct names include none detected.

Control flow: this file is a shared implementation or variant wrapper; compile-time macros select the syscall number, xlat style, fd/path mode, success behavior, or namespace mode before the included/shared test body runs.  This is a wrapper/variant file that reuses shared test implementation through local includes: `cachestat.c`.

State and persistence behavior: runtime state is intentionally temporary and test-local. Most state lives in stack variables, tail-allocated buffers, compile-time macros, and errno/return-code snapshots.

Dependencies: strace test harness headers such as `tests.h`, `scno.h`, `print_utils.h`, `pidns.h`, `secontext.h`, local xlat tables, libc headers, and Linux UAPI headers provide syscall numbers, fallback structs, constants, and output helpers. This file directly includes `cachestat.c`.

Integration points: the file participates in strace's testsuite as a compiled C test, AWK normalizer, header, or generator input. It integrates with generated xlat tables, syscall-number selection, test-driver `.test` scripts, and expected-output comparison. The variant also exercises path/fd decoding options such as `-P`, `-y`, `-yy`, or `--decode-fds`.

Risks: Primary risks are kernel/architecture feature availability, ABI-width differences, host header drift, permissions, namespace-dependent pid/fd/path rendering, and expected-output brittleness when symbolic constants change.

Test signals: useful validation is the corresponding strace testsuite target under the same basename, comparison of stdout against expected decoder lines, successful compilation under the configured personality/time ABI, and skip behavior when the kernel lacks the syscall or permission. The source was read in full for this report: 2 lines, 44 bytes, sha256 prefix `1ddae268e9a7`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/cachestat-P.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/cachestat-fd.c -->
# sources/test-tools/strace/tests/cachestat-fd.c

Purpose: `cachestat-fd.c` covers the cachestat syscall decoder, its range/stat structures, fd/path qualification variants, and success/error output formatting.

Important APIs/types/functions: local functions include none detected; macros include `TRACE_FDS`; included headers include `cachestat.c`. Kernel/user ABI names observed in the full file include `cachestat`. Prominent constants include `TRACE_FDS`; prominent struct names include none detected.

Control flow: this file is a shared implementation or variant wrapper; compile-time macros select the syscall number, xlat style, fd/path mode, success behavior, or namespace mode before the included/shared test body runs.  This is a wrapper/variant file that reuses shared test implementation through local includes: `cachestat.c`.

State and persistence behavior: runtime state is intentionally temporary and test-local. Most state lives in stack variables, tail-allocated buffers, compile-time macros, and errno/return-code snapshots.

Dependencies: strace test harness headers such as `tests.h`, `scno.h`, `print_utils.h`, `pidns.h`, `secontext.h`, local xlat tables, libc headers, and Linux UAPI headers provide syscall numbers, fallback structs, constants, and output helpers. This file directly includes `cachestat.c`.

Integration points: the file participates in strace's testsuite as a compiled C test, AWK normalizer, header, or generator input. It integrates with generated xlat tables, syscall-number selection, test-driver `.test` scripts, and expected-output comparison.

Risks: Primary risks are kernel/architecture feature availability, ABI-width differences, host header drift, permissions, namespace-dependent pid/fd/path rendering, and expected-output brittleness when symbolic constants change.

Test signals: useful validation is the corresponding strace testsuite target under the same basename, comparison of stdout against expected decoder lines, successful compilation under the configured personality/time ABI, and skip behavior when the kernel lacks the syscall or permission. The source was read in full for this report: 2 lines, 43 bytes, sha256 prefix `a414a6c87696`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/cachestat-fd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/cachestat-success.c -->
# sources/test-tools/strace/tests/cachestat-success.c

Purpose: `cachestat-success.c` covers the cachestat syscall decoder, its range/stat structures, fd/path qualification variants, and success/error output formatting.

Important APIs/types/functions: local functions include none detected; macros include `SKIP_IF_PROC_IS_UNAVAILABLE`, `FD9_PATH`, `RETVAL_INJECTED`; included headers include `cachestat.c`. Kernel/user ABI names observed in the full file include `cachestat`. Prominent constants include `SKIP_IF_PROC_IS_UNAVAILABLE`, `FD9_PATH`, `RETVAL_INJECTED`; prominent struct names include none detected.

Control flow: this file is a shared implementation or variant wrapper; compile-time macros select the syscall number, xlat style, fd/path mode, success behavior, or namespace mode before the included/shared test body runs.  This is a wrapper/variant file that reuses shared test implementation through local includes: `cachestat.c`.

State and persistence behavior: runtime state is intentionally temporary and test-local. Most state lives in stack variables, tail-allocated buffers, compile-time macros, and errno/return-code snapshots.

Dependencies: strace test harness headers such as `tests.h`, `scno.h`, `print_utils.h`, `pidns.h`, `secontext.h`, local xlat tables, libc headers, and Linux UAPI headers provide syscall numbers, fallback structs, constants, and output helpers. This file directly includes `cachestat.c`.

Integration points: the file participates in strace's testsuite as a compiled C test, AWK normalizer, header, or generator input. It integrates with generated xlat tables, syscall-number selection, test-driver `.test` scripts, and expected-output comparison.

Risks: Primary risks are kernel/architecture feature availability, ABI-width differences, host header drift, permissions, namespace-dependent pid/fd/path rendering, and expected-output brittleness when symbolic constants change.

Test signals: useful validation is the corresponding strace testsuite target under the same basename, comparison of stdout against expected decoder lines, successful compilation under the configured personality/time ABI, and skip behavior when the kernel lacks the syscall or permission. The source was read in full for this report: 4 lines, 106 bytes, sha256 prefix `f423b789df64`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/cachestat-success.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/cachestat.c -->
# sources/test-tools/strace/tests/cachestat.c

Purpose: `cachestat.c` covers the cachestat syscall decoder, its range/stat structures, fd/path qualification variants, and success/error output formatting.

Important APIs/types/functions: local functions include `k_cachestat`, `main`; macros include `SKIP_IF_PROC_IS_UNAVAILABLE`, `FD9_PATH`, `INJ_STR`, `TRACE_FDS`, `TRACE_PATH`, `TRACE_FILTERED`; included headers include `tests.h`, `scno.h`, `cachestat.h`, `stdio.h`, `unistd.h`. Kernel/user ABI names observed in the full file include `cachestat`. Prominent constants include `SPDX`, `GPL`, `SKIP_IF_PROC_IS_UNAVAILABLE`, `FD9_PATH`, `RETVAL_INJECTED`, `INJ_STR`, `INJECTED`, `TRACE_FDS`, `TRACE_PATH`, `TRACE_FILTERED`, `NULL`, `TAIL_ALLOC_OBJECT_CONST_PTR`; prominent struct names include `cachestat_range`, `cachestat`.

Control flow: `main` builds deterministic arguments, invokes the target syscall or helper sequence, prints the expected strace line with `printf`/test helpers, and exits through the strace test harness.

State and persistence behavior: runtime state is intentionally temporary and test-local. Most state lives in stack variables, tail-allocated buffers, compile-time macros, and errno/return-code snapshots.

Dependencies: strace test harness headers such as `tests.h`, `scno.h`, `print_utils.h`, `pidns.h`, `secontext.h`, local xlat tables, libc headers, and Linux UAPI headers provide syscall numbers, fallback structs, constants, and output helpers. This file directly includes `tests.h`, `scno.h`, `cachestat.h`, `stdio.h`, `unistd.h`.

Integration points: the file participates in strace's testsuite as a compiled C test, AWK normalizer, header, or generator input. It integrates with generated xlat tables, syscall-number selection, test-driver `.test` scripts, and expected-output comparison.

Risks: Primary risks are kernel/architecture feature availability, ABI-width differences, host header drift, permissions, namespace-dependent pid/fd/path rendering, and expected-output brittleness when symbolic constants change.

Test signals: useful validation is the corresponding strace testsuite target under the same basename, comparison of stdout against expected decoder lines, successful compilation under the configured personality/time ABI, and skip behavior when the kernel lacks the syscall or permission. The source was read in full for this report: 108 lines, 2886 bytes, sha256 prefix `56d39a48c47e`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/cachestat.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/caps-abbrev.awk -->
# sources/test-tools/strace/tests/caps-abbrev.awk

Purpose: `caps-abbrev.awk` post-processes strace test output for capability-related expected lines, normalizing symbolic capability sets for the matching `.c` test variant.

Important APIs/types/functions: this is AWK program text rather than C. It uses pattern/action rules, regular-expression matching, field variables, and `print`/substitution operations to reshape test output. Representative regex/action fragments include `bin`.

Control flow: AWK scans strace output line by line, applies the first matching capability-format rules, emits normalized lines, and leaves non-target input unchanged or filtered according to the script body. State is limited to AWK variables for the current record; there is no persistent filesystem state.

Control flow: this file is a shared implementation or variant wrapper; compile-time macros select the syscall number, xlat style, fd/path mode, success behavior, or namespace mode before the included/shared test body runs.

State and persistence behavior: runtime state is intentionally temporary and test-local. Most state lives in stack variables, tail-allocated buffers, compile-time macros, and errno/return-code snapshots.

Dependencies: strace test harness headers such as `tests.h`, `scno.h`, `print_utils.h`, `pidns.h`, `secontext.h`, local xlat tables, libc headers, and Linux UAPI headers provide syscall numbers, fallback structs, constants, and output helpers.

Integration points: the file participates in strace's testsuite as a compiled C test, AWK normalizer, header, or generator input. It integrates with generated xlat tables, syscall-number selection, test-driver `.test` scripts, and expected-output comparison.

Risks: Primary risks are kernel/architecture feature availability, ABI-width differences, host header drift, permissions, namespace-dependent pid/fd/path rendering, and expected-output brittleness when symbolic constants change.

Test signals: useful validation is the corresponding strace testsuite target under the same basename, comparison of stdout against expected decoder lines, successful compilation under the configured personality/time ABI, and skip behavior when the kernel lacks the syscall or permission. The source was read in full for this report: 33 lines, 1073 bytes, sha256 prefix `fc7b2a1009fd`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/caps-abbrev.awk -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/caps-abbrev.c -->
# sources/test-tools/strace/tests/caps-abbrev.c

Purpose: `caps-abbrev.c` tests Linux capability syscall decoding and abbreviation behavior for capget/capset capability header/data structures.

Important APIs/types/functions: local functions include none detected; macros include none detected; included headers include `caps.c`. Kernel/user ABI names observed in the full file include none detected. Prominent constants include none detected; prominent struct names include none detected.

Control flow: this file is a shared implementation or variant wrapper; compile-time macros select the syscall number, xlat style, fd/path mode, success behavior, or namespace mode before the included/shared test body runs.  This is a wrapper/variant file that reuses shared test implementation through local includes: `caps.c`.

State and persistence behavior: runtime state is intentionally temporary and test-local. Most state lives in stack variables, tail-allocated buffers, compile-time macros, and errno/return-code snapshots.

Dependencies: strace test harness headers such as `tests.h`, `scno.h`, `print_utils.h`, `pidns.h`, `secontext.h`, local xlat tables, libc headers, and Linux UAPI headers provide syscall numbers, fallback structs, constants, and output helpers. This file directly includes `caps.c`.

Integration points: the file participates in strace's testsuite as a compiled C test, AWK normalizer, header, or generator input. It integrates with generated xlat tables, syscall-number selection, test-driver `.test` scripts, and expected-output comparison.

Risks: Primary risks are kernel/architecture feature availability, ABI-width differences, host header drift, permissions, namespace-dependent pid/fd/path rendering, and expected-output brittleness when symbolic constants change.

Test signals: useful validation is the corresponding strace testsuite target under the same basename, comparison of stdout against expected decoder lines, successful compilation under the configured personality/time ABI, and skip behavior when the kernel lacks the syscall or permission. The source was read in full for this report: 1 lines, 18 bytes, sha256 prefix `9e0ac1310357`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/caps-abbrev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/caps.awk -->
# sources/test-tools/strace/tests/caps.awk

Purpose: `caps.awk` post-processes strace test output for capability-related expected lines, normalizing symbolic capability sets for the matching `.c` test variant.

Important APIs/types/functions: this is AWK program text rather than C. It uses pattern/action rules, regular-expression matching, field variables, and `print`/substitution operations to reshape test output. Representative regex/action fragments include `bin`, `\\* _LINUX_CAPABILITY_VERSION_\\?\\?\\? \\*`.

Control flow: AWK scans strace output line by line, applies the first matching capability-format rules, emits normalized lines, and leaves non-target input unchanged or filtered according to the script body. State is limited to AWK variables for the current record; there is no persistent filesystem state.

Control flow: this file is a shared implementation or variant wrapper; compile-time macros select the syscall number, xlat style, fd/path mode, success behavior, or namespace mode before the included/shared test body runs.

State and persistence behavior: runtime state is intentionally temporary and test-local. Most state lives in stack variables, tail-allocated buffers, compile-time macros, and errno/return-code snapshots.

Dependencies: strace test harness headers such as `tests.h`, `scno.h`, `print_utils.h`, `pidns.h`, `secontext.h`, local xlat tables, libc headers, and Linux UAPI headers provide syscall numbers, fallback structs, constants, and output helpers.

Integration points: the file participates in strace's testsuite as a compiled C test, AWK normalizer, header, or generator input. It integrates with generated xlat tables, syscall-number selection, test-driver `.test` scripts, and expected-output comparison.

Risks: Primary risks are kernel/architecture feature availability, ABI-width differences, host header drift, permissions, namespace-dependent pid/fd/path rendering, and expected-output brittleness when symbolic constants change.

Test signals: useful validation is the corresponding strace testsuite target under the same basename, comparison of stdout against expected decoder lines, successful compilation under the configured personality/time ABI, and skip behavior when the kernel lacks the syscall or permission. The source was read in full for this report: 37 lines, 1893 bytes, sha256 prefix `7f1083f025f9`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/caps.awk -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/caps.c -->
# sources/test-tools/strace/tests/caps.c

Purpose: `caps.c` tests Linux capability syscall decoding and abbreviation behavior for capget/capset capability header/data structures.

Important APIs/types/functions: local functions include `main`; macros include none detected; included headers include `tests.h`, `errno.h`, `string.h`. Kernel/user ABI names observed in the full file include `capget`, `capset`. Prominent constants include `SPDX`, `GPL`, `TAIL_ALLOC_OBJECT_CONST_ARR`, `NULL`, `ARRAY_SIZE`, `EPERM`; prominent struct names include none detected.

Control flow: `main` builds deterministic arguments, invokes the target syscall or helper sequence, prints the expected strace line with `printf`/test helpers, and exits through the strace test harness.

State and persistence behavior: runtime state is intentionally temporary and test-local. The test may allocate tail buffers and/or create temporary files, directories, descriptors, sockets, eventfds, epoll instances, or mount/file handles, then relies on process exit or explicit cleanup for disposal.

Dependencies: strace test harness headers such as `tests.h`, `scno.h`, `print_utils.h`, `pidns.h`, `secontext.h`, local xlat tables, libc headers, and Linux UAPI headers provide syscall numbers, fallback structs, constants, and output helpers. This file directly includes `tests.h`, `errno.h`, `string.h`.

Integration points: the file participates in strace's testsuite as a compiled C test, AWK normalizer, header, or generator input. It integrates with generated xlat tables, syscall-number selection, test-driver `.test` scripts, and expected-output comparison.

Risks: Primary risks are kernel/architecture feature availability, ABI-width differences, host header drift, permissions, namespace-dependent pid/fd/path rendering, and expected-output brittleness when symbolic constants change.

Test signals: useful validation is the corresponding strace testsuite target under the same basename, comparison of stdout against expected decoder lines, successful compilation under the configured personality/time ABI, and skip behavior when the kernel lacks the syscall or permission. The source was read in full for this report: 68 lines, 1561 bytes, sha256 prefix `03696fa5a1f9`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/caps.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/chdir.c -->
# sources/test-tools/strace/tests/chdir.c

Purpose: `chdir.c` checks directory-changing or root-changing syscall decoding, including path rendering and failure paths.

Important APIs/types/functions: local functions include `main`; macros include none detected; included headers include `tests.h`, `scno.h`, `limits.h`, `stdio.h`, `string.h`, `unistd.h`. Kernel/user ABI names observed in the full file include `chdir`. Prominent constants include `SPDX`, `GPL`, `PATH_MAX`, `NULL`; prominent struct names include none detected.

Control flow: `main` builds deterministic arguments, invokes the target syscall or helper sequence, prints the expected strace line with `printf`/test helpers, and exits through the strace test harness.

State and persistence behavior: runtime state is intentionally temporary and test-local. The test may allocate tail buffers and/or create temporary files, directories, descriptors, sockets, eventfds, epoll instances, or mount/file handles, then relies on process exit or explicit cleanup for disposal.

Dependencies: strace test harness headers such as `tests.h`, `scno.h`, `print_utils.h`, `pidns.h`, `secontext.h`, local xlat tables, libc headers, and Linux UAPI headers provide syscall numbers, fallback structs, constants, and output helpers. This file directly includes `tests.h`, `scno.h`, `limits.h`, `stdio.h`, `string.h`, `unistd.h`.

Integration points: the file participates in strace's testsuite as a compiled C test, AWK normalizer, header, or generator input. It integrates with generated xlat tables, syscall-number selection, test-driver `.test` scripts, and expected-output comparison.

Risks: Primary risks are kernel/architecture feature availability, ABI-width differences, host header drift, permissions, namespace-dependent pid/fd/path rendering, and expected-output brittleness when symbolic constants change.

Test signals: useful validation is the corresponding strace testsuite target under the same basename, comparison of stdout against expected decoder lines, successful compilation under the configured personality/time ABI, and skip behavior when the kernel lacks the syscall or permission. The source was read in full for this report: 37 lines, 742 bytes, sha256 prefix `855866101ec0`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/chdir.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/check_sigblock.c -->
# sources/test-tools/strace/tests/check_sigblock.c

Purpose: `check_sigblock.c` is a strace regression test source for one syscall decoder or helper surface in the test suite.

Important APIs/types/functions: local functions include `main`; macros include none detected; included headers include `tests.h`, `signal.h`, `stdlib.h`. Kernel/user ABI names observed in the full file include none detected. Prominent constants include `SPDX`, `GPL`, `SIG_SETMASK`, `NULL`; prominent struct names include none detected.

Control flow: `main` builds deterministic arguments, invokes the target syscall or helper sequence, prints the expected strace line with `printf`/test helpers, and exits through the strace test harness.  This is a wrapper/variant file that reuses shared test implementation through local includes: `tests.h`.

State and persistence behavior: runtime state is intentionally temporary and test-local. Most state lives in stack variables, tail-allocated buffers, compile-time macros, and errno/return-code snapshots.

Dependencies: strace test harness headers such as `tests.h`, `scno.h`, `print_utils.h`, `pidns.h`, `secontext.h`, local xlat tables, libc headers, and Linux UAPI headers provide syscall numbers, fallback structs, constants, and output helpers. This file directly includes `tests.h`, `signal.h`, `stdlib.h`.

Integration points: the file participates in strace's testsuite as a compiled C test, AWK normalizer, header, or generator input. It integrates with generated xlat tables, syscall-number selection, test-driver `.test` scripts, and expected-output comparison.

Risks: Primary risks are kernel/architecture feature availability, ABI-width differences, host header drift, permissions, namespace-dependent pid/fd/path rendering, and expected-output brittleness when symbolic constants change.

Test signals: useful validation is the corresponding strace testsuite target under the same basename, comparison of stdout against expected decoder lines, successful compilation under the configured personality/time ABI, and skip behavior when the kernel lacks the syscall or permission. The source was read in full for this report: 29 lines, 603 bytes, sha256 prefix `62b7c96bb8f2`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/check_sigblock.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/check_sigign.c -->
# sources/test-tools/strace/tests/check_sigign.c

Purpose: `check_sigign.c` is a strace regression test source for one syscall decoder or helper surface in the test suite.

Important APIs/types/functions: local functions include `main`; macros include none detected; included headers include `tests.h`, `signal.h`, `stdlib.h`. Kernel/user ABI names observed in the full file include none detected. Prominent constants include `SIG_IGN`, `SIG_DFL`, `SPDX`, `GPL`, `NULL`; prominent struct names include `sigaction`.

Control flow: `main` builds deterministic arguments, invokes the target syscall or helper sequence, prints the expected strace line with `printf`/test helpers, and exits through the strace test harness.  This is a wrapper/variant file that reuses shared test implementation through local includes: `tests.h`.

State and persistence behavior: runtime state is intentionally temporary and test-local. Most state lives in stack variables, tail-allocated buffers, compile-time macros, and errno/return-code snapshots.

Dependencies: strace test harness headers such as `tests.h`, `scno.h`, `print_utils.h`, `pidns.h`, `secontext.h`, local xlat tables, libc headers, and Linux UAPI headers provide syscall numbers, fallback structs, constants, and output helpers. This file directly includes `tests.h`, `signal.h`, `stdlib.h`.

Integration points: the file participates in strace's testsuite as a compiled C test, AWK normalizer, header, or generator input. It integrates with generated xlat tables, syscall-number selection, test-driver `.test` scripts, and expected-output comparison.

Risks: Primary risks are kernel/architecture feature availability, ABI-width differences, host header drift, permissions, namespace-dependent pid/fd/path rendering, and expected-output brittleness when symbolic constants change.

Test signals: useful validation is the corresponding strace testsuite target under the same basename, comparison of stdout against expected decoder lines, successful compilation under the configured personality/time ABI, and skip behavior when the kernel lacks the syscall or permission. The source was read in full for this report: 29 lines, 616 bytes, sha256 prefix `0665e3de3dc6`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/check_sigign.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/chmod.c -->
# sources/test-tools/strace/tests/chmod.c

Purpose: `chmod.c` validates mode-changing syscall decoders and their path/fd variants, including octal mode output and flag handling.

Important APIs/types/functions: local functions include `main`; macros include none detected; included headers include `tests.h`, `scno.h`, `fcntl.h`, `stdio.h`, `unistd.h`, `secontext.h`. Kernel/user ABI names observed in the full file include `chmod`, `fcntl`. Prominent constants include `SPDX`, `GPL`, `SECONTEXT_PID_MY`, `O_CREAT`, `O_RDONLY`, `SECONTEXT_FILE`, `SKIP_MAIN_UNDEFINED`; prominent struct names include none detected.

Control flow: `main` builds deterministic arguments, invokes the target syscall or helper sequence, prints the expected strace line with `printf`/test helpers, and exits through the strace test harness. The path/fd variants allocate stable pathnames or descriptors, run failing and successful forms where possible, and print both symbolic flags and raw fallback bits.

State and persistence behavior: runtime state is intentionally temporary and test-local. The test may allocate tail buffers and/or create temporary files, directories, descriptors, sockets, eventfds, epoll instances, or mount/file handles, then relies on process exit or explicit cleanup for disposal.

Dependencies: strace test harness headers such as `tests.h`, `scno.h`, `print_utils.h`, `pidns.h`, `secontext.h`, local xlat tables, libc headers, and Linux UAPI headers provide syscall numbers, fallback structs, constants, and output helpers. This file directly includes `tests.h`, `scno.h`, `fcntl.h`, `stdio.h`, `unistd.h`, `secontext.h`.

Integration points: the file participates in strace's testsuite as a compiled C test, AWK normalizer, header, or generator input. It integrates with generated xlat tables, syscall-number selection, test-driver `.test` scripts, and expected-output comparison.

Risks: Primary risks are kernel/architecture feature availability, ABI-width differences, host header drift, permissions, namespace-dependent pid/fd/path rendering, and expected-output brittleness when symbolic constants change.

Test signals: useful validation is the corresponding strace testsuite target under the same basename, comparison of stdout against expected decoder lines, successful compilation under the configured personality/time ABI, and skip behavior when the kernel lacks the syscall or permission. The source was read in full for this report: 68 lines, 1445 bytes, sha256 prefix `ec50e3c62a7d`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/chmod.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/chown.c -->
# sources/test-tools/strace/tests/chown.c

Purpose: `chown.c` validates ownership-changing syscall decoders and 32-bit compatibility variants, including uid/gid sentinel and path/fd forms.

Important APIs/types/functions: local functions include none detected; macros include `SYSCALL_NR`, `SYSCALL_NAME`, `UGID_TYPE_IS_SHORT`; included headers include `tests.h`, `scno.h`, `xchownx.c`. Kernel/user ABI names observed in the full file include `chown`. Prominent constants include `SPDX`, `GPL`, `SYSCALL_NR`, `SYSCALL_NAME`, `UGID_TYPE_IS_SHORT`, `SKIP_MAIN_UNDEFINED`; prominent struct names include none detected.

Control flow: this file is a shared implementation or variant wrapper; compile-time macros select the syscall number, xlat style, fd/path mode, success behavior, or namespace mode before the included/shared test body runs. The path/fd variants allocate stable pathnames or descriptors, run failing and successful forms where possible, and print both symbolic flags and raw fallback bits.  This is a wrapper/variant file that reuses shared test implementation through local includes: `tests.h`, `scno.h`, `xchownx.c`.

State and persistence behavior: runtime state is intentionally temporary and test-local. Most state lives in stack variables, tail-allocated buffers, compile-time macros, and errno/return-code snapshots.

Dependencies: strace test harness headers such as `tests.h`, `scno.h`, `print_utils.h`, `pidns.h`, `secontext.h`, local xlat tables, libc headers, and Linux UAPI headers provide syscall numbers, fallback structs, constants, and output helpers. This file directly includes `tests.h`, `scno.h`, `xchownx.c`.

Integration points: the file participates in strace's testsuite as a compiled C test, AWK normalizer, header, or generator input. It integrates with generated xlat tables, syscall-number selection, test-driver `.test` scripts, and expected-output comparison.

Risks: Primary risks are kernel/architecture feature availability, ABI-width differences, host header drift, permissions, namespace-dependent pid/fd/path rendering, and expected-output brittleness when symbolic constants change.

Test signals: useful validation is the corresponding strace testsuite target under the same basename, comparison of stdout against expected decoder lines, successful compilation under the configured personality/time ABI, and skip behavior when the kernel lacks the syscall or permission. The source was read in full for this report: 26 lines, 415 bytes, sha256 prefix `01f305440515`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/chown.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/chown32.c -->
# sources/test-tools/strace/tests/chown32.c

Purpose: `chown32.c` validates ownership-changing syscall decoders and 32-bit compatibility variants, including uid/gid sentinel and path/fd forms.

Important APIs/types/functions: local functions include none detected; macros include `SYSCALL_NR`, `SYSCALL_NAME`; included headers include `tests.h`, `scno.h`, `xchownx.c`. Kernel/user ABI names observed in the full file include none detected. Prominent constants include `SPDX`, `GPL`, `SYSCALL_NR`, `SYSCALL_NAME`, `SKIP_MAIN_UNDEFINED`; prominent struct names include none detected.

Control flow: this file is a shared implementation or variant wrapper; compile-time macros select the syscall number, xlat style, fd/path mode, success behavior, or namespace mode before the included/shared test body runs. The path/fd variants allocate stable pathnames or descriptors, run failing and successful forms where possible, and print both symbolic flags and raw fallback bits.  This is a wrapper/variant file that reuses shared test implementation through local includes: `tests.h`, `scno.h`, `xchownx.c`.

State and persistence behavior: runtime state is intentionally temporary and test-local. Most state lives in stack variables, tail-allocated buffers, compile-time macros, and errno/return-code snapshots.

Dependencies: strace test harness headers such as `tests.h`, `scno.h`, `print_utils.h`, `pidns.h`, `secontext.h`, local xlat tables, libc headers, and Linux UAPI headers provide syscall numbers, fallback structs, constants, and output helpers. This file directly includes `tests.h`, `scno.h`, `xchownx.c`.

Integration points: the file participates in strace's testsuite as a compiled C test, AWK normalizer, header, or generator input. It integrates with generated xlat tables, syscall-number selection, test-driver `.test` scripts, and expected-output comparison.

Risks: Primary risks are kernel/architecture feature availability, ABI-width differences, host header drift, permissions, namespace-dependent pid/fd/path rendering, and expected-output brittleness when symbolic constants change.

Test signals: useful validation is the corresponding strace testsuite target under the same basename, comparison of stdout against expected decoder lines, successful compilation under the configured personality/time ABI, and skip behavior when the kernel lacks the syscall or permission. The source was read in full for this report: 21 lines, 328 bytes, sha256 prefix `a2682093042a`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/chown32.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/chroot.c -->
# sources/test-tools/strace/tests/chroot.c

Purpose: `chroot.c` checks directory-changing or root-changing syscall decoding, including path rendering and failure paths.

Important APIs/types/functions: local functions include `main`; macros include none detected; included headers include `tests.h`, `scno.h`, `stdio.h`, `unistd.h`. Kernel/user ABI names observed in the full file include `chroot`. Prominent constants include `SPDX`, `GPL`, `NULL`; prominent struct names include none detected.

Control flow: `main` builds deterministic arguments, invokes the target syscall or helper sequence, prints the expected strace line with `printf`/test helpers, and exits through the strace test harness.  This is a wrapper/variant file that reuses shared test implementation through local includes: `tests.h`, `scno.h`.

State and persistence behavior: runtime state is intentionally temporary and test-local. Most state lives in stack variables, tail-allocated buffers, compile-time macros, and errno/return-code snapshots.

Dependencies: strace test harness headers such as `tests.h`, `scno.h`, `print_utils.h`, `pidns.h`, `secontext.h`, local xlat tables, libc headers, and Linux UAPI headers provide syscall numbers, fallback structs, constants, and output helpers. This file directly includes `tests.h`, `scno.h`, `stdio.h`, `unistd.h`.

Integration points: the file participates in strace's testsuite as a compiled C test, AWK normalizer, header, or generator input. It integrates with generated xlat tables, syscall-number selection, test-driver `.test` scripts, and expected-output comparison.

Risks: Primary risks are kernel/architecture feature availability, ABI-width differences, host header drift, permissions, namespace-dependent pid/fd/path rendering, and expected-output brittleness when symbolic constants change.

Test signals: useful validation is the corresponding strace testsuite target under the same basename, comparison of stdout against expected decoder lines, successful compilation under the configured personality/time ABI, and skip behavior when the kernel lacks the syscall or permission. The source was read in full for this report: 28 lines, 527 bytes, sha256 prefix `93bd6e03de6c`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/chroot.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/clock.in -->
# sources/test-tools/strace/tests/clock.in

Purpose: `clock.in` is a test generator input table. It enumerates clock-related syscall test instances that the strace test build expands into concrete tests.

Important APIs/types/functions: this file is consumed by the strace test generator rather than compiled directly. It has 5 non-comment input rows; representative rows are `clock_adjtime	-a37`, `clock_adjtime64	-a39`, `clock_nanosleep`, `clock_xettime	-a36`, `clock_xettime64	-a39`.

Control flow: the build/test generator reads each row, expands it into a concrete clock test target, and wires that target to the relevant common C implementation. State is static source metadata only; persistence is the generated test list in the build tree.

Control flow: this file is a shared implementation or variant wrapper; compile-time macros select the syscall number, xlat style, fd/path mode, success behavior, or namespace mode before the included/shared test body runs.

State and persistence behavior: runtime state is intentionally temporary and test-local. Most state lives in stack variables, tail-allocated buffers, compile-time macros, and errno/return-code snapshots.

Dependencies: strace test harness headers such as `tests.h`, `scno.h`, `print_utils.h`, `pidns.h`, `secontext.h`, local xlat tables, libc headers, and Linux UAPI headers provide syscall numbers, fallback structs, constants, and output helpers.

Integration points: the file participates in strace's testsuite as a compiled C test, AWK normalizer, header, or generator input. It integrates with generated xlat tables, syscall-number selection, test-driver `.test` scripts, and expected-output comparison.

Risks: Primary risks are kernel/architecture feature availability, ABI-width differences, host header drift, permissions, namespace-dependent pid/fd/path rendering, and expected-output brittleness when symbolic constants change.

Test signals: useful validation is the corresponding strace testsuite target under the same basename, comparison of stdout against expected decoder lines, successful compilation under the configured personality/time ABI, and skip behavior when the kernel lacks the syscall or permission. The source was read in full for this report: 5 lines, 96 bytes, sha256 prefix `f5a86691d0ad`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/clock.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/clock_adjtime-common.c -->
# sources/test-tools/strace/tests/clock_adjtime-common.c

Purpose: `clock_adjtime-common.c` exercises clock and time syscall decoders, especially clock ids, timespec/timex structures, 32-bit versus 64-bit time ABI variants, and restartable sleep output.

Important APIs/types/functions: local functions include `main`; macros include none detected; included headers include `stdio.h`, `time.h`, `unistd.h`. Kernel/user ABI names observed in the full file include `clock_adjtime`. Prominent constants include `SPDX`, `GPL`, `SYSCALL_NR`, `CLOCK_MONOTONIC`, `NULL`, `SYSCALL_NAME`, `CLOCK_REALTIME`; prominent struct names include none detected.

Control flow: `main` builds deterministic arguments, invokes the target syscall or helper sequence, prints the expected strace line with `printf`/test helpers, and exits through the strace test harness.

State and persistence behavior: runtime state is intentionally temporary and test-local. The test may allocate tail buffers and/or create temporary files, directories, descriptors, sockets, eventfds, epoll instances, or mount/file handles, then relies on process exit or explicit cleanup for disposal.

Dependencies: strace test harness headers such as `tests.h`, `scno.h`, `print_utils.h`, `pidns.h`, `secontext.h`, local xlat tables, libc headers, and Linux UAPI headers provide syscall numbers, fallback structs, constants, and output helpers. This file directly includes `stdio.h`, `time.h`, `unistd.h`.

Integration points: the file participates in strace's testsuite as a compiled C test, AWK normalizer, header, or generator input. It integrates with generated xlat tables, syscall-number selection, test-driver `.test` scripts, and expected-output comparison.

Risks: time64/time32 splits and architecture-specific clock ids can alter syscall numbers and structure layout, so tests need conditional compilation and tolerant unsupported-syscall handling.

Test signals: useful validation is the corresponding strace testsuite target under the same basename, comparison of stdout against expected decoder lines, successful compilation under the configured personality/time ABI, and skip behavior when the kernel lacks the syscall or permission. The source was read in full for this report: 29 lines, 625 bytes, sha256 prefix `27ba47a13611`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/clock_adjtime-common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/clock_adjtime.c -->
# sources/test-tools/strace/tests/clock_adjtime.c

Purpose: `clock_adjtime.c` exercises clock and time syscall decoders, especially clock ids, timespec/timex structures, 32-bit versus 64-bit time ABI variants, and restartable sleep output.

Important APIs/types/functions: local functions include none detected; macros include `SYSCALL_NR`, `SYSCALL_NAME`; included headers include `tests.h`, `scno.h`, `clock_adjtime-common.c`. Kernel/user ABI names observed in the full file include `clock_adjtime`. Prominent constants include `SPDX`, `GPL`, `SYSCALL_NR`, `SYSCALL_NAME`, `SKIP_MAIN_UNDEFINED`; prominent struct names include none detected.

Control flow: this file is a shared implementation or variant wrapper; compile-time macros select the syscall number, xlat style, fd/path mode, success behavior, or namespace mode before the included/shared test body runs.  This is a wrapper/variant file that reuses shared test implementation through local includes: `tests.h`, `scno.h`, `clock_adjtime-common.c`.

State and persistence behavior: runtime state is intentionally temporary and test-local. Most state lives in stack variables, tail-allocated buffers, compile-time macros, and errno/return-code snapshots.

Dependencies: strace test harness headers such as `tests.h`, `scno.h`, `print_utils.h`, `pidns.h`, `secontext.h`, local xlat tables, libc headers, and Linux UAPI headers provide syscall numbers, fallback structs, constants, and output helpers. This file directly includes `tests.h`, `scno.h`, `clock_adjtime-common.c`.

Integration points: the file participates in strace's testsuite as a compiled C test, AWK normalizer, header, or generator input. It integrates with generated xlat tables, syscall-number selection, test-driver `.test` scripts, and expected-output comparison.

Risks: time64/time32 splits and architecture-specific clock ids can alter syscall numbers and structure layout, so tests need conditional compilation and tolerant unsupported-syscall handling.

Test signals: useful validation is the corresponding strace testsuite target under the same basename, comparison of stdout against expected decoder lines, successful compilation under the configured personality/time ABI, and skip behavior when the kernel lacks the syscall or permission. The source was read in full for this report: 24 lines, 408 bytes, sha256 prefix `2b0217062bad`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/clock_adjtime.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/clock_adjtime64.c -->
# sources/test-tools/strace/tests/clock_adjtime64.c

Purpose: `clock_adjtime64.c` exercises clock and time syscall decoders, especially clock ids, timespec/timex structures, 32-bit versus 64-bit time ABI variants, and restartable sleep output.

Important APIs/types/functions: local functions include none detected; macros include `SYSCALL_NR`, `SYSCALL_NAME`; included headers include `tests.h`, `scno.h`, `clock_adjtime-common.c`. Kernel/user ABI names observed in the full file include `clock_adjtime`. Prominent constants include `SPDX`, `GPL`, `SYSCALL_NR`, `SYSCALL_NAME`, `SKIP_MAIN_UNDEFINED`; prominent struct names include none detected.

Control flow: this file is a shared implementation or variant wrapper; compile-time macros select the syscall number, xlat style, fd/path mode, success behavior, or namespace mode before the included/shared test body runs.  This is a wrapper/variant file that reuses shared test implementation through local includes: `tests.h`, `scno.h`, `clock_adjtime-common.c`.

State and persistence behavior: runtime state is intentionally temporary and test-local. Most state lives in stack variables, tail-allocated buffers, compile-time macros, and errno/return-code snapshots.

Dependencies: strace test harness headers such as `tests.h`, `scno.h`, `print_utils.h`, `pidns.h`, `secontext.h`, local xlat tables, libc headers, and Linux UAPI headers provide syscall numbers, fallback structs, constants, and output helpers. This file directly includes `tests.h`, `scno.h`, `clock_adjtime-common.c`.

Integration points: the file participates in strace's testsuite as a compiled C test, AWK normalizer, header, or generator input. It integrates with generated xlat tables, syscall-number selection, test-driver `.test` scripts, and expected-output comparison.

Risks: time64/time32 splits and architecture-specific clock ids can alter syscall numbers and structure layout, so tests need conditional compilation and tolerant unsupported-syscall handling.

Test signals: useful validation is the corresponding strace testsuite target under the same basename, comparison of stdout against expected decoder lines, successful compilation under the configured personality/time ABI, and skip behavior when the kernel lacks the syscall or permission. The source was read in full for this report: 24 lines, 418 bytes, sha256 prefix `5bd5f0eb5767`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/clock_adjtime64.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/clock_nanosleep.c -->
# sources/test-tools/strace/tests/clock_nanosleep.c

Purpose: `clock_nanosleep.c` exercises clock and time syscall decoders, especially clock ids, timespec/timex structures, 32-bit versus 64-bit time ABI variants, and restartable sleep output.

Important APIs/types/functions: local functions include `handler`, `main`; macros include none detected; included headers include `tests.h`, `scno.h`, `assert.h`, `stdio.h`, `stdint.h`, `signal.h`, `time.h`, `unistd.h`, `sys/time.h`. Kernel/user ABI names observed in the full file include `clock_nanosleep`, `clock_gettime`. Prominent constants include `SPDX`, `GPL`, `CLOCK_REALTIME`, `NULL`, `RVAL_EFAULT`, `CLOCK_MONOTONIC`, `RVAL_EINVAL`, `SIGALRM`, `SIG_SETMASK`, ... (15 total), `TIMER_ABSTIME`, `ERESTARTNOHAND`, `SKIP_MAIN_UNDEFINED`; prominent struct names include `sigaction`, `itimerval`.

Control flow: `main` builds deterministic arguments, invokes the target syscall or helper sequence, prints the expected strace line with `printf`/test helpers, and exits through the strace test harness.

State and persistence behavior: runtime state is intentionally temporary and test-local. Most state lives in stack variables, tail-allocated buffers, compile-time macros, and errno/return-code snapshots.

Dependencies: strace test harness headers such as `tests.h`, `scno.h`, `print_utils.h`, `pidns.h`, `secontext.h`, local xlat tables, libc headers, and Linux UAPI headers provide syscall numbers, fallback structs, constants, and output helpers. This file directly includes `tests.h`, `scno.h`, `assert.h`, `stdio.h`, `stdint.h`, `signal.h`, `time.h`, `unistd.h`, `sys/time.h`.

Integration points: the file participates in strace's testsuite as a compiled C test, AWK normalizer, header, or generator input. It integrates with generated xlat tables, syscall-number selection, test-driver `.test` scripts, and expected-output comparison.

Risks: time64/time32 splits and architecture-specific clock ids can alter syscall numbers and structure layout, so tests need conditional compilation and tolerant unsupported-syscall handling.

Test signals: useful validation is the corresponding strace testsuite target under the same basename, comparison of stdout against expected decoder lines, successful compilation under the configured personality/time ABI, and skip behavior when the kernel lacks the syscall or permission. The source was read in full for this report: 145 lines, 4616 bytes, sha256 prefix `5125976f9c6a`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/clock_nanosleep.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/clock_t_str.c -->
# sources/test-tools/strace/tests/clock_t_str.c

Purpose: `clock_t_str.c` exercises clock and time syscall decoders, especially clock ids, timespec/timex structures, 32-bit versus 64-bit time ABI variants, and restartable sleep output.

Important APIs/types/functions: local functions include `clock_t_str`; macros include none detected; included headers include `tests.h`, `inttypes.h`, `math.h`, `stdint.h`, `stdio.h`, `unistd.h`. Kernel/user ABI names observed in the full file include none detected. Prominent constants include `SPDX`, `GPL`, `MIN`; prominent struct names include none detected.

Control flow: this file is a shared implementation or variant wrapper; compile-time macros select the syscall number, xlat style, fd/path mode, success behavior, or namespace mode before the included/shared test body runs.

State and persistence behavior: runtime state is intentionally temporary and test-local. Most state lives in stack variables, tail-allocated buffers, compile-time macros, and errno/return-code snapshots.

Dependencies: strace test harness headers such as `tests.h`, `scno.h`, `print_utils.h`, `pidns.h`, `secontext.h`, local xlat tables, libc headers, and Linux UAPI headers provide syscall numbers, fallback structs, constants, and output helpers. This file directly includes `tests.h`, `inttypes.h`, `math.h`, `stdint.h`, `stdio.h`, `unistd.h`.

Integration points: the file participates in strace's testsuite as a compiled C test, AWK normalizer, header, or generator input. It integrates with generated xlat tables, syscall-number selection, test-driver `.test` scripts, and expected-output comparison.

Risks: time64/time32 splits and architecture-specific clock ids can alter syscall numbers and structure layout, so tests need conditional compilation and tolerant unsupported-syscall handling.

Test signals: useful validation is the corresponding strace testsuite target under the same basename, comparison of stdout against expected decoder lines, successful compilation under the configured personality/time ABI, and skip behavior when the kernel lacks the syscall or permission. The source was read in full for this report: 38 lines, 820 bytes, sha256 prefix `5d10c89cfe94`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/clock_t_str.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/clock_xettime-common.c -->
# sources/test-tools/strace/tests/clock_xettime-common.c

Purpose: `clock_xettime-common.c` exercises clock and time syscall decoders, especially clock ids, timespec/timex structures, 32-bit versus 64-bit time ABI variants, and restartable sleep output.

Important APIs/types/functions: local functions include `k_syscall`, `k_getres`, `k_gettime`, `k_settime`, `main`; macros include none detected; included headers include `stdio.h`, `time.h`, `unistd.h`, `kernel_timespec.h`. Kernel/user ABI names observed in the full file include `clock_gettime`. Prominent constants include `SPDX`, `GPL`, `TAIL_ALLOC_OBJECT_CONST_PTR`, `CLOCK_MONOTONIC`, `NULL`, `CLOCK_REALTIME`, `CLOCK_PROCESS_CPUTIME_ID`, `CLOCK_THREAD_CPUTIME_ID`; prominent struct names include none detected.

Control flow: `main` builds deterministic arguments, invokes the target syscall or helper sequence, prints the expected strace line with `printf`/test helpers, and exits through the strace test harness.

State and persistence behavior: runtime state is intentionally temporary and test-local. Most state lives in stack variables, tail-allocated buffers, compile-time macros, and errno/return-code snapshots.

Dependencies: strace test harness headers such as `tests.h`, `scno.h`, `print_utils.h`, `pidns.h`, `secontext.h`, local xlat tables, libc headers, and Linux UAPI headers provide syscall numbers, fallback structs, constants, and output helpers. This file directly includes `stdio.h`, `time.h`, `unistd.h`, `kernel_timespec.h`.

Integration points: the file participates in strace's testsuite as a compiled C test, AWK normalizer, header, or generator input. It integrates with generated xlat tables, syscall-number selection, test-driver `.test` scripts, and expected-output comparison.

Risks: time64/time32 splits and architecture-specific clock ids can alter syscall numbers and structure layout, so tests need conditional compilation and tolerant unsupported-syscall handling.

Test signals: useful validation is the corresponding strace testsuite target under the same basename, comparison of stdout against expected decoder lines, successful compilation under the configured personality/time ABI, and skip behavior when the kernel lacks the syscall or permission. The source was read in full for this report: 116 lines, 3505 bytes, sha256 prefix `8792e3495a04`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/clock_xettime-common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/clock_xettime.c -->
# sources/test-tools/strace/tests/clock_xettime.c

Purpose: `clock_xettime.c` exercises clock and time syscall decoders, especially clock ids, timespec/timex structures, 32-bit versus 64-bit time ABI variants, and restartable sleep output.

Important APIs/types/functions: local functions include none detected; macros include `SYSCALL_NR_gettime`, `SYSCALL_NR_settime`, `SYSCALL_NR_getres`, `SYSCALL_NAME_gettime`, `SYSCALL_NAME_settime`, `SYSCALL_NAME_getres`, `clock_timespec_t`; included headers include `tests.h`, `scno.h`, `clock_xettime-common.c`. Kernel/user ABI names observed in the full file include `clock_gettime`, `clock_settime`. Prominent constants include `SPDX`, `GPL`, `SKIP_MAIN_UNDEFINED`; prominent struct names include none detected.

Control flow: this file is a shared implementation or variant wrapper; compile-time macros select the syscall number, xlat style, fd/path mode, success behavior, or namespace mode before the included/shared test body runs.

State and persistence behavior: runtime state is intentionally temporary and test-local. Most state lives in stack variables, tail-allocated buffers, compile-time macros, and errno/return-code snapshots.

Dependencies: strace test harness headers such as `tests.h`, `scno.h`, `print_utils.h`, `pidns.h`, `secontext.h`, local xlat tables, libc headers, and Linux UAPI headers provide syscall numbers, fallback structs, constants, and output helpers. This file directly includes `tests.h`, `scno.h`, `clock_xettime-common.c`.

Integration points: the file participates in strace's testsuite as a compiled C test, AWK normalizer, header, or generator input. It integrates with generated xlat tables, syscall-number selection, test-driver `.test` scripts, and expected-output comparison.

Risks: time64/time32 splits and architecture-specific clock ids can alter syscall numbers and structure layout, so tests need conditional compilation and tolerant unsupported-syscall handling.

Test signals: useful validation is the corresponding strace testsuite target under the same basename, comparison of stdout against expected decoder lines, successful compilation under the configured personality/time ABI, and skip behavior when the kernel lacks the syscall or permission. The source was read in full for this report: 40 lines, 982 bytes, sha256 prefix `fb219b92be48`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/clock_xettime.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/clock_xettime64.c -->
# sources/test-tools/strace/tests/clock_xettime64.c

Purpose: `clock_xettime64.c` exercises clock and time syscall decoders, especially clock ids, timespec/timex structures, 32-bit versus 64-bit time ABI variants, and restartable sleep output.

Important APIs/types/functions: local functions include none detected; macros include `SYSCALL_NR_gettime`, `SYSCALL_NR_settime`, `SYSCALL_NR_getres`, `SYSCALL_NAME_gettime`, `SYSCALL_NAME_settime`, `SYSCALL_NAME_getres`, `clock_timespec_t`; included headers include `tests.h`, `scno.h`, `clock_xettime-common.c`. Kernel/user ABI names observed in the full file include none detected. Prominent constants include `SPDX`, `GPL`, `SKIP_MAIN_UNDEFINED`; prominent struct names include none detected.

Control flow: this file is a shared implementation or variant wrapper; compile-time macros select the syscall number, xlat style, fd/path mode, success behavior, or namespace mode before the included/shared test body runs.

State and persistence behavior: runtime state is intentionally temporary and test-local. Most state lives in stack variables, tail-allocated buffers, compile-time macros, and errno/return-code snapshots.

Dependencies: strace test harness headers such as `tests.h`, `scno.h`, `print_utils.h`, `pidns.h`, `secontext.h`, local xlat tables, libc headers, and Linux UAPI headers provide syscall numbers, fallback structs, constants, and output helpers. This file directly includes `tests.h`, `scno.h`, `clock_xettime-common.c`.

Integration points: the file participates in strace's testsuite as a compiled C test, AWK normalizer, header, or generator input. It integrates with generated xlat tables, syscall-number selection, test-driver `.test` scripts, and expected-output comparison.

Risks: time64/time32 splits and architecture-specific clock ids can alter syscall numbers and structure layout, so tests need conditional compilation and tolerant unsupported-syscall handling.

Test signals: useful validation is the corresponding strace testsuite target under the same basename, comparison of stdout against expected decoder lines, successful compilation under the configured personality/time ABI, and skip behavior when the kernel lacks the syscall or permission. The source was read in full for this report: 34 lines, 859 bytes, sha256 prefix `b19d4ec1f303`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/clock_xettime64.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/clone-flags.c -->
# sources/test-tools/strace/tests/clone-flags.c

Purpose: `clone-flags.c` prints and validates clone flag xlat combinations, signal bits, and unknown-bit handling used by clone-family decoders.

Important APIs/types/functions: local functions include `retrieve_userns`, `wait_cloned`, `child`, `main`; macros include `do_clone`, `do_clone_newns`, `SYSCALL_NAME`, `STACK_SIZE_FMT`, `STACK_SIZE_ARG`; included headers include `tests.h`, `xmalloc.h`, `errno.h`, `limits.h`, `sched.h`, `signal.h`, `stdio.h`, ... (11 total), `sys/wait.h`, `unistd.h`, `linux/sched.h`. Kernel/user ABI names observed in the full file include `clone`. Prominent constants include `SPDX`, `GPL`, `WIFEXITED`, `WEXITSTATUS`, `IA64`, `NULL`, `SYSCALL_NAME`, `STACK_SIZE_FMT`, `STACK_SIZE_ARG`, ... (18 total), `PATH_MAX`, `CLONE_PIDFD`, `CLONE_NEWUSER`; prominent struct names include none detected.

Control flow: `main` builds deterministic arguments, invokes the target syscall or helper sequence, prints the expected strace line with `printf`/test helpers, and exits through the strace test harness.

State and persistence behavior: runtime state is intentionally temporary and test-local. The test may allocate tail buffers and/or create temporary files, directories, descriptors, sockets, eventfds, epoll instances, or mount/file handles, then relies on process exit or explicit cleanup for disposal.

Dependencies: strace test harness headers such as `tests.h`, `scno.h`, `print_utils.h`, `pidns.h`, `secontext.h`, local xlat tables, libc headers, and Linux UAPI headers provide syscall numbers, fallback structs, constants, and output helpers. This file directly includes `tests.h`, `xmalloc.h`, `errno.h`, `limits.h`, `sched.h`, `signal.h`, `stdio.h`, ... (11 total), `sys/wait.h`, `unistd.h`, `linux/sched.h`.

Integration points: the file participates in strace's testsuite as a compiled C test, AWK normalizer, header, or generator input. It integrates with generated xlat tables, syscall-number selection, test-driver `.test` scripts, and expected-output comparison.

Risks: Primary risks are kernel/architecture feature availability, ABI-width differences, host header drift, permissions, namespace-dependent pid/fd/path rendering, and expected-output brittleness when symbolic constants change.

Test signals: useful validation is the corresponding strace testsuite target under the same basename, comparison of stdout against expected decoder lines, successful compilation under the configured personality/time ABI, and skip behavior when the kernel lacks the syscall or permission. The source was read in full for this report: 192 lines, 6189 bytes, sha256 prefix `f137b9f7a803`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/clone-flags.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/clone3-Xabbrev.c -->
# sources/test-tools/strace/tests/clone3-Xabbrev.c

Purpose: `clone3-Xabbrev.c` drives clone3 decoder coverage across raw, abbreviated, verbose, injected-success, namespace-id-reporting, and invalid-argument cases.

Important APIs/types/functions: local functions include none detected; macros include none detected; included headers include `clone3.c`. Kernel/user ABI names observed in the full file include `clone3`. Prominent constants include none detected; prominent struct names include none detected.

Control flow: this file is a shared implementation or variant wrapper; compile-time macros select the syscall number, xlat style, fd/path mode, success behavior, or namespace mode before the included/shared test body runs. `do_clone3_` centralizes syscall execution, expected errno masks, injected-return handling, child exit, and parent wait logic; `print_clone3` mirrors decoder output for every tested argument shape.  This is a wrapper/variant file that reuses shared test implementation through local includes: `clone3.c`.

State and persistence behavior: runtime state is intentionally temporary and test-local. Most state lives in stack variables, tail-allocated buffers, compile-time macros, and errno/return-code snapshots. clone/clone3 tests create real child tasks for success cases and must wait/reap them to avoid stray processes.

Dependencies: strace test harness headers such as `tests.h`, `scno.h`, `print_utils.h`, `pidns.h`, `secontext.h`, local xlat tables, libc headers, and Linux UAPI headers provide syscall numbers, fallback structs, constants, and output helpers. This file directly includes `clone3.c`.

Integration points: the file participates in strace's testsuite as a compiled C test, AWK normalizer, header, or generator input. It integrates with generated xlat tables, syscall-number selection, test-driver `.test` scripts, and expected-output comparison. Its filename selects an xlat rendering mode, so the same syscall surface is compared under abbreviated, raw, or verbose symbolic output.

Risks: clone3 behavior is kernel, architecture, and seccomp dependent; success paths fork real children and require careful wait handling, while xlat verbosity macros must match the generated test variant.

Test signals: useful validation is the corresponding strace testsuite target under the same basename, comparison of stdout against expected decoder lines, successful compilation under the configured personality/time ABI, and skip behavior when the kernel lacks the syscall or permission. The source was read in full for this report: 1 lines, 20 bytes, sha256 prefix `f31f114af11e`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/clone3-Xabbrev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/clone3-Xraw.c -->
# sources/test-tools/strace/tests/clone3-Xraw.c

Purpose: `clone3-Xraw.c` drives clone3 decoder coverage across raw, abbreviated, verbose, injected-success, namespace-id-reporting, and invalid-argument cases.

Important APIs/types/functions: local functions include none detected; macros include `XLAT_RAW`; included headers include `clone3.c`. Kernel/user ABI names observed in the full file include `clone3`. Prominent constants include `XLAT_RAW`; prominent struct names include none detected.

Control flow: this file is a shared implementation or variant wrapper; compile-time macros select the syscall number, xlat style, fd/path mode, success behavior, or namespace mode before the included/shared test body runs. `do_clone3_` centralizes syscall execution, expected errno masks, injected-return handling, child exit, and parent wait logic; `print_clone3` mirrors decoder output for every tested argument shape.  This is a wrapper/variant file that reuses shared test implementation through local includes: `clone3.c`.

State and persistence behavior: runtime state is intentionally temporary and test-local. Most state lives in stack variables, tail-allocated buffers, compile-time macros, and errno/return-code snapshots. clone/clone3 tests create real child tasks for success cases and must wait/reap them to avoid stray processes.

Dependencies: strace test harness headers such as `tests.h`, `scno.h`, `print_utils.h`, `pidns.h`, `secontext.h`, local xlat tables, libc headers, and Linux UAPI headers provide syscall numbers, fallback structs, constants, and output helpers. This file directly includes `clone3.c`.

Integration points: the file participates in strace's testsuite as a compiled C test, AWK normalizer, header, or generator input. It integrates with generated xlat tables, syscall-number selection, test-driver `.test` scripts, and expected-output comparison. Its filename selects an xlat rendering mode, so the same syscall surface is compared under abbreviated, raw, or verbose symbolic output.

Risks: clone3 behavior is kernel, architecture, and seccomp dependent; success paths fork real children and require careful wait handling, while xlat verbosity macros must match the generated test variant.

Test signals: useful validation is the corresponding strace testsuite target under the same basename, comparison of stdout against expected decoder lines, successful compilation under the configured personality/time ABI, and skip behavior when the kernel lacks the syscall or permission. The source was read in full for this report: 2 lines, 39 bytes, sha256 prefix `955300c53388`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/clone3-Xraw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/clone3-Xverbose.c -->
# sources/test-tools/strace/tests/clone3-Xverbose.c

Purpose: `clone3-Xverbose.c` drives clone3 decoder coverage across raw, abbreviated, verbose, injected-success, namespace-id-reporting, and invalid-argument cases.

Important APIs/types/functions: local functions include none detected; macros include `XLAT_VERBOSE`; included headers include `clone3.c`. Kernel/user ABI names observed in the full file include `clone3`. Prominent constants include `XLAT_VERBOSE`; prominent struct names include none detected.

Control flow: this file is a shared implementation or variant wrapper; compile-time macros select the syscall number, xlat style, fd/path mode, success behavior, or namespace mode before the included/shared test body runs. `do_clone3_` centralizes syscall execution, expected errno masks, injected-return handling, child exit, and parent wait logic; `print_clone3` mirrors decoder output for every tested argument shape.  This is a wrapper/variant file that reuses shared test implementation through local includes: `clone3.c`.

State and persistence behavior: runtime state is intentionally temporary and test-local. Most state lives in stack variables, tail-allocated buffers, compile-time macros, and errno/return-code snapshots. clone/clone3 tests create real child tasks for success cases and must wait/reap them to avoid stray processes.

Dependencies: strace test harness headers such as `tests.h`, `scno.h`, `print_utils.h`, `pidns.h`, `secontext.h`, local xlat tables, libc headers, and Linux UAPI headers provide syscall numbers, fallback structs, constants, and output helpers. This file directly includes `clone3.c`.

Integration points: the file participates in strace's testsuite as a compiled C test, AWK normalizer, header, or generator input. It integrates with generated xlat tables, syscall-number selection, test-driver `.test` scripts, and expected-output comparison. Its filename selects an xlat rendering mode, so the same syscall surface is compared under abbreviated, raw, or verbose symbolic output.

Risks: clone3 behavior is kernel, architecture, and seccomp dependent; success paths fork real children and require careful wait handling, while xlat verbosity macros must match the generated test variant.

Test signals: useful validation is the corresponding strace testsuite target under the same basename, comparison of stdout against expected decoder lines, successful compilation under the configured personality/time ABI, and skip behavior when the kernel lacks the syscall or permission. The source was read in full for this report: 2 lines, 43 bytes, sha256 prefix `fb6e2ee7f597`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/clone3-Xverbose.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/clone3-report-ns-id.c -->
# sources/test-tools/strace/tests/clone3-report-ns-id.c

Purpose: `clone3-report-ns-id.c` drives clone3 decoder coverage across raw, abbreviated, verbose, injected-success, namespace-id-reporting, and invalid-argument cases.

Important APIs/types/functions: local functions include `main`; macros include none detected; included headers include `tests.h`, `xmalloc.h`, `limits.h`, `stdio.h`, `unistd.h`, `linux/sched.h`, `scno.h`. Kernel/user ABI names observed in the full file include `clone3`. Prominent constants include `SPDX`, `GPL`, `CLONE_NEWUSER`, `PATH_MAX`, `NULL`; prominent struct names include `clone_args`.

Control flow: `main` builds deterministic arguments, invokes the target syscall or helper sequence, prints the expected strace line with `printf`/test helpers, and exits through the strace test harness. `do_clone3_` centralizes syscall execution, expected errno masks, injected-return handling, child exit, and parent wait logic; `print_clone3` mirrors decoder output for every tested argument shape.

State and persistence behavior: runtime state is intentionally temporary and test-local. Most state lives in stack variables, tail-allocated buffers, compile-time macros, and errno/return-code snapshots. clone/clone3 tests create real child tasks for success cases and must wait/reap them to avoid stray processes.

Dependencies: strace test harness headers such as `tests.h`, `scno.h`, `print_utils.h`, `pidns.h`, `secontext.h`, local xlat tables, libc headers, and Linux UAPI headers provide syscall numbers, fallback structs, constants, and output helpers. This file directly includes `tests.h`, `xmalloc.h`, `limits.h`, `stdio.h`, `unistd.h`, `linux/sched.h`, `scno.h`.

Integration points: the file participates in strace's testsuite as a compiled C test, AWK normalizer, header, or generator input. It integrates with generated xlat tables, syscall-number selection, test-driver `.test` scripts, and expected-output comparison.

Risks: clone3 behavior is kernel, architecture, and seccomp dependent; success paths fork real children and require careful wait handling, while xlat verbosity macros must match the generated test variant.

Test signals: useful validation is the corresponding strace testsuite target under the same basename, comparison of stdout against expected decoder lines, successful compilation under the configured personality/time ABI, and skip behavior when the kernel lacks the syscall or permission. The source was read in full for this report: 44 lines, 1107 bytes, sha256 prefix `8a8877d5598e`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/clone3-report-ns-id.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/clone3-success-Xabbrev.c -->
# sources/test-tools/strace/tests/clone3-success-Xabbrev.c

Purpose: `clone3-success-Xabbrev.c` drives clone3 decoder coverage across raw, abbreviated, verbose, injected-success, namespace-id-reporting, and invalid-argument cases.

Important APIs/types/functions: local functions include none detected; macros include `RETVAL_INJECTED`; included headers include `clone3.c`. Kernel/user ABI names observed in the full file include `clone3`. Prominent constants include `RETVAL_INJECTED`; prominent struct names include none detected.

Control flow: this file is a shared implementation or variant wrapper; compile-time macros select the syscall number, xlat style, fd/path mode, success behavior, or namespace mode before the included/shared test body runs. `do_clone3_` centralizes syscall execution, expected errno masks, injected-return handling, child exit, and parent wait logic; `print_clone3` mirrors decoder output for every tested argument shape.  This is a wrapper/variant file that reuses shared test implementation through local includes: `clone3.c`.

State and persistence behavior: runtime state is intentionally temporary and test-local. Most state lives in stack variables, tail-allocated buffers, compile-time macros, and errno/return-code snapshots. clone/clone3 tests create real child tasks for success cases and must wait/reap them to avoid stray processes.

Dependencies: strace test harness headers such as `tests.h`, `scno.h`, `print_utils.h`, `pidns.h`, `secontext.h`, local xlat tables, libc headers, and Linux UAPI headers provide syscall numbers, fallback structs, constants, and output helpers. This file directly includes `clone3.c`.

Integration points: the file participates in strace's testsuite as a compiled C test, AWK normalizer, header, or generator input. It integrates with generated xlat tables, syscall-number selection, test-driver `.test` scripts, and expected-output comparison. Its filename selects an xlat rendering mode, so the same syscall surface is compared under abbreviated, raw, or verbose symbolic output.

Risks: clone3 behavior is kernel, architecture, and seccomp dependent; success paths fork real children and require careful wait handling, while xlat verbosity macros must match the generated test variant.

Test signals: useful validation is the corresponding strace testsuite target under the same basename, comparison of stdout against expected decoder lines, successful compilation under the configured personality/time ABI, and skip behavior when the kernel lacks the syscall or permission. The source was read in full for this report: 2 lines, 46 bytes, sha256 prefix `42f18c274ba0`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/clone3-success-Xabbrev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/clone3-success-Xraw.c -->
# sources/test-tools/strace/tests/clone3-success-Xraw.c

Purpose: `clone3-success-Xraw.c` drives clone3 decoder coverage across raw, abbreviated, verbose, injected-success, namespace-id-reporting, and invalid-argument cases.

Important APIs/types/functions: local functions include none detected; macros include `RETVAL_INJECTED`, `XLAT_RAW`; included headers include `clone3.c`. Kernel/user ABI names observed in the full file include `clone3`. Prominent constants include `RETVAL_INJECTED`, `XLAT_RAW`; prominent struct names include none detected.

Control flow: this file is a shared implementation or variant wrapper; compile-time macros select the syscall number, xlat style, fd/path mode, success behavior, or namespace mode before the included/shared test body runs. `do_clone3_` centralizes syscall execution, expected errno masks, injected-return handling, child exit, and parent wait logic; `print_clone3` mirrors decoder output for every tested argument shape.  This is a wrapper/variant file that reuses shared test implementation through local includes: `clone3.c`.

State and persistence behavior: runtime state is intentionally temporary and test-local. Most state lives in stack variables, tail-allocated buffers, compile-time macros, and errno/return-code snapshots. clone/clone3 tests create real child tasks for success cases and must wait/reap them to avoid stray processes.

Dependencies: strace test harness headers such as `tests.h`, `scno.h`, `print_utils.h`, `pidns.h`, `secontext.h`, local xlat tables, libc headers, and Linux UAPI headers provide syscall numbers, fallback structs, constants, and output helpers. This file directly includes `clone3.c`.

Integration points: the file participates in strace's testsuite as a compiled C test, AWK normalizer, header, or generator input. It integrates with generated xlat tables, syscall-number selection, test-driver `.test` scripts, and expected-output comparison. Its filename selects an xlat rendering mode, so the same syscall surface is compared under abbreviated, raw, or verbose symbolic output.

Risks: clone3 behavior is kernel, architecture, and seccomp dependent; success paths fork real children and require careful wait handling, while xlat verbosity macros must match the generated test variant.

Test signals: useful validation is the corresponding strace testsuite target under the same basename, comparison of stdout against expected decoder lines, successful compilation under the configured personality/time ABI, and skip behavior when the kernel lacks the syscall or permission. The source was read in full for this report: 3 lines, 65 bytes, sha256 prefix `dd7613d55155`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/clone3-success-Xraw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/clone3-success-Xverbose.c -->
# sources/test-tools/strace/tests/clone3-success-Xverbose.c

Purpose: `clone3-success-Xverbose.c` drives clone3 decoder coverage across raw, abbreviated, verbose, injected-success, namespace-id-reporting, and invalid-argument cases.

Important APIs/types/functions: local functions include none detected; macros include `RETVAL_INJECTED`, `XLAT_VERBOSE`; included headers include `clone3.c`. Kernel/user ABI names observed in the full file include `clone3`. Prominent constants include `RETVAL_INJECTED`, `XLAT_VERBOSE`; prominent struct names include none detected.

Control flow: this file is a shared implementation or variant wrapper; compile-time macros select the syscall number, xlat style, fd/path mode, success behavior, or namespace mode before the included/shared test body runs. `do_clone3_` centralizes syscall execution, expected errno masks, injected-return handling, child exit, and parent wait logic; `print_clone3` mirrors decoder output for every tested argument shape.  This is a wrapper/variant file that reuses shared test implementation through local includes: `clone3.c`.

State and persistence behavior: runtime state is intentionally temporary and test-local. Most state lives in stack variables, tail-allocated buffers, compile-time macros, and errno/return-code snapshots. clone/clone3 tests create real child tasks for success cases and must wait/reap them to avoid stray processes.

Dependencies: strace test harness headers such as `tests.h`, `scno.h`, `print_utils.h`, `pidns.h`, `secontext.h`, local xlat tables, libc headers, and Linux UAPI headers provide syscall numbers, fallback structs, constants, and output helpers. This file directly includes `clone3.c`.

Integration points: the file participates in strace's testsuite as a compiled C test, AWK normalizer, header, or generator input. It integrates with generated xlat tables, syscall-number selection, test-driver `.test` scripts, and expected-output comparison. Its filename selects an xlat rendering mode, so the same syscall surface is compared under abbreviated, raw, or verbose symbolic output.

Risks: clone3 behavior is kernel, architecture, and seccomp dependent; success paths fork real children and require careful wait handling, while xlat verbosity macros must match the generated test variant.

Test signals: useful validation is the corresponding strace testsuite target under the same basename, comparison of stdout against expected decoder lines, successful compilation under the configured personality/time ABI, and skip behavior when the kernel lacks the syscall or permission. The source was read in full for this report: 3 lines, 69 bytes, sha256 prefix `8e0a48226061`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/clone3-success-Xverbose.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/clone3-success.c -->
# sources/test-tools/strace/tests/clone3-success.c

Purpose: `clone3-success.c` drives clone3 decoder coverage across raw, abbreviated, verbose, injected-success, namespace-id-reporting, and invalid-argument cases.

Important APIs/types/functions: local functions include none detected; macros include `RETVAL_INJECTED`; included headers include `clone3.c`. Kernel/user ABI names observed in the full file include `clone3`. Prominent constants include `RETVAL_INJECTED`; prominent struct names include none detected.

Control flow: this file is a shared implementation or variant wrapper; compile-time macros select the syscall number, xlat style, fd/path mode, success behavior, or namespace mode before the included/shared test body runs. `do_clone3_` centralizes syscall execution, expected errno masks, injected-return handling, child exit, and parent wait logic; `print_clone3` mirrors decoder output for every tested argument shape.  This is a wrapper/variant file that reuses shared test implementation through local includes: `clone3.c`.

State and persistence behavior: runtime state is intentionally temporary and test-local. Most state lives in stack variables, tail-allocated buffers, compile-time macros, and errno/return-code snapshots. clone/clone3 tests create real child tasks for success cases and must wait/reap them to avoid stray processes.

Dependencies: strace test harness headers such as `tests.h`, `scno.h`, `print_utils.h`, `pidns.h`, `secontext.h`, local xlat tables, libc headers, and Linux UAPI headers provide syscall numbers, fallback structs, constants, and output helpers. This file directly includes `clone3.c`.

Integration points: the file participates in strace's testsuite as a compiled C test, AWK normalizer, header, or generator input. It integrates with generated xlat tables, syscall-number selection, test-driver `.test` scripts, and expected-output comparison.

Risks: clone3 behavior is kernel, architecture, and seccomp dependent; success paths fork real children and require careful wait handling, while xlat verbosity macros must match the generated test variant.

Test signals: useful validation is the corresponding strace testsuite target under the same basename, comparison of stdout against expected decoder lines, successful compilation under the configured personality/time ABI, and skip behavior when the kernel lacks the syscall or permission. The source was read in full for this report: 2 lines, 46 bytes, sha256 prefix `42f18c274ba0`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/clone3-success.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/clone3.c -->
# sources/test-tools/strace/tests/clone3.c

Purpose: `clone3.c` drives clone3 decoder coverage across raw, abbreviated, verbose, injected-success, namespace-id-reporting, and invalid-argument cases.

Important APIs/types/functions: local functions include `wait_cloned`, `do_clone3_`, `print_addr64`, `print_tls`, `print_set_tid`, `print_clone3`, `main`; macros include `VERBOSE`, `RETVAL_INJECTED`, `MAX_SET_TID_SIZE`, `INJ_STR`, `ERR`, `do_clone3`; included headers include `tests.h`, `errno.h`, `stdint.h`, `inttypes.h`, `stdio.h`, `string.h`, `unistd.h`, ... (11 total), `linux/sched.h`, `asm/ldt.h`, `scno.h`. Kernel/user ABI names observed in the full file include `clone3`. Prominent constants include `SPDX`, `GPL`, `HAVE_STRUCT_USER_DESC`, `VERBOSE`, `RETVAL_INJECTED`, `STRUCT_VALID_BIT`, `PIDFD_VALID_BIT`, `CHILD_TID_VALID_BIT`, `PARENT_TID_VALID_BIT`, ... (66 total), `ARRAY_SIZE`, `XLAT_FMT_U`, `XLAT_ARGS`; prominent struct names include `clone_args`, `user_desc`.

Control flow: `main` builds deterministic arguments, invokes the target syscall or helper sequence, prints the expected strace line with `printf`/test helpers, and exits through the strace test harness. `do_clone3_` centralizes syscall execution, expected errno masks, injected-return handling, child exit, and parent wait logic; `print_clone3` mirrors decoder output for every tested argument shape.

State and persistence behavior: runtime state is intentionally temporary and test-local. The test may allocate tail buffers and/or create temporary files, directories, descriptors, sockets, eventfds, epoll instances, or mount/file handles, then relies on process exit or explicit cleanup for disposal. clone/clone3 tests create real child tasks for success cases and must wait/reap them to avoid stray processes.

Dependencies: strace test harness headers such as `tests.h`, `scno.h`, `print_utils.h`, `pidns.h`, `secontext.h`, local xlat tables, libc headers, and Linux UAPI headers provide syscall numbers, fallback structs, constants, and output helpers. This file directly includes `tests.h`, `errno.h`, `stdint.h`, `inttypes.h`, `stdio.h`, `string.h`, `unistd.h`, ... (11 total), `linux/sched.h`, `asm/ldt.h`, `scno.h`.

Integration points: the file participates in strace's testsuite as a compiled C test, AWK normalizer, header, or generator input. It integrates with generated xlat tables, syscall-number selection, test-driver `.test` scripts, and expected-output comparison.

Risks: clone3 behavior is kernel, architecture, and seccomp dependent; success paths fork real children and require careful wait handling, while xlat verbosity macros must match the generated test variant.

Test signals: useful validation is the corresponding strace testsuite target under the same basename, comparison of stdout against expected decoder lines, successful compilation under the configured personality/time ABI, and skip behavior when the kernel lacks the syscall or permission. The source was read in full for this report: 601 lines, 17156 bytes, sha256 prefix `9572a76ecf18`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/clone3.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/clone_parent--quiet-exit.c -->
# sources/test-tools/strace/tests/clone_parent--quiet-exit.c

Purpose: `clone_parent--quiet-exit.c` checks clone/CLONE_PARENT tracing output and quiet-mode behavior across parent/child process relationships.

Important APIs/types/functions: local functions include none detected; macros include `QUIET_MSG`; included headers include `clone_parent.c`. Kernel/user ABI names observed in the full file include none detected. Prominent constants include `QUIET_MSG`; prominent struct names include none detected.

Control flow: this file is a shared implementation or variant wrapper; compile-time macros select the syscall number, xlat style, fd/path mode, success behavior, or namespace mode before the included/shared test body runs.  This is a wrapper/variant file that reuses shared test implementation through local includes: `clone_parent.c`.

State and persistence behavior: runtime state is intentionally temporary and test-local. Most state lives in stack variables, tail-allocated buffers, compile-time macros, and errno/return-code snapshots.

Dependencies: strace test harness headers such as `tests.h`, `scno.h`, `print_utils.h`, `pidns.h`, `secontext.h`, local xlat tables, libc headers, and Linux UAPI headers provide syscall numbers, fallback structs, constants, and output helpers. This file directly includes `clone_parent.c`.

Integration points: the file participates in strace's testsuite as a compiled C test, AWK normalizer, header, or generator input. It integrates with generated xlat tables, syscall-number selection, test-driver `.test` scripts, and expected-output comparison.

Risks: Primary risks are kernel/architecture feature availability, ABI-width differences, host header drift, permissions, namespace-dependent pid/fd/path rendering, and expected-output brittleness when symbolic constants change.

Test signals: useful validation is the corresponding strace testsuite target under the same basename, comparison of stdout against expected decoder lines, successful compilation under the configured personality/time ABI, and skip behavior when the kernel lacks the syscall or permission. The source was read in full for this report: 2 lines, 46 bytes, sha256 prefix `8d792b6469e4`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/clone_parent--quiet-exit.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/clone_parent-q.c -->
# sources/test-tools/strace/tests/clone_parent-q.c

Purpose: `clone_parent-q.c` checks clone/CLONE_PARENT tracing output and quiet-mode behavior across parent/child process relationships.

Important APIs/types/functions: local functions include none detected; macros include `QUIET_MSG`; included headers include `clone_parent.c`. Kernel/user ABI names observed in the full file include none detected. Prominent constants include `QUIET_MSG`; prominent struct names include none detected.

Control flow: this file is a shared implementation or variant wrapper; compile-time macros select the syscall number, xlat style, fd/path mode, success behavior, or namespace mode before the included/shared test body runs.  This is a wrapper/variant file that reuses shared test implementation through local includes: `clone_parent.c`.

State and persistence behavior: runtime state is intentionally temporary and test-local. Most state lives in stack variables, tail-allocated buffers, compile-time macros, and errno/return-code snapshots.

Dependencies: strace test harness headers such as `tests.h`, `scno.h`, `print_utils.h`, `pidns.h`, `secontext.h`, local xlat tables, libc headers, and Linux UAPI headers provide syscall numbers, fallback structs, constants, and output helpers. This file directly includes `clone_parent.c`.

Integration points: the file participates in strace's testsuite as a compiled C test, AWK normalizer, header, or generator input. It integrates with generated xlat tables, syscall-number selection, test-driver `.test` scripts, and expected-output comparison.

Risks: Primary risks are kernel/architecture feature availability, ABI-width differences, host header drift, permissions, namespace-dependent pid/fd/path rendering, and expected-output brittleness when symbolic constants change.

Test signals: useful validation is the corresponding strace testsuite target under the same basename, comparison of stdout against expected decoder lines, successful compilation under the configured personality/time ABI, and skip behavior when the kernel lacks the syscall or permission. The source was read in full for this report: 2 lines, 46 bytes, sha256 prefix `bbd20866ca32`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/clone_parent-q.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/clone_parent-qq.c -->
# sources/test-tools/strace/tests/clone_parent-qq.c

Purpose: `clone_parent-qq.c` checks clone/CLONE_PARENT tracing output and quiet-mode behavior across parent/child process relationships.

Important APIs/types/functions: local functions include none detected; macros include `QUIET_MSG`; included headers include `clone_parent.c`. Kernel/user ABI names observed in the full file include none detected. Prominent constants include `QUIET_MSG`; prominent struct names include none detected.

Control flow: this file is a shared implementation or variant wrapper; compile-time macros select the syscall number, xlat style, fd/path mode, success behavior, or namespace mode before the included/shared test body runs.  This is a wrapper/variant file that reuses shared test implementation through local includes: `clone_parent.c`.

State and persistence behavior: runtime state is intentionally temporary and test-local. Most state lives in stack variables, tail-allocated buffers, compile-time macros, and errno/return-code snapshots.

Dependencies: strace test harness headers such as `tests.h`, `scno.h`, `print_utils.h`, `pidns.h`, `secontext.h`, local xlat tables, libc headers, and Linux UAPI headers provide syscall numbers, fallback structs, constants, and output helpers. This file directly includes `clone_parent.c`.

Integration points: the file participates in strace's testsuite as a compiled C test, AWK normalizer, header, or generator input. It integrates with generated xlat tables, syscall-number selection, test-driver `.test` scripts, and expected-output comparison.

Risks: Primary risks are kernel/architecture feature availability, ABI-width differences, host header drift, permissions, namespace-dependent pid/fd/path rendering, and expected-output brittleness when symbolic constants change.

Test signals: useful validation is the corresponding strace testsuite target under the same basename, comparison of stdout against expected decoder lines, successful compilation under the configured personality/time ABI, and skip behavior when the kernel lacks the syscall or permission. The source was read in full for this report: 2 lines, 46 bytes, sha256 prefix `8d792b6469e4`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/clone_parent-qq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/clone_parent.c -->
# sources/test-tools/strace/tests/clone_parent.c

Purpose: `clone_parent.c` checks clone/CLONE_PARENT tracing output and quiet-mode behavior across parent/child process relationships.

Important APIs/types/functions: local functions include `child`, `main`; macros include `QUIET_MSG`, `do_clone`; included headers include `tests.h`, `errno.h`, `sched.h`, `signal.h`, `stdio.h`, `stdlib.h`, `sys/wait.h`, `unistd.h`. Kernel/user ABI names observed in the full file include `clone`. Prominent constants include `CLONE_PARENT`, `SPDX`, `GPL`, `QUIET_MSG`, `IA64`, `SIGCHLD`, `ESRCH`, `FILE`, `STRACE_EXE`; prominent struct names include none detected.

Control flow: `main` builds deterministic arguments, invokes the target syscall or helper sequence, prints the expected strace line with `printf`/test helpers, and exits through the strace test harness.

State and persistence behavior: runtime state is intentionally temporary and test-local. The test may allocate tail buffers and/or create temporary files, directories, descriptors, sockets, eventfds, epoll instances, or mount/file handles, then relies on process exit or explicit cleanup for disposal.

Dependencies: strace test harness headers such as `tests.h`, `scno.h`, `print_utils.h`, `pidns.h`, `secontext.h`, local xlat tables, libc headers, and Linux UAPI headers provide syscall numbers, fallback structs, constants, and output helpers. This file directly includes `tests.h`, `errno.h`, `sched.h`, `signal.h`, `stdio.h`, `stdlib.h`, `sys/wait.h`, `unistd.h`.

Integration points: the file participates in strace's testsuite as a compiled C test, AWK normalizer, header, or generator input. It integrates with generated xlat tables, syscall-number selection, test-driver `.test` scripts, and expected-output comparison.

Risks: Primary risks are kernel/architecture feature availability, ABI-width differences, host header drift, permissions, namespace-dependent pid/fd/path rendering, and expected-output brittleness when symbolic constants change.

Test signals: useful validation is the corresponding strace testsuite target under the same basename, comparison of stdout against expected decoder lines, successful compilation under the configured personality/time ABI, and skip behavior when the kernel lacks the syscall or permission. The source was read in full for this report: 73 lines, 1573 bytes, sha256 prefix `c4e832f2c76a`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/clone_parent.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/clone_ptrace--quiet-attach.c -->
# sources/test-tools/strace/tests/clone_ptrace--quiet-attach.c

Purpose: `clone_ptrace--quiet-attach.c` checks clone with ptrace-related tracing and quiet attach/exit modes, validating how strace reports traced children.

Important APIs/types/functions: local functions include none detected; macros include `QUIET_ATTACH`; included headers include `clone_ptrace.c`. Kernel/user ABI names observed in the full file include none detected. Prominent constants include `QUIET_ATTACH`; prominent struct names include none detected.

Control flow: this file is a shared implementation or variant wrapper; compile-time macros select the syscall number, xlat style, fd/path mode, success behavior, or namespace mode before the included/shared test body runs.  This is a wrapper/variant file that reuses shared test implementation through local includes: `clone_ptrace.c`.

State and persistence behavior: runtime state is intentionally temporary and test-local. Most state lives in stack variables, tail-allocated buffers, compile-time macros, and errno/return-code snapshots.

Dependencies: strace test harness headers such as `tests.h`, `scno.h`, `print_utils.h`, `pidns.h`, `secontext.h`, local xlat tables, libc headers, and Linux UAPI headers provide syscall numbers, fallback structs, constants, and output helpers. This file directly includes `clone_ptrace.c`.

Integration points: the file participates in strace's testsuite as a compiled C test, AWK normalizer, header, or generator input. It integrates with generated xlat tables, syscall-number selection, test-driver `.test` scripts, and expected-output comparison.

Risks: Primary risks are kernel/architecture feature availability, ABI-width differences, host header drift, permissions, namespace-dependent pid/fd/path rendering, and expected-output brittleness when symbolic constants change.

Test signals: useful validation is the corresponding strace testsuite target under the same basename, comparison of stdout against expected decoder lines, successful compilation under the configured personality/time ABI, and skip behavior when the kernel lacks the syscall or permission. The source was read in full for this report: 2 lines, 49 bytes, sha256 prefix `371689afaf0c`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/clone_ptrace--quiet-attach.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/clone_ptrace--quiet-exit.c -->
# sources/test-tools/strace/tests/clone_ptrace--quiet-exit.c

Purpose: `clone_ptrace--quiet-exit.c` checks clone with ptrace-related tracing and quiet attach/exit modes, validating how strace reports traced children.

Important APIs/types/functions: local functions include none detected; macros include `QUIET_EXIT`; included headers include `clone_ptrace.c`. Kernel/user ABI names observed in the full file include none detected. Prominent constants include `QUIET_EXIT`; prominent struct names include none detected.

Control flow: this file is a shared implementation or variant wrapper; compile-time macros select the syscall number, xlat style, fd/path mode, success behavior, or namespace mode before the included/shared test body runs.  This is a wrapper/variant file that reuses shared test implementation through local includes: `clone_ptrace.c`.

State and persistence behavior: runtime state is intentionally temporary and test-local. Most state lives in stack variables, tail-allocated buffers, compile-time macros, and errno/return-code snapshots.

Dependencies: strace test harness headers such as `tests.h`, `scno.h`, `print_utils.h`, `pidns.h`, `secontext.h`, local xlat tables, libc headers, and Linux UAPI headers provide syscall numbers, fallback structs, constants, and output helpers. This file directly includes `clone_ptrace.c`.

Integration points: the file participates in strace's testsuite as a compiled C test, AWK normalizer, header, or generator input. It integrates with generated xlat tables, syscall-number selection, test-driver `.test` scripts, and expected-output comparison.

Risks: Primary risks are kernel/architecture feature availability, ABI-width differences, host header drift, permissions, namespace-dependent pid/fd/path rendering, and expected-output brittleness when symbolic constants change.

Test signals: useful validation is the corresponding strace testsuite target under the same basename, comparison of stdout against expected decoder lines, successful compilation under the configured personality/time ABI, and skip behavior when the kernel lacks the syscall or permission. The source was read in full for this report: 2 lines, 47 bytes, sha256 prefix `959d6f2e1cf4`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/clone_ptrace--quiet-exit.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/clone_ptrace-q.c -->
# sources/test-tools/strace/tests/clone_ptrace-q.c

Purpose: `clone_ptrace-q.c` checks clone with ptrace-related tracing and quiet attach/exit modes, validating how strace reports traced children.

Important APIs/types/functions: local functions include none detected; macros include `QUIET_ATTACH`; included headers include `clone_ptrace.c`. Kernel/user ABI names observed in the full file include none detected. Prominent constants include `QUIET_ATTACH`; prominent struct names include none detected.

Control flow: this file is a shared implementation or variant wrapper; compile-time macros select the syscall number, xlat style, fd/path mode, success behavior, or namespace mode before the included/shared test body runs.  This is a wrapper/variant file that reuses shared test implementation through local includes: `clone_ptrace.c`.

State and persistence behavior: runtime state is intentionally temporary and test-local. Most state lives in stack variables, tail-allocated buffers, compile-time macros, and errno/return-code snapshots.

Dependencies: strace test harness headers such as `tests.h`, `scno.h`, `print_utils.h`, `pidns.h`, `secontext.h`, local xlat tables, libc headers, and Linux UAPI headers provide syscall numbers, fallback structs, constants, and output helpers. This file directly includes `clone_ptrace.c`.

Integration points: the file participates in strace's testsuite as a compiled C test, AWK normalizer, header, or generator input. It integrates with generated xlat tables, syscall-number selection, test-driver `.test` scripts, and expected-output comparison.

Risks: Primary risks are kernel/architecture feature availability, ABI-width differences, host header drift, permissions, namespace-dependent pid/fd/path rendering, and expected-output brittleness when symbolic constants change.

Test signals: useful validation is the corresponding strace testsuite target under the same basename, comparison of stdout against expected decoder lines, successful compilation under the configured personality/time ABI, and skip behavior when the kernel lacks the syscall or permission. The source was read in full for this report: 2 lines, 49 bytes, sha256 prefix `371689afaf0c`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/clone_ptrace-q.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/clone_ptrace-qq.c -->
# sources/test-tools/strace/tests/clone_ptrace-qq.c

Purpose: `clone_ptrace-qq.c` checks clone with ptrace-related tracing and quiet attach/exit modes, validating how strace reports traced children.

Important APIs/types/functions: local functions include none detected; macros include `QUIET_ATTACH`, `QUIET_EXIT`; included headers include `clone_ptrace.c`. Kernel/user ABI names observed in the full file include none detected. Prominent constants include `QUIET_ATTACH`, `QUIET_EXIT`; prominent struct names include none detected.

Control flow: this file is a shared implementation or variant wrapper; compile-time macros select the syscall number, xlat style, fd/path mode, success behavior, or namespace mode before the included/shared test body runs.  This is a wrapper/variant file that reuses shared test implementation through local includes: `clone_ptrace.c`.

State and persistence behavior: runtime state is intentionally temporary and test-local. Most state lives in stack variables, tail-allocated buffers, compile-time macros, and errno/return-code snapshots.

Dependencies: strace test harness headers such as `tests.h`, `scno.h`, `print_utils.h`, `pidns.h`, `secontext.h`, local xlat tables, libc headers, and Linux UAPI headers provide syscall numbers, fallback structs, constants, and output helpers. This file directly includes `clone_ptrace.c`.

Integration points: the file participates in strace's testsuite as a compiled C test, AWK normalizer, header, or generator input. It integrates with generated xlat tables, syscall-number selection, test-driver `.test` scripts, and expected-output comparison.

Risks: Primary risks are kernel/architecture feature availability, ABI-width differences, host header drift, permissions, namespace-dependent pid/fd/path rendering, and expected-output brittleness when symbolic constants change.

Test signals: useful validation is the corresponding strace testsuite target under the same basename, comparison of stdout against expected decoder lines, successful compilation under the configured personality/time ABI, and skip behavior when the kernel lacks the syscall or permission. The source was read in full for this report: 3 lines, 70 bytes, sha256 prefix `4bec1646db10`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/clone_ptrace-qq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/clone_ptrace.c -->
# sources/test-tools/strace/tests/clone_ptrace.c

Purpose: `clone_ptrace.c` checks clone with ptrace-related tracing and quiet attach/exit modes, validating how strace reports traced children.

Important APIs/types/functions: local functions include `handler`, `child`, `main`; macros include `QUIET_ATTACH`, `QUIET_EXIT`, `do_clone`; included headers include `tests.h`, `errno.h`, `sched.h`, `signal.h`, `stdio.h`, `stdlib.h`, `string.h`, `sys/wait.h`, `unistd.h`. Kernel/user ABI names observed in the full file include `clone`. Prominent constants include `CLONE_PTRACE`, `SPDX`, `GPL`, `QUIET_ATTACH`, `QUIET_EXIT`, `IA64`, `SIGUSR1`, `SIG_UNBLOCK`, `NULL`, ... (18 total), `WTERMSIG`, `CLD_KILLED`, `ARRSZ_PAIR`; prominent struct names include `sigaction`.

Control flow: `main` builds deterministic arguments, invokes the target syscall or helper sequence, prints the expected strace line with `printf`/test helpers, and exits through the strace test harness.

State and persistence behavior: runtime state is intentionally temporary and test-local. The test may allocate tail buffers and/or create temporary files, directories, descriptors, sockets, eventfds, epoll instances, or mount/file handles, then relies on process exit or explicit cleanup for disposal.

Dependencies: strace test harness headers such as `tests.h`, `scno.h`, `print_utils.h`, `pidns.h`, `secontext.h`, local xlat tables, libc headers, and Linux UAPI headers provide syscall numbers, fallback structs, constants, and output helpers. This file directly includes `tests.h`, `errno.h`, `sched.h`, `signal.h`, `stdio.h`, `stdlib.h`, `string.h`, `sys/wait.h`, `unistd.h`.

Integration points: the file participates in strace's testsuite as a compiled C test, AWK normalizer, header, or generator input. It integrates with generated xlat tables, syscall-number selection, test-driver `.test` scripts, and expected-output comparison.

Risks: Primary risks are kernel/architecture feature availability, ABI-width differences, host header drift, permissions, namespace-dependent pid/fd/path rendering, and expected-output brittleness when symbolic constants change.

Test signals: useful validation is the corresponding strace testsuite target under the same basename, comparison of stdout against expected decoder lines, successful compilation under the configured personality/time ABI, and skip behavior when the kernel lacks the syscall or permission. The source was read in full for this report: 110 lines, 2565 bytes, sha256 prefix `aef7084fda00`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/clone_ptrace.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/close_range.c -->
# sources/test-tools/strace/tests/close_range.c

Purpose: `close_range.c` tests filesystem utility syscall decoding for file creation, temp-file creation, range copy, close_range, sockets/helpers, and synchronization wrappers.

Important APIs/types/functions: local functions include `k_close_range`, `main`; macros include none detected; included headers include `tests.h`, `scno.h`, `fcntl.h`, `stdio.h`, `unistd.h`, `linux/close_range.h`. Kernel/user ABI names observed in the full file include `close_range`, `fcntl`. Prominent constants include `SPDX`, `GPL`, `CLOSE_RANGE_`, `CLOSE_RANGE_UNSHARE`, `CLOSE_RANGE_CLOEXEC`; prominent struct names include none detected.

Control flow: `main` builds deterministic arguments, invokes the target syscall or helper sequence, prints the expected strace line with `printf`/test helpers, and exits through the strace test harness.

State and persistence behavior: runtime state is intentionally temporary and test-local. Most state lives in stack variables, tail-allocated buffers, compile-time macros, and errno/return-code snapshots.

Dependencies: strace test harness headers such as `tests.h`, `scno.h`, `print_utils.h`, `pidns.h`, `secontext.h`, local xlat tables, libc headers, and Linux UAPI headers provide syscall numbers, fallback structs, constants, and output helpers. This file directly includes `tests.h`, `scno.h`, `fcntl.h`, `stdio.h`, `unistd.h`, `linux/close_range.h`.

Integration points: the file participates in strace's testsuite as a compiled C test, AWK normalizer, header, or generator input. It integrates with generated xlat tables, syscall-number selection, test-driver `.test` scripts, and expected-output comparison.

Risks: Primary risks are kernel/architecture feature availability, ABI-width differences, host header drift, permissions, namespace-dependent pid/fd/path rendering, and expected-output brittleness when symbolic constants change.

Test signals: useful validation is the corresponding strace testsuite target under the same basename, comparison of stdout against expected decoder lines, successful compilation under the configured personality/time ABI, and skip behavior when the kernel lacks the syscall or permission. The source was read in full for this report: 79 lines, 2091 bytes, sha256 prefix `572bde4ef7cf`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/close_range.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/copy_file_range.c -->
# sources/test-tools/strace/tests/copy_file_range.c

Purpose: `copy_file_range.c` tests filesystem utility syscall decoding for file creation, temp-file creation, range copy, close_range, sockets/helpers, and synchronization wrappers.

Important APIs/types/functions: local functions include `main`; macros include none detected; included headers include `tests.h`, `scno.h`, `stdio.h`, `unistd.h`. Kernel/user ABI names observed in the full file include `copy_file_range`. Prominent constants include `SPDX`, `GPL`, `TAIL_ALLOC_OBJECT_CONST_PTR`; prominent struct names include none detected.

Control flow: `main` builds deterministic arguments, invokes the target syscall or helper sequence, prints the expected strace line with `printf`/test helpers, and exits through the strace test harness.

State and persistence behavior: runtime state is intentionally temporary and test-local. Most state lives in stack variables, tail-allocated buffers, compile-time macros, and errno/return-code snapshots.

Dependencies: strace test harness headers such as `tests.h`, `scno.h`, `print_utils.h`, `pidns.h`, `secontext.h`, local xlat tables, libc headers, and Linux UAPI headers provide syscall numbers, fallback structs, constants, and output helpers. This file directly includes `tests.h`, `scno.h`, `stdio.h`, `unistd.h`.

Integration points: the file participates in strace's testsuite as a compiled C test, AWK normalizer, header, or generator input. It integrates with generated xlat tables, syscall-number selection, test-driver `.test` scripts, and expected-output comparison.

Risks: Primary risks are kernel/architecture feature availability, ABI-width differences, host header drift, permissions, namespace-dependent pid/fd/path rendering, and expected-output brittleness when symbolic constants change.

Test signals: useful validation is the corresponding strace testsuite target under the same basename, comparison of stdout against expected decoder lines, successful compilation under the configured personality/time ABI, and skip behavior when the kernel lacks the syscall or permission. The source was read in full for this report: 37 lines, 986 bytes, sha256 prefix `ac492f841a5b`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/copy_file_range.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/count-f.c -->
# sources/test-tools/strace/tests/count-f.c

Purpose: `count-f.c` supports strace summary/counting tests for normal and unknown syscalls, including mixed and many-unknown cases.

Important APIs/types/functions: local functions include `process`, `main`, `thread`; macros include `N`, `P`, `T`; included headers include `tests.h`, `assert.h`, `errno.h`, `pthread.h`, `stdio.h`, `stdlib.h`, `sys/wait.h`, `unistd.h`. Kernel/user ABI names observed in the full file include `chdir`. Prominent constants include `SPDX`, `GPL`, `NULL`, `EINTR`, `WIFEXITED`, `WEXITSTATUS`; prominent struct names include none detected.

Control flow: `main` builds deterministic arguments, invokes the target syscall or helper sequence, prints the expected strace line with `printf`/test helpers, and exits through the strace test harness.

State and persistence behavior: runtime state is intentionally temporary and test-local. Most state lives in stack variables, tail-allocated buffers, compile-time macros, and errno/return-code snapshots.

Dependencies: strace test harness headers such as `tests.h`, `scno.h`, `print_utils.h`, `pidns.h`, `secontext.h`, local xlat tables, libc headers, and Linux UAPI headers provide syscall numbers, fallback structs, constants, and output helpers. This file directly includes `tests.h`, `assert.h`, `errno.h`, `pthread.h`, `stdio.h`, `stdlib.h`, `sys/wait.h`, `unistd.h`.

Integration points: the file participates in strace's testsuite as a compiled C test, AWK normalizer, header, or generator input. It integrates with generated xlat tables, syscall-number selection, test-driver `.test` scripts, and expected-output comparison.

Risks: Primary risks are kernel/architecture feature availability, ABI-width differences, host header drift, permissions, namespace-dependent pid/fd/path rendering, and expected-output brittleness when symbolic constants change.

Test signals: useful validation is the corresponding strace testsuite target under the same basename, comparison of stdout against expected decoder lines, successful compilation under the configured personality/time ABI, and skip behavior when the kernel lacks the syscall or permission. The source was read in full for this report: 83 lines, 1392 bytes, sha256 prefix `82b43f4e41f4`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/count-f.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/count_unknown.c -->
# sources/test-tools/strace/tests/count_unknown.c

Purpose: `count_unknown.c` supports strace summary/counting tests for normal and unknown syscalls, including mixed and many-unknown cases.

Important APIs/types/functions: local functions include `main`; macros include none detected; included headers include `nsyscalls.h`. Kernel/user ABI names observed in the full file include none detected. Prominent constants include `SPDX`, `GPL`, `ARRAY_SIZE`, `SYSCALL_BIT`; prominent struct names include none detected.

Control flow: `main` builds deterministic arguments, invokes the target syscall or helper sequence, prints the expected strace line with `printf`/test helpers, and exits through the strace test harness.  This is a wrapper/variant file that reuses shared test implementation through local includes: `nsyscalls.h`.

State and persistence behavior: runtime state is intentionally temporary and test-local. Most state lives in stack variables, tail-allocated buffers, compile-time macros, and errno/return-code snapshots.

Dependencies: strace test harness headers such as `tests.h`, `scno.h`, `print_utils.h`, `pidns.h`, `secontext.h`, local xlat tables, libc headers, and Linux UAPI headers provide syscall numbers, fallback structs, constants, and output helpers. This file directly includes `nsyscalls.h`.

Integration points: the file participates in strace's testsuite as a compiled C test, AWK normalizer, header, or generator input. It integrates with generated xlat tables, syscall-number selection, test-driver `.test` scripts, and expected-output comparison.

Risks: Primary risks are kernel/architecture feature availability, ABI-width differences, host header drift, permissions, namespace-dependent pid/fd/path rendering, and expected-output brittleness when symbolic constants change.

Test signals: useful validation is the corresponding strace testsuite target under the same basename, comparison of stdout against expected decoder lines, successful compilation under the configured personality/time ABI, and skip behavior when the kernel lacks the syscall or permission. The source was read in full for this report: 28 lines, 594 bytes, sha256 prefix `0319044618d3`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/count_unknown.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/count_unknown_many.c -->
# sources/test-tools/strace/tests/count_unknown_many.c

Purpose: `count_unknown_many.c` supports strace summary/counting tests for normal and unknown syscalls, including mixed and many-unknown cases.

Important APIs/types/functions: local functions include `main`; macros include none detected; included headers include `nsyscalls.h`. Kernel/user ABI names observed in the full file include none detected. Prominent constants include `SPDX`, `GPL`, `ARRAY_SIZE`, `SYSCALL_BIT`; prominent struct names include none detected.

Control flow: `main` builds deterministic arguments, invokes the target syscall or helper sequence, prints the expected strace line with `printf`/test helpers, and exits through the strace test harness.  This is a wrapper/variant file that reuses shared test implementation through local includes: `nsyscalls.h`.

State and persistence behavior: runtime state is intentionally temporary and test-local. Most state lives in stack variables, tail-allocated buffers, compile-time macros, and errno/return-code snapshots.

Dependencies: strace test harness headers such as `tests.h`, `scno.h`, `print_utils.h`, `pidns.h`, `secontext.h`, local xlat tables, libc headers, and Linux UAPI headers provide syscall numbers, fallback structs, constants, and output helpers. This file directly includes `nsyscalls.h`.

Integration points: the file participates in strace's testsuite as a compiled C test, AWK normalizer, header, or generator input. It integrates with generated xlat tables, syscall-number selection, test-driver `.test` scripts, and expected-output comparison.

Risks: Primary risks are kernel/architecture feature availability, ABI-width differences, host header drift, permissions, namespace-dependent pid/fd/path rendering, and expected-output brittleness when symbolic constants change.

Test signals: useful validation is the corresponding strace testsuite target under the same basename, comparison of stdout against expected decoder lines, successful compilation under the configured personality/time ABI, and skip behavior when the kernel lacks the syscall or permission. The source was read in full for this report: 25 lines, 486 bytes, sha256 prefix `4b72175750c1`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/count_unknown_many.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/count_unknown_mixed.c -->
# sources/test-tools/strace/tests/count_unknown_mixed.c

Purpose: `count_unknown_mixed.c` supports strace summary/counting tests for normal and unknown syscalls, including mixed and many-unknown cases.

Important APIs/types/functions: local functions include `main`; macros include none detected; included headers include `nsyscalls.h`. Kernel/user ABI names observed in the full file include none detected. Prominent constants include `SPDX`, `GPL`, `ARRAY_SIZE`, `SYSCALL_BIT`; prominent struct names include none detected.

Control flow: `main` builds deterministic arguments, invokes the target syscall or helper sequence, prints the expected strace line with `printf`/test helpers, and exits through the strace test harness.  This is a wrapper/variant file that reuses shared test implementation through local includes: `nsyscalls.h`.

State and persistence behavior: runtime state is intentionally temporary and test-local. Most state lives in stack variables, tail-allocated buffers, compile-time macros, and errno/return-code snapshots.

Dependencies: strace test harness headers such as `tests.h`, `scno.h`, `print_utils.h`, `pidns.h`, `secontext.h`, local xlat tables, libc headers, and Linux UAPI headers provide syscall numbers, fallback structs, constants, and output helpers. This file directly includes `nsyscalls.h`.

Integration points: the file participates in strace's testsuite as a compiled C test, AWK normalizer, header, or generator input. It integrates with generated xlat tables, syscall-number selection, test-driver `.test` scripts, and expected-output comparison.

Risks: Primary risks are kernel/architecture feature availability, ABI-width differences, host header drift, permissions, namespace-dependent pid/fd/path rendering, and expected-output brittleness when symbolic constants change.

Test signals: useful validation is the corresponding strace testsuite target under the same basename, comparison of stdout against expected decoder lines, successful compilation under the configured personality/time ABI, and skip behavior when the kernel lacks the syscall or permission. The source was read in full for this report: 24 lines, 432 bytes, sha256 prefix `05d200128e34`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/count_unknown_mixed.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/creat.c -->
# sources/test-tools/strace/tests/creat.c

Purpose: `creat.c` tests filesystem utility syscall decoding for file creation, temp-file creation, range copy, close_range, sockets/helpers, and synchronization wrappers.

Important APIs/types/functions: local functions include none detected; macros include `TEST_SYSCALL_NR`, `TEST_SYSCALL_STR`; included headers include `tests.h`, `scno.h`, `umode_t.c`. Kernel/user ABI names observed in the full file include `creat`. Prominent constants include `SPDX`, `GPL`, `TEST_SYSCALL_NR`, `TEST_SYSCALL_STR`, `SKIP_MAIN_UNDEFINED`; prominent struct names include none detected.

Control flow: this file is a shared implementation or variant wrapper; compile-time macros select the syscall number, xlat style, fd/path mode, success behavior, or namespace mode before the included/shared test body runs.  This is a wrapper/variant file that reuses shared test implementation through local includes: `tests.h`, `scno.h`, `umode_t.c`.

State and persistence behavior: runtime state is intentionally temporary and test-local. Most state lives in stack variables, tail-allocated buffers, compile-time macros, and errno/return-code snapshots.

Dependencies: strace test harness headers such as `tests.h`, `scno.h`, `print_utils.h`, `pidns.h`, `secontext.h`, local xlat tables, libc headers, and Linux UAPI headers provide syscall numbers, fallback structs, constants, and output helpers. This file directly includes `tests.h`, `scno.h`, `umode_t.c`.

Integration points: the file participates in strace's testsuite as a compiled C test, AWK normalizer, header, or generator input. It integrates with generated xlat tables, syscall-number selection, test-driver `.test` scripts, and expected-output comparison.

Risks: Primary risks are kernel/architecture feature availability, ABI-width differences, host header drift, permissions, namespace-dependent pid/fd/path rendering, and expected-output brittleness when symbolic constants change.

Test signals: useful validation is the corresponding strace testsuite target under the same basename, comparison of stdout against expected decoder lines, successful compilation under the configured personality/time ABI, and skip behavior when the kernel lacks the syscall or permission. The source was read in full for this report: 21 lines, 329 bytes, sha256 prefix `fa40fcf649db`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/creat.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/create_nl_socket.c -->
# sources/test-tools/strace/tests/create_nl_socket.c

Purpose: `create_nl_socket.c` tests filesystem utility syscall decoding for file creation, temp-file creation, range copy, close_range, sockets/helpers, and synchronization wrappers.

Important APIs/types/functions: local functions include `create_nl_socket_ext`; macros include none detected; included headers include `tests.h`, `sys/socket.h`, `netlink.h`. Kernel/user ABI names observed in the full file include `socket`. Prominent constants include `SPDX`, `GPL`, `AF_NETLINK`, `SOCK_RAW`, `SOL_SOCKET`, `SO_ACCEPTCONN`; prominent struct names include `sockaddr_nl`, `sockaddr`.

Control flow: this file is a shared implementation or variant wrapper; compile-time macros select the syscall number, xlat style, fd/path mode, success behavior, or namespace mode before the included/shared test body runs.

State and persistence behavior: runtime state is intentionally temporary and test-local. Most state lives in stack variables, tail-allocated buffers, compile-time macros, and errno/return-code snapshots.

Dependencies: strace test harness headers such as `tests.h`, `scno.h`, `print_utils.h`, `pidns.h`, `secontext.h`, local xlat tables, libc headers, and Linux UAPI headers provide syscall numbers, fallback structs, constants, and output helpers. This file directly includes `tests.h`, `sys/socket.h`, `netlink.h`.

Integration points: the file participates in strace's testsuite as a compiled C test, AWK normalizer, header, or generator input. It integrates with generated xlat tables, syscall-number selection, test-driver `.test` scripts, and expected-output comparison.

Risks: Primary risks are kernel/architecture feature availability, ABI-width differences, host header drift, permissions, namespace-dependent pid/fd/path rendering, and expected-output brittleness when symbolic constants change.

Test signals: useful validation is the corresponding strace testsuite target under the same basename, comparison of stdout against expected decoder lines, successful compilation under the configured personality/time ABI, and skip behavior when the kernel lacks the syscall or permission. The source was read in full for this report: 33 lines, 858 bytes, sha256 prefix `813c514977e0`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/create_nl_socket.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/create_tmpfile.c -->
# sources/test-tools/strace/tests/create_tmpfile.c

Purpose: `create_tmpfile.c` tests filesystem utility syscall decoding for file creation, temp-file creation, range copy, close_range, sockets/helpers, and synchronization wrappers.

Important APIs/types/functions: local functions include `create_tmpfile`; macros include `O_TMPFILE`; included headers include `tests.h`, `fcntl.h`, `unistd.h`. Kernel/user ABI names observed in the full file include `fcntl`. Prominent constants include `SPDX`, `GPL`, `O_TMPFILE`, `O_DIRECTORY`, `O_EXCL`, `O_CREAT`; prominent struct names include none detected.

Control flow: this file is a shared implementation or variant wrapper; compile-time macros select the syscall number, xlat style, fd/path mode, success behavior, or namespace mode before the included/shared test body runs.

State and persistence behavior: runtime state is intentionally temporary and test-local. The test may allocate tail buffers and/or create temporary files, directories, descriptors, sockets, eventfds, epoll instances, or mount/file handles, then relies on process exit or explicit cleanup for disposal.

Dependencies: strace test harness headers such as `tests.h`, `scno.h`, `print_utils.h`, `pidns.h`, `secontext.h`, local xlat tables, libc headers, and Linux UAPI headers provide syscall numbers, fallback structs, constants, and output helpers. This file directly includes `tests.h`, `fcntl.h`, `unistd.h`.

Integration points: the file participates in strace's testsuite as a compiled C test, AWK normalizer, header, or generator input. It integrates with generated xlat tables, syscall-number selection, test-driver `.test` scripts, and expected-output comparison.

Risks: Primary risks are kernel/architecture feature availability, ABI-width differences, host header drift, permissions, namespace-dependent pid/fd/path rendering, and expected-output brittleness when symbolic constants change.

Test signals: useful validation is the corresponding strace testsuite target under the same basename, comparison of stdout against expected decoder lines, successful compilation under the configured personality/time ABI, and skip behavior when the kernel lacks the syscall or permission. The source was read in full for this report: 46 lines, 977 bytes, sha256 prefix `61c91daa13cf`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/create_tmpfile.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/cur_audit_arch.h -->
# sources/test-tools/strace/tests/cur_audit_arch.h

Purpose: `cur_audit_arch.h` is a shared test header that supplies architecture-specific constants or helper declarations to generated/compiled strace tests.

Important APIs/types/functions: local functions include none detected; macros include `STRACE_TESTS_CUR_AUDIT_ARCH_H`, `CUR_AUDIT_ARCH`, `CUR_AUDIT_ARCH_STR`, `M32_AUDIT_ARCH`, `M32_AUDIT_ARCH_STR`, `M32__NR_gettid`, `PERS0_AUDIT_ARCH`, ... (12 total), `MX32_AUDIT_ARCH`, `MX32_AUDIT_ARCH_STR`, `MX32__NR_gettid`; included headers include `linux/audit.h`. Kernel/user ABI names observed in the full file include none detected. Prominent constants include `AUDIT_ARCH_`, `CUR_AUDIT_ARCH`, `SPDX`, `GPL`, `STRACE_TESTS_CUR_AUDIT_ARCH_H`, `CUR_AUDIT_ARCH_STR`, `PERS0_AUDIT_ARCH`, `PERS0_AUDIT_ARCH_STR`, `M32_AUDIT_ARCH`, ... (46 total), `AUDIT_ARCH_XTENSA`, `HAVE_M32_MPERS`, `HAVE_MX32_MPERS`; prominent struct names include none detected.

Control flow: this file is a shared implementation or variant wrapper; compile-time macros select the syscall number, xlat style, fd/path mode, success behavior, or namespace mode before the included/shared test body runs.

State and persistence behavior: runtime state is intentionally temporary and test-local. Most state lives in stack variables, tail-allocated buffers, compile-time macros, and errno/return-code snapshots.

Dependencies: strace test harness headers such as `tests.h`, `scno.h`, `print_utils.h`, `pidns.h`, `secontext.h`, local xlat tables, libc headers, and Linux UAPI headers provide syscall numbers, fallback structs, constants, and output helpers. This file directly includes `linux/audit.h`.

Integration points: the file participates in strace's testsuite as a compiled C test, AWK normalizer, header, or generator input. It integrates with generated xlat tables, syscall-number selection, test-driver `.test` scripts, and expected-output comparison.

Risks: Primary risks are kernel/architecture feature availability, ABI-width differences, host header drift, permissions, namespace-dependent pid/fd/path rendering, and expected-output brittleness when symbolic constants change.

Test signals: useful validation is the corresponding strace testsuite target under the same basename, comparison of stdout against expected decoder lines, successful compilation under the configured personality/time ABI, and skip behavior when the kernel lacks the syscall or permission. The source was read in full for this report: 212 lines, 7021 bytes, sha256 prefix `bf5b27da3a3a`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/cur_audit_arch.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/delay.c -->
# sources/test-tools/strace/tests/delay.c

Purpose: `delay.c` drives process-control or harness behavior needed by strace tests, such as vfork detach, delay/timing, or sanitized environment execution.

Important APIs/types/functions: local functions include `check_expected`, `check_expectations`, `check_delay`, `do_child`, `run_checks`, `main`, `usecs_from_tv`, `usecs_from_ts`; macros include none detected; included headers include `tests.h`, `errno.h`, `inttypes.h`, `limits.h`, `stdio.h`, `stdint.h`, `stdlib.h`, ... (13 total), `sys/wait.h`, `scno.h`, `kernel_timeval.h`. Kernel/user ABI names observed in the full file include `clock_gettime`. Prominent constants include `SPDX`, `GPL`, `BAD_OTHER`, `DELAY_ENTER_TOO_SHORT`, `DELAY_EXIT_TOO_SHORT`, `DELAY_ENTER_TOO_LONG`, `DELAY_EXIT_TOO_LONG`, `MASK_DELAY_TOO_LONG`, `NULL`, ... (14 total), `WIFEXITED`, `WEXITSTATUS`, `ECHILD`; prominent struct names include `timespec`.

Control flow: `main` builds deterministic arguments, invokes the target syscall or helper sequence, prints the expected strace line with `printf`/test helpers, and exits through the strace test harness.

State and persistence behavior: runtime state is intentionally temporary and test-local. Most state lives in stack variables, tail-allocated buffers, compile-time macros, and errno/return-code snapshots.

Dependencies: strace test harness headers such as `tests.h`, `scno.h`, `print_utils.h`, `pidns.h`, `secontext.h`, local xlat tables, libc headers, and Linux UAPI headers provide syscall numbers, fallback structs, constants, and output helpers. This file directly includes `tests.h`, `errno.h`, `inttypes.h`, `limits.h`, `stdio.h`, `stdint.h`, `stdlib.h`, ... (13 total), `sys/wait.h`, `scno.h`, `kernel_timeval.h`.

Integration points: the file participates in strace's testsuite as a compiled C test, AWK normalizer, header, or generator input. It integrates with generated xlat tables, syscall-number selection, test-driver `.test` scripts, and expected-output comparison.

Risks: Primary risks are kernel/architecture feature availability, ABI-width differences, host header drift, permissions, namespace-dependent pid/fd/path rendering, and expected-output brittleness when symbolic constants change.

Test signals: useful validation is the corresponding strace testsuite target under the same basename, comparison of stdout against expected decoder lines, successful compilation under the configured personality/time ABI, and skip behavior when the kernel lacks the syscall or permission. The source was read in full for this report: 188 lines, 4203 bytes, sha256 prefix `08fdbb9bbc0d`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/delay.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/delete_module.c -->
# sources/test-tools/strace/tests/delete_module.c

Purpose: `delete_module.c` tests delete_module syscall decoder output for module names and delete flags.

Important APIs/types/functions: local functions include `main`; macros include none detected; included headers include `tests.h`, `scno.h`, `stdio.h`, `unistd.h`, `kernel_fcntl.h`, `init_delete_module.h`. Kernel/user ABI names observed in the full file include `delete_module`. Prominent constants include `SPDX`, `GPL`, `ARG_STR`, `F8ILL_KULONG_MASK`, `O_NONBLOCK`, `O_TRUNC`, `PARAM1_LEN`, `PARAM2_LEN`, `PARAM1_BASE`, ... (13 total), `NULL`, `MAX_STRLEN`, `SKIP_MAIN_UNDEFINED`; prominent struct names include none detected.

Control flow: `main` builds deterministic arguments, invokes the target syscall or helper sequence, prints the expected strace line with `printf`/test helpers, and exits through the strace test harness.

State and persistence behavior: runtime state is intentionally temporary and test-local. The test may allocate tail buffers and/or create temporary files, directories, descriptors, sockets, eventfds, epoll instances, or mount/file handles, then relies on process exit or explicit cleanup for disposal.

Dependencies: strace test harness headers such as `tests.h`, `scno.h`, `print_utils.h`, `pidns.h`, `secontext.h`, local xlat tables, libc headers, and Linux UAPI headers provide syscall numbers, fallback structs, constants, and output helpers. This file directly includes `tests.h`, `scno.h`, `stdio.h`, `unistd.h`, `kernel_fcntl.h`, `init_delete_module.h`.

Integration points: the file participates in strace's testsuite as a compiled C test, AWK normalizer, header, or generator input. It integrates with generated xlat tables, syscall-number selection, test-driver `.test` scripts, and expected-output comparison.

Risks: Primary risks are kernel/architecture feature availability, ABI-width differences, host header drift, permissions, namespace-dependent pid/fd/path rendering, and expected-output brittleness when symbolic constants change.

Test signals: useful validation is the corresponding strace testsuite target under the same basename, comparison of stdout against expected decoder lines, successful compilation under the configured personality/time ABI, and skip behavior when the kernel lacks the syscall or permission. The source was read in full for this report: 94 lines, 2580 bytes, sha256 prefix `d8f6741aba69`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/delete_module.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/detach-vfork.c -->
# sources/test-tools/strace/tests/detach-vfork.c

Purpose: `detach-vfork.c` drives process-control or harness behavior needed by strace tests, such as vfork detach, delay/timing, or sanitized environment execution.

Important APIs/types/functions: local functions include `main`; macros include none detected; included headers include `tests.h`, `errno.h`, `signal.h`, `stdio.h`, `stdlib.h`, `unistd.h`, `sys/wait.h`. Kernel/user ABI names observed in the full file include none detected. Prominent constants include `SPDX`, `GPL`, `SIGTERM`, `SIG_IGN`, `EINTR`, `STRACE_EXE`, `WIFEXITED`, `WEXITSTATUS`, `WIFSIGNALED`, `WTERMSIG`; prominent struct names include none detected.

Control flow: `main` builds deterministic arguments, invokes the target syscall or helper sequence, prints the expected strace line with `printf`/test helpers, and exits through the strace test harness.

State and persistence behavior: runtime state is intentionally temporary and test-local. Most state lives in stack variables, tail-allocated buffers, compile-time macros, and errno/return-code snapshots.

Dependencies: strace test harness headers such as `tests.h`, `scno.h`, `print_utils.h`, `pidns.h`, `secontext.h`, local xlat tables, libc headers, and Linux UAPI headers provide syscall numbers, fallback structs, constants, and output helpers. This file directly includes `tests.h`, `errno.h`, `signal.h`, `stdio.h`, `stdlib.h`, `unistd.h`, `sys/wait.h`.

Integration points: the file participates in strace's testsuite as a compiled C test, AWK normalizer, header, or generator input. It integrates with generated xlat tables, syscall-number selection, test-driver `.test` scripts, and expected-output comparison.

Risks: Primary risks are kernel/architecture feature availability, ABI-width differences, host header drift, permissions, namespace-dependent pid/fd/path rendering, and expected-output brittleness when symbolic constants change.

Test signals: useful validation is the corresponding strace testsuite target under the same basename, comparison of stdout against expected decoder lines, successful compilation under the configured personality/time ABI, and skip behavior when the kernel lacks the syscall or permission. The source was read in full for this report: 57 lines, 1087 bytes, sha256 prefix `e7c19453ad76`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/detach-vfork.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/dev--decode-fds-all.c -->
# sources/test-tools/strace/tests/dev--decode-fds-all.c

Purpose: `dev--decode-fds-all.c` checks `--decode-fds` output modes for device, path, socket, pty, and disabled decoding forms.

Important APIs/types/functions: local functions include none detected; macros include `PRINT_DEVNUM`; included headers include `dev-yy.c`. Kernel/user ABI names observed in the full file include none detected. Prominent constants include `PRINT_DEVNUM`; prominent struct names include none detected.

Control flow: this file is a shared implementation or variant wrapper; compile-time macros select the syscall number, xlat style, fd/path mode, success behavior, or namespace mode before the included/shared test body runs.  This is a wrapper/variant file that reuses shared test implementation through local includes: `dev-yy.c`.

State and persistence behavior: runtime state is intentionally temporary and test-local. Most state lives in stack variables, tail-allocated buffers, compile-time macros, and errno/return-code snapshots.

Dependencies: strace test harness headers such as `tests.h`, `scno.h`, `print_utils.h`, `pidns.h`, `secontext.h`, local xlat tables, libc headers, and Linux UAPI headers provide syscall numbers, fallback structs, constants, and output helpers. This file directly includes `dev-yy.c`.

Integration points: the file participates in strace's testsuite as a compiled C test, AWK normalizer, header, or generator input. It integrates with generated xlat tables, syscall-number selection, test-driver `.test` scripts, and expected-output comparison. The variant also exercises path/fd decoding options such as `-P`, `-y`, `-yy`, or `--decode-fds`.

Risks: Primary risks are kernel/architecture feature availability, ABI-width differences, host header drift, permissions, namespace-dependent pid/fd/path rendering, and expected-output brittleness when symbolic constants change.

Test signals: useful validation is the corresponding strace testsuite target under the same basename, comparison of stdout against expected decoder lines, successful compilation under the configured personality/time ABI, and skip behavior when the kernel lacks the syscall or permission. The source was read in full for this report: 2 lines, 43 bytes, sha256 prefix `e165c5142ee8`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/dev--decode-fds-all.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/dev--decode-fds-dev.c -->
# sources/test-tools/strace/tests/dev--decode-fds-dev.c

Purpose: `dev--decode-fds-dev.c` checks `--decode-fds` output modes for device, path, socket, pty, and disabled decoding forms.

Important APIs/types/functions: local functions include none detected; macros include `PRINT_DEVNUM`, `PRINT_AT_FDCWD_PATH`; included headers include `dev-yy.c`. Kernel/user ABI names observed in the full file include none detected. Prominent constants include `PRINT_DEVNUM`, `PRINT_AT_FDCWD_PATH`; prominent struct names include none detected.

Control flow: this file is a shared implementation or variant wrapper; compile-time macros select the syscall number, xlat style, fd/path mode, success behavior, or namespace mode before the included/shared test body runs.  This is a wrapper/variant file that reuses shared test implementation through local includes: `dev-yy.c`.

State and persistence behavior: runtime state is intentionally temporary and test-local. Most state lives in stack variables, tail-allocated buffers, compile-time macros, and errno/return-code snapshots.

Dependencies: strace test harness headers such as `tests.h`, `scno.h`, `print_utils.h`, `pidns.h`, `secontext.h`, local xlat tables, libc headers, and Linux UAPI headers provide syscall numbers, fallback structs, constants, and output helpers. This file directly includes `dev-yy.c`.

Integration points: the file participates in strace's testsuite as a compiled C test, AWK normalizer, header, or generator input. It integrates with generated xlat tables, syscall-number selection, test-driver `.test` scripts, and expected-output comparison. The variant also exercises path/fd decoding options such as `-P`, `-y`, `-yy`, or `--decode-fds`.

Risks: Primary risks are kernel/architecture feature availability, ABI-width differences, host header drift, permissions, namespace-dependent pid/fd/path rendering, and expected-output brittleness when symbolic constants change.

Test signals: useful validation is the corresponding strace testsuite target under the same basename, comparison of stdout against expected decoder lines, successful compilation under the configured personality/time ABI, and skip behavior when the kernel lacks the syscall or permission. The source was read in full for this report: 3 lines, 73 bytes, sha256 prefix `dc07bb135663`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/dev--decode-fds-dev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/dev--decode-fds-none.c -->
# sources/test-tools/strace/tests/dev--decode-fds-none.c

Purpose: `dev--decode-fds-none.c` checks `--decode-fds` output modes for device, path, socket, pty, and disabled decoding forms.

Important APIs/types/functions: local functions include none detected; macros include `PRINT_PATH`; included headers include `dev-yy.c`. Kernel/user ABI names observed in the full file include none detected. Prominent constants include `PRINT_PATH`; prominent struct names include none detected.

Control flow: this file is a shared implementation or variant wrapper; compile-time macros select the syscall number, xlat style, fd/path mode, success behavior, or namespace mode before the included/shared test body runs.  This is a wrapper/variant file that reuses shared test implementation through local includes: `dev-yy.c`.

State and persistence behavior: runtime state is intentionally temporary and test-local. Most state lives in stack variables, tail-allocated buffers, compile-time macros, and errno/return-code snapshots.

Dependencies: strace test harness headers such as `tests.h`, `scno.h`, `print_utils.h`, `pidns.h`, `secontext.h`, local xlat tables, libc headers, and Linux UAPI headers provide syscall numbers, fallback structs, constants, and output helpers. This file directly includes `dev-yy.c`.

Integration points: the file participates in strace's testsuite as a compiled C test, AWK normalizer, header, or generator input. It integrates with generated xlat tables, syscall-number selection, test-driver `.test` scripts, and expected-output comparison. The variant also exercises path/fd decoding options such as `-P`, `-y`, `-yy`, or `--decode-fds`.

Risks: Primary risks are kernel/architecture feature availability, ABI-width differences, host header drift, permissions, namespace-dependent pid/fd/path rendering, and expected-output brittleness when symbolic constants change.

Test signals: useful validation is the corresponding strace testsuite target under the same basename, comparison of stdout against expected decoder lines, successful compilation under the configured personality/time ABI, and skip behavior when the kernel lacks the syscall or permission. The source was read in full for this report: 2 lines, 41 bytes, sha256 prefix `6057595b974e`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/dev--decode-fds-none.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/dev--decode-fds-path.c -->
# sources/test-tools/strace/tests/dev--decode-fds-path.c

Purpose: `dev--decode-fds-path.c` checks `--decode-fds` output modes for device, path, socket, pty, and disabled decoding forms.

Important APIs/types/functions: local functions include none detected; macros include `PRINT_DEVNUM`, `PRINT_AT_FDCWD_PATH`; included headers include `dev-yy.c`. Kernel/user ABI names observed in the full file include none detected. Prominent constants include `PRINT_DEVNUM`, `PRINT_AT_FDCWD_PATH`; prominent struct names include none detected.

Control flow: this file is a shared implementation or variant wrapper; compile-time macros select the syscall number, xlat style, fd/path mode, success behavior, or namespace mode before the included/shared test body runs.  This is a wrapper/variant file that reuses shared test implementation through local includes: `dev-yy.c`.

State and persistence behavior: runtime state is intentionally temporary and test-local. Most state lives in stack variables, tail-allocated buffers, compile-time macros, and errno/return-code snapshots.

Dependencies: strace test harness headers such as `tests.h`, `scno.h`, `print_utils.h`, `pidns.h`, `secontext.h`, local xlat tables, libc headers, and Linux UAPI headers provide syscall numbers, fallback structs, constants, and output helpers. This file directly includes `dev-yy.c`.

Integration points: the file participates in strace's testsuite as a compiled C test, AWK normalizer, header, or generator input. It integrates with generated xlat tables, syscall-number selection, test-driver `.test` scripts, and expected-output comparison. The variant also exercises path/fd decoding options such as `-P`, `-y`, `-yy`, or `--decode-fds`.

Risks: Primary risks are kernel/architecture feature availability, ABI-width differences, host header drift, permissions, namespace-dependent pid/fd/path rendering, and expected-output brittleness when symbolic constants change.

Test signals: useful validation is the corresponding strace testsuite target under the same basename, comparison of stdout against expected decoder lines, successful compilation under the configured personality/time ABI, and skip behavior when the kernel lacks the syscall or permission. The source was read in full for this report: 3 lines, 73 bytes, sha256 prefix `fc04648e5f31`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/dev--decode-fds-path.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/dev--decode-fds-socket.c -->
# sources/test-tools/strace/tests/dev--decode-fds-socket.c

Purpose: `dev--decode-fds-socket.c` checks `--decode-fds` output modes for device, path, socket, pty, and disabled decoding forms.

Important APIs/types/functions: local functions include none detected; macros include none detected; included headers include `dev--decode-fds-none.c`. Kernel/user ABI names observed in the full file include none detected. Prominent constants include none detected; prominent struct names include none detected.

Control flow: this file is a shared implementation or variant wrapper; compile-time macros select the syscall number, xlat style, fd/path mode, success behavior, or namespace mode before the included/shared test body runs.  This is a wrapper/variant file that reuses shared test implementation through local includes: `dev--decode-fds-none.c`.

State and persistence behavior: runtime state is intentionally temporary and test-local. Most state lives in stack variables, tail-allocated buffers, compile-time macros, and errno/return-code snapshots.

Dependencies: strace test harness headers such as `tests.h`, `scno.h`, `print_utils.h`, `pidns.h`, `secontext.h`, local xlat tables, libc headers, and Linux UAPI headers provide syscall numbers, fallback structs, constants, and output helpers. This file directly includes `dev--decode-fds-none.c`.

Integration points: the file participates in strace's testsuite as a compiled C test, AWK normalizer, header, or generator input. It integrates with generated xlat tables, syscall-number selection, test-driver `.test` scripts, and expected-output comparison. The variant also exercises path/fd decoding options such as `-P`, `-y`, `-yy`, or `--decode-fds`.

Risks: Primary risks are kernel/architecture feature availability, ABI-width differences, host header drift, permissions, namespace-dependent pid/fd/path rendering, and expected-output brittleness when symbolic constants change.

Test signals: useful validation is the corresponding strace testsuite target under the same basename, comparison of stdout against expected decoder lines, successful compilation under the configured personality/time ABI, and skip behavior when the kernel lacks the syscall or permission. The source was read in full for this report: 1 lines, 34 bytes, sha256 prefix `29c269f013b1`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/dev--decode-fds-socket.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/dev-pty-yy.c -->
# sources/test-tools/strace/tests/dev-pty-yy.c

Purpose: `dev-pty-yy.c` checks `--decode-fds` output modes for device, path, socket, pty, and disabled decoding forms.

Important APIs/types/functions: local functions include `main`; macros include none detected; included headers include `tests.h`, `stdio.h`, `stdlib.h`, `unistd.h`, `fcntl.h`, `sys/ioctl.h`. Kernel/user ABI names observed in the full file include `ioctl`, `fcntl`. Prominent constants include `SPDX`, `GPL`, `O_RDWR`, `O_NOCTTY`, `NULL`; prominent struct names include none detected.

Control flow: `main` builds deterministic arguments, invokes the target syscall or helper sequence, prints the expected strace line with `printf`/test helpers, and exits through the strace test harness.

State and persistence behavior: runtime state is intentionally temporary and test-local. The test may allocate tail buffers and/or create temporary files, directories, descriptors, sockets, eventfds, epoll instances, or mount/file handles, then relies on process exit or explicit cleanup for disposal.

Dependencies: strace test harness headers such as `tests.h`, `scno.h`, `print_utils.h`, `pidns.h`, `secontext.h`, local xlat tables, libc headers, and Linux UAPI headers provide syscall numbers, fallback structs, constants, and output helpers. This file directly includes `tests.h`, `stdio.h`, `stdlib.h`, `unistd.h`, `fcntl.h`, `sys/ioctl.h`.

Integration points: the file participates in strace's testsuite as a compiled C test, AWK normalizer, header, or generator input. It integrates with generated xlat tables, syscall-number selection, test-driver `.test` scripts, and expected-output comparison. The variant also exercises path/fd decoding options such as `-P`, `-y`, `-yy`, or `--decode-fds`.

Risks: Primary risks are kernel/architecture feature availability, ABI-width differences, host header drift, permissions, namespace-dependent pid/fd/path rendering, and expected-output brittleness when symbolic constants change.

Test signals: useful validation is the corresponding strace testsuite target under the same basename, comparison of stdout against expected decoder lines, successful compilation under the configured personality/time ABI, and skip behavior when the kernel lacks the syscall or permission. The source was read in full for this report: 40 lines, 860 bytes, sha256 prefix `052cc3a3b8d6`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/dev-pty-yy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/dev-yy.c -->
# sources/test-tools/strace/tests/dev-yy.c

Purpose: `dev-yy.c` checks `--decode-fds` output modes for device, path, socket, pty, and disabled decoding forms.

Important APIs/types/functions: local functions include `main`; macros include `PRINT_PATH`, `PRINT_DEVNUM`, `PRINT_AT_FDCWD_PATH`, `DEV_FMT`; included headers include `tests.h`, `stdio.h`, `unistd.h`, `scno.h`, `linux/fcntl.h`, `sys/sysmacros.h`. Kernel/user ABI names observed in the full file include `fcntl`. Prominent constants include `SPDX`, `GPL`, `PRINT_PATH`, `PRINT_DEVNUM`, `PRINT_AT_FDCWD_PATH`, `DEV_FMT`, `O_PATH`, `ARRAY_SIZE`, `AT_FDCWD`, `O_RDONLY`, `SKIP_MAIN_UNDEFINED`; prominent struct names include none detected.

Control flow: `main` builds deterministic arguments, invokes the target syscall or helper sequence, prints the expected strace line with `printf`/test helpers, and exits through the strace test harness.

State and persistence behavior: runtime state is intentionally temporary and test-local. Most state lives in stack variables, tail-allocated buffers, compile-time macros, and errno/return-code snapshots.

Dependencies: strace test harness headers such as `tests.h`, `scno.h`, `print_utils.h`, `pidns.h`, `secontext.h`, local xlat tables, libc headers, and Linux UAPI headers provide syscall numbers, fallback structs, constants, and output helpers. This file directly includes `tests.h`, `stdio.h`, `unistd.h`, `scno.h`, `linux/fcntl.h`, `sys/sysmacros.h`.

Integration points: the file participates in strace's testsuite as a compiled C test, AWK normalizer, header, or generator input. It integrates with generated xlat tables, syscall-number selection, test-driver `.test` scripts, and expected-output comparison. The variant also exercises path/fd decoding options such as `-P`, `-y`, `-yy`, or `--decode-fds`.

Risks: Primary risks are kernel/architecture feature availability, ABI-width differences, host header drift, permissions, namespace-dependent pid/fd/path rendering, and expected-output brittleness when symbolic constants change.

Test signals: useful validation is the corresponding strace testsuite target under the same basename, comparison of stdout against expected decoder lines, successful compilation under the configured personality/time ABI, and skip behavior when the kernel lacks the syscall or permission. The source was read in full for this report: 129 lines, 2410 bytes, sha256 prefix `41a922f7f2a5`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/dev-yy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/dirfd.c -->
# sources/test-tools/strace/tests/dirfd.c

Purpose: `dirfd.c` tests filesystem utility syscall decoding for file creation, temp-file creation, range copy, close_range, sockets/helpers, and synchronization wrappers.

Important APIs/types/functions: local functions include `get_dir_fd`, `get_fd_path`; macros include none detected; included headers include `tests.h`, `dirent.h`, `limits.h`, `stdlib.h`, `unistd.h`, `xmalloc.h`. Kernel/user ABI names observed in the full file include none detected. Prominent constants include `SPDX`, `GPL`, `DIR`, `NULL`, `PATH_MAX`; prominent struct names include none detected.

Control flow: this file is a shared implementation or variant wrapper; compile-time macros select the syscall number, xlat style, fd/path mode, success behavior, or namespace mode before the included/shared test body runs.

State and persistence behavior: runtime state is intentionally temporary and test-local. Most state lives in stack variables, tail-allocated buffers, compile-time macros, and errno/return-code snapshots.

Dependencies: strace test harness headers such as `tests.h`, `scno.h`, `print_utils.h`, `pidns.h`, `secontext.h`, local xlat tables, libc headers, and Linux UAPI headers provide syscall numbers, fallback structs, constants, and output helpers. This file directly includes `tests.h`, `dirent.h`, `limits.h`, `stdlib.h`, `unistd.h`, `xmalloc.h`.

Integration points: the file participates in strace's testsuite as a compiled C test, AWK normalizer, header, or generator input. It integrates with generated xlat tables, syscall-number selection, test-driver `.test` scripts, and expected-output comparison.

Risks: Primary risks are kernel/architecture feature availability, ABI-width differences, host header drift, permissions, namespace-dependent pid/fd/path rendering, and expected-output brittleness when symbolic constants change.

Test signals: useful validation is the corresponding strace testsuite target under the same basename, comparison of stdout against expected decoder lines, successful compilation under the configured personality/time ABI, and skip behavior when the kernel lacks the syscall or permission. The source was read in full for this report: 43 lines, 830 bytes, sha256 prefix `ef11a52be3f0`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/dirfd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/dup-P.c -->
# sources/test-tools/strace/tests/dup-P.c

Purpose: `dup-P.c` validates dup/dup2/dup3 decoder output, fd filtering, path decoding, and trace-fd qualifier behavior.

Important APIs/types/functions: local functions include none detected; macros include `PATH_TRACING`, `SKIP_IF_PROC_IS_UNAVAILABLE`; included headers include `dup.c`. Kernel/user ABI names observed in the full file include `dup`. Prominent constants include `PATH_TRACING`, `SKIP_IF_PROC_IS_UNAVAILABLE`; prominent struct names include none detected.

Control flow: this file is a shared implementation or variant wrapper; compile-time macros select the syscall number, xlat style, fd/path mode, success behavior, or namespace mode before the included/shared test body runs. The test cases deliberately create, duplicate, and filter file descriptors so strace can prove descriptor qualifiers and decoded paths remain attached to the expected fd numbers.  This is a wrapper/variant file that reuses shared test implementation through local includes: `dup.c`.

State and persistence behavior: runtime state is intentionally temporary and test-local. Most state lives in stack variables, tail-allocated buffers, compile-time macros, and errno/return-code snapshots.

Dependencies: strace test harness headers such as `tests.h`, `scno.h`, `print_utils.h`, `pidns.h`, `secontext.h`, local xlat tables, libc headers, and Linux UAPI headers provide syscall numbers, fallback structs, constants, and output helpers. This file directly includes `dup.c`.

Integration points: the file participates in strace's testsuite as a compiled C test, AWK normalizer, header, or generator input. It integrates with generated xlat tables, syscall-number selection, test-driver `.test` scripts, and expected-output comparison. The variant also exercises path/fd decoding options such as `-P`, `-y`, `-yy`, or `--decode-fds`.

Risks: Primary risks are kernel/architecture feature availability, ABI-width differences, host header drift, permissions, namespace-dependent pid/fd/path rendering, and expected-output brittleness when symbolic constants change.

Test signals: useful validation is the corresponding strace testsuite target under the same basename, comparison of stdout against expected decoder lines, successful compilation under the configured personality/time ABI, and skip behavior when the kernel lacks the syscall or permission. The source was read in full for this report: 4 lines, 115 bytes, sha256 prefix `1ad9cded2977`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/dup-P.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/dup-trace-fds-0-9.c -->
# sources/test-tools/strace/tests/dup-trace-fds-0-9.c

Purpose: `dup-trace-fds-0-9.c` validates dup/dup2/dup3 decoder output, fd filtering, path decoding, and trace-fd qualifier behavior.

Important APIs/types/functions: local functions include none detected; macros include `TRACE_FDS`, `TRACE_FD_0`, `TRACE_FD_9`; included headers include `dup.c`. Kernel/user ABI names observed in the full file include `dup`. Prominent constants include `TRACE_FDS`, `TRACE_FD_0`, `TRACE_FD_9`; prominent struct names include none detected.

Control flow: this file is a shared implementation or variant wrapper; compile-time macros select the syscall number, xlat style, fd/path mode, success behavior, or namespace mode before the included/shared test body runs. The test cases deliberately create, duplicate, and filter file descriptors so strace can prove descriptor qualifiers and decoded paths remain attached to the expected fd numbers.  This is a wrapper/variant file that reuses shared test implementation through local includes: `dup.c`.

State and persistence behavior: runtime state is intentionally temporary and test-local. Most state lives in stack variables, tail-allocated buffers, compile-time macros, and errno/return-code snapshots.

Dependencies: strace test harness headers such as `tests.h`, `scno.h`, `print_utils.h`, `pidns.h`, `secontext.h`, local xlat tables, libc headers, and Linux UAPI headers provide syscall numbers, fallback structs, constants, and output helpers. This file directly includes `dup.c`.

Integration points: the file participates in strace's testsuite as a compiled C test, AWK normalizer, header, or generator input. It integrates with generated xlat tables, syscall-number selection, test-driver `.test` scripts, and expected-output comparison.

Risks: Primary risks are kernel/architecture feature availability, ABI-width differences, host header drift, permissions, namespace-dependent pid/fd/path rendering, and expected-output brittleness when symbolic constants change.

Test signals: useful validation is the corresponding strace testsuite target under the same basename, comparison of stdout against expected decoder lines, successful compilation under the configured personality/time ABI, and skip behavior when the kernel lacks the syscall or permission. The source was read in full for this report: 4 lines, 80 bytes, sha256 prefix `b96d3cf79bfd`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/dup-trace-fds-0-9.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/dup-trace-fds-0-P.c -->
# sources/test-tools/strace/tests/dup-trace-fds-0-P.c

Purpose: `dup-trace-fds-0-P.c` validates dup/dup2/dup3 decoder output, fd filtering, path decoding, and trace-fd qualifier behavior.

Important APIs/types/functions: local functions include none detected; macros include `TRACE_FDS`, `TRACE_FD_0`; included headers include `dup-P.c`. Kernel/user ABI names observed in the full file include `dup`. Prominent constants include `TRACE_FDS`, `TRACE_FD_0`; prominent struct names include none detected.

Control flow: this file is a shared implementation or variant wrapper; compile-time macros select the syscall number, xlat style, fd/path mode, success behavior, or namespace mode before the included/shared test body runs. The test cases deliberately create, duplicate, and filter file descriptors so strace can prove descriptor qualifiers and decoded paths remain attached to the expected fd numbers.  This is a wrapper/variant file that reuses shared test implementation through local includes: `dup-P.c`.

State and persistence behavior: runtime state is intentionally temporary and test-local. Most state lives in stack variables, tail-allocated buffers, compile-time macros, and errno/return-code snapshots.

Dependencies: strace test harness headers such as `tests.h`, `scno.h`, `print_utils.h`, `pidns.h`, `secontext.h`, local xlat tables, libc headers, and Linux UAPI headers provide syscall numbers, fallback structs, constants, and output helpers. This file directly includes `dup-P.c`.

Integration points: the file participates in strace's testsuite as a compiled C test, AWK normalizer, header, or generator input. It integrates with generated xlat tables, syscall-number selection, test-driver `.test` scripts, and expected-output comparison. The variant also exercises path/fd decoding options such as `-P`, `-y`, `-yy`, or `--decode-fds`.

Risks: Primary risks are kernel/architecture feature availability, ABI-width differences, host header drift, permissions, namespace-dependent pid/fd/path rendering, and expected-output brittleness when symbolic constants change.

Test signals: useful validation is the corresponding strace testsuite target under the same basename, comparison of stdout against expected decoder lines, successful compilation under the configured personality/time ABI, and skip behavior when the kernel lacks the syscall or permission. The source was read in full for this report: 3 lines, 65 bytes, sha256 prefix `94f523ce5b5b`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/dup-trace-fds-0-P.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/dup-trace-fds-0.c -->
# sources/test-tools/strace/tests/dup-trace-fds-0.c

Purpose: `dup-trace-fds-0.c` validates dup/dup2/dup3 decoder output, fd filtering, path decoding, and trace-fd qualifier behavior.

Important APIs/types/functions: local functions include none detected; macros include `TRACE_FDS`, `TRACE_FD_0`; included headers include `dup.c`. Kernel/user ABI names observed in the full file include `dup`. Prominent constants include `TRACE_FDS`, `TRACE_FD_0`; prominent struct names include none detected.

Control flow: this file is a shared implementation or variant wrapper; compile-time macros select the syscall number, xlat style, fd/path mode, success behavior, or namespace mode before the included/shared test body runs. The test cases deliberately create, duplicate, and filter file descriptors so strace can prove descriptor qualifiers and decoded paths remain attached to the expected fd numbers.  This is a wrapper/variant file that reuses shared test implementation through local includes: `dup.c`.

State and persistence behavior: runtime state is intentionally temporary and test-local. Most state lives in stack variables, tail-allocated buffers, compile-time macros, and errno/return-code snapshots.

Dependencies: strace test harness headers such as `tests.h`, `scno.h`, `print_utils.h`, `pidns.h`, `secontext.h`, local xlat tables, libc headers, and Linux UAPI headers provide syscall numbers, fallback structs, constants, and output helpers. This file directly includes `dup.c`.

Integration points: the file participates in strace's testsuite as a compiled C test, AWK normalizer, header, or generator input. It integrates with generated xlat tables, syscall-number selection, test-driver `.test` scripts, and expected-output comparison.

Risks: Primary risks are kernel/architecture feature availability, ABI-width differences, host header drift, permissions, namespace-dependent pid/fd/path rendering, and expected-output brittleness when symbolic constants change.

Test signals: useful validation is the corresponding strace testsuite target under the same basename, comparison of stdout against expected decoder lines, successful compilation under the configured personality/time ABI, and skip behavior when the kernel lacks the syscall or permission. The source was read in full for this report: 3 lines, 59 bytes, sha256 prefix `255aa6e469e9`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/dup-trace-fds-0.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/dup-trace-fds-not-9.c -->
# sources/test-tools/strace/tests/dup-trace-fds-not-9.c

Purpose: `dup-trace-fds-not-9.c` validates dup/dup2/dup3 decoder output, fd filtering, path decoding, and trace-fd qualifier behavior.

Important APIs/types/functions: local functions include none detected; macros include `TRACE_FDS`, `TRACE_FD_0`, `TRACE_OTHER_FDS`; included headers include `dup.c`. Kernel/user ABI names observed in the full file include `dup`. Prominent constants include `TRACE_FDS`, `TRACE_FD_0`, `TRACE_OTHER_FDS`; prominent struct names include none detected.

Control flow: this file is a shared implementation or variant wrapper; compile-time macros select the syscall number, xlat style, fd/path mode, success behavior, or namespace mode before the included/shared test body runs. The test cases deliberately create, duplicate, and filter file descriptors so strace can prove descriptor qualifiers and decoded paths remain attached to the expected fd numbers.  This is a wrapper/variant file that reuses shared test implementation through local includes: `dup.c`.

State and persistence behavior: runtime state is intentionally temporary and test-local. Most state lives in stack variables, tail-allocated buffers, compile-time macros, and errno/return-code snapshots.

Dependencies: strace test harness headers such as `tests.h`, `scno.h`, `print_utils.h`, `pidns.h`, `secontext.h`, local xlat tables, libc headers, and Linux UAPI headers provide syscall numbers, fallback structs, constants, and output helpers. This file directly includes `dup.c`.

Integration points: the file participates in strace's testsuite as a compiled C test, AWK normalizer, header, or generator input. It integrates with generated xlat tables, syscall-number selection, test-driver `.test` scripts, and expected-output comparison.

Risks: Primary risks are kernel/architecture feature availability, ABI-width differences, host header drift, permissions, namespace-dependent pid/fd/path rendering, and expected-output brittleness when symbolic constants change.

Test signals: useful validation is the corresponding strace testsuite target under the same basename, comparison of stdout against expected decoder lines, successful compilation under the configured personality/time ABI, and skip behavior when the kernel lacks the syscall or permission. The source was read in full for this report: 4 lines, 85 bytes, sha256 prefix `4915a96e282b`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/dup-trace-fds-not-9.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/dup-y.c -->
# sources/test-tools/strace/tests/dup-y.c

Purpose: `dup-y.c` validates dup/dup2/dup3 decoder output, fd filtering, path decoding, and trace-fd qualifier behavior.

Important APIs/types/functions: local functions include none detected; macros include `FD0_PATH`, `FD9_PATH`, `SKIP_IF_PROC_IS_UNAVAILABLE`; included headers include `dup.c`. Kernel/user ABI names observed in the full file include `dup`. Prominent constants include `FD0_PATH`, `FD9_PATH`, `SKIP_IF_PROC_IS_UNAVAILABLE`; prominent struct names include none detected.

Control flow: this file is a shared implementation or variant wrapper; compile-time macros select the syscall number, xlat style, fd/path mode, success behavior, or namespace mode before the included/shared test body runs. The test cases deliberately create, duplicate, and filter file descriptors so strace can prove descriptor qualifiers and decoded paths remain attached to the expected fd numbers.  This is a wrapper/variant file that reuses shared test implementation through local includes: `dup.c`.

State and persistence behavior: runtime state is intentionally temporary and test-local. Most state lives in stack variables, tail-allocated buffers, compile-time macros, and errno/return-code snapshots.

Dependencies: strace test harness headers such as `tests.h`, `scno.h`, `print_utils.h`, `pidns.h`, `secontext.h`, local xlat tables, libc headers, and Linux UAPI headers provide syscall numbers, fallback structs, constants, and output helpers. This file directly includes `dup.c`.

Integration points: the file participates in strace's testsuite as a compiled C test, AWK normalizer, header, or generator input. It integrates with generated xlat tables, syscall-number selection, test-driver `.test` scripts, and expected-output comparison. The variant also exercises path/fd decoding options such as `-P`, `-y`, `-yy`, or `--decode-fds`.

Risks: Primary risks are kernel/architecture feature availability, ABI-width differences, host header drift, permissions, namespace-dependent pid/fd/path rendering, and expected-output brittleness when symbolic constants change.

Test signals: useful validation is the corresponding strace testsuite target under the same basename, comparison of stdout against expected decoder lines, successful compilation under the configured personality/time ABI, and skip behavior when the kernel lacks the syscall or permission. The source was read in full for this report: 5 lines, 154 bytes, sha256 prefix `3cc44092724a`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/dup-y.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/dup-yy.c -->
# sources/test-tools/strace/tests/dup-yy.c

Purpose: `dup-yy.c` validates dup/dup2/dup3 decoder output, fd filtering, path decoding, and trace-fd qualifier behavior.

Important APIs/types/functions: local functions include none detected; macros include `FD0_PATH`, `FD9_PATH`, `SKIP_IF_PROC_IS_UNAVAILABLE`; included headers include `dup.c`. Kernel/user ABI names observed in the full file include `dup`. Prominent constants include `FD0_PATH`, `FD9_PATH`, `SKIP_IF_PROC_IS_UNAVAILABLE`; prominent struct names include none detected.

Control flow: this file is a shared implementation or variant wrapper; compile-time macros select the syscall number, xlat style, fd/path mode, success behavior, or namespace mode before the included/shared test body runs. The test cases deliberately create, duplicate, and filter file descriptors so strace can prove descriptor qualifiers and decoded paths remain attached to the expected fd numbers.  This is a wrapper/variant file that reuses shared test implementation through local includes: `dup.c`.

State and persistence behavior: runtime state is intentionally temporary and test-local. Most state lives in stack variables, tail-allocated buffers, compile-time macros, and errno/return-code snapshots.

Dependencies: strace test harness headers such as `tests.h`, `scno.h`, `print_utils.h`, `pidns.h`, `secontext.h`, local xlat tables, libc headers, and Linux UAPI headers provide syscall numbers, fallback structs, constants, and output helpers. This file directly includes `dup.c`.

Integration points: the file participates in strace's testsuite as a compiled C test, AWK normalizer, header, or generator input. It integrates with generated xlat tables, syscall-number selection, test-driver `.test` scripts, and expected-output comparison. The variant also exercises path/fd decoding options such as `-P`, `-y`, `-yy`, or `--decode-fds`.

Risks: Primary risks are kernel/architecture feature availability, ABI-width differences, host header drift, permissions, namespace-dependent pid/fd/path rendering, and expected-output brittleness when symbolic constants change.

Test signals: useful validation is the corresponding strace testsuite target under the same basename, comparison of stdout against expected decoder lines, successful compilation under the configured personality/time ABI, and skip behavior when the kernel lacks the syscall or permission. The source was read in full for this report: 5 lines, 174 bytes, sha256 prefix `23fa1e31f457`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/dup-yy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/dup.c -->
# sources/test-tools/strace/tests/dup.c

Purpose: `dup.c` validates dup/dup2/dup3 decoder output, fd filtering, path decoding, and trace-fd qualifier behavior.

Important APIs/types/functions: local functions include `k_dup`, `main`; macros include `FD0_PATH`, `FD9_PATH`, `SKIP_IF_PROC_IS_UNAVAILABLE`, `TRACE_FDS`, `PATH_TRACING`, `TRACE_FD_0`, `TRACE_OTHER_FDS`, `TRACE_FD_9`; included headers include `tests.h`, `scno.h`, `stdio.h`, `unistd.h`. Kernel/user ABI names observed in the full file include `dup`. Prominent constants include `SPDX`, `GPL`, `FD0_PATH`, `FD9_PATH`, `SKIP_IF_PROC_IS_UNAVAILABLE`, `TRACE_FDS`, `PATH_TRACING`, `TRACE_FD_0`, `TRACE_OTHER_FDS`, `TRACE_FD_9`; prominent struct names include none detected.

Control flow: `main` builds deterministic arguments, invokes the target syscall or helper sequence, prints the expected strace line with `printf`/test helpers, and exits through the strace test harness. The test cases deliberately create, duplicate, and filter file descriptors so strace can prove descriptor qualifiers and decoded paths remain attached to the expected fd numbers.

State and persistence behavior: runtime state is intentionally temporary and test-local. Most state lives in stack variables, tail-allocated buffers, compile-time macros, and errno/return-code snapshots.

Dependencies: strace test harness headers such as `tests.h`, `scno.h`, `print_utils.h`, `pidns.h`, `secontext.h`, local xlat tables, libc headers, and Linux UAPI headers provide syscall numbers, fallback structs, constants, and output helpers. This file directly includes `tests.h`, `scno.h`, `stdio.h`, `unistd.h`.

Integration points: the file participates in strace's testsuite as a compiled C test, AWK normalizer, header, or generator input. It integrates with generated xlat tables, syscall-number selection, test-driver `.test` scripts, and expected-output comparison.

Risks: Primary risks are kernel/architecture feature availability, ABI-width differences, host header drift, permissions, namespace-dependent pid/fd/path rendering, and expected-output brittleness when symbolic constants change.

Test signals: useful validation is the corresponding strace testsuite target under the same basename, comparison of stdout against expected decoder lines, successful compilation under the configured personality/time ABI, and skip behavior when the kernel lacks the syscall or permission. The source was read in full for this report: 87 lines, 1720 bytes, sha256 prefix `a83a2d7d028a`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/dup.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/dup2-P.c -->
# sources/test-tools/strace/tests/dup2-P.c

Purpose: `dup2-P.c` validates dup/dup2/dup3 decoder output, fd filtering, path decoding, and trace-fd qualifier behavior.

Important APIs/types/functions: local functions include none detected; macros include `PATH_TRACING`, `SKIP_IF_PROC_IS_UNAVAILABLE`; included headers include `dup2.c`. Kernel/user ABI names observed in the full file include `dup2`. Prominent constants include `PATH_TRACING`, `SKIP_IF_PROC_IS_UNAVAILABLE`; prominent struct names include none detected.

Control flow: this file is a shared implementation or variant wrapper; compile-time macros select the syscall number, xlat style, fd/path mode, success behavior, or namespace mode before the included/shared test body runs. The test cases deliberately create, duplicate, and filter file descriptors so strace can prove descriptor qualifiers and decoded paths remain attached to the expected fd numbers.  This is a wrapper/variant file that reuses shared test implementation through local includes: `dup2.c`.

State and persistence behavior: runtime state is intentionally temporary and test-local. Most state lives in stack variables, tail-allocated buffers, compile-time macros, and errno/return-code snapshots.

Dependencies: strace test harness headers such as `tests.h`, `scno.h`, `print_utils.h`, `pidns.h`, `secontext.h`, local xlat tables, libc headers, and Linux UAPI headers provide syscall numbers, fallback structs, constants, and output helpers. This file directly includes `dup2.c`.

Integration points: the file participates in strace's testsuite as a compiled C test, AWK normalizer, header, or generator input. It integrates with generated xlat tables, syscall-number selection, test-driver `.test` scripts, and expected-output comparison. The variant also exercises path/fd decoding options such as `-P`, `-y`, `-yy`, or `--decode-fds`.

Risks: Primary risks are kernel/architecture feature availability, ABI-width differences, host header drift, permissions, namespace-dependent pid/fd/path rendering, and expected-output brittleness when symbolic constants change.

Test signals: useful validation is the corresponding strace testsuite target under the same basename, comparison of stdout against expected decoder lines, successful compilation under the configured personality/time ABI, and skip behavior when the kernel lacks the syscall or permission. The source was read in full for this report: 4 lines, 116 bytes, sha256 prefix `006887e0ae6a`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/dup2-P.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/dup2-e-fd-0-9.c -->
# sources/test-tools/strace/tests/dup2-e-fd-0-9.c

Purpose: `dup2-e-fd-0-9.c` validates dup/dup2/dup3 decoder output, fd filtering, path decoding, and trace-fd qualifier behavior.

Important APIs/types/functions: local functions include none detected; macros include `TRACE_FDS`, `TRACE_FD_0`, `TRACE_FD_9`; included headers include `dup2.c`. Kernel/user ABI names observed in the full file include `dup2`. Prominent constants include `TRACE_FDS`, `TRACE_FD_0`, `TRACE_FD_9`; prominent struct names include none detected.

Control flow: this file is a shared implementation or variant wrapper; compile-time macros select the syscall number, xlat style, fd/path mode, success behavior, or namespace mode before the included/shared test body runs. The test cases deliberately create, duplicate, and filter file descriptors so strace can prove descriptor qualifiers and decoded paths remain attached to the expected fd numbers.  This is a wrapper/variant file that reuses shared test implementation through local includes: `dup2.c`.

State and persistence behavior: runtime state is intentionally temporary and test-local. Most state lives in stack variables, tail-allocated buffers, compile-time macros, and errno/return-code snapshots.

Dependencies: strace test harness headers such as `tests.h`, `scno.h`, `print_utils.h`, `pidns.h`, `secontext.h`, local xlat tables, libc headers, and Linux UAPI headers provide syscall numbers, fallback structs, constants, and output helpers. This file directly includes `dup2.c`.

Integration points: the file participates in strace's testsuite as a compiled C test, AWK normalizer, header, or generator input. It integrates with generated xlat tables, syscall-number selection, test-driver `.test` scripts, and expected-output comparison.

Risks: Primary risks are kernel/architecture feature availability, ABI-width differences, host header drift, permissions, namespace-dependent pid/fd/path rendering, and expected-output brittleness when symbolic constants change.

Test signals: useful validation is the corresponding strace testsuite target under the same basename, comparison of stdout against expected decoder lines, successful compilation under the configured personality/time ABI, and skip behavior when the kernel lacks the syscall or permission. The source was read in full for this report: 4 lines, 81 bytes, sha256 prefix `96c4262830c4`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/dup2-e-fd-0-9.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/dup2-e-fd-0-P.c -->
# sources/test-tools/strace/tests/dup2-e-fd-0-P.c

Purpose: `dup2-e-fd-0-P.c` validates dup/dup2/dup3 decoder output, fd filtering, path decoding, and trace-fd qualifier behavior.

Important APIs/types/functions: local functions include none detected; macros include `TRACE_FDS`, `TRACE_FD_0`, `TRACE_FD_9`; included headers include `dup2-P.c`. Kernel/user ABI names observed in the full file include `dup2`. Prominent constants include `TRACE_FDS`, `TRACE_FD_0`, `TRACE_FD_9`; prominent struct names include none detected.

Control flow: this file is a shared implementation or variant wrapper; compile-time macros select the syscall number, xlat style, fd/path mode, success behavior, or namespace mode before the included/shared test body runs. The test cases deliberately create, duplicate, and filter file descriptors so strace can prove descriptor qualifiers and decoded paths remain attached to the expected fd numbers.  This is a wrapper/variant file that reuses shared test implementation through local includes: `dup2-P.c`.

State and persistence behavior: runtime state is intentionally temporary and test-local. Most state lives in stack variables, tail-allocated buffers, compile-time macros, and errno/return-code snapshots.

Dependencies: strace test harness headers such as `tests.h`, `scno.h`, `print_utils.h`, `pidns.h`, `secontext.h`, local xlat tables, libc headers, and Linux UAPI headers provide syscall numbers, fallback structs, constants, and output helpers. This file directly includes `dup2-P.c`.

Integration points: the file participates in strace's testsuite as a compiled C test, AWK normalizer, header, or generator input. It integrates with generated xlat tables, syscall-number selection, test-driver `.test` scripts, and expected-output comparison. The variant also exercises path/fd decoding options such as `-P`, `-y`, `-yy`, or `--decode-fds`.

Risks: Primary risks are kernel/architecture feature availability, ABI-width differences, host header drift, permissions, namespace-dependent pid/fd/path rendering, and expected-output brittleness when symbolic constants change.

Test signals: useful validation is the corresponding strace testsuite target under the same basename, comparison of stdout against expected decoder lines, successful compilation under the configured personality/time ABI, and skip behavior when the kernel lacks the syscall or permission. The source was read in full for this report: 4 lines, 83 bytes, sha256 prefix `ef51b515a2fe`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/dup2-e-fd-0-P.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/dup2-e-fd-0.c -->
# sources/test-tools/strace/tests/dup2-e-fd-0.c

Purpose: `dup2-e-fd-0.c` validates dup/dup2/dup3 decoder output, fd filtering, path decoding, and trace-fd qualifier behavior.

Important APIs/types/functions: local functions include none detected; macros include `TRACE_FDS`, `TRACE_FD_0`; included headers include `dup2.c`. Kernel/user ABI names observed in the full file include `dup2`. Prominent constants include `TRACE_FDS`, `TRACE_FD_0`; prominent struct names include none detected.

Control flow: this file is a shared implementation or variant wrapper; compile-time macros select the syscall number, xlat style, fd/path mode, success behavior, or namespace mode before the included/shared test body runs. The test cases deliberately create, duplicate, and filter file descriptors so strace can prove descriptor qualifiers and decoded paths remain attached to the expected fd numbers.  This is a wrapper/variant file that reuses shared test implementation through local includes: `dup2.c`.

State and persistence behavior: runtime state is intentionally temporary and test-local. Most state lives in stack variables, tail-allocated buffers, compile-time macros, and errno/return-code snapshots.

Dependencies: strace test harness headers such as `tests.h`, `scno.h`, `print_utils.h`, `pidns.h`, `secontext.h`, local xlat tables, libc headers, and Linux UAPI headers provide syscall numbers, fallback structs, constants, and output helpers. This file directly includes `dup2.c`.

Integration points: the file participates in strace's testsuite as a compiled C test, AWK normalizer, header, or generator input. It integrates with generated xlat tables, syscall-number selection, test-driver `.test` scripts, and expected-output comparison.

Risks: Primary risks are kernel/architecture feature availability, ABI-width differences, host header drift, permissions, namespace-dependent pid/fd/path rendering, and expected-output brittleness when symbolic constants change.

Test signals: useful validation is the corresponding strace testsuite target under the same basename, comparison of stdout against expected decoder lines, successful compilation under the configured personality/time ABI, and skip behavior when the kernel lacks the syscall or permission. The source was read in full for this report: 3 lines, 60 bytes, sha256 prefix `b95d5c27f940`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/dup2-e-fd-0.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/dup2-e-fd-not-9.c -->
# sources/test-tools/strace/tests/dup2-e-fd-not-9.c

Purpose: `dup2-e-fd-not-9.c` validates dup/dup2/dup3 decoder output, fd filtering, path decoding, and trace-fd qualifier behavior.

Important APIs/types/functions: local functions include none detected; macros include `TRACE_FDS`, `TRACE_FD_0`, `TRACE_OTHER_FDS`; included headers include `dup2.c`. Kernel/user ABI names observed in the full file include `dup2`. Prominent constants include `TRACE_FDS`, `TRACE_FD_0`, `TRACE_OTHER_FDS`; prominent struct names include none detected.

Control flow: this file is a shared implementation or variant wrapper; compile-time macros select the syscall number, xlat style, fd/path mode, success behavior, or namespace mode before the included/shared test body runs. The test cases deliberately create, duplicate, and filter file descriptors so strace can prove descriptor qualifiers and decoded paths remain attached to the expected fd numbers.  This is a wrapper/variant file that reuses shared test implementation through local includes: `dup2.c`.

State and persistence behavior: runtime state is intentionally temporary and test-local. Most state lives in stack variables, tail-allocated buffers, compile-time macros, and errno/return-code snapshots.

Dependencies: strace test harness headers such as `tests.h`, `scno.h`, `print_utils.h`, `pidns.h`, `secontext.h`, local xlat tables, libc headers, and Linux UAPI headers provide syscall numbers, fallback structs, constants, and output helpers. This file directly includes `dup2.c`.

Integration points: the file participates in strace's testsuite as a compiled C test, AWK normalizer, header, or generator input. It integrates with generated xlat tables, syscall-number selection, test-driver `.test` scripts, and expected-output comparison.

Risks: Primary risks are kernel/architecture feature availability, ABI-width differences, host header drift, permissions, namespace-dependent pid/fd/path rendering, and expected-output brittleness when symbolic constants change.

Test signals: useful validation is the corresponding strace testsuite target under the same basename, comparison of stdout against expected decoder lines, successful compilation under the configured personality/time ABI, and skip behavior when the kernel lacks the syscall or permission. The source was read in full for this report: 4 lines, 86 bytes, sha256 prefix `7448bc62d67a`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/dup2-e-fd-not-9.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/dup2-y.c -->
# sources/test-tools/strace/tests/dup2-y.c

Purpose: `dup2-y.c` validates dup/dup2/dup3 decoder output, fd filtering, path decoding, and trace-fd qualifier behavior.

Important APIs/types/functions: local functions include none detected; macros include `FD0_PATH`, `FD9_PATH`, `SKIP_IF_PROC_IS_UNAVAILABLE`; included headers include `dup2.c`. Kernel/user ABI names observed in the full file include `dup2`. Prominent constants include `FD0_PATH`, `FD9_PATH`, `SKIP_IF_PROC_IS_UNAVAILABLE`; prominent struct names include none detected.

Control flow: this file is a shared implementation or variant wrapper; compile-time macros select the syscall number, xlat style, fd/path mode, success behavior, or namespace mode before the included/shared test body runs. The test cases deliberately create, duplicate, and filter file descriptors so strace can prove descriptor qualifiers and decoded paths remain attached to the expected fd numbers.  This is a wrapper/variant file that reuses shared test implementation through local includes: `dup2.c`.

State and persistence behavior: runtime state is intentionally temporary and test-local. Most state lives in stack variables, tail-allocated buffers, compile-time macros, and errno/return-code snapshots.

Dependencies: strace test harness headers such as `tests.h`, `scno.h`, `print_utils.h`, `pidns.h`, `secontext.h`, local xlat tables, libc headers, and Linux UAPI headers provide syscall numbers, fallback structs, constants, and output helpers. This file directly includes `dup2.c`.

Integration points: the file participates in strace's testsuite as a compiled C test, AWK normalizer, header, or generator input. It integrates with generated xlat tables, syscall-number selection, test-driver `.test` scripts, and expected-output comparison. The variant also exercises path/fd decoding options such as `-P`, `-y`, `-yy`, or `--decode-fds`.

Risks: Primary risks are kernel/architecture feature availability, ABI-width differences, host header drift, permissions, namespace-dependent pid/fd/path rendering, and expected-output brittleness when symbolic constants change.

Test signals: useful validation is the corresponding strace testsuite target under the same basename, comparison of stdout against expected decoder lines, successful compilation under the configured personality/time ABI, and skip behavior when the kernel lacks the syscall or permission. The source was read in full for this report: 5 lines, 155 bytes, sha256 prefix `869ac19ccb1b`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/dup2-y.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/dup2-yy.c -->
# sources/test-tools/strace/tests/dup2-yy.c

Purpose: `dup2-yy.c` validates dup/dup2/dup3 decoder output, fd filtering, path decoding, and trace-fd qualifier behavior.

Important APIs/types/functions: local functions include none detected; macros include `FD0_PATH`, `FD9_PATH`, `SKIP_IF_PROC_IS_UNAVAILABLE`; included headers include `dup2.c`. Kernel/user ABI names observed in the full file include `dup2`. Prominent constants include `FD0_PATH`, `FD9_PATH`, `SKIP_IF_PROC_IS_UNAVAILABLE`; prominent struct names include none detected.

Control flow: this file is a shared implementation or variant wrapper; compile-time macros select the syscall number, xlat style, fd/path mode, success behavior, or namespace mode before the included/shared test body runs. The test cases deliberately create, duplicate, and filter file descriptors so strace can prove descriptor qualifiers and decoded paths remain attached to the expected fd numbers.  This is a wrapper/variant file that reuses shared test implementation through local includes: `dup2.c`.

State and persistence behavior: runtime state is intentionally temporary and test-local. Most state lives in stack variables, tail-allocated buffers, compile-time macros, and errno/return-code snapshots.

Dependencies: strace test harness headers such as `tests.h`, `scno.h`, `print_utils.h`, `pidns.h`, `secontext.h`, local xlat tables, libc headers, and Linux UAPI headers provide syscall numbers, fallback structs, constants, and output helpers. This file directly includes `dup2.c`.

Integration points: the file participates in strace's testsuite as a compiled C test, AWK normalizer, header, or generator input. It integrates with generated xlat tables, syscall-number selection, test-driver `.test` scripts, and expected-output comparison. The variant also exercises path/fd decoding options such as `-P`, `-y`, `-yy`, or `--decode-fds`.

Risks: Primary risks are kernel/architecture feature availability, ABI-width differences, host header drift, permissions, namespace-dependent pid/fd/path rendering, and expected-output brittleness when symbolic constants change.

Test signals: useful validation is the corresponding strace testsuite target under the same basename, comparison of stdout against expected decoder lines, successful compilation under the configured personality/time ABI, and skip behavior when the kernel lacks the syscall or permission. The source was read in full for this report: 5 lines, 175 bytes, sha256 prefix `4853900ddb51`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/dup2-yy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/dup2.c -->
# sources/test-tools/strace/tests/dup2.c

Purpose: `dup2.c` validates dup/dup2/dup3 decoder output, fd filtering, path decoding, and trace-fd qualifier behavior.

Important APIs/types/functions: local functions include `k_dup2`, `main`; macros include `FD0_PATH`, `FD9_PATH`, `SKIP_IF_PROC_IS_UNAVAILABLE`, `PATH_TRACING`, `TRACE_FDS`, `TRACE_FD_0`, `TRACE_OTHER_FDS`, `TRACE_FD_9`; included headers include `tests.h`, `scno.h`, `stdio.h`, `unistd.h`. Kernel/user ABI names observed in the full file include `dup`, `dup2`. Prominent constants include `SPDX`, `GPL`, `FD0_PATH`, `FD9_PATH`, `SKIP_IF_PROC_IS_UNAVAILABLE`, `PATH_TRACING`, `TRACE_FDS`, `TRACE_FD_0`, `TRACE_OTHER_FDS`, `TRACE_FD_9`, `SKIP_MAIN_UNDEFINED`; prominent struct names include none detected.

Control flow: `main` builds deterministic arguments, invokes the target syscall or helper sequence, prints the expected strace line with `printf`/test helpers, and exits through the strace test harness. The test cases deliberately create, duplicate, and filter file descriptors so strace can prove descriptor qualifiers and decoded paths remain attached to the expected fd numbers.

State and persistence behavior: runtime state is intentionally temporary and test-local. Most state lives in stack variables, tail-allocated buffers, compile-time macros, and errno/return-code snapshots.

Dependencies: strace test harness headers such as `tests.h`, `scno.h`, `print_utils.h`, `pidns.h`, `secontext.h`, local xlat tables, libc headers, and Linux UAPI headers provide syscall numbers, fallback structs, constants, and output helpers. This file directly includes `tests.h`, `scno.h`, `stdio.h`, `unistd.h`.

Integration points: the file participates in strace's testsuite as a compiled C test, AWK normalizer, header, or generator input. It integrates with generated xlat tables, syscall-number selection, test-driver `.test` scripts, and expected-output comparison.

Risks: Primary risks are kernel/architecture feature availability, ABI-width differences, host header drift, permissions, namespace-dependent pid/fd/path rendering, and expected-output brittleness when symbolic constants change.

Test signals: useful validation is the corresponding strace testsuite target under the same basename, comparison of stdout against expected decoder lines, successful compilation under the configured personality/time ABI, and skip behavior when the kernel lacks the syscall or permission. The source was read in full for this report: 167 lines, 3444 bytes, sha256 prefix `20d94fbd39c2`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/dup2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/dup3-P.c -->
# sources/test-tools/strace/tests/dup3-P.c

Purpose: `dup3-P.c` validates dup/dup2/dup3 decoder output, fd filtering, path decoding, and trace-fd qualifier behavior.

Important APIs/types/functions: local functions include none detected; macros include `PATH_TRACING`, `SKIP_IF_PROC_IS_UNAVAILABLE`; included headers include `dup3.c`. Kernel/user ABI names observed in the full file include `dup3`. Prominent constants include `PATH_TRACING`, `SKIP_IF_PROC_IS_UNAVAILABLE`; prominent struct names include none detected.

Control flow: this file is a shared implementation or variant wrapper; compile-time macros select the syscall number, xlat style, fd/path mode, success behavior, or namespace mode before the included/shared test body runs. The test cases deliberately create, duplicate, and filter file descriptors so strace can prove descriptor qualifiers and decoded paths remain attached to the expected fd numbers.  This is a wrapper/variant file that reuses shared test implementation through local includes: `dup3.c`.

State and persistence behavior: runtime state is intentionally temporary and test-local. Most state lives in stack variables, tail-allocated buffers, compile-time macros, and errno/return-code snapshots.

Dependencies: strace test harness headers such as `tests.h`, `scno.h`, `print_utils.h`, `pidns.h`, `secontext.h`, local xlat tables, libc headers, and Linux UAPI headers provide syscall numbers, fallback structs, constants, and output helpers. This file directly includes `dup3.c`.

Integration points: the file participates in strace's testsuite as a compiled C test, AWK normalizer, header, or generator input. It integrates with generated xlat tables, syscall-number selection, test-driver `.test` scripts, and expected-output comparison. The variant also exercises path/fd decoding options such as `-P`, `-y`, `-yy`, or `--decode-fds`.

Risks: Primary risks are kernel/architecture feature availability, ABI-width differences, host header drift, permissions, namespace-dependent pid/fd/path rendering, and expected-output brittleness when symbolic constants change.

Test signals: useful validation is the corresponding strace testsuite target under the same basename, comparison of stdout against expected decoder lines, successful compilation under the configured personality/time ABI, and skip behavior when the kernel lacks the syscall or permission. The source was read in full for this report: 4 lines, 114 bytes, sha256 prefix `7b0567156f4e`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/dup3-P.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/dup3-y.c -->
# sources/test-tools/strace/tests/dup3-y.c

Purpose: `dup3-y.c` validates dup/dup2/dup3 decoder output, fd filtering, path decoding, and trace-fd qualifier behavior.

Important APIs/types/functions: local functions include none detected; macros include `FD0_PATH`, `FD7_PATH`, `SKIP_IF_PROC_IS_UNAVAILABLE`; included headers include `dup3.c`. Kernel/user ABI names observed in the full file include `dup3`. Prominent constants include `FD0_PATH`, `FD7_PATH`, `SKIP_IF_PROC_IS_UNAVAILABLE`; prominent struct names include none detected.

Control flow: this file is a shared implementation or variant wrapper; compile-time macros select the syscall number, xlat style, fd/path mode, success behavior, or namespace mode before the included/shared test body runs. The test cases deliberately create, duplicate, and filter file descriptors so strace can prove descriptor qualifiers and decoded paths remain attached to the expected fd numbers.  This is a wrapper/variant file that reuses shared test implementation through local includes: `dup3.c`.

State and persistence behavior: runtime state is intentionally temporary and test-local. Most state lives in stack variables, tail-allocated buffers, compile-time macros, and errno/return-code snapshots.

Dependencies: strace test harness headers such as `tests.h`, `scno.h`, `print_utils.h`, `pidns.h`, `secontext.h`, local xlat tables, libc headers, and Linux UAPI headers provide syscall numbers, fallback structs, constants, and output helpers. This file directly includes `dup3.c`.

Integration points: the file participates in strace's testsuite as a compiled C test, AWK normalizer, header, or generator input. It integrates with generated xlat tables, syscall-number selection, test-driver `.test` scripts, and expected-output comparison. The variant also exercises path/fd decoding options such as `-P`, `-y`, `-yy`, or `--decode-fds`.

Risks: Primary risks are kernel/architecture feature availability, ABI-width differences, host header drift, permissions, namespace-dependent pid/fd/path rendering, and expected-output brittleness when symbolic constants change.

Test signals: useful validation is the corresponding strace testsuite target under the same basename, comparison of stdout against expected decoder lines, successful compilation under the configured personality/time ABI, and skip behavior when the kernel lacks the syscall or permission. The source was read in full for this report: 5 lines, 155 bytes, sha256 prefix `b5bb8c7683a6`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/dup3-y.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/dup3-yy.c -->
# sources/test-tools/strace/tests/dup3-yy.c

Purpose: `dup3-yy.c` validates dup/dup2/dup3 decoder output, fd filtering, path decoding, and trace-fd qualifier behavior.

Important APIs/types/functions: local functions include none detected; macros include `FD0_PATH`, `FD7_PATH`, `SKIP_IF_PROC_IS_UNAVAILABLE`; included headers include `dup3.c`. Kernel/user ABI names observed in the full file include `dup3`. Prominent constants include `FD0_PATH`, `FD7_PATH`, `SKIP_IF_PROC_IS_UNAVAILABLE`; prominent struct names include none detected.

Control flow: this file is a shared implementation or variant wrapper; compile-time macros select the syscall number, xlat style, fd/path mode, success behavior, or namespace mode before the included/shared test body runs. The test cases deliberately create, duplicate, and filter file descriptors so strace can prove descriptor qualifiers and decoded paths remain attached to the expected fd numbers.  This is a wrapper/variant file that reuses shared test implementation through local includes: `dup3.c`.

State and persistence behavior: runtime state is intentionally temporary and test-local. Most state lives in stack variables, tail-allocated buffers, compile-time macros, and errno/return-code snapshots.

Dependencies: strace test harness headers such as `tests.h`, `scno.h`, `print_utils.h`, `pidns.h`, `secontext.h`, local xlat tables, libc headers, and Linux UAPI headers provide syscall numbers, fallback structs, constants, and output helpers. This file directly includes `dup3.c`.

Integration points: the file participates in strace's testsuite as a compiled C test, AWK normalizer, header, or generator input. It integrates with generated xlat tables, syscall-number selection, test-driver `.test` scripts, and expected-output comparison. The variant also exercises path/fd decoding options such as `-P`, `-y`, `-yy`, or `--decode-fds`.

Risks: Primary risks are kernel/architecture feature availability, ABI-width differences, host header drift, permissions, namespace-dependent pid/fd/path rendering, and expected-output brittleness when symbolic constants change.

Test signals: useful validation is the corresponding strace testsuite target under the same basename, comparison of stdout against expected decoder lines, successful compilation under the configured personality/time ABI, and skip behavior when the kernel lacks the syscall or permission. The source was read in full for this report: 5 lines, 175 bytes, sha256 prefix `640c9f11dd83`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/dup3-yy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/dup3.c -->
# sources/test-tools/strace/tests/dup3.c

Purpose: `dup3.c` validates dup/dup2/dup3 decoder output, fd filtering, path decoding, and trace-fd qualifier behavior.

Important APIs/types/functions: local functions include `k_dup3`, `main`; macros include `FD0_PATH`, `FD7_PATH`, `SKIP_IF_PROC_IS_UNAVAILABLE`; included headers include `tests.h`, `scno.h`, `stdio.h`, `unistd.h`, `kernel_fcntl.h`. Kernel/user ABI names observed in the full file include `dup`, `dup3`. Prominent constants include `SPDX`, `GPL`, `FD0_PATH`, `FD7_PATH`, `SKIP_IF_PROC_IS_UNAVAILABLE`, `PATH_TRACING`, `O_CLOEXEC`, `O_TRUNC`, `O_RDONLY`, `O_WRONLY`, `O_RDWR`; prominent struct names include none detected.

Control flow: `main` builds deterministic arguments, invokes the target syscall or helper sequence, prints the expected strace line with `printf`/test helpers, and exits through the strace test harness. The test cases deliberately create, duplicate, and filter file descriptors so strace can prove descriptor qualifiers and decoded paths remain attached to the expected fd numbers.

State and persistence behavior: runtime state is intentionally temporary and test-local. Most state lives in stack variables, tail-allocated buffers, compile-time macros, and errno/return-code snapshots.

Dependencies: strace test harness headers such as `tests.h`, `scno.h`, `print_utils.h`, `pidns.h`, `secontext.h`, local xlat tables, libc headers, and Linux UAPI headers provide syscall numbers, fallback structs, constants, and output helpers. This file directly includes `tests.h`, `scno.h`, `stdio.h`, `unistd.h`, `kernel_fcntl.h`.

Integration points: the file participates in strace's testsuite as a compiled C test, AWK normalizer, header, or generator input. It integrates with generated xlat tables, syscall-number selection, test-driver `.test` scripts, and expected-output comparison.

Risks: Primary risks are kernel/architecture feature availability, ABI-width differences, host header drift, permissions, namespace-dependent pid/fd/path rendering, and expected-output brittleness when symbolic constants change.

Test signals: useful validation is the corresponding strace testsuite target under the same basename, comparison of stdout against expected decoder lines, successful compilation under the configured personality/time ABI, and skip behavior when the kernel lacks the syscall or permission. The source was read in full for this report: 123 lines, 2834 bytes, sha256 prefix `76eb60c5fb07`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/dup3.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/env-i.c -->
# sources/test-tools/strace/tests/env-i.c

Purpose: `env-i.c` drives process-control or harness behavior needed by strace tests, such as vfork detach, delay/timing, or sanitized environment execution.

Important APIs/types/functions: local functions include `main`; macros include none detected; included headers include `tests.h`, `unistd.h`. Kernel/user ABI names observed in the full file include `execve`. Prominent constants include `SPDX`, `GPL`, `NULL`; prominent struct names include none detected.

Control flow: `main` builds deterministic arguments, invokes the target syscall or helper sequence, prints the expected strace line with `printf`/test helpers, and exits through the strace test harness.  This is a wrapper/variant file that reuses shared test implementation through local includes: `tests.h`.

State and persistence behavior: runtime state is intentionally temporary and test-local. Most state lives in stack variables, tail-allocated buffers, compile-time macros, and errno/return-code snapshots.

Dependencies: strace test harness headers such as `tests.h`, `scno.h`, `print_utils.h`, `pidns.h`, `secontext.h`, local xlat tables, libc headers, and Linux UAPI headers provide syscall numbers, fallback structs, constants, and output helpers. This file directly includes `tests.h`, `unistd.h`.

Integration points: the file participates in strace's testsuite as a compiled C test, AWK normalizer, header, or generator input. It integrates with generated xlat tables, syscall-number selection, test-driver `.test` scripts, and expected-output comparison.

Risks: Primary risks are kernel/architecture feature availability, ABI-width differences, host header drift, permissions, namespace-dependent pid/fd/path rendering, and expected-output brittleness when symbolic constants change.

Test signals: useful validation is the corresponding strace testsuite target under the same basename, comparison of stdout against expected decoder lines, successful compilation under the configured personality/time ABI, and skip behavior when the kernel lacks the syscall or permission. The source was read in full for this report: 19 lines, 347 bytes, sha256 prefix `2a778a0b4e79`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/env-i.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/epoll_create.c -->
# sources/test-tools/strace/tests/epoll_create.c

Purpose: `epoll_create.c` covers epoll creation, control, wait, pwait, and pwait2 decoders, including event masks, timeout structures, sigmask pointers, and fd/path variants.

Important APIs/types/functions: local functions include `main`; macros include none detected; included headers include `tests.h`, `scno.h`, `stdio.h`, `unistd.h`. Kernel/user ABI names observed in the full file include `epoll_create`. Prominent constants include `SPDX`, `GPL`, `SKIP_MAIN_UNDEFINED`; prominent struct names include none detected.

Control flow: `main` builds deterministic arguments, invokes the target syscall or helper sequence, prints the expected strace line with `printf`/test helpers, and exits through the strace test harness. The epoll tests create descriptors/events, drive control or wait calls, and print event masks, timeout values, and signal-mask arguments in the same shape strace should decode.

State and persistence behavior: runtime state is intentionally temporary and test-local. Most state lives in stack variables, tail-allocated buffers, compile-time macros, and errno/return-code snapshots.

Dependencies: strace test harness headers such as `tests.h`, `scno.h`, `print_utils.h`, `pidns.h`, `secontext.h`, local xlat tables, libc headers, and Linux UAPI headers provide syscall numbers, fallback structs, constants, and output helpers. This file directly includes `tests.h`, `scno.h`, `stdio.h`, `unistd.h`.

Integration points: the file participates in strace's testsuite as a compiled C test, AWK normalizer, header, or generator input. It integrates with generated xlat tables, syscall-number selection, test-driver `.test` scripts, and expected-output comparison.

Risks: Primary risks are kernel/architecture feature availability, ABI-width differences, host header drift, permissions, namespace-dependent pid/fd/path rendering, and expected-output brittleness when symbolic constants change.

Test signals: useful validation is the corresponding strace testsuite target under the same basename, comparison of stdout against expected decoder lines, successful compilation under the configured personality/time ABI, and skip behavior when the kernel lacks the syscall or permission. The source was read in full for this report: 32 lines, 520 bytes, sha256 prefix `687e4f0231ac`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/epoll_create.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/epoll_create1.c -->
# sources/test-tools/strace/tests/epoll_create1.c

Purpose: `epoll_create1.c` covers epoll creation, control, wait, pwait, and pwait2 decoders, including event masks, timeout structures, sigmask pointers, and fd/path variants.

Important APIs/types/functions: local functions include `main`; macros include none detected; included headers include `tests.h`, `scno.h`, `stdio.h`, `unistd.h`, `kernel_fcntl.h`. Kernel/user ABI names observed in the full file include `epoll_create1`. Prominent constants include `SPDX`, `GPL`, `O_CLOEXEC`, `EPOLL_CLOEXEC`, `O_NONBLOCK`; prominent struct names include none detected.

Control flow: `main` builds deterministic arguments, invokes the target syscall or helper sequence, prints the expected strace line with `printf`/test helpers, and exits through the strace test harness. The epoll tests create descriptors/events, drive control or wait calls, and print event masks, timeout values, and signal-mask arguments in the same shape strace should decode.  This is a wrapper/variant file that reuses shared test implementation through local includes: `tests.h`, `scno.h`, `kernel_fcntl.h`.

State and persistence behavior: runtime state is intentionally temporary and test-local. Most state lives in stack variables, tail-allocated buffers, compile-time macros, and errno/return-code snapshots.

Dependencies: strace test harness headers such as `tests.h`, `scno.h`, `print_utils.h`, `pidns.h`, `secontext.h`, local xlat tables, libc headers, and Linux UAPI headers provide syscall numbers, fallback structs, constants, and output helpers. This file directly includes `tests.h`, `scno.h`, `stdio.h`, `unistd.h`, `kernel_fcntl.h`.

Integration points: the file participates in strace's testsuite as a compiled C test, AWK normalizer, header, or generator input. It integrates with generated xlat tables, syscall-number selection, test-driver `.test` scripts, and expected-output comparison.

Risks: Primary risks are kernel/architecture feature availability, ABI-width differences, host header drift, permissions, namespace-dependent pid/fd/path rendering, and expected-output brittleness when symbolic constants change.

Test signals: useful validation is the corresponding strace testsuite target under the same basename, comparison of stdout against expected decoder lines, successful compilation under the configured personality/time ABI, and skip behavior when the kernel lacks the syscall or permission. The source was read in full for this report: 30 lines, 662 bytes, sha256 prefix `21c743a1333c`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/epoll_create1.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/epoll_ctl.c -->
# sources/test-tools/strace/tests/epoll_ctl.c

Purpose: `epoll_ctl.c` covers epoll creation, control, wait, pwait, and pwait2 decoders, including event masks, timeout structures, sigmask pointers, and fd/path variants.

Important APIs/types/functions: local functions include `invoke_syscall`, `main`; macros include none detected; included headers include `tests.h`, `scno.h`, `inttypes.h`, `stdio.h`, `unistd.h`, `linux/eventpoll.h`. Kernel/user ABI names observed in the full file include `epoll_ctl`. Prominent constants include `SPDX`, `GPL`, `F8ILL_KULONG_MASK`, `TAIL_ALLOC_OBJECT_CONST_PTR`, `EPOLLIN`, `EPOLL_CTL_ADD`, `EPOLL_CTL_DEL`, `EPOLL_CTL_MOD`, `NULL`; prominent struct names include `epoll_event`.

Control flow: `main` builds deterministic arguments, invokes the target syscall or helper sequence, prints the expected strace line with `printf`/test helpers, and exits through the strace test harness. The epoll tests create descriptors/events, drive control or wait calls, and print event masks, timeout values, and signal-mask arguments in the same shape strace should decode.

State and persistence behavior: runtime state is intentionally temporary and test-local. Most state lives in stack variables, tail-allocated buffers, compile-time macros, and errno/return-code snapshots.

Dependencies: strace test harness headers such as `tests.h`, `scno.h`, `print_utils.h`, `pidns.h`, `secontext.h`, local xlat tables, libc headers, and Linux UAPI headers provide syscall numbers, fallback structs, constants, and output helpers. This file directly includes `tests.h`, `scno.h`, `inttypes.h`, `stdio.h`, `unistd.h`, `linux/eventpoll.h`.

Integration points: the file participates in strace's testsuite as a compiled C test, AWK normalizer, header, or generator input. It integrates with generated xlat tables, syscall-number selection, test-driver `.test` scripts, and expected-output comparison.

Risks: Primary risks are kernel/architecture feature availability, ABI-width differences, host header drift, permissions, namespace-dependent pid/fd/path rendering, and expected-output brittleness when symbolic constants change.

Test signals: useful validation is the corresponding strace testsuite target under the same basename, comparison of stdout against expected decoder lines, successful compilation under the configured personality/time ABI, and skip behavior when the kernel lacks the syscall or permission. The source was read in full for this report: 46 lines, 1096 bytes, sha256 prefix `a0aa16644aa5`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/epoll_ctl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/epoll_pwait.c -->
# sources/test-tools/strace/tests/epoll_pwait.c

Purpose: `epoll_pwait.c` covers epoll creation, control, wait, pwait, and pwait2 decoders, including event masks, timeout structures, sigmask pointers, and fd/path variants.

Important APIs/types/functions: local functions include `main`; macros include none detected; included headers include `tests.h`, `scno.h`, `signal.h`, `stdio.h`, `unistd.h`, `linux/eventpoll.h`. Kernel/user ABI names observed in the full file include `epoll_pwait`. Prominent constants include `SPDX`, `GPL`, `TAIL_ALLOC_OBJECT_CONST_PTR`, `SKIP_MAIN_UNDEFINED`; prominent struct names include `epoll_event`.

Control flow: `main` builds deterministic arguments, invokes the target syscall or helper sequence, prints the expected strace line with `printf`/test helpers, and exits through the strace test harness. The epoll tests create descriptors/events, drive control or wait calls, and print event masks, timeout values, and signal-mask arguments in the same shape strace should decode.

State and persistence behavior: runtime state is intentionally temporary and test-local. Most state lives in stack variables, tail-allocated buffers, compile-time macros, and errno/return-code snapshots.

Dependencies: strace test harness headers such as `tests.h`, `scno.h`, `print_utils.h`, `pidns.h`, `secontext.h`, local xlat tables, libc headers, and Linux UAPI headers provide syscall numbers, fallback structs, constants, and output helpers. This file directly includes `tests.h`, `scno.h`, `signal.h`, `stdio.h`, `unistd.h`, `linux/eventpoll.h`.

Integration points: the file participates in strace's testsuite as a compiled C test, AWK normalizer, header, or generator input. It integrates with generated xlat tables, syscall-number selection, test-driver `.test` scripts, and expected-output comparison.

Risks: Primary risks are kernel/architecture feature availability, ABI-width differences, host header drift, permissions, namespace-dependent pid/fd/path rendering, and expected-output brittleness when symbolic constants change.

Test signals: useful validation is the corresponding strace testsuite target under the same basename, comparison of stdout against expected decoder lines, successful compilation under the configured personality/time ABI, and skip behavior when the kernel lacks the syscall or permission. The source was read in full for this report: 37 lines, 680 bytes, sha256 prefix `445274817293`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/epoll_pwait.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/epoll_pwait2-P.c -->
# sources/test-tools/strace/tests/epoll_pwait2-P.c

Purpose: `epoll_pwait2-P.c` covers epoll creation, control, wait, pwait, and pwait2 decoders, including event masks, timeout structures, sigmask pointers, and fd/path variants.

Important APIs/types/functions: local functions include none detected; macros include `PATH_TRACING`, `SKIP_IF_PROC_IS_UNAVAILABLE`; included headers include `epoll_pwait2.c`. Kernel/user ABI names observed in the full file include `epoll_pwait2`. Prominent constants include `PATH_TRACING`, `SKIP_IF_PROC_IS_UNAVAILABLE`; prominent struct names include none detected.

Control flow: this file is a shared implementation or variant wrapper; compile-time macros select the syscall number, xlat style, fd/path mode, success behavior, or namespace mode before the included/shared test body runs. The epoll tests create descriptors/events, drive control or wait calls, and print event masks, timeout values, and signal-mask arguments in the same shape strace should decode.  This is a wrapper/variant file that reuses shared test implementation through local includes: `epoll_pwait2.c`.

State and persistence behavior: runtime state is intentionally temporary and test-local. Most state lives in stack variables, tail-allocated buffers, compile-time macros, and errno/return-code snapshots.

Dependencies: strace test harness headers such as `tests.h`, `scno.h`, `print_utils.h`, `pidns.h`, `secontext.h`, local xlat tables, libc headers, and Linux UAPI headers provide syscall numbers, fallback structs, constants, and output helpers. This file directly includes `epoll_pwait2.c`.

Integration points: the file participates in strace's testsuite as a compiled C test, AWK normalizer, header, or generator input. It integrates with generated xlat tables, syscall-number selection, test-driver `.test` scripts, and expected-output comparison. The variant also exercises path/fd decoding options such as `-P`, `-y`, `-yy`, or `--decode-fds`.

Risks: Primary risks are kernel/architecture feature availability, ABI-width differences, host header drift, permissions, namespace-dependent pid/fd/path rendering, and expected-output brittleness when symbolic constants change.

Test signals: useful validation is the corresponding strace testsuite target under the same basename, comparison of stdout against expected decoder lines, successful compilation under the configured personality/time ABI, and skip behavior when the kernel lacks the syscall or permission. The source was read in full for this report: 4 lines, 122 bytes, sha256 prefix `4e9e98dd671c`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/epoll_pwait2-P.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/epoll_pwait2-y.c -->
# sources/test-tools/strace/tests/epoll_pwait2-y.c

Purpose: `epoll_pwait2-y.c` covers epoll creation, control, wait, pwait, and pwait2 decoders, including event masks, timeout structures, sigmask pointers, and fd/path variants.

Important APIs/types/functions: local functions include none detected; macros include `FD9_PATH`, `SKIP_IF_PROC_IS_UNAVAILABLE`; included headers include `epoll_pwait2.c`. Kernel/user ABI names observed in the full file include `epoll_pwait2`. Prominent constants include `FD9_PATH`, `SKIP_IF_PROC_IS_UNAVAILABLE`; prominent struct names include none detected.

Control flow: this file is a shared implementation or variant wrapper; compile-time macros select the syscall number, xlat style, fd/path mode, success behavior, or namespace mode before the included/shared test body runs. The epoll tests create descriptors/events, drive control or wait calls, and print event masks, timeout values, and signal-mask arguments in the same shape strace should decode.  This is a wrapper/variant file that reuses shared test implementation through local includes: `epoll_pwait2.c`.

State and persistence behavior: runtime state is intentionally temporary and test-local. Most state lives in stack variables, tail-allocated buffers, compile-time macros, and errno/return-code snapshots.

Dependencies: strace test harness headers such as `tests.h`, `scno.h`, `print_utils.h`, `pidns.h`, `secontext.h`, local xlat tables, libc headers, and Linux UAPI headers provide syscall numbers, fallback structs, constants, and output helpers. This file directly includes `epoll_pwait2.c`.

Integration points: the file participates in strace's testsuite as a compiled C test, AWK normalizer, header, or generator input. It integrates with generated xlat tables, syscall-number selection, test-driver `.test` scripts, and expected-output comparison. The variant also exercises path/fd decoding options such as `-P`, `-y`, `-yy`, or `--decode-fds`.

Risks: Primary risks are kernel/architecture feature availability, ABI-width differences, host header drift, permissions, namespace-dependent pid/fd/path rendering, and expected-output brittleness when symbolic constants change.

Test signals: useful validation is the corresponding strace testsuite target under the same basename, comparison of stdout against expected decoder lines, successful compilation under the configured personality/time ABI, and skip behavior when the kernel lacks the syscall or permission. The source was read in full for this report: 4 lines, 132 bytes, sha256 prefix `1fb9b6dc3e24`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/epoll_pwait2-y.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/epoll_pwait2.c -->
# sources/test-tools/strace/tests/epoll_pwait2.c

Purpose: `epoll_pwait2.c` covers epoll creation, control, wait, pwait, and pwait2 decoders, including event masks, timeout structures, sigmask pointers, and fd/path variants.

Important APIs/types/functions: local functions include `k_epoll_pwait2`, `main`; macros include `FD9_PATH`, `SKIP_IF_PROC_IS_UNAVAILABLE`; included headers include `tests.h`, `scno.h`, `xmalloc.h`, `stdio.h`, `stdlib.h`, `unistd.h`, `linux/eventpoll.h`, `kernel_timespec.h`. Kernel/user ABI names observed in the full file include `epoll_pwait2`. Prominent constants include `SPDX`, `GPL`, `FD9_PATH`, `SKIP_IF_PROC_IS_UNAVAILABLE`, `TAIL_ALLOC_OBJECT_CONST_PTR`, `PATH_TRACING`; prominent struct names include `epoll_event`.

Control flow: `main` builds deterministic arguments, invokes the target syscall or helper sequence, prints the expected strace line with `printf`/test helpers, and exits through the strace test harness. The epoll tests create descriptors/events, drive control or wait calls, and print event masks, timeout values, and signal-mask arguments in the same shape strace should decode.

State and persistence behavior: runtime state is intentionally temporary and test-local. Most state lives in stack variables, tail-allocated buffers, compile-time macros, and errno/return-code snapshots.

Dependencies: strace test harness headers such as `tests.h`, `scno.h`, `print_utils.h`, `pidns.h`, `secontext.h`, local xlat tables, libc headers, and Linux UAPI headers provide syscall numbers, fallback structs, constants, and output helpers. This file directly includes `tests.h`, `scno.h`, `xmalloc.h`, `stdio.h`, `stdlib.h`, `unistd.h`, `linux/eventpoll.h`, `kernel_timespec.h`.

Integration points: the file participates in strace's testsuite as a compiled C test, AWK normalizer, header, or generator input. It integrates with generated xlat tables, syscall-number selection, test-driver `.test` scripts, and expected-output comparison.

Risks: Primary risks are kernel/architecture feature availability, ABI-width differences, host header drift, permissions, namespace-dependent pid/fd/path rendering, and expected-output brittleness when symbolic constants change.

Test signals: useful validation is the corresponding strace testsuite target under the same basename, comparison of stdout against expected decoder lines, successful compilation under the configured personality/time ABI, and skip behavior when the kernel lacks the syscall or permission. The source was read in full for this report: 79 lines, 2091 bytes, sha256 prefix `496f0e962833`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/epoll_pwait2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/epoll_wait.c -->
# sources/test-tools/strace/tests/epoll_wait.c

Purpose: `epoll_wait.c` covers epoll creation, control, wait, pwait, and pwait2 decoders, including event masks, timeout structures, sigmask pointers, and fd/path variants.

Important APIs/types/functions: local functions include `main`; macros include none detected; included headers include `tests.h`, `scno.h`, `stdio.h`, `unistd.h`, `linux/eventpoll.h`. Kernel/user ABI names observed in the full file include `epoll_wait`. Prominent constants include `SPDX`, `GPL`, `TAIL_ALLOC_OBJECT_CONST_PTR`, `SKIP_MAIN_UNDEFINED`; prominent struct names include `epoll_event`.

Control flow: `main` builds deterministic arguments, invokes the target syscall or helper sequence, prints the expected strace line with `printf`/test helpers, and exits through the strace test harness. The epoll tests create descriptors/events, drive control or wait calls, and print event masks, timeout values, and signal-mask arguments in the same shape strace should decode.

State and persistence behavior: runtime state is intentionally temporary and test-local. Most state lives in stack variables, tail-allocated buffers, compile-time macros, and errno/return-code snapshots.

Dependencies: strace test harness headers such as `tests.h`, `scno.h`, `print_utils.h`, `pidns.h`, `secontext.h`, local xlat tables, libc headers, and Linux UAPI headers provide syscall numbers, fallback structs, constants, and output helpers. This file directly includes `tests.h`, `scno.h`, `stdio.h`, `unistd.h`, `linux/eventpoll.h`.

Integration points: the file participates in strace's testsuite as a compiled C test, AWK normalizer, header, or generator input. It integrates with generated xlat tables, syscall-number selection, test-driver `.test` scripts, and expected-output comparison.

Risks: Primary risks are kernel/architecture feature availability, ABI-width differences, host header drift, permissions, namespace-dependent pid/fd/path rendering, and expected-output brittleness when symbolic constants change.

Test signals: useful validation is the corresponding strace testsuite target under the same basename, comparison of stdout against expected decoder lines, successful compilation under the configured personality/time ABI, and skip behavior when the kernel lacks the syscall or permission. The source was read in full for this report: 33 lines, 552 bytes, sha256 prefix `4b209c2d2b62`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/epoll_wait.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/erestartsys.c -->
# sources/test-tools/strace/tests/erestartsys.c

Purpose: `erestartsys.c` is a focused test-harness utility or diagnostic test for strace errno, restart, or error-message behavior.

Important APIs/types/functions: local functions include `handler`, `main`; macros include none detected; included headers include `tests.h`, `signal.h`, `stdio.h`, `sys/time.h`, `sys/socket.h`, `unistd.h`. Kernel/user ABI names observed in the full file include `socket`. Prominent constants include `ERESTARTSYS`, `SPDX`, `GPL`, `AF_UNIX`, `SOCK_STREAM`, `SA_RESTART`, `SIGALRM`, `NULL`, `SIG_UNBLOCK`, `ITIMER_REAL`; prominent struct names include `sigaction`, `itimerval`.

Control flow: `main` builds deterministic arguments, invokes the target syscall or helper sequence, prints the expected strace line with `printf`/test helpers, and exits through the strace test harness.

State and persistence behavior: runtime state is intentionally temporary and test-local. Most state lives in stack variables, tail-allocated buffers, compile-time macros, and errno/return-code snapshots.

Dependencies: strace test harness headers such as `tests.h`, `scno.h`, `print_utils.h`, `pidns.h`, `secontext.h`, local xlat tables, libc headers, and Linux UAPI headers provide syscall numbers, fallback structs, constants, and output helpers. This file directly includes `tests.h`, `signal.h`, `stdio.h`, `sys/time.h`, `sys/socket.h`, `unistd.h`.

Integration points: the file participates in strace's testsuite as a compiled C test, AWK normalizer, header, or generator input. It integrates with generated xlat tables, syscall-number selection, test-driver `.test` scripts, and expected-output comparison.

Risks: Primary risks are kernel/architecture feature availability, ABI-width differences, host header drift, permissions, namespace-dependent pid/fd/path rendering, and expected-output brittleness when symbolic constants change.

Test signals: useful validation is the corresponding strace testsuite target under the same basename, comparison of stdout against expected decoder lines, successful compilation under the configured personality/time ABI, and skip behavior when the kernel lacks the syscall or permission. The source was read in full for this report: 61 lines, 1337 bytes, sha256 prefix `8f5928df983a`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/erestartsys.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/errno2name.c -->
# sources/test-tools/strace/tests/errno2name.c

Purpose: `errno2name.c` is a focused test-harness utility or diagnostic test for strace errno, restart, or error-message behavior.

Important APIs/types/functions: local functions include `errno2name`; macros include `CASE`, `ERESTARTSYS`, `ERESTARTNOINTR`, `ERESTARTNOHAND`, `ENOIOCTLCMD`, `ERESTART_RESTARTBLOCK`, `EPROBE_DEFER`, ... (18 total), `EJUKEBOX`, `EIOCBQUEUED`, `ERECALLCONFLICT`; included headers include `tests.h`, `errno.h`. Kernel/user ABI names observed in the full file include none detected. Prominent constants include `SPDX`, `GPL`, `CASE`, `ERESTARTSYS`, `ERESTARTNOINTR`, `ERESTARTNOHAND`, `ENOIOCTLCMD`, `ERESTART_RESTARTBLOCK`, `EPROBE_DEFER`, ... (151 total), `EUSERS`, `EXDEV`, `EXFULL`; prominent struct names include none detected.

Control flow: this file is a shared implementation or variant wrapper; compile-time macros select the syscall number, xlat style, fd/path mode, success behavior, or namespace mode before the included/shared test body runs.

State and persistence behavior: runtime state is intentionally temporary and test-local. Most state lives in stack variables, tail-allocated buffers, compile-time macros, and errno/return-code snapshots.

Dependencies: strace test harness headers such as `tests.h`, `scno.h`, `print_utils.h`, `pidns.h`, `secontext.h`, local xlat tables, libc headers, and Linux UAPI headers provide syscall numbers, fallback structs, constants, and output helpers. This file directly includes `tests.h`, `errno.h`.

Integration points: the file participates in strace's testsuite as a compiled C test, AWK normalizer, header, or generator input. It integrates with generated xlat tables, syscall-number selection, test-driver `.test` scripts, and expected-output comparison.

Risks: Primary risks are kernel/architecture feature availability, ABI-width differences, host header drift, permissions, namespace-dependent pid/fd/path rendering, and expected-output brittleness when symbolic constants change.

Test signals: useful validation is the corresponding strace testsuite target under the same basename, comparison of stdout against expected decoder lines, successful compilation under the configured personality/time ABI, and skip behavior when the kernel lacks the syscall or permission. The source was read in full for this report: 518 lines, 7214 bytes, sha256 prefix `2f66ba68167c`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/errno2name.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/error_msg.c -->
# sources/test-tools/strace/tests/error_msg.c

Purpose: `error_msg.c` is a focused test-harness utility or diagnostic test for strace errno, restart, or error-message behavior.

Important APIs/types/functions: local functions include `perror_msg_and_fail`, `error_msg_and_fail`, `error_msg_and_skip`, `perror_msg_and_skip`; macros include `perror_msg_and_fail`, `error_msg_and_fail`; included headers include `tests.h`, `errno.h`, `stdarg.h`, `stdio.h`, `stdlib.h`, `string.h`. Kernel/user ABI names observed in the full file include none detected. Prominent constants include `SPDX`, `GPL`; prominent struct names include none detected.

Control flow: this file is a shared implementation or variant wrapper; compile-time macros select the syscall number, xlat style, fd/path mode, success behavior, or namespace mode before the included/shared test body runs.

State and persistence behavior: runtime state is intentionally temporary and test-local. Most state lives in stack variables, tail-allocated buffers, compile-time macros, and errno/return-code snapshots.

Dependencies: strace test harness headers such as `tests.h`, `scno.h`, `print_utils.h`, `pidns.h`, `secontext.h`, local xlat tables, libc headers, and Linux UAPI headers provide syscall numbers, fallback structs, constants, and output helpers. This file directly includes `tests.h`, `errno.h`, `stdarg.h`, `stdio.h`, `stdlib.h`, `string.h`.

Integration points: the file participates in strace's testsuite as a compiled C test, AWK normalizer, header, or generator input. It integrates with generated xlat tables, syscall-number selection, test-driver `.test` scripts, and expected-output comparison.

Risks: Primary risks are kernel/architecture feature availability, ABI-width differences, host header drift, permissions, namespace-dependent pid/fd/path rendering, and expected-output brittleness when symbolic constants change.

Test signals: useful validation is the corresponding strace testsuite target under the same basename, comparison of stdout against expected decoder lines, successful compilation under the configured personality/time ABI, and skip behavior when the kernel lacks the syscall or permission. The source was read in full for this report: 69 lines, 1140 bytes, sha256 prefix `f9f58440e35f`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/error_msg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/eventfd--decode-fd-eventfd.c -->
# sources/test-tools/strace/tests/eventfd--decode-fd-eventfd.c

Purpose: `eventfd--decode-fd-eventfd.c` tests eventfd decoder output and fd decoding variants for event counter descriptors.

Important APIs/types/functions: local functions include none detected; macros include none detected; included headers include `eventfd-yy.c`. Kernel/user ABI names observed in the full file include `eventfd`. Prominent constants include none detected; prominent struct names include none detected.

Control flow: this file is a shared implementation or variant wrapper; compile-time macros select the syscall number, xlat style, fd/path mode, success behavior, or namespace mode before the included/shared test body runs.  This is a wrapper/variant file that reuses shared test implementation through local includes: `eventfd-yy.c`.

State and persistence behavior: runtime state is intentionally temporary and test-local. Most state lives in stack variables, tail-allocated buffers, compile-time macros, and errno/return-code snapshots.

Dependencies: strace test harness headers such as `tests.h`, `scno.h`, `print_utils.h`, `pidns.h`, `secontext.h`, local xlat tables, libc headers, and Linux UAPI headers provide syscall numbers, fallback structs, constants, and output helpers. This file directly includes `eventfd-yy.c`.

Integration points: the file participates in strace's testsuite as a compiled C test, AWK normalizer, header, or generator input. It integrates with generated xlat tables, syscall-number selection, test-driver `.test` scripts, and expected-output comparison.

Risks: Primary risks are kernel/architecture feature availability, ABI-width differences, host header drift, permissions, namespace-dependent pid/fd/path rendering, and expected-output brittleness when symbolic constants change.

Test signals: useful validation is the corresponding strace testsuite target under the same basename, comparison of stdout against expected decoder lines, successful compilation under the configured personality/time ABI, and skip behavior when the kernel lacks the syscall or permission. The source was read in full for this report: 1 lines, 24 bytes, sha256 prefix `47f92d2cef86`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/eventfd--decode-fd-eventfd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/eventfd-yy.c -->
# sources/test-tools/strace/tests/eventfd-yy.c

Purpose: `eventfd-yy.c` tests eventfd decoder output and fd decoding variants for event counter descriptors.

Important APIs/types/functions: local functions include `k_eventfd`, `parse_fdinfo_efd_id`, `procfs_check_avail_efd_data`, `print_eventfd_details`, `main`; macros include none detected; included headers include `tests.h`, `scno.h`, `xmalloc.h`, `inttypes.h`, `stdio.h`, `stdlib.h`, `string.h`, `unistd.h`, `sys/eventfd.h`. Kernel/user ABI names observed in the full file include `fchdir`, `eventfd`. Prominent constants include `SPDX`, `GPL`, `HAVE_SYS_EVENTFD_H`, `NULL`, `FILE`, `ARRAY_SIZE`, `EFD_SEMAPHORE`, `SKIP_MAIN_UNDEFINED`; prominent struct names include `fdinfo`.

Control flow: `main` builds deterministic arguments, invokes the target syscall or helper sequence, prints the expected strace line with `printf`/test helpers, and exits through the strace test harness.

State and persistence behavior: runtime state is intentionally temporary and test-local. The test may allocate tail buffers and/or create temporary files, directories, descriptors, sockets, eventfds, epoll instances, or mount/file handles, then relies on process exit or explicit cleanup for disposal.

Dependencies: strace test harness headers such as `tests.h`, `scno.h`, `print_utils.h`, `pidns.h`, `secontext.h`, local xlat tables, libc headers, and Linux UAPI headers provide syscall numbers, fallback structs, constants, and output helpers. This file directly includes `tests.h`, `scno.h`, `xmalloc.h`, `inttypes.h`, `stdio.h`, `stdlib.h`, `string.h`, `unistd.h`, `sys/eventfd.h`.

Integration points: the file participates in strace's testsuite as a compiled C test, AWK normalizer, header, or generator input. It integrates with generated xlat tables, syscall-number selection, test-driver `.test` scripts, and expected-output comparison. The variant also exercises path/fd decoding options such as `-P`, `-y`, `-yy`, or `--decode-fds`.

Risks: Primary risks are kernel/architecture feature availability, ABI-width differences, host header drift, permissions, namespace-dependent pid/fd/path rendering, and expected-output brittleness when symbolic constants change.

Test signals: useful validation is the corresponding strace testsuite target under the same basename, comparison of stdout against expected decoder lines, successful compilation under the configured personality/time ABI, and skip behavior when the kernel lacks the syscall or permission. The source was read in full for this report: 193 lines, 4488 bytes, sha256 prefix `574130506a5d`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/eventfd-yy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/eventfd.c -->
# sources/test-tools/strace/tests/eventfd.c

Purpose: `eventfd.c` tests eventfd decoder output and fd decoding variants for event counter descriptors.

Important APIs/types/functions: local functions include `main`; macros include none detected; included headers include `tests.h`, `scno.h`, `unistd.h`, `kernel_fcntl.h`. Kernel/user ABI names observed in the full file include none detected. Prominent constants include `SPDX`, `GPL`, `O_CLOEXEC`, `O_NONBLOCK`; prominent struct names include none detected.

Control flow: `main` builds deterministic arguments, invokes the target syscall or helper sequence, prints the expected strace line with `printf`/test helpers, and exits through the strace test harness.  This is a wrapper/variant file that reuses shared test implementation through local includes: `tests.h`, `scno.h`, `kernel_fcntl.h`.

State and persistence behavior: runtime state is intentionally temporary and test-local. Most state lives in stack variables, tail-allocated buffers, compile-time macros, and errno/return-code snapshots.

Dependencies: strace test harness headers such as `tests.h`, `scno.h`, `print_utils.h`, `pidns.h`, `secontext.h`, local xlat tables, libc headers, and Linux UAPI headers provide syscall numbers, fallback structs, constants, and output helpers. This file directly includes `tests.h`, `scno.h`, `unistd.h`, `kernel_fcntl.h`.

Integration points: the file participates in strace's testsuite as a compiled C test, AWK normalizer, header, or generator input. It integrates with generated xlat tables, syscall-number selection, test-driver `.test` scripts, and expected-output comparison.

Risks: Primary risks are kernel/architecture feature availability, ABI-width differences, host header drift, permissions, namespace-dependent pid/fd/path rendering, and expected-output brittleness when symbolic constants change.

Test signals: useful validation is the corresponding strace testsuite target under the same basename, comparison of stdout against expected decoder lines, successful compilation under the configured personality/time ABI, and skip behavior when the kernel lacks the syscall or permission. The source was read in full for this report: 24 lines, 461 bytes, sha256 prefix `8035269b8c8c`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/eventfd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/execve-v.c -->
# sources/test-tools/strace/tests/execve-v.c

Purpose: `execve-v.c` checks execve and execveat argument/envp/path decoding, verbose argument rendering, and AT_* flag behavior.

Important APIs/types/functions: local functions include none detected; macros include `VERBOSE`; included headers include `execve.c`. Kernel/user ABI names observed in the full file include `execve`. Prominent constants include `VERBOSE`; prominent struct names include none detected.

Control flow: this file is a shared implementation or variant wrapper; compile-time macros select the syscall number, xlat style, fd/path mode, success behavior, or namespace mode before the included/shared test body runs. The exec tests stage argv/envp/pathname combinations and use controlled failure or child execution so the trace line can be compared without losing the harness process unexpectedly.  This is a wrapper/variant file that reuses shared test implementation through local includes: `execve.c`.

State and persistence behavior: runtime state is intentionally temporary and test-local. Most state lives in stack variables, tail-allocated buffers, compile-time macros, and errno/return-code snapshots. exec tests intentionally manipulate process image boundaries and environment vectors, so their persistence boundary is the child/process invocation.

Dependencies: strace test harness headers such as `tests.h`, `scno.h`, `print_utils.h`, `pidns.h`, `secontext.h`, local xlat tables, libc headers, and Linux UAPI headers provide syscall numbers, fallback structs, constants, and output helpers. This file directly includes `execve.c`.

Integration points: the file participates in strace's testsuite as a compiled C test, AWK normalizer, header, or generator input. It integrates with generated xlat tables, syscall-number selection, test-driver `.test` scripts, and expected-output comparison.

Risks: exec tests replace the process image on success, so they rely on controlled failing paths or child execution and must preserve argv/envp quoting and truncation expectations.

Test signals: useful validation is the corresponding strace testsuite target under the same basename, comparison of stdout against expected decoder lines, successful compilation under the configured personality/time ABI, and skip behavior when the kernel lacks the syscall or permission. The source was read in full for this report: 3 lines, 87 bytes, sha256 prefix `b03a452a8c18`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/execve-v.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/execve.c -->
# sources/test-tools/strace/tests/execve.c

Purpose: `execve.c` checks execve and execveat argument/envp/path decoding, verbose argument rendering, and AT_* flag behavior.

Important APIs/types/functions: local functions include `call_execve`, `main`; macros include `FILENAME`, `Q_FILENAME`; included headers include `tests.h`, `fcntl.h`, `stdio.h`, `unistd.h`, `secontext.h`. Kernel/user ABI names observed in the full file include `execve`, `fcntl`. Prominent constants include `SPDX`, `GPL`, `FILENAME`, `Q_FILENAME`, `SECONTEXT_PID_MY`, `O_RDONLY`, `O_CREAT`, `SECONTEXT_FILE`, `VERBOSE`, ... (13 total), `NULL`, `TAIL_ALLOC_OBJECT_CONST_PTR`, `DEFAULT_STRLEN`; prominent struct names include none detected.

Control flow: `main` builds deterministic arguments, invokes the target syscall or helper sequence, prints the expected strace line with `printf`/test helpers, and exits through the strace test harness. The exec tests stage argv/envp/pathname combinations and use controlled failure or child execution so the trace line can be compared without losing the harness process unexpectedly.

State and persistence behavior: runtime state is intentionally temporary and test-local. The test may allocate tail buffers and/or create temporary files, directories, descriptors, sockets, eventfds, epoll instances, or mount/file handles, then relies on process exit or explicit cleanup for disposal. exec tests intentionally manipulate process image boundaries and environment vectors, so their persistence boundary is the child/process invocation.

Dependencies: strace test harness headers such as `tests.h`, `scno.h`, `print_utils.h`, `pidns.h`, `secontext.h`, local xlat tables, libc headers, and Linux UAPI headers provide syscall numbers, fallback structs, constants, and output helpers. This file directly includes `tests.h`, `fcntl.h`, `stdio.h`, `unistd.h`, `secontext.h`.

Integration points: the file participates in strace's testsuite as a compiled C test, AWK normalizer, header, or generator input. It integrates with generated xlat tables, syscall-number selection, test-driver `.test` scripts, and expected-output comparison.

Risks: exec tests replace the process image on success, so they rely on controlled failing paths or child execution and must preserve argv/envp quoting and truncation expectations.

Test signals: useful validation is the corresponding strace testsuite target under the same basename, comparison of stdout against expected decoder lines, successful compilation under the configured personality/time ABI, and skip behavior when the kernel lacks the syscall or permission. The source was read in full for this report: 218 lines, 5382 bytes, sha256 prefix `241f21c97db0`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/execve.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/execveat-v.c -->
# sources/test-tools/strace/tests/execveat-v.c

Purpose: `execveat-v.c` checks execve and execveat argument/envp/path decoding, verbose argument rendering, and AT_* flag behavior.

Important APIs/types/functions: local functions include none detected; macros include `VERBOSE`; included headers include `execveat.c`. Kernel/user ABI names observed in the full file include `execveat`. Prominent constants include `VERBOSE`; prominent struct names include none detected.

Control flow: this file is a shared implementation or variant wrapper; compile-time macros select the syscall number, xlat style, fd/path mode, success behavior, or namespace mode before the included/shared test body runs. The exec tests stage argv/envp/pathname combinations and use controlled failure or child execution so the trace line can be compared without losing the harness process unexpectedly.  This is a wrapper/variant file that reuses shared test implementation through local includes: `execveat.c`.

State and persistence behavior: runtime state is intentionally temporary and test-local. Most state lives in stack variables, tail-allocated buffers, compile-time macros, and errno/return-code snapshots. exec tests intentionally manipulate process image boundaries and environment vectors, so their persistence boundary is the child/process invocation.

Dependencies: strace test harness headers such as `tests.h`, `scno.h`, `print_utils.h`, `pidns.h`, `secontext.h`, local xlat tables, libc headers, and Linux UAPI headers provide syscall numbers, fallback structs, constants, and output helpers. This file directly includes `execveat.c`.

Integration points: the file participates in strace's testsuite as a compiled C test, AWK normalizer, header, or generator input. It integrates with generated xlat tables, syscall-number selection, test-driver `.test` scripts, and expected-output comparison.

Risks: exec tests replace the process image on success, so they rely on controlled failing paths or child execution and must preserve argv/envp quoting and truncation expectations.

Test signals: useful validation is the corresponding strace testsuite target under the same basename, comparison of stdout against expected decoder lines, successful compilation under the configured personality/time ABI, and skip behavior when the kernel lacks the syscall or permission. The source was read in full for this report: 3 lines, 91 bytes, sha256 prefix `f7e4df84a353`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/execveat-v.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/execveat.c -->
# sources/test-tools/strace/tests/execveat.c

Purpose: `execveat.c` checks execve and execveat argument/envp/path decoding, verbose argument rendering, and AT_* flag behavior.

Important APIs/types/functions: local functions include `k_execveat`, `tests_with_existing_file`, `main`; macros include `FILENAME`, `Q_FILENAME`; included headers include `tests.h`, `scno.h`, `fcntl.h`, `stdio.h`, `unistd.h`, `secontext.h`. Kernel/user ABI names observed in the full file include `chdir`, `fchdir`, `execveat`, `fcntl`. Prominent constants include `SPDX`, `GPL`, `SECONTEXT_PID_MY`, `O_RDONLY`, `O_CREAT`, `SECONTEXT_FILE`, `NULL`, `AT_FDCWD`, `FILENAME`, ... (18 total), `DEFAULT_STRLEN`, `AT_EXECVE_CHECK`, `AT_`; prominent struct names include none detected.

Control flow: `main` builds deterministic arguments, invokes the target syscall or helper sequence, prints the expected strace line with `printf`/test helpers, and exits through the strace test harness. The exec tests stage argv/envp/pathname combinations and use controlled failure or child execution so the trace line can be compared without losing the harness process unexpectedly.

State and persistence behavior: runtime state is intentionally temporary and test-local. The test may allocate tail buffers and/or create temporary files, directories, descriptors, sockets, eventfds, epoll instances, or mount/file handles, then relies on process exit or explicit cleanup for disposal. exec tests intentionally manipulate process image boundaries and environment vectors, so their persistence boundary is the child/process invocation.

Dependencies: strace test harness headers such as `tests.h`, `scno.h`, `print_utils.h`, `pidns.h`, `secontext.h`, local xlat tables, libc headers, and Linux UAPI headers provide syscall numbers, fallback structs, constants, and output helpers. This file directly includes `tests.h`, `scno.h`, `fcntl.h`, `stdio.h`, `unistd.h`, `secontext.h`.

Integration points: the file participates in strace's testsuite as a compiled C test, AWK normalizer, header, or generator input. It integrates with generated xlat tables, syscall-number selection, test-driver `.test` scripts, and expected-output comparison.

Risks: exec tests replace the process image on success, so they rely on controlled failing paths or child execution and must preserve argv/envp quoting and truncation expectations.

Test signals: useful validation is the corresponding strace testsuite target under the same basename, comparison of stdout against expected decoder lines, successful compilation under the configured personality/time ABI, and skip behavior when the kernel lacks the syscall or permission. The source was read in full for this report: 308 lines, 8149 bytes, sha256 prefix `8b33106cb9ac`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/execveat.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/faccessat-P.c -->
# sources/test-tools/strace/tests/faccessat-P.c

Purpose: `faccessat-P.c` validates faccessat/faccessat2 decoder output for dirfd, path, mode, flags, and path-decoding variants.

Important APIs/types/functions: local functions include none detected; macros include `PATH_TRACING`, `SKIP_IF_PROC_IS_UNAVAILABLE`; included headers include `faccessat.c`. Kernel/user ABI names observed in the full file include `faccessat`. Prominent constants include `PATH_TRACING`, `SKIP_IF_PROC_IS_UNAVAILABLE`; prominent struct names include none detected.

Control flow: this file is a shared implementation or variant wrapper; compile-time macros select the syscall number, xlat style, fd/path mode, success behavior, or namespace mode before the included/shared test body runs. The path/fd variants allocate stable pathnames or descriptors, run failing and successful forms where possible, and print both symbolic flags and raw fallback bits.  This is a wrapper/variant file that reuses shared test implementation through local includes: `faccessat.c`.

State and persistence behavior: runtime state is intentionally temporary and test-local. Most state lives in stack variables, tail-allocated buffers, compile-time macros, and errno/return-code snapshots.

Dependencies: strace test harness headers such as `tests.h`, `scno.h`, `print_utils.h`, `pidns.h`, `secontext.h`, local xlat tables, libc headers, and Linux UAPI headers provide syscall numbers, fallback structs, constants, and output helpers. This file directly includes `faccessat.c`.

Integration points: the file participates in strace's testsuite as a compiled C test, AWK normalizer, header, or generator input. It integrates with generated xlat tables, syscall-number selection, test-driver `.test` scripts, and expected-output comparison. The variant also exercises path/fd decoding options such as `-P`, `-y`, `-yy`, or `--decode-fds`.

Risks: Primary risks are kernel/architecture feature availability, ABI-width differences, host header drift, permissions, namespace-dependent pid/fd/path rendering, and expected-output brittleness when symbolic constants change.

Test signals: useful validation is the corresponding strace testsuite target under the same basename, comparison of stdout against expected decoder lines, successful compilation under the configured personality/time ABI, and skip behavior when the kernel lacks the syscall or permission. The source was read in full for this report: 4 lines, 119 bytes, sha256 prefix `d94eecb1c9a4`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/faccessat-P.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/faccessat-y.c -->
# sources/test-tools/strace/tests/faccessat-y.c

Purpose: `faccessat-y.c` validates faccessat/faccessat2 decoder output for dirfd, path, mode, flags, and path-decoding variants.

Important APIs/types/functions: local functions include none detected; macros include `FD_PATH`, `SKIP_IF_PROC_IS_UNAVAILABLE`; included headers include `faccessat.c`. Kernel/user ABI names observed in the full file include `faccessat`. Prominent constants include `FD_PATH`, `SKIP_IF_PROC_IS_UNAVAILABLE`; prominent struct names include none detected.

Control flow: this file is a shared implementation or variant wrapper; compile-time macros select the syscall number, xlat style, fd/path mode, success behavior, or namespace mode before the included/shared test body runs. The path/fd variants allocate stable pathnames or descriptors, run failing and successful forms where possible, and print both symbolic flags and raw fallback bits.  This is a wrapper/variant file that reuses shared test implementation through local includes: `faccessat.c`.

State and persistence behavior: runtime state is intentionally temporary and test-local. Most state lives in stack variables, tail-allocated buffers, compile-time macros, and errno/return-code snapshots.

Dependencies: strace test harness headers such as `tests.h`, `scno.h`, `print_utils.h`, `pidns.h`, `secontext.h`, local xlat tables, libc headers, and Linux UAPI headers provide syscall numbers, fallback structs, constants, and output helpers. This file directly includes `faccessat.c`.

Integration points: the file participates in strace's testsuite as a compiled C test, AWK normalizer, header, or generator input. It integrates with generated xlat tables, syscall-number selection, test-driver `.test` scripts, and expected-output comparison. The variant also exercises path/fd decoding options such as `-P`, `-y`, `-yy`, or `--decode-fds`.

Risks: Primary risks are kernel/architecture feature availability, ABI-width differences, host header drift, permissions, namespace-dependent pid/fd/path rendering, and expected-output brittleness when symbolic constants change.

Test signals: useful validation is the corresponding strace testsuite target under the same basename, comparison of stdout against expected decoder lines, successful compilation under the configured personality/time ABI, and skip behavior when the kernel lacks the syscall or permission. The source was read in full for this report: 4 lines, 128 bytes, sha256 prefix `f5509767a4aa`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/faccessat-y.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/faccessat-yy.c -->
# sources/test-tools/strace/tests/faccessat-yy.c

Purpose: `faccessat-yy.c` validates faccessat/faccessat2 decoder output for dirfd, path, mode, flags, and path-decoding variants.

Important APIs/types/functions: local functions include none detected; macros include `FD_PATH`, `SKIP_IF_PROC_IS_UNAVAILABLE`; included headers include `faccessat.c`. Kernel/user ABI names observed in the full file include `faccessat`. Prominent constants include `FD_PATH`, `SKIP_IF_PROC_IS_UNAVAILABLE`; prominent struct names include none detected.

Control flow: this file is a shared implementation or variant wrapper; compile-time macros select the syscall number, xlat style, fd/path mode, success behavior, or namespace mode before the included/shared test body runs. The path/fd variants allocate stable pathnames or descriptors, run failing and successful forms where possible, and print both symbolic flags and raw fallback bits.  This is a wrapper/variant file that reuses shared test implementation through local includes: `faccessat.c`.

State and persistence behavior: runtime state is intentionally temporary and test-local. Most state lives in stack variables, tail-allocated buffers, compile-time macros, and errno/return-code snapshots.

Dependencies: strace test harness headers such as `tests.h`, `scno.h`, `print_utils.h`, `pidns.h`, `secontext.h`, local xlat tables, libc headers, and Linux UAPI headers provide syscall numbers, fallback structs, constants, and output helpers. This file directly includes `faccessat.c`.

Integration points: the file participates in strace's testsuite as a compiled C test, AWK normalizer, header, or generator input. It integrates with generated xlat tables, syscall-number selection, test-driver `.test` scripts, and expected-output comparison. The variant also exercises path/fd decoding options such as `-P`, `-y`, `-yy`, or `--decode-fds`.

Risks: Primary risks are kernel/architecture feature availability, ABI-width differences, host header drift, permissions, namespace-dependent pid/fd/path rendering, and expected-output brittleness when symbolic constants change.

Test signals: useful validation is the corresponding strace testsuite target under the same basename, comparison of stdout against expected decoder lines, successful compilation under the configured personality/time ABI, and skip behavior when the kernel lacks the syscall or permission. The source was read in full for this report: 4 lines, 138 bytes, sha256 prefix `c3ed89d30d3c`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/faccessat-yy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/faccessat.c -->
# sources/test-tools/strace/tests/faccessat.c

Purpose: `faccessat.c` validates faccessat/faccessat2 decoder output for dirfd, path, mode, flags, and path-decoding variants.

Important APIs/types/functions: local functions include `k_faccessat`, `tests_with_existing_file`, `main`; macros include `YFLAG`, `FD_PATH`, `SKIP_IF_PROC_IS_UNAVAILABLE`, `AT_FDCWD_FMT`, `AT_FDCWD_ARG`; included headers include `tests.h`, `scno.h`, `fcntl.h`, `stdio.h`, `unistd.h`, `secontext.h`, `xmalloc.h`. Kernel/user ABI names observed in the full file include `chdir`, `fchdir`, `faccessat`, `fcntl`. Prominent constants include `SPDX`, `GPL`, `FD_PATH`, `YFLAG`, `SKIP_IF_PROC_IS_UNAVAILABLE`, `AT_FDCWD_FMT`, `AT_FDCWD_ARG`, `PATH_TRACING`, `SECONTEXT_PID_MY`, ... (24 total), `X_OK`, `ARRAY_SIZE`, `SKIP_MAIN_UNDEFINED`; prominent struct names include `strival32`.

Control flow: `main` builds deterministic arguments, invokes the target syscall or helper sequence, prints the expected strace line with `printf`/test helpers, and exits through the strace test harness. The path/fd variants allocate stable pathnames or descriptors, run failing and successful forms where possible, and print both symbolic flags and raw fallback bits.

State and persistence behavior: runtime state is intentionally temporary and test-local. The test may allocate tail buffers and/or create temporary files, directories, descriptors, sockets, eventfds, epoll instances, or mount/file handles, then relies on process exit or explicit cleanup for disposal.

Dependencies: strace test harness headers such as `tests.h`, `scno.h`, `print_utils.h`, `pidns.h`, `secontext.h`, local xlat tables, libc headers, and Linux UAPI headers provide syscall numbers, fallback structs, constants, and output helpers. This file directly includes `tests.h`, `scno.h`, `fcntl.h`, `stdio.h`, `unistd.h`, `secontext.h`, `xmalloc.h`.

Integration points: the file participates in strace's testsuite as a compiled C test, AWK normalizer, header, or generator input. It integrates with generated xlat tables, syscall-number selection, test-driver `.test` scripts, and expected-output comparison.

Risks: Primary risks are kernel/architecture feature availability, ABI-width differences, host header drift, permissions, namespace-dependent pid/fd/path rendering, and expected-output brittleness when symbolic constants change.

Test signals: useful validation is the corresponding strace testsuite target under the same basename, comparison of stdout against expected decoder lines, successful compilation under the configured personality/time ABI, and skip behavior when the kernel lacks the syscall or permission. The source was read in full for this report: 287 lines, 6255 bytes, sha256 prefix `46a4b6185912`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/faccessat.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/faccessat2-P.c -->
# sources/test-tools/strace/tests/faccessat2-P.c

Purpose: `faccessat2-P.c` validates faccessat/faccessat2 decoder output for dirfd, path, mode, flags, and path-decoding variants.

Important APIs/types/functions: local functions include none detected; macros include `PATH_TRACING`, `SKIP_IF_PROC_IS_UNAVAILABLE`; included headers include `faccessat2.c`. Kernel/user ABI names observed in the full file include `faccessat2`. Prominent constants include `PATH_TRACING`, `SKIP_IF_PROC_IS_UNAVAILABLE`; prominent struct names include none detected.

Control flow: this file is a shared implementation or variant wrapper; compile-time macros select the syscall number, xlat style, fd/path mode, success behavior, or namespace mode before the included/shared test body runs. The path/fd variants allocate stable pathnames or descriptors, run failing and successful forms where possible, and print both symbolic flags and raw fallback bits.  This is a wrapper/variant file that reuses shared test implementation through local includes: `faccessat2.c`.

State and persistence behavior: runtime state is intentionally temporary and test-local. Most state lives in stack variables, tail-allocated buffers, compile-time macros, and errno/return-code snapshots.

Dependencies: strace test harness headers such as `tests.h`, `scno.h`, `print_utils.h`, `pidns.h`, `secontext.h`, local xlat tables, libc headers, and Linux UAPI headers provide syscall numbers, fallback structs, constants, and output helpers. This file directly includes `faccessat2.c`.

Integration points: the file participates in strace's testsuite as a compiled C test, AWK normalizer, header, or generator input. It integrates with generated xlat tables, syscall-number selection, test-driver `.test` scripts, and expected-output comparison. The variant also exercises path/fd decoding options such as `-P`, `-y`, `-yy`, or `--decode-fds`.

Risks: Primary risks are kernel/architecture feature availability, ABI-width differences, host header drift, permissions, namespace-dependent pid/fd/path rendering, and expected-output brittleness when symbolic constants change.

Test signals: useful validation is the corresponding strace testsuite target under the same basename, comparison of stdout against expected decoder lines, successful compilation under the configured personality/time ABI, and skip behavior when the kernel lacks the syscall or permission. The source was read in full for this report: 4 lines, 120 bytes, sha256 prefix `02d9e709b509`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/faccessat2-P.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/faccessat2-y.c -->
# sources/test-tools/strace/tests/faccessat2-y.c

Purpose: `faccessat2-y.c` validates faccessat/faccessat2 decoder output for dirfd, path, mode, flags, and path-decoding variants.

Important APIs/types/functions: local functions include none detected; macros include `FD_PATH`, `SKIP_IF_PROC_IS_UNAVAILABLE`; included headers include `faccessat2.c`. Kernel/user ABI names observed in the full file include `faccessat2`. Prominent constants include `FD_PATH`, `SKIP_IF_PROC_IS_UNAVAILABLE`; prominent struct names include none detected.

Control flow: this file is a shared implementation or variant wrapper; compile-time macros select the syscall number, xlat style, fd/path mode, success behavior, or namespace mode before the included/shared test body runs. The path/fd variants allocate stable pathnames or descriptors, run failing and successful forms where possible, and print both symbolic flags and raw fallback bits.  This is a wrapper/variant file that reuses shared test implementation through local includes: `faccessat2.c`.

State and persistence behavior: runtime state is intentionally temporary and test-local. Most state lives in stack variables, tail-allocated buffers, compile-time macros, and errno/return-code snapshots.

Dependencies: strace test harness headers such as `tests.h`, `scno.h`, `print_utils.h`, `pidns.h`, `secontext.h`, local xlat tables, libc headers, and Linux UAPI headers provide syscall numbers, fallback structs, constants, and output helpers. This file directly includes `faccessat2.c`.

Integration points: the file participates in strace's testsuite as a compiled C test, AWK normalizer, header, or generator input. It integrates with generated xlat tables, syscall-number selection, test-driver `.test` scripts, and expected-output comparison. The variant also exercises path/fd decoding options such as `-P`, `-y`, `-yy`, or `--decode-fds`.

Risks: Primary risks are kernel/architecture feature availability, ABI-width differences, host header drift, permissions, namespace-dependent pid/fd/path rendering, and expected-output brittleness when symbolic constants change.

Test signals: useful validation is the corresponding strace testsuite target under the same basename, comparison of stdout against expected decoder lines, successful compilation under the configured personality/time ABI, and skip behavior when the kernel lacks the syscall or permission. The source was read in full for this report: 4 lines, 129 bytes, sha256 prefix `3650f0fe00a4`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/faccessat2-y.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/faccessat2-yy.c -->
# sources/test-tools/strace/tests/faccessat2-yy.c

Purpose: `faccessat2-yy.c` validates faccessat/faccessat2 decoder output for dirfd, path, mode, flags, and path-decoding variants.

Important APIs/types/functions: local functions include none detected; macros include `FD_PATH`, `SKIP_IF_PROC_IS_UNAVAILABLE`; included headers include `faccessat2.c`. Kernel/user ABI names observed in the full file include `faccessat2`. Prominent constants include `FD_PATH`, `SKIP_IF_PROC_IS_UNAVAILABLE`; prominent struct names include none detected.

Control flow: this file is a shared implementation or variant wrapper; compile-time macros select the syscall number, xlat style, fd/path mode, success behavior, or namespace mode before the included/shared test body runs. The path/fd variants allocate stable pathnames or descriptors, run failing and successful forms where possible, and print both symbolic flags and raw fallback bits.  This is a wrapper/variant file that reuses shared test implementation through local includes: `faccessat2.c`.

State and persistence behavior: runtime state is intentionally temporary and test-local. Most state lives in stack variables, tail-allocated buffers, compile-time macros, and errno/return-code snapshots.

Dependencies: strace test harness headers such as `tests.h`, `scno.h`, `print_utils.h`, `pidns.h`, `secontext.h`, local xlat tables, libc headers, and Linux UAPI headers provide syscall numbers, fallback structs, constants, and output helpers. This file directly includes `faccessat2.c`.

Integration points: the file participates in strace's testsuite as a compiled C test, AWK normalizer, header, or generator input. It integrates with generated xlat tables, syscall-number selection, test-driver `.test` scripts, and expected-output comparison. The variant also exercises path/fd decoding options such as `-P`, `-y`, `-yy`, or `--decode-fds`.

Risks: Primary risks are kernel/architecture feature availability, ABI-width differences, host header drift, permissions, namespace-dependent pid/fd/path rendering, and expected-output brittleness when symbolic constants change.

Test signals: useful validation is the corresponding strace testsuite target under the same basename, comparison of stdout against expected decoder lines, successful compilation under the configured personality/time ABI, and skip behavior when the kernel lacks the syscall or permission. The source was read in full for this report: 4 lines, 139 bytes, sha256 prefix `2277430b90ac`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/faccessat2-yy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/faccessat2.c -->
# sources/test-tools/strace/tests/faccessat2.c

Purpose: `faccessat2.c` validates faccessat/faccessat2 decoder output for dirfd, path, mode, flags, and path-decoding variants.

Important APIs/types/functions: local functions include `k_faccessat2`, `main`; macros include `XLAT_MACROS_ONLY`, `FD_PATH`, `YFLAG`, `SKIP_IF_PROC_IS_UNAVAILABLE`; included headers include `tests.h`, `scno.h`, `xmalloc.h`, `fcntl.h`, `stdio.h`, `unistd.h`, `xlat/faccessat_flags.h`. Kernel/user ABI names observed in the full file include `faccessat2`, `fcntl`. Prominent constants include `SPDX`, `GPL`, `XLAT_MACROS_ONLY`, `FD_PATH`, `YFLAG`, `SKIP_IF_PROC_IS_UNAVAILABLE`, `TAIL_ALLOC_OBJECT_CONST_PTR`, `O_WRONLY`, `AT_FDCWD`, ... (21 total), `NULL`, `ARRAY_SIZE`, `PATH_TRACING`; prominent struct names include `strival32`.

Control flow: `main` builds deterministic arguments, invokes the target syscall or helper sequence, prints the expected strace line with `printf`/test helpers, and exits through the strace test harness. The path/fd variants allocate stable pathnames or descriptors, run failing and successful forms where possible, and print both symbolic flags and raw fallback bits.

State and persistence behavior: runtime state is intentionally temporary and test-local. The test may allocate tail buffers and/or create temporary files, directories, descriptors, sockets, eventfds, epoll instances, or mount/file handles, then relies on process exit or explicit cleanup for disposal.

Dependencies: strace test harness headers such as `tests.h`, `scno.h`, `print_utils.h`, `pidns.h`, `secontext.h`, local xlat tables, libc headers, and Linux UAPI headers provide syscall numbers, fallback structs, constants, and output helpers. This file directly includes `tests.h`, `scno.h`, `xmalloc.h`, `fcntl.h`, `stdio.h`, `unistd.h`, `xlat/faccessat_flags.h`.

Integration points: the file participates in strace's testsuite as a compiled C test, AWK normalizer, header, or generator input. It integrates with generated xlat tables, syscall-number selection, test-driver `.test` scripts, and expected-output comparison.

Risks: Primary risks are kernel/architecture feature availability, ABI-width differences, host header drift, permissions, namespace-dependent pid/fd/path rendering, and expected-output brittleness when symbolic constants change.

Test signals: useful validation is the corresponding strace testsuite target under the same basename, comparison of stdout against expected decoder lines, successful compilation under the configured personality/time ABI, and skip behavior when the kernel lacks the syscall or permission. The source was read in full for this report: 165 lines, 3990 bytes, sha256 prefix `4c6148eb426a`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/faccessat2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/fadvise.h -->
# sources/test-tools/strace/tests/fadvise.h

Purpose: `fadvise.h` is a shared test header that supplies architecture-specific constants or helper declarations to generated/compiled strace tests.

Important APIs/types/functions: local functions include `do_fadvise`, `main`; macros include `STRACE_TESTS_FADVISE_H`; included headers include `limits.h`, `stdio.h`, `unistd.h`, `xlat.h`, `xlat/advise.h`. Kernel/user ABI names observed in the full file include `fadvise64`. Prominent constants include `SPDX`, `GPL`, `STRACE_TESTS_FADVISE_H`; prominent struct names include none detected.

Control flow: `main` builds deterministic arguments, invokes the target syscall or helper sequence, prints the expected strace line with `printf`/test helpers, and exits through the strace test harness.

State and persistence behavior: runtime state is intentionally temporary and test-local. Most state lives in stack variables, tail-allocated buffers, compile-time macros, and errno/return-code snapshots.

Dependencies: strace test harness headers such as `tests.h`, `scno.h`, `print_utils.h`, `pidns.h`, `secontext.h`, local xlat tables, libc headers, and Linux UAPI headers provide syscall numbers, fallback structs, constants, and output helpers. This file directly includes `limits.h`, `stdio.h`, `unistd.h`, `xlat.h`, `xlat/advise.h`.

Integration points: the file participates in strace's testsuite as a compiled C test, AWK normalizer, header, or generator input. It integrates with generated xlat tables, syscall-number selection, test-driver `.test` scripts, and expected-output comparison.

Risks: Primary risks are kernel/architecture feature availability, ABI-width differences, host header drift, permissions, namespace-dependent pid/fd/path rendering, and expected-output brittleness when symbolic constants change.

Test signals: useful validation is the corresponding strace testsuite target under the same basename, comparison of stdout against expected decoder lines, successful compilation under the configured personality/time ABI, and skip behavior when the kernel lacks the syscall or permission. The source was read in full for this report: 38 lines, 972 bytes, sha256 prefix `caaf753fb855`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/fadvise.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/fadvise64.c -->
# sources/test-tools/strace/tests/fadvise64.c

Purpose: `fadvise64.c` covers fadvise64/fadvise64_64 argument layout and advice-name decoding across ABI layouts.

Important APIs/types/functions: local functions include `do_fadvise`; macros include none detected; included headers include `tests.h`, `scno.h`, `fadvise.h`. Kernel/user ABI names observed in the full file include `fadvise64`. Prominent constants include `SPDX`, `GPL`, `LONG_MAX`, `INT_MAX`, `LINUX_MIPSN32`, `LINUX_MIPSO32`, `LL_VAL_TO_PAIR`, `X32`, `POWERPC`, `POSIX_FADV_`, `SKIP_MAIN_UNDEFINED`; prominent struct names include none detected.

Control flow: this file is a shared implementation or variant wrapper; compile-time macros select the syscall number, xlat style, fd/path mode, success behavior, or namespace mode before the included/shared test body runs.

State and persistence behavior: runtime state is intentionally temporary and test-local. Most state lives in stack variables, tail-allocated buffers, compile-time macros, and errno/return-code snapshots.

Dependencies: strace test harness headers such as `tests.h`, `scno.h`, `print_utils.h`, `pidns.h`, `secontext.h`, local xlat tables, libc headers, and Linux UAPI headers provide syscall numbers, fallback structs, constants, and output helpers. This file directly includes `tests.h`, `scno.h`, `fadvise.h`.

Integration points: the file participates in strace's testsuite as a compiled C test, AWK normalizer, header, or generator input. It integrates with generated xlat tables, syscall-number selection, test-driver `.test` scripts, and expected-output comparison.

Risks: Primary risks are kernel/architecture feature availability, ABI-width differences, host header drift, permissions, namespace-dependent pid/fd/path rendering, and expected-output brittleness when symbolic constants change.

Test signals: useful validation is the corresponding strace testsuite target under the same basename, comparison of stdout against expected decoder lines, successful compilation under the configured personality/time ABI, and skip behavior when the kernel lacks the syscall or permission. The source was read in full for this report: 57 lines, 1533 bytes, sha256 prefix `9e4b75a9e827`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/fadvise64.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/fadvise64_64.c -->
# sources/test-tools/strace/tests/fadvise64_64.c

Purpose: `fadvise64_64.c` covers fadvise64/fadvise64_64 argument layout and advice-name decoding across ABI layouts.

Important APIs/types/functions: local functions include `do_fadvise`; macros include `__NR_fadvise64_64`; included headers include `tests.h`, `scno.h`, `fadvise.h`. Kernel/user ABI names observed in the full file include none detected. Prominent constants include `SPDX`, `GPL`, `LONG_MAX`, `INT_MAX`, `LINUX_MIPSN32`, `POWERPC`, `XTENSA`, `LL_VAL_TO_PAIR`, `POSIX_FADV_`, `SKIP_MAIN_UNDEFINED`; prominent struct names include none detected.

Control flow: this file is a shared implementation or variant wrapper; compile-time macros select the syscall number, xlat style, fd/path mode, success behavior, or namespace mode before the included/shared test body runs.

State and persistence behavior: runtime state is intentionally temporary and test-local. Most state lives in stack variables, tail-allocated buffers, compile-time macros, and errno/return-code snapshots.

Dependencies: strace test harness headers such as `tests.h`, `scno.h`, `print_utils.h`, `pidns.h`, `secontext.h`, local xlat tables, libc headers, and Linux UAPI headers provide syscall numbers, fallback structs, constants, and output helpers. This file directly includes `tests.h`, `scno.h`, `fadvise.h`.

Integration points: the file participates in strace's testsuite as a compiled C test, AWK normalizer, header, or generator input. It integrates with generated xlat tables, syscall-number selection, test-driver `.test` scripts, and expected-output comparison.

Risks: Primary risks are kernel/architecture feature availability, ABI-width differences, host header drift, permissions, namespace-dependent pid/fd/path rendering, and expected-output brittleness when symbolic constants change.

Test signals: useful validation is the corresponding strace testsuite target under the same basename, comparison of stdout against expected decoder lines, successful compilation under the configured personality/time ABI, and skip behavior when the kernel lacks the syscall or permission. The source was read in full for this report: 55 lines, 1359 bytes, sha256 prefix `ea398b4df329`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/fadvise64_64.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/fallocate.c -->
# sources/test-tools/strace/tests/fallocate.c

Purpose: `fallocate.c` tests fallocate mode flags and offset/length argument rendering.

Important APIs/types/functions: local functions include `main`; macros include none detected; included headers include `tests.h`, `scno.h`, `errno.h`, `fcntl.h`, `stdio.h`, `linux/falloc.h`, `xlat.h`, `xlat/falloc_flags.h`. Kernel/user ABI names observed in the full file include `fallocate`, `fcntl`. Prominent constants include `SPDX`, `GPL`, `HAVE_FALLOCATE`, `FALLOC_FL_WRITE_ZEROES`, `FALLOC_FL_KEEP_SIZE`, `FALLOC_FL_PUNCH_HOLE`, `FALLOC_FL_NO_HIDE_STALE`, `FALLOC_FL_COLLAPSE_RANGE`, `FALLOC_FL_ZERO_RANGE`, ... (13 total), `FALLOC_FL_UNSHARE_RANGE`, `FALLOC_FL_`, `SKIP_MAIN_UNDEFINED`; prominent struct names include none detected.

Control flow: `main` builds deterministic arguments, invokes the target syscall or helper sequence, prints the expected strace line with `printf`/test helpers, and exits through the strace test harness.

State and persistence behavior: runtime state is intentionally temporary and test-local. Most state lives in stack variables, tail-allocated buffers, compile-time macros, and errno/return-code snapshots.

Dependencies: strace test harness headers such as `tests.h`, `scno.h`, `print_utils.h`, `pidns.h`, `secontext.h`, local xlat tables, libc headers, and Linux UAPI headers provide syscall numbers, fallback structs, constants, and output helpers. This file directly includes `tests.h`, `scno.h`, `errno.h`, `fcntl.h`, `stdio.h`, `linux/falloc.h`, `xlat.h`, `xlat/falloc_flags.h`.

Integration points: the file participates in strace's testsuite as a compiled C test, AWK normalizer, header, or generator input. It integrates with generated xlat tables, syscall-number selection, test-driver `.test` scripts, and expected-output comparison.

Risks: Primary risks are kernel/architecture feature availability, ABI-width differences, host header drift, permissions, namespace-dependent pid/fd/path rendering, and expected-output brittleness when symbolic constants change.

Test signals: useful validation is the corresponding strace testsuite target under the same basename, comparison of stdout against expected decoder lines, successful compilation under the configured personality/time ABI, and skip behavior when the kernel lacks the syscall or permission. The source was read in full for this report: 68 lines, 1587 bytes, sha256 prefix `1e05c1b3b286`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/fallocate.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/fanotify_init.c -->
# sources/test-tools/strace/tests/fanotify_init.c

Purpose: `fanotify_init.c` covers fanotify_init and fanotify_mark decoding, including init flags, event masks, mark flags, fd/path variants, and xlat verbosity.

Important APIs/types/functions: local functions include `do_call`, `main`; macros include none detected; included headers include `tests.h`, `scno.h`, `limits.h`, `stdio.h`, `unistd.h`. Kernel/user ABI names observed in the full file include `fanotify_init`. Prominent constants include `SPDX`, `GPL`, `F8ILL_KULONG_MASK`, `FAN_CLASS_NOTIF`, `FAN_CLASS_`, `FAN_CLASS_CONTENT`, `FAN_`, `FAN_CLOEXEC`, `FAN_NONBLOCK`, ... (23 total), `O_RDONLY`, `O_WRONLY`, `ARRAY_SIZE`; prominent struct names include `strval`.

Control flow: `main` builds deterministic arguments, invokes the target syscall or helper sequence, prints the expected strace line with `printf`/test helpers, and exits through the strace test harness. Variant wrappers select xlat verbosity while the main implementation iterates mark/init flags and fd/path combinations.

State and persistence behavior: runtime state is intentionally temporary and test-local. Most state lives in stack variables, tail-allocated buffers, compile-time macros, and errno/return-code snapshots.

Dependencies: strace test harness headers such as `tests.h`, `scno.h`, `print_utils.h`, `pidns.h`, `secontext.h`, local xlat tables, libc headers, and Linux UAPI headers provide syscall numbers, fallback structs, constants, and output helpers. This file directly includes `tests.h`, `scno.h`, `limits.h`, `stdio.h`, `unistd.h`.

Integration points: the file participates in strace's testsuite as a compiled C test, AWK normalizer, header, or generator input. It integrates with generated xlat tables, syscall-number selection, test-driver `.test` scripts, and expected-output comparison.

Risks: fanotify availability and permission restrictions vary by kernel and credentials, making graceful skip/error handling as important as the printed mask text.

Test signals: useful validation is the corresponding strace testsuite target under the same basename, comparison of stdout against expected decoder lines, successful compilation under the configured personality/time ABI, and skip behavior when the kernel lacks the syscall or permission. The source was read in full for this report: 67 lines, 1778 bytes, sha256 prefix `33e9b6ab52db`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/fanotify_init.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/fanotify_mark-Xabbrev.c -->
# sources/test-tools/strace/tests/fanotify_mark-Xabbrev.c

Purpose: `fanotify_mark-Xabbrev.c` covers fanotify_init and fanotify_mark decoding, including init flags, event masks, mark flags, fd/path variants, and xlat verbosity.

Important APIs/types/functions: local functions include none detected; macros include none detected; included headers include `fanotify_mark.c`. Kernel/user ABI names observed in the full file include `fanotify_mark`. Prominent constants include none detected; prominent struct names include none detected.

Control flow: this file is a shared implementation or variant wrapper; compile-time macros select the syscall number, xlat style, fd/path mode, success behavior, or namespace mode before the included/shared test body runs. Variant wrappers select xlat verbosity while the main implementation iterates mark/init flags and fd/path combinations.  This is a wrapper/variant file that reuses shared test implementation through local includes: `fanotify_mark.c`.

State and persistence behavior: runtime state is intentionally temporary and test-local. Most state lives in stack variables, tail-allocated buffers, compile-time macros, and errno/return-code snapshots.

Dependencies: strace test harness headers such as `tests.h`, `scno.h`, `print_utils.h`, `pidns.h`, `secontext.h`, local xlat tables, libc headers, and Linux UAPI headers provide syscall numbers, fallback structs, constants, and output helpers. This file directly includes `fanotify_mark.c`.

Integration points: the file participates in strace's testsuite as a compiled C test, AWK normalizer, header, or generator input. It integrates with generated xlat tables, syscall-number selection, test-driver `.test` scripts, and expected-output comparison. Its filename selects an xlat rendering mode, so the same syscall surface is compared under abbreviated, raw, or verbose symbolic output.

Risks: fanotify availability and permission restrictions vary by kernel and credentials, making graceful skip/error handling as important as the printed mask text.

Test signals: useful validation is the corresponding strace testsuite target under the same basename, comparison of stdout against expected decoder lines, successful compilation under the configured personality/time ABI, and skip behavior when the kernel lacks the syscall or permission. The source was read in full for this report: 1 lines, 27 bytes, sha256 prefix `f0bc4f0269bc`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/fanotify_mark-Xabbrev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/fanotify_mark-Xraw.c -->
# sources/test-tools/strace/tests/fanotify_mark-Xraw.c

Purpose: `fanotify_mark-Xraw.c` covers fanotify_init and fanotify_mark decoding, including init flags, event masks, mark flags, fd/path variants, and xlat verbosity.

Important APIs/types/functions: local functions include none detected; macros include `XLAT_RAW`; included headers include `fanotify_mark.c`. Kernel/user ABI names observed in the full file include `fanotify_mark`. Prominent constants include `XLAT_RAW`; prominent struct names include none detected.

Control flow: this file is a shared implementation or variant wrapper; compile-time macros select the syscall number, xlat style, fd/path mode, success behavior, or namespace mode before the included/shared test body runs. Variant wrappers select xlat verbosity while the main implementation iterates mark/init flags and fd/path combinations.  This is a wrapper/variant file that reuses shared test implementation through local includes: `fanotify_mark.c`.

State and persistence behavior: runtime state is intentionally temporary and test-local. Most state lives in stack variables, tail-allocated buffers, compile-time macros, and errno/return-code snapshots.

Dependencies: strace test harness headers such as `tests.h`, `scno.h`, `print_utils.h`, `pidns.h`, `secontext.h`, local xlat tables, libc headers, and Linux UAPI headers provide syscall numbers, fallback structs, constants, and output helpers. This file directly includes `fanotify_mark.c`.

Integration points: the file participates in strace's testsuite as a compiled C test, AWK normalizer, header, or generator input. It integrates with generated xlat tables, syscall-number selection, test-driver `.test` scripts, and expected-output comparison. Its filename selects an xlat rendering mode, so the same syscall surface is compared under abbreviated, raw, or verbose symbolic output.

Risks: fanotify availability and permission restrictions vary by kernel and credentials, making graceful skip/error handling as important as the printed mask text.

Test signals: useful validation is the corresponding strace testsuite target under the same basename, comparison of stdout against expected decoder lines, successful compilation under the configured personality/time ABI, and skip behavior when the kernel lacks the syscall or permission. The source was read in full for this report: 2 lines, 46 bytes, sha256 prefix `85f4c674dcc5`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/fanotify_mark-Xraw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/fanotify_mark-Xverbose.c -->
# sources/test-tools/strace/tests/fanotify_mark-Xverbose.c

Purpose: `fanotify_mark-Xverbose.c` covers fanotify_init and fanotify_mark decoding, including init flags, event masks, mark flags, fd/path variants, and xlat verbosity.

Important APIs/types/functions: local functions include none detected; macros include `XLAT_VERBOSE`; included headers include `fanotify_mark.c`. Kernel/user ABI names observed in the full file include `fanotify_mark`. Prominent constants include `XLAT_VERBOSE`; prominent struct names include none detected.

Control flow: this file is a shared implementation or variant wrapper; compile-time macros select the syscall number, xlat style, fd/path mode, success behavior, or namespace mode before the included/shared test body runs. Variant wrappers select xlat verbosity while the main implementation iterates mark/init flags and fd/path combinations.  This is a wrapper/variant file that reuses shared test implementation through local includes: `fanotify_mark.c`.

State and persistence behavior: runtime state is intentionally temporary and test-local. Most state lives in stack variables, tail-allocated buffers, compile-time macros, and errno/return-code snapshots.

Dependencies: strace test harness headers such as `tests.h`, `scno.h`, `print_utils.h`, `pidns.h`, `secontext.h`, local xlat tables, libc headers, and Linux UAPI headers provide syscall numbers, fallback structs, constants, and output helpers. This file directly includes `fanotify_mark.c`.

Integration points: the file participates in strace's testsuite as a compiled C test, AWK normalizer, header, or generator input. It integrates with generated xlat tables, syscall-number selection, test-driver `.test` scripts, and expected-output comparison. Its filename selects an xlat rendering mode, so the same syscall surface is compared under abbreviated, raw, or verbose symbolic output.

Risks: fanotify availability and permission restrictions vary by kernel and credentials, making graceful skip/error handling as important as the printed mask text.

Test signals: useful validation is the corresponding strace testsuite target under the same basename, comparison of stdout against expected decoder lines, successful compilation under the configured personality/time ABI, and skip behavior when the kernel lacks the syscall or permission. The source was read in full for this report: 2 lines, 50 bytes, sha256 prefix `3a948558bbce`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/fanotify_mark-Xverbose.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/fanotify_mark.c -->
# sources/test-tools/strace/tests/fanotify_mark.c

Purpose: `fanotify_mark.c` covers fanotify_init and fanotify_mark decoding, including init flags, event masks, mark flags, fd/path variants, and xlat verbosity.

Important APIs/types/functions: local functions include `do_call`, `main`; macros include `str_fan_mark_add`, `str_fan_modify_ondir`, `str_at_fdcwd`, `STR16`, `STR64`; included headers include `tests.h`, `scno.h`, `limits.h`, `stdint.h`, `stdio.h`, `unistd.h`, `sys/fanotify.h`, `secontext.h`. Kernel/user ABI names observed in the full file include `fanotify_mark`. Prominent constants include `SPDX`, `GPL`, `HAVE_SYS_FANOTIFY_H`, `HAVE_FANOTIFY_MARK`, `XLAT_RAW`, `XLAT_VERBOSE`, `FAN_MARK_ADD`, `FAN_MODIFY`, `FAN_ONDIR`, ... (62 total), `SECONTEXT_PID_MY`, `SECONTEXT_FILE`, `SKIP_MAIN_UNDEFINED`; prominent struct names include `strval`, `strval64`.

Control flow: `main` builds deterministic arguments, invokes the target syscall or helper sequence, prints the expected strace line with `printf`/test helpers, and exits through the strace test harness. Variant wrappers select xlat verbosity while the main implementation iterates mark/init flags and fd/path combinations.

State and persistence behavior: runtime state is intentionally temporary and test-local. Most state lives in stack variables, tail-allocated buffers, compile-time macros, and errno/return-code snapshots.

Dependencies: strace test harness headers such as `tests.h`, `scno.h`, `print_utils.h`, `pidns.h`, `secontext.h`, local xlat tables, libc headers, and Linux UAPI headers provide syscall numbers, fallback structs, constants, and output helpers. This file directly includes `tests.h`, `scno.h`, `limits.h`, `stdint.h`, `stdio.h`, `unistd.h`, `sys/fanotify.h`, `secontext.h`.

Integration points: the file participates in strace's testsuite as a compiled C test, AWK normalizer, header, or generator input. It integrates with generated xlat tables, syscall-number selection, test-driver `.test` scripts, and expected-output comparison.

Risks: fanotify availability and permission restrictions vary by kernel and credentials, making graceful skip/error handling as important as the printed mask text.

Test signals: useful validation is the corresponding strace testsuite target under the same basename, comparison of stdout against expected decoder lines, successful compilation under the configured personality/time ABI, and skip behavior when the kernel lacks the syscall or permission. The source was read in full for this report: 283 lines, 6813 bytes, sha256 prefix `6358a0905d14`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/fanotify_mark.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/fchdir.c -->
# sources/test-tools/strace/tests/fchdir.c

Purpose: `fchdir.c` checks directory-changing or root-changing syscall decoding, including path rendering and failure paths.

Important APIs/types/functions: local functions include `main`; macros include none detected; included headers include `tests.h`, `scno.h`, `stdio.h`, `unistd.h`. Kernel/user ABI names observed in the full file include `fchdir`. Prominent constants include `SPDX`, `GPL`; prominent struct names include none detected.

Control flow: `main` builds deterministic arguments, invokes the target syscall or helper sequence, prints the expected strace line with `printf`/test helpers, and exits through the strace test harness.  This is a wrapper/variant file that reuses shared test implementation through local includes: `tests.h`, `scno.h`.

State and persistence behavior: runtime state is intentionally temporary and test-local. Most state lives in stack variables, tail-allocated buffers, compile-time macros, and errno/return-code snapshots.

Dependencies: strace test harness headers such as `tests.h`, `scno.h`, `print_utils.h`, `pidns.h`, `secontext.h`, local xlat tables, libc headers, and Linux UAPI headers provide syscall numbers, fallback structs, constants, and output helpers. This file directly includes `tests.h`, `scno.h`, `stdio.h`, `unistd.h`.

Integration points: the file participates in strace's testsuite as a compiled C test, AWK normalizer, header, or generator input. It integrates with generated xlat tables, syscall-number selection, test-driver `.test` scripts, and expected-output comparison.

Risks: Primary risks are kernel/architecture feature availability, ABI-width differences, host header drift, permissions, namespace-dependent pid/fd/path rendering, and expected-output brittleness when symbolic constants change.

Test signals: useful validation is the corresponding strace testsuite target under the same basename, comparison of stdout against expected decoder lines, successful compilation under the configured personality/time ABI, and skip behavior when the kernel lacks the syscall or permission. The source was read in full for this report: 26 lines, 461 bytes, sha256 prefix `9528b3d2e0ac`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/fchdir.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/fchmod-y.c -->
# sources/test-tools/strace/tests/fchmod-y.c

Purpose: `fchmod-y.c` validates mode-changing syscall decoders and their path/fd variants, including octal mode output and flag handling.

Important APIs/types/functions: local functions include none detected; macros include `YFLAG`; included headers include `fchmod.c`. Kernel/user ABI names observed in the full file include `fchmod`. Prominent constants include `SPDX`, `GPL`, `YFLAG`; prominent struct names include none detected.

Control flow: this file is a shared implementation or variant wrapper; compile-time macros select the syscall number, xlat style, fd/path mode, success behavior, or namespace mode before the included/shared test body runs. The path/fd variants allocate stable pathnames or descriptors, run failing and successful forms where possible, and print both symbolic flags and raw fallback bits.  This is a wrapper/variant file that reuses shared test implementation through local includes: `fchmod.c`.

State and persistence behavior: runtime state is intentionally temporary and test-local. Most state lives in stack variables, tail-allocated buffers, compile-time macros, and errno/return-code snapshots.

Dependencies: strace test harness headers such as `tests.h`, `scno.h`, `print_utils.h`, `pidns.h`, `secontext.h`, local xlat tables, libc headers, and Linux UAPI headers provide syscall numbers, fallback structs, constants, and output helpers. This file directly includes `fchmod.c`.

Integration points: the file participates in strace's testsuite as a compiled C test, AWK normalizer, header, or generator input. It integrates with generated xlat tables, syscall-number selection, test-driver `.test` scripts, and expected-output comparison. The variant also exercises path/fd decoding options such as `-P`, `-y`, `-yy`, or `--decode-fds`.

Risks: Primary risks are kernel/architecture feature availability, ABI-width differences, host header drift, permissions, namespace-dependent pid/fd/path rendering, and expected-output brittleness when symbolic constants change.

Test signals: useful validation is the corresponding strace testsuite target under the same basename, comparison of stdout against expected decoder lines, successful compilation under the configured personality/time ABI, and skip behavior when the kernel lacks the syscall or permission. The source was read in full for this report: 10 lines, 160 bytes, sha256 prefix `153a7f4f7e8e`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/fchmod-y.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/fchmod.c -->
# sources/test-tools/strace/tests/fchmod.c

Purpose: `fchmod.c` validates mode-changing syscall decoders and their path/fd variants, including octal mode output and flag handling.

Important APIs/types/functions: local functions include `main`; macros include none detected; included headers include `tests.h`, `scno.h`, `fcntl.h`, `stdio.h`, `unistd.h`, `secontext.h`. Kernel/user ABI names observed in the full file include `fchmod`, `fcntl`. Prominent constants include `SPDX`, `GPL`, `SECONTEXT_PID_MY`, `O_CREAT`, `O_RDONLY`, `YFLAG`, `SECONTEXT_FILE`, `SKIP_MAIN_UNDEFINED`; prominent struct names include none detected.

Control flow: `main` builds deterministic arguments, invokes the target syscall or helper sequence, prints the expected strace line with `printf`/test helpers, and exits through the strace test harness. The path/fd variants allocate stable pathnames or descriptors, run failing and successful forms where possible, and print both symbolic flags and raw fallback bits.

State and persistence behavior: runtime state is intentionally temporary and test-local. The test may allocate tail buffers and/or create temporary files, directories, descriptors, sockets, eventfds, epoll instances, or mount/file handles, then relies on process exit or explicit cleanup for disposal.

Dependencies: strace test harness headers such as `tests.h`, `scno.h`, `print_utils.h`, `pidns.h`, `secontext.h`, local xlat tables, libc headers, and Linux UAPI headers provide syscall numbers, fallback structs, constants, and output helpers. This file directly includes `tests.h`, `scno.h`, `fcntl.h`, `stdio.h`, `unistd.h`, `secontext.h`.

Integration points: the file participates in strace's testsuite as a compiled C test, AWK normalizer, header, or generator input. It integrates with generated xlat tables, syscall-number selection, test-driver `.test` scripts, and expected-output comparison.

Risks: Primary risks are kernel/architecture feature availability, ABI-width differences, host header drift, permissions, namespace-dependent pid/fd/path rendering, and expected-output brittleness when symbolic constants change.

Test signals: useful validation is the corresponding strace testsuite target under the same basename, comparison of stdout against expected decoder lines, successful compilation under the configured personality/time ABI, and skip behavior when the kernel lacks the syscall or permission. The source was read in full for this report: 139 lines, 3025 bytes, sha256 prefix `30f7c259009a`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/fchmod.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/fchmodat.c -->
# sources/test-tools/strace/tests/fchmodat.c

Purpose: `fchmodat.c` validates mode-changing syscall decoders and their path/fd variants, including octal mode output and flag handling.

Important APIs/types/functions: local functions include `main`; macros include none detected; included headers include `tests.h`, `scno.h`, `fcntl.h`, `stdio.h`, `unistd.h`, `secontext.h`. Kernel/user ABI names observed in the full file include `chdir`, `fchdir`, `fchmodat`, `fcntl`. Prominent constants include `SPDX`, `GPL`, `SECONTEXT_PID_MY`, `O_RDONLY`, `O_CREAT`, `SECONTEXT_FILE`, `AT_FDCWD`; prominent struct names include none detected.

Control flow: `main` builds deterministic arguments, invokes the target syscall or helper sequence, prints the expected strace line with `printf`/test helpers, and exits through the strace test harness. The path/fd variants allocate stable pathnames or descriptors, run failing and successful forms where possible, and print both symbolic flags and raw fallback bits.

State and persistence behavior: runtime state is intentionally temporary and test-local. The test may allocate tail buffers and/or create temporary files, directories, descriptors, sockets, eventfds, epoll instances, or mount/file handles, then relies on process exit or explicit cleanup for disposal.

Dependencies: strace test harness headers such as `tests.h`, `scno.h`, `print_utils.h`, `pidns.h`, `secontext.h`, local xlat tables, libc headers, and Linux UAPI headers provide syscall numbers, fallback structs, constants, and output helpers. This file directly includes `tests.h`, `scno.h`, `fcntl.h`, `stdio.h`, `unistd.h`, `secontext.h`.

Integration points: the file participates in strace's testsuite as a compiled C test, AWK normalizer, header, or generator input. It integrates with generated xlat tables, syscall-number selection, test-driver `.test` scripts, and expected-output comparison.

Risks: Primary risks are kernel/architecture feature availability, ABI-width differences, host header drift, permissions, namespace-dependent pid/fd/path rendering, and expected-output brittleness when symbolic constants change.

Test signals: useful validation is the corresponding strace testsuite target under the same basename, comparison of stdout against expected decoder lines, successful compilation under the configured personality/time ABI, and skip behavior when the kernel lacks the syscall or permission. The source was read in full for this report: 108 lines, 2602 bytes, sha256 prefix `b2bc6c95f3c9`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/fchmodat.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/fchmodat2.c -->
# sources/test-tools/strace/tests/fchmodat2.c

Purpose: `fchmodat2.c` validates mode-changing syscall decoders and their path/fd variants, including octal mode output and flag handling.

Important APIs/types/functions: local functions include `k_fchmodat2`, `main`; macros include `AT_SYMLINK_NOFOLLOW`, `AT_EMPTY_PATH`; included headers include `tests.h`, `scno.h`, `secontext.h`, `fcntl.h`, `stdio.h`, `unistd.h`. Kernel/user ABI names observed in the full file include `chdir`, `fchdir`, `fchmodat2`, `fcntl`. Prominent constants include `SPDX`, `GPL`, `AT_SYMLINK_NOFOLLOW`, `AT_EMPTY_PATH`, `SECONTEXT_PID_MY`, `O_RDONLY`, `O_CREAT`, `SECONTEXT_FILE`, `AT_FDCWD`, `AT_`; prominent struct names include none detected.

Control flow: `main` builds deterministic arguments, invokes the target syscall or helper sequence, prints the expected strace line with `printf`/test helpers, and exits through the strace test harness. The path/fd variants allocate stable pathnames or descriptors, run failing and successful forms where possible, and print both symbolic flags and raw fallback bits.

State and persistence behavior: runtime state is intentionally temporary and test-local. The test may allocate tail buffers and/or create temporary files, directories, descriptors, sockets, eventfds, epoll instances, or mount/file handles, then relies on process exit or explicit cleanup for disposal.

Dependencies: strace test harness headers such as `tests.h`, `scno.h`, `print_utils.h`, `pidns.h`, `secontext.h`, local xlat tables, libc headers, and Linux UAPI headers provide syscall numbers, fallback structs, constants, and output helpers. This file directly includes `tests.h`, `scno.h`, `secontext.h`, `fcntl.h`, `stdio.h`, `unistd.h`.

Integration points: the file participates in strace's testsuite as a compiled C test, AWK normalizer, header, or generator input. It integrates with generated xlat tables, syscall-number selection, test-driver `.test` scripts, and expected-output comparison.

Risks: Primary risks are kernel/architecture feature availability, ABI-width differences, host header drift, permissions, namespace-dependent pid/fd/path rendering, and expected-output brittleness when symbolic constants change.

Test signals: useful validation is the corresponding strace testsuite target under the same basename, comparison of stdout against expected decoder lines, successful compilation under the configured personality/time ABI, and skip behavior when the kernel lacks the syscall or permission. The source was read in full for this report: 131 lines, 3601 bytes, sha256 prefix `7ac789117814`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/fchmodat2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/fchown.c -->
# sources/test-tools/strace/tests/fchown.c

Purpose: `fchown.c` validates ownership-changing syscall decoders and 32-bit compatibility variants, including uid/gid sentinel and path/fd forms.

Important APIs/types/functions: local functions include none detected; macros include `SYSCALL_NR`, `SYSCALL_NAME`, `ACCESS_BY_DESCRIPTOR`, `UGID_TYPE_IS_SHORT`; included headers include `tests.h`, `scno.h`, `xchownx.c`. Kernel/user ABI names observed in the full file include `fchown`. Prominent constants include `SPDX`, `GPL`, `SYSCALL_NR`, `SYSCALL_NAME`, `ACCESS_BY_DESCRIPTOR`, `UGID_TYPE_IS_SHORT`, `SKIP_MAIN_UNDEFINED`; prominent struct names include none detected.

Control flow: this file is a shared implementation or variant wrapper; compile-time macros select the syscall number, xlat style, fd/path mode, success behavior, or namespace mode before the included/shared test body runs. The path/fd variants allocate stable pathnames or descriptors, run failing and successful forms where possible, and print both symbolic flags and raw fallback bits.  This is a wrapper/variant file that reuses shared test implementation through local includes: `tests.h`, `scno.h`, `xchownx.c`.

State and persistence behavior: runtime state is intentionally temporary and test-local. Most state lives in stack variables, tail-allocated buffers, compile-time macros, and errno/return-code snapshots.

Dependencies: strace test harness headers such as `tests.h`, `scno.h`, `print_utils.h`, `pidns.h`, `secontext.h`, local xlat tables, libc headers, and Linux UAPI headers provide syscall numbers, fallback structs, constants, and output helpers. This file directly includes `tests.h`, `scno.h`, `xchownx.c`.

Integration points: the file participates in strace's testsuite as a compiled C test, AWK normalizer, header, or generator input. It integrates with generated xlat tables, syscall-number selection, test-driver `.test` scripts, and expected-output comparison.

Risks: Primary risks are kernel/architecture feature availability, ABI-width differences, host header drift, permissions, namespace-dependent pid/fd/path rendering, and expected-output brittleness when symbolic constants change.

Test signals: useful validation is the corresponding strace testsuite target under the same basename, comparison of stdout against expected decoder lines, successful compilation under the configured personality/time ABI, and skip behavior when the kernel lacks the syscall or permission. The source was read in full for this report: 27 lines, 452 bytes, sha256 prefix `c9bc95453783`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/fchown.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/fchown32.c -->
# sources/test-tools/strace/tests/fchown32.c

Purpose: `fchown32.c` validates ownership-changing syscall decoders and 32-bit compatibility variants, including uid/gid sentinel and path/fd forms.

Important APIs/types/functions: local functions include none detected; macros include `SYSCALL_NR`, `SYSCALL_NAME`, `ACCESS_BY_DESCRIPTOR`; included headers include `tests.h`, `scno.h`, `xchownx.c`. Kernel/user ABI names observed in the full file include none detected. Prominent constants include `SPDX`, `GPL`, `SYSCALL_NR`, `SYSCALL_NAME`, `ACCESS_BY_DESCRIPTOR`, `SKIP_MAIN_UNDEFINED`; prominent struct names include none detected.

Control flow: this file is a shared implementation or variant wrapper; compile-time macros select the syscall number, xlat style, fd/path mode, success behavior, or namespace mode before the included/shared test body runs. The path/fd variants allocate stable pathnames or descriptors, run failing and successful forms where possible, and print both symbolic flags and raw fallback bits.  This is a wrapper/variant file that reuses shared test implementation through local includes: `tests.h`, `scno.h`, `xchownx.c`.

State and persistence behavior: runtime state is intentionally temporary and test-local. Most state lives in stack variables, tail-allocated buffers, compile-time macros, and errno/return-code snapshots.

Dependencies: strace test harness headers such as `tests.h`, `scno.h`, `print_utils.h`, `pidns.h`, `secontext.h`, local xlat tables, libc headers, and Linux UAPI headers provide syscall numbers, fallback structs, constants, and output helpers. This file directly includes `tests.h`, `scno.h`, `xchownx.c`.

Integration points: the file participates in strace's testsuite as a compiled C test, AWK normalizer, header, or generator input. It integrates with generated xlat tables, syscall-number selection, test-driver `.test` scripts, and expected-output comparison.

Risks: Primary risks are kernel/architecture feature availability, ABI-width differences, host header drift, permissions, namespace-dependent pid/fd/path rendering, and expected-output brittleness when symbolic constants change.

Test signals: useful validation is the corresponding strace testsuite target under the same basename, comparison of stdout against expected decoder lines, successful compilation under the configured personality/time ABI, and skip behavior when the kernel lacks the syscall or permission. The source was read in full for this report: 22 lines, 362 bytes, sha256 prefix `93ef691a7c5c`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/fchown32.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/fchownat.c -->
# sources/test-tools/strace/tests/fchownat.c

Purpose: `fchownat.c` validates ownership-changing syscall decoders and 32-bit compatibility variants, including uid/gid sentinel and path/fd forms.

Important APIs/types/functions: local functions include `main`; macros include none detected; included headers include `tests.h`, `scno.h`, `fcntl.h`, `stdio.h`, `unistd.h`, `secontext.h`. Kernel/user ABI names observed in the full file include `chdir`, `fchdir`, `fchownat`, `fcntl`. Prominent constants include `SPDX`, `GPL`, `AT_FDCWD`, `AT_SYMLINK_NOFOLLOW`, `SECONTEXT_PID_MY`, `O_RDONLY`, `O_CREAT`, `SECONTEXT_FILE`, `SKIP_MAIN_UNDEFINED`; prominent struct names include none detected.

Control flow: `main` builds deterministic arguments, invokes the target syscall or helper sequence, prints the expected strace line with `printf`/test helpers, and exits through the strace test harness. The path/fd variants allocate stable pathnames or descriptors, run failing and successful forms where possible, and print both symbolic flags and raw fallback bits.

State and persistence behavior: runtime state is intentionally temporary and test-local. The test may allocate tail buffers and/or create temporary files, directories, descriptors, sockets, eventfds, epoll instances, or mount/file handles, then relies on process exit or explicit cleanup for disposal.

Dependencies: strace test harness headers such as `tests.h`, `scno.h`, `print_utils.h`, `pidns.h`, `secontext.h`, local xlat tables, libc headers, and Linux UAPI headers provide syscall numbers, fallback structs, constants, and output helpers. This file directly includes `tests.h`, `scno.h`, `fcntl.h`, `stdio.h`, `unistd.h`, `secontext.h`.

Integration points: the file participates in strace's testsuite as a compiled C test, AWK normalizer, header, or generator input. It integrates with generated xlat tables, syscall-number selection, test-driver `.test` scripts, and expected-output comparison.

Risks: Primary risks are kernel/architecture feature availability, ABI-width differences, host header drift, permissions, namespace-dependent pid/fd/path rendering, and expected-output brittleness when symbolic constants change.

Test signals: useful validation is the corresponding strace testsuite target under the same basename, comparison of stdout against expected decoder lines, successful compilation under the configured personality/time ABI, and skip behavior when the kernel lacks the syscall or permission. The source was read in full for this report: 121 lines, 2839 bytes, sha256 prefix `697e35dfbd8c`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/fchownat.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/fcntl--pidns-translation.c -->
# sources/test-tools/strace/tests/fcntl--pidns-translation.c

Purpose: `fcntl--pidns-translation.c` is shared or variant coverage for fcntl/fcntl64 command decoding, flock structures, owner records, seals, leases, pipe size, pid namespace translation, and unknown commands.

Important APIs/types/functions: local functions include none detected; macros include `PIDNS_TRANSLATION`; included headers include `fcntl.c`. Kernel/user ABI names observed in the full file include `fcntl`. Prominent constants include `PIDNS_TRANSLATION`; prominent struct names include none detected.

Control flow: this file is a shared implementation or variant wrapper; compile-time macros select the syscall number, xlat style, fd/path mode, success behavior, or namespace mode before the included/shared test body runs. The common fcntl body dispatches command-specific helpers for flock, flock64/OFD, ownership, seals, leases, pipe sizing, and unknown commands; pid namespace helpers prepend translated pid context when enabled.  This is a wrapper/variant file that reuses shared test implementation through local includes: `fcntl.c`.

State and persistence behavior: runtime state is intentionally temporary and test-local. Most state lives in stack variables, tail-allocated buffers, compile-time macros, and errno/return-code snapshots.

Dependencies: strace test harness headers such as `tests.h`, `scno.h`, `print_utils.h`, `pidns.h`, `secontext.h`, local xlat tables, libc headers, and Linux UAPI headers provide syscall numbers, fallback structs, constants, and output helpers. This file directly includes `fcntl.c`.

Integration points: the file participates in strace's testsuite as a compiled C test, AWK normalizer, header, or generator input. It integrates with generated xlat tables, syscall-number selection, test-driver `.test` scripts, and expected-output comparison.

Risks: fcntl structures differ across ABIs and pid namespace translation changes expected pid text, so offset widths, flock64 availability, and owner pid rendering are the main regression risks.

Test signals: useful validation is the corresponding strace testsuite target under the same basename, comparison of stdout against expected decoder lines, successful compilation under the configured personality/time ABI, and skip behavior when the kernel lacks the syscall or permission. The source was read in full for this report: 2 lines, 45 bytes, sha256 prefix `be42ef508670`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/fcntl--pidns-translation.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/fcntl-common.c -->
# sources/test-tools/strace/tests/fcntl-common.c

Purpose: `fcntl-common.c` is shared or variant coverage for fcntl/fcntl64 command decoding, flock structures, owner records, seals, leases, pipe size, pid namespace translation, and unknown commands.

Important APIs/types/functions: local functions include `invoke_test_syscall`, `test_flock_einval`, `test_flock64_einval`, `test_flock`, `test_flock64_ofd`, `test_flock64_lk64`, `test_flock64`, `test_f_owner_ex_type_pid`, `test_f_owner_ex_umove_or_printaddr`, ... (26 total), `test_fcntl_others`, `create_sample`, `main`; macros include `FILE_LEN`, `TEST_FLOCK_EINVAL`, `TEST_FLOCK64_EINVAL`, `NEED_TEST_FLOCK64_EINVAL`, `TYPEOF_FLOCK_OFF_T`; included headers include `stdio.h`, `stdint.h`, `inttypes.h`, `stdlib.h`, `string.h`, `unistd.h`, `assert.h`, `linux/fcntl.h`, `pidns.h`, `scno.h`. Kernel/user ABI names observed in the full file include `fcntl`. Prominent constants include `SPDX`, `GPL`, `FILE_LEN`, `TEST_FLOCK_EINVAL`, `TEST_FLOCK64_EINVAL`, `NEED_TEST_FLOCK64_EINVAL`, `F_OFD_GETLK`, `F_OFD_SETLK`, `F_OFD_SETLKW`, ... (74 total), `F_GETLEASE`, `F_GETSIG`, `PIDNS_TEST_INIT`; prominent struct names include `flock`, `flock64`, `f_owner_ex`, `fcntl_cmd_check`, `strval64`, `delegation`, `strval32`, `strval16`.

Control flow: `main` builds deterministic arguments, invokes the target syscall or helper sequence, prints the expected strace line with `printf`/test helpers, and exits through the strace test harness. The common fcntl body dispatches command-specific helpers for flock, flock64/OFD, ownership, seals, leases, pipe sizing, and unknown commands; pid namespace helpers prepend translated pid context when enabled.

State and persistence behavior: runtime state is intentionally temporary and test-local. The test may allocate tail buffers and/or create temporary files, directories, descriptors, sockets, eventfds, epoll instances, or mount/file handles, then relies on process exit or explicit cleanup for disposal.

Dependencies: strace test harness headers such as `tests.h`, `scno.h`, `print_utils.h`, `pidns.h`, `secontext.h`, local xlat tables, libc headers, and Linux UAPI headers provide syscall numbers, fallback structs, constants, and output helpers. This file directly includes `stdio.h`, `stdint.h`, `inttypes.h`, `stdlib.h`, `string.h`, `unistd.h`, `assert.h`, `linux/fcntl.h`, `pidns.h`, `scno.h`.

Integration points: the file participates in strace's testsuite as a compiled C test, AWK normalizer, header, or generator input. It integrates with generated xlat tables, syscall-number selection, test-driver `.test` scripts, and expected-output comparison.

Risks: fcntl structures differ across ABIs and pid namespace translation changes expected pid text, so offset widths, flock64 availability, and owner pid rendering are the main regression risks.

Test signals: useful validation is the corresponding strace testsuite target under the same basename, comparison of stdout against expected decoder lines, successful compilation under the configured personality/time ABI, and skip behavior when the kernel lacks the syscall or permission. The source was read in full for this report: 609 lines, 16852 bytes, sha256 prefix `6cb185791b3e`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/fcntl-common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/fcntl.c -->
# sources/test-tools/strace/tests/fcntl.c

Purpose: `fcntl.c` is shared or variant coverage for fcntl/fcntl64 command decoding, flock structures, owner records, seals, leases, pipe size, pid namespace translation, and unknown commands.

Important APIs/types/functions: local functions include `test_flock64_undecoded`, `test_flock64_lk64`; macros include `TEST_SYSCALL_NR`, `TEST_SYSCALL_STR`, `TEST_FLOCK64_UNDECODED`; included headers include `tests.h`, `scno.h`, `fcntl-common.c`. Kernel/user ABI names observed in the full file include `fcntl`. Prominent constants include `SPDX`, `GPL`, `TEST_SYSCALL_NR`, `TEST_SYSCALL_STR`, `F_SETLK64`, `F_GETOWN_EX`, `F_SETLKW64`, `F_GETLK`, `F_GETLK64`, ... (15 total), `ETOWN_EX`, `ETLK64`, `SKIP_MAIN_UNDEFINED`; prominent struct names include `flock64`.

Control flow: this file is a shared implementation or variant wrapper; compile-time macros select the syscall number, xlat style, fd/path mode, success behavior, or namespace mode before the included/shared test body runs. The common fcntl body dispatches command-specific helpers for flock, flock64/OFD, ownership, seals, leases, pipe sizing, and unknown commands; pid namespace helpers prepend translated pid context when enabled.

State and persistence behavior: runtime state is intentionally temporary and test-local. Most state lives in stack variables, tail-allocated buffers, compile-time macros, and errno/return-code snapshots.

Dependencies: strace test harness headers such as `tests.h`, `scno.h`, `print_utils.h`, `pidns.h`, `secontext.h`, local xlat tables, libc headers, and Linux UAPI headers provide syscall numbers, fallback structs, constants, and output helpers. This file directly includes `tests.h`, `scno.h`, `fcntl-common.c`.

Integration points: the file participates in strace's testsuite as a compiled C test, AWK normalizer, header, or generator input. It integrates with generated xlat tables, syscall-number selection, test-driver `.test` scripts, and expected-output comparison.

Risks: fcntl structures differ across ABIs and pid namespace translation changes expected pid text, so offset widths, flock64 availability, and owner pid rendering are the main regression risks.

Test signals: useful validation is the corresponding strace testsuite target under the same basename, comparison of stdout against expected decoder lines, successful compilation under the configured personality/time ABI, and skip behavior when the kernel lacks the syscall or permission. The source was read in full for this report: 62 lines, 1683 bytes, sha256 prefix `1fe22cb569fe`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/fcntl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/fcntl64--pidns-translation.c -->
# sources/test-tools/strace/tests/fcntl64--pidns-translation.c

Purpose: `fcntl64--pidns-translation.c` is shared or variant coverage for fcntl/fcntl64 command decoding, flock structures, owner records, seals, leases, pipe size, pid namespace translation, and unknown commands.

Important APIs/types/functions: local functions include none detected; macros include `PIDNS_TRANSLATION`; included headers include `fcntl64.c`. Kernel/user ABI names observed in the full file include `fcntl64`. Prominent constants include `PIDNS_TRANSLATION`; prominent struct names include none detected.

Control flow: this file is a shared implementation or variant wrapper; compile-time macros select the syscall number, xlat style, fd/path mode, success behavior, or namespace mode before the included/shared test body runs. The common fcntl body dispatches command-specific helpers for flock, flock64/OFD, ownership, seals, leases, pipe sizing, and unknown commands; pid namespace helpers prepend translated pid context when enabled.  This is a wrapper/variant file that reuses shared test implementation through local includes: `fcntl64.c`.

State and persistence behavior: runtime state is intentionally temporary and test-local. Most state lives in stack variables, tail-allocated buffers, compile-time macros, and errno/return-code snapshots.

Dependencies: strace test harness headers such as `tests.h`, `scno.h`, `print_utils.h`, `pidns.h`, `secontext.h`, local xlat tables, libc headers, and Linux UAPI headers provide syscall numbers, fallback structs, constants, and output helpers. This file directly includes `fcntl64.c`.

Integration points: the file participates in strace's testsuite as a compiled C test, AWK normalizer, header, or generator input. It integrates with generated xlat tables, syscall-number selection, test-driver `.test` scripts, and expected-output comparison.

Risks: fcntl structures differ across ABIs and pid namespace translation changes expected pid text, so offset widths, flock64 availability, and owner pid rendering are the main regression risks.

Test signals: useful validation is the corresponding strace testsuite target under the same basename, comparison of stdout against expected decoder lines, successful compilation under the configured personality/time ABI, and skip behavior when the kernel lacks the syscall or permission. The source was read in full for this report: 2 lines, 47 bytes, sha256 prefix `f2b03a0668db`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/fcntl64--pidns-translation.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/fcntl64.c -->
# sources/test-tools/strace/tests/fcntl64.c

Purpose: `fcntl64.c` is shared or variant coverage for fcntl/fcntl64 command decoding, flock structures, owner records, seals, leases, pipe size, pid namespace translation, and unknown commands.

Important APIs/types/functions: local functions include `test_flock64_lk64`; macros include `TEST_SYSCALL_NR`, `TEST_SYSCALL_STR`, `NEED_TEST_FLOCK64_EINVAL`; included headers include `tests.h`, `scno.h`, `fcntl-common.c`. Kernel/user ABI names observed in the full file include `fcntl`, `fcntl64`. Prominent constants include `SPDX`, `GPL`, `TEST_SYSCALL_NR`, `TEST_SYSCALL_STR`, `NEED_TEST_FLOCK64_EINVAL`, `TEST_FLOCK64_EINVAL`, `F_SETLK64`, `F_SETLKW64`, `TAIL_ALLOC_OBJECT_CONST_PTR`, ... (15 total), `F_GETLK64`, `F_UNLCK`, `SKIP_MAIN_UNDEFINED`; prominent struct names include `flock64`.

Control flow: this file is a shared implementation or variant wrapper; compile-time macros select the syscall number, xlat style, fd/path mode, success behavior, or namespace mode before the included/shared test body runs. The common fcntl body dispatches command-specific helpers for flock, flock64/OFD, ownership, seals, leases, pipe sizing, and unknown commands; pid namespace helpers prepend translated pid context when enabled.

State and persistence behavior: runtime state is intentionally temporary and test-local. Most state lives in stack variables, tail-allocated buffers, compile-time macros, and errno/return-code snapshots.

Dependencies: strace test harness headers such as `tests.h`, `scno.h`, `print_utils.h`, `pidns.h`, `secontext.h`, local xlat tables, libc headers, and Linux UAPI headers provide syscall numbers, fallback structs, constants, and output helpers. This file directly includes `tests.h`, `scno.h`, `fcntl-common.c`.

Integration points: the file participates in strace's testsuite as a compiled C test, AWK normalizer, header, or generator input. It integrates with generated xlat tables, syscall-number selection, test-driver `.test` scripts, and expected-output comparison.

Risks: fcntl structures differ across ABIs and pid namespace translation changes expected pid text, so offset widths, flock64 availability, and owner pid rendering are the main regression risks.

Test signals: useful validation is the corresponding strace testsuite target under the same basename, comparison of stdout against expected decoder lines, successful compilation under the configured personality/time ABI, and skip behavior when the kernel lacks the syscall or permission. The source was read in full for this report: 56 lines, 1331 bytes, sha256 prefix `64bf3536173a`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/fcntl64.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/fdatasync.c -->
# sources/test-tools/strace/tests/fdatasync.c

Purpose: `fdatasync.c` tests filesystem utility syscall decoding for file creation, temp-file creation, range copy, close_range, sockets/helpers, and synchronization wrappers.

Important APIs/types/functions: local functions include `main`; macros include none detected; included headers include `tests.h`, `scno.h`, `stdio.h`, `unistd.h`. Kernel/user ABI names observed in the full file include `fdatasync`. Prominent constants include `SPDX`, `GPL`; prominent struct names include none detected.

Control flow: `main` builds deterministic arguments, invokes the target syscall or helper sequence, prints the expected strace line with `printf`/test helpers, and exits through the strace test harness.  This is a wrapper/variant file that reuses shared test implementation through local includes: `tests.h`, `scno.h`.

State and persistence behavior: runtime state is intentionally temporary and test-local. Most state lives in stack variables, tail-allocated buffers, compile-time macros, and errno/return-code snapshots.

Dependencies: strace test harness headers such as `tests.h`, `scno.h`, `print_utils.h`, `pidns.h`, `secontext.h`, local xlat tables, libc headers, and Linux UAPI headers provide syscall numbers, fallback structs, constants, and output helpers. This file directly includes `tests.h`, `scno.h`, `stdio.h`, `unistd.h`.

Integration points: the file participates in strace's testsuite as a compiled C test, AWK normalizer, header, or generator input. It integrates with generated xlat tables, syscall-number selection, test-driver `.test` scripts, and expected-output comparison.

Risks: Primary risks are kernel/architecture feature availability, ABI-width differences, host header drift, permissions, namespace-dependent pid/fd/path rendering, and expected-output brittleness when symbolic constants change.

Test signals: useful validation is the corresponding strace testsuite target under the same basename, comparison of stdout against expected decoder lines, successful compilation under the configured personality/time ABI, and skip behavior when the kernel lacks the syscall or permission. The source was read in full for this report: 26 lines, 467 bytes, sha256 prefix `fd588545fac3`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/fdatasync.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/fflush.c -->
# sources/test-tools/strace/tests/fflush.c

Purpose: `fflush.c` tests filesystem utility syscall decoding for file creation, temp-file creation, range copy, close_range, sockets/helpers, and synchronization wrappers.

Important APIs/types/functions: local functions include `main`; macros include none detected; included headers include `tests.h`, `errno.h`, `stdio.h`, `stdlib.h`. Kernel/user ABI names observed in the full file include none detected. Prominent constants include `SPDX`, `GPL`, `ENOSPC`, `STRACE_EXE`; prominent struct names include none detected.

Control flow: `main` builds deterministic arguments, invokes the target syscall or helper sequence, prints the expected strace line with `printf`/test helpers, and exits through the strace test harness.  This is a wrapper/variant file that reuses shared test implementation through local includes: `tests.h`.

State and persistence behavior: runtime state is intentionally temporary and test-local. Most state lives in stack variables, tail-allocated buffers, compile-time macros, and errno/return-code snapshots.

Dependencies: strace test harness headers such as `tests.h`, `scno.h`, `print_utils.h`, `pidns.h`, `secontext.h`, local xlat tables, libc headers, and Linux UAPI headers provide syscall numbers, fallback structs, constants, and output helpers. This file directly includes `tests.h`, `errno.h`, `stdio.h`, `stdlib.h`.

Integration points: the file participates in strace's testsuite as a compiled C test, AWK normalizer, header, or generator input. It integrates with generated xlat tables, syscall-number selection, test-driver `.test` scripts, and expected-output comparison.

Risks: Primary risks are kernel/architecture feature availability, ABI-width differences, host header drift, permissions, namespace-dependent pid/fd/path rendering, and expected-output brittleness when symbolic constants change.

Test signals: useful validation is the corresponding strace testsuite target under the same basename, comparison of stdout against expected decoder lines, successful compilation under the configured personality/time ABI, and skip behavior when the kernel lacks the syscall or permission. The source was read in full for this report: 22 lines, 360 bytes, sha256 prefix `cc24e01a6cb8`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/fflush.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/file_getattr-P.c -->
# sources/test-tools/strace/tests/file_getattr-P.c

Purpose: `file_getattr-P.c` covers file attribute retrieval decoder output for path/fd forms, success structure rendering, and xlat verbosity.

Important APIs/types/functions: local functions include none detected; macros include `PATH_TRACING`, `SKIP_IF_PROC_IS_UNAVAILABLE`; included headers include `file_getattr.c`. Kernel/user ABI names observed in the full file include none detected. Prominent constants include `PATH_TRACING`, `SKIP_IF_PROC_IS_UNAVAILABLE`; prominent struct names include none detected.

Control flow: this file is a shared implementation or variant wrapper; compile-time macros select the syscall number, xlat style, fd/path mode, success behavior, or namespace mode before the included/shared test body runs. The path/fd variants allocate stable pathnames or descriptors, run failing and successful forms where possible, and print both symbolic flags and raw fallback bits.  This is a wrapper/variant file that reuses shared test implementation through local includes: `file_getattr.c`.

State and persistence behavior: runtime state is intentionally temporary and test-local. Most state lives in stack variables, tail-allocated buffers, compile-time macros, and errno/return-code snapshots.

Dependencies: strace test harness headers such as `tests.h`, `scno.h`, `print_utils.h`, `pidns.h`, `secontext.h`, local xlat tables, libc headers, and Linux UAPI headers provide syscall numbers, fallback structs, constants, and output helpers. This file directly includes `file_getattr.c`.

Integration points: the file participates in strace's testsuite as a compiled C test, AWK normalizer, header, or generator input. It integrates with generated xlat tables, syscall-number selection, test-driver `.test` scripts, and expected-output comparison. The variant also exercises path/fd decoding options such as `-P`, `-y`, `-yy`, or `--decode-fds`.

Risks: Primary risks are kernel/architecture feature availability, ABI-width differences, host header drift, permissions, namespace-dependent pid/fd/path rendering, and expected-output brittleness when symbolic constants change.

Test signals: useful validation is the corresponding strace testsuite target under the same basename, comparison of stdout against expected decoder lines, successful compilation under the configured personality/time ABI, and skip behavior when the kernel lacks the syscall or permission. The source was read in full for this report: 4 lines, 122 bytes, sha256 prefix `9351f1b1fbcd`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/file_getattr-P.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/file_getattr-success-Xabbrev.c -->
# sources/test-tools/strace/tests/file_getattr-success-Xabbrev.c

Purpose: `file_getattr-success-Xabbrev.c` covers file attribute retrieval decoder output for path/fd forms, success structure rendering, and xlat verbosity.

Important APIs/types/functions: local functions include none detected; macros include none detected; included headers include `file_getattr-success.c`. Kernel/user ABI names observed in the full file include none detected. Prominent constants include none detected; prominent struct names include none detected.

Control flow: this file is a shared implementation or variant wrapper; compile-time macros select the syscall number, xlat style, fd/path mode, success behavior, or namespace mode before the included/shared test body runs. The path/fd variants allocate stable pathnames or descriptors, run failing and successful forms where possible, and print both symbolic flags and raw fallback bits.  This is a wrapper/variant file that reuses shared test implementation through local includes: `file_getattr-success.c`.

State and persistence behavior: runtime state is intentionally temporary and test-local. Most state lives in stack variables, tail-allocated buffers, compile-time macros, and errno/return-code snapshots.

Dependencies: strace test harness headers such as `tests.h`, `scno.h`, `print_utils.h`, `pidns.h`, `secontext.h`, local xlat tables, libc headers, and Linux UAPI headers provide syscall numbers, fallback structs, constants, and output helpers. This file directly includes `file_getattr-success.c`.

Integration points: the file participates in strace's testsuite as a compiled C test, AWK normalizer, header, or generator input. It integrates with generated xlat tables, syscall-number selection, test-driver `.test` scripts, and expected-output comparison. Its filename selects an xlat rendering mode, so the same syscall surface is compared under abbreviated, raw, or verbose symbolic output.

Risks: Primary risks are kernel/architecture feature availability, ABI-width differences, host header drift, permissions, namespace-dependent pid/fd/path rendering, and expected-output brittleness when symbolic constants change.

Test signals: useful validation is the corresponding strace testsuite target under the same basename, comparison of stdout against expected decoder lines, successful compilation under the configured personality/time ABI, and skip behavior when the kernel lacks the syscall or permission. The source was read in full for this report: 1 lines, 34 bytes, sha256 prefix `76a1ab62e9a5`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/file_getattr-success-Xabbrev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/file_getattr-success-Xraw.c -->
# sources/test-tools/strace/tests/file_getattr-success-Xraw.c

Purpose: `file_getattr-success-Xraw.c` covers file attribute retrieval decoder output for path/fd forms, success structure rendering, and xlat verbosity.

Important APIs/types/functions: local functions include none detected; macros include `XLAT_RAW`; included headers include `file_getattr-success.c`. Kernel/user ABI names observed in the full file include none detected. Prominent constants include `XLAT_RAW`; prominent struct names include none detected.

Control flow: this file is a shared implementation or variant wrapper; compile-time macros select the syscall number, xlat style, fd/path mode, success behavior, or namespace mode before the included/shared test body runs. The path/fd variants allocate stable pathnames or descriptors, run failing and successful forms where possible, and print both symbolic flags and raw fallback bits.  This is a wrapper/variant file that reuses shared test implementation through local includes: `file_getattr-success.c`.

State and persistence behavior: runtime state is intentionally temporary and test-local. Most state lives in stack variables, tail-allocated buffers, compile-time macros, and errno/return-code snapshots.

Dependencies: strace test harness headers such as `tests.h`, `scno.h`, `print_utils.h`, `pidns.h`, `secontext.h`, local xlat tables, libc headers, and Linux UAPI headers provide syscall numbers, fallback structs, constants, and output helpers. This file directly includes `file_getattr-success.c`.

Integration points: the file participates in strace's testsuite as a compiled C test, AWK normalizer, header, or generator input. It integrates with generated xlat tables, syscall-number selection, test-driver `.test` scripts, and expected-output comparison. Its filename selects an xlat rendering mode, so the same syscall surface is compared under abbreviated, raw, or verbose symbolic output.

Risks: Primary risks are kernel/architecture feature availability, ABI-width differences, host header drift, permissions, namespace-dependent pid/fd/path rendering, and expected-output brittleness when symbolic constants change.

Test signals: useful validation is the corresponding strace testsuite target under the same basename, comparison of stdout against expected decoder lines, successful compilation under the configured personality/time ABI, and skip behavior when the kernel lacks the syscall or permission. The source was read in full for this report: 2 lines, 53 bytes, sha256 prefix `1f4e2ac4a082`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/file_getattr-success-Xraw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/file_getattr-success-Xverbose.c -->
# sources/test-tools/strace/tests/file_getattr-success-Xverbose.c

Purpose: `file_getattr-success-Xverbose.c` covers file attribute retrieval decoder output for path/fd forms, success structure rendering, and xlat verbosity.

Important APIs/types/functions: local functions include none detected; macros include `XLAT_VERBOSE`; included headers include `file_getattr-success.c`. Kernel/user ABI names observed in the full file include none detected. Prominent constants include `XLAT_VERBOSE`; prominent struct names include none detected.

Control flow: this file is a shared implementation or variant wrapper; compile-time macros select the syscall number, xlat style, fd/path mode, success behavior, or namespace mode before the included/shared test body runs. The path/fd variants allocate stable pathnames or descriptors, run failing and successful forms where possible, and print both symbolic flags and raw fallback bits.  This is a wrapper/variant file that reuses shared test implementation through local includes: `file_getattr-success.c`.

State and persistence behavior: runtime state is intentionally temporary and test-local. Most state lives in stack variables, tail-allocated buffers, compile-time macros, and errno/return-code snapshots.

Dependencies: strace test harness headers such as `tests.h`, `scno.h`, `print_utils.h`, `pidns.h`, `secontext.h`, local xlat tables, libc headers, and Linux UAPI headers provide syscall numbers, fallback structs, constants, and output helpers. This file directly includes `file_getattr-success.c`.

Integration points: the file participates in strace's testsuite as a compiled C test, AWK normalizer, header, or generator input. It integrates with generated xlat tables, syscall-number selection, test-driver `.test` scripts, and expected-output comparison. Its filename selects an xlat rendering mode, so the same syscall surface is compared under abbreviated, raw, or verbose symbolic output.

Risks: Primary risks are kernel/architecture feature availability, ABI-width differences, host header drift, permissions, namespace-dependent pid/fd/path rendering, and expected-output brittleness when symbolic constants change.

Test signals: useful validation is the corresponding strace testsuite target under the same basename, comparison of stdout against expected decoder lines, successful compilation under the configured personality/time ABI, and skip behavior when the kernel lacks the syscall or permission. The source was read in full for this report: 2 lines, 57 bytes, sha256 prefix `16588c84adeb`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/file_getattr-success-Xverbose.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/file_getattr-success.c -->
# sources/test-tools/strace/tests/file_getattr-success.c

Purpose: `file_getattr-success.c` covers file attribute retrieval decoder output for path/fd forms, success structure rendering, and xlat verbosity.

Important APIs/types/functions: local functions include none detected; macros include `RETVAL_INJECTED`; included headers include `file_getattr.c`. Kernel/user ABI names observed in the full file include none detected. Prominent constants include `RETVAL_INJECTED`; prominent struct names include none detected.

Control flow: this file is a shared implementation or variant wrapper; compile-time macros select the syscall number, xlat style, fd/path mode, success behavior, or namespace mode before the included/shared test body runs. The path/fd variants allocate stable pathnames or descriptors, run failing and successful forms where possible, and print both symbolic flags and raw fallback bits.  This is a wrapper/variant file that reuses shared test implementation through local includes: `file_getattr.c`.

State and persistence behavior: runtime state is intentionally temporary and test-local. Most state lives in stack variables, tail-allocated buffers, compile-time macros, and errno/return-code snapshots.

Dependencies: strace test harness headers such as `tests.h`, `scno.h`, `print_utils.h`, `pidns.h`, `secontext.h`, local xlat tables, libc headers, and Linux UAPI headers provide syscall numbers, fallback structs, constants, and output helpers. This file directly includes `file_getattr.c`.

Integration points: the file participates in strace's testsuite as a compiled C test, AWK normalizer, header, or generator input. It integrates with generated xlat tables, syscall-number selection, test-driver `.test` scripts, and expected-output comparison.

Risks: Primary risks are kernel/architecture feature availability, ABI-width differences, host header drift, permissions, namespace-dependent pid/fd/path rendering, and expected-output brittleness when symbolic constants change.

Test signals: useful validation is the corresponding strace testsuite target under the same basename, comparison of stdout against expected decoder lines, successful compilation under the configured personality/time ABI, and skip behavior when the kernel lacks the syscall or permission. The source was read in full for this report: 2 lines, 52 bytes, sha256 prefix `b4f3c2e72cfe`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/file_getattr-success.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/file_getattr-y.c -->
# sources/test-tools/strace/tests/file_getattr-y.c

Purpose: `file_getattr-y.c` covers file attribute retrieval decoder output for path/fd forms, success structure rendering, and xlat verbosity.

Important APIs/types/functions: local functions include none detected; macros include `FD_PATH`, `SKIP_IF_PROC_IS_UNAVAILABLE`; included headers include `file_getattr.c`. Kernel/user ABI names observed in the full file include none detected. Prominent constants include `FD_PATH`, `SKIP_IF_PROC_IS_UNAVAILABLE`; prominent struct names include none detected.

Control flow: this file is a shared implementation or variant wrapper; compile-time macros select the syscall number, xlat style, fd/path mode, success behavior, or namespace mode before the included/shared test body runs. The path/fd variants allocate stable pathnames or descriptors, run failing and successful forms where possible, and print both symbolic flags and raw fallback bits.  This is a wrapper/variant file that reuses shared test implementation through local includes: `file_getattr.c`.

State and persistence behavior: runtime state is intentionally temporary and test-local. Most state lives in stack variables, tail-allocated buffers, compile-time macros, and errno/return-code snapshots.

Dependencies: strace test harness headers such as `tests.h`, `scno.h`, `print_utils.h`, `pidns.h`, `secontext.h`, local xlat tables, libc headers, and Linux UAPI headers provide syscall numbers, fallback structs, constants, and output helpers. This file directly includes `file_getattr.c`.

Integration points: the file participates in strace's testsuite as a compiled C test, AWK normalizer, header, or generator input. It integrates with generated xlat tables, syscall-number selection, test-driver `.test` scripts, and expected-output comparison. The variant also exercises path/fd decoding options such as `-P`, `-y`, `-yy`, or `--decode-fds`.

Risks: Primary risks are kernel/architecture feature availability, ABI-width differences, host header drift, permissions, namespace-dependent pid/fd/path rendering, and expected-output brittleness when symbolic constants change.

Test signals: useful validation is the corresponding strace testsuite target under the same basename, comparison of stdout against expected decoder lines, successful compilation under the configured personality/time ABI, and skip behavior when the kernel lacks the syscall or permission. The source was read in full for this report: 4 lines, 131 bytes, sha256 prefix `fa103e810fc5`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/file_getattr-y.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/file_getattr-yy.c -->
# sources/test-tools/strace/tests/file_getattr-yy.c

Purpose: `file_getattr-yy.c` covers file attribute retrieval decoder output for path/fd forms, success structure rendering, and xlat verbosity.

Important APIs/types/functions: local functions include none detected; macros include `FD_PATH`, `SKIP_IF_PROC_IS_UNAVAILABLE`; included headers include `file_getattr.c`. Kernel/user ABI names observed in the full file include none detected. Prominent constants include `FD_PATH`, `SKIP_IF_PROC_IS_UNAVAILABLE`; prominent struct names include none detected.

Control flow: this file is a shared implementation or variant wrapper; compile-time macros select the syscall number, xlat style, fd/path mode, success behavior, or namespace mode before the included/shared test body runs. The path/fd variants allocate stable pathnames or descriptors, run failing and successful forms where possible, and print both symbolic flags and raw fallback bits.  This is a wrapper/variant file that reuses shared test implementation through local includes: `file_getattr.c`.

State and persistence behavior: runtime state is intentionally temporary and test-local. Most state lives in stack variables, tail-allocated buffers, compile-time macros, and errno/return-code snapshots.

Dependencies: strace test harness headers such as `tests.h`, `scno.h`, `print_utils.h`, `pidns.h`, `secontext.h`, local xlat tables, libc headers, and Linux UAPI headers provide syscall numbers, fallback structs, constants, and output helpers. This file directly includes `file_getattr.c`.

Integration points: the file participates in strace's testsuite as a compiled C test, AWK normalizer, header, or generator input. It integrates with generated xlat tables, syscall-number selection, test-driver `.test` scripts, and expected-output comparison. The variant also exercises path/fd decoding options such as `-P`, `-y`, `-yy`, or `--decode-fds`.

Risks: Primary risks are kernel/architecture feature availability, ABI-width differences, host header drift, permissions, namespace-dependent pid/fd/path rendering, and expected-output brittleness when symbolic constants change.

Test signals: useful validation is the corresponding strace testsuite target under the same basename, comparison of stdout against expected decoder lines, successful compilation under the configured personality/time ABI, and skip behavior when the kernel lacks the syscall or permission. The source was read in full for this report: 4 lines, 141 bytes, sha256 prefix `5604ef913012`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/file_getattr-yy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/file_getattr.c -->
# sources/test-tools/strace/tests/file_getattr.c

Purpose: `file_getattr.c` covers file attribute retrieval decoder output for path/fd forms, success structure rendering, and xlat verbosity.

Important APIs/types/functions: local functions include none detected; macros include `SYSCALL_NR`, `SYSCALL_NAME`, `SYSCALL_is_set`; included headers include `file_xetattr-common.c`. Kernel/user ABI names observed in the full file include none detected. Prominent constants include `SPDX`, `GPL`, `SYSCALL_NR`, `SYSCALL_NAME`; prominent struct names include none detected.

Control flow: this file is a shared implementation or variant wrapper; compile-time macros select the syscall number, xlat style, fd/path mode, success behavior, or namespace mode before the included/shared test body runs. The path/fd variants allocate stable pathnames or descriptors, run failing and successful forms where possible, and print both symbolic flags and raw fallback bits.  This is a wrapper/variant file that reuses shared test implementation through local includes: `file_xetattr-common.c`.

State and persistence behavior: runtime state is intentionally temporary and test-local. Most state lives in stack variables, tail-allocated buffers, compile-time macros, and errno/return-code snapshots.

Dependencies: strace test harness headers such as `tests.h`, `scno.h`, `print_utils.h`, `pidns.h`, `secontext.h`, local xlat tables, libc headers, and Linux UAPI headers provide syscall numbers, fallback structs, constants, and output helpers. This file directly includes `file_xetattr-common.c`.

Integration points: the file participates in strace's testsuite as a compiled C test, AWK normalizer, header, or generator input. It integrates with generated xlat tables, syscall-number selection, test-driver `.test` scripts, and expected-output comparison.

Risks: Primary risks are kernel/architecture feature availability, ABI-width differences, host header drift, permissions, namespace-dependent pid/fd/path rendering, and expected-output brittleness when symbolic constants change.

Test signals: useful validation is the corresponding strace testsuite target under the same basename, comparison of stdout against expected decoder lines, successful compilation under the configured personality/time ABI, and skip behavior when the kernel lacks the syscall or permission. The source was read in full for this report: 14 lines, 303 bytes, sha256 prefix `81be204a5dfa`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/file_getattr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/file_handle.c -->
# sources/test-tools/strace/tests/file_handle.c

Purpose: `file_handle.c` checks name_to_handle_at/open_by_handle_at decoding, handle buffer sizes, mount ids, flags, and optional SELinux context annotations.

Important APIs/types/functions: local functions include `print_handle_data`, `do_name_to_handle_at`, `do_open_by_handle_at`, `main`; macros include `MAX_HANDLE_SZ`, `STR16`, `STR64`; included headers include `tests.h`, `scno.h`, `assert.h`, `errno.h`, `inttypes.h`, `fcntl.h`, `stdio.h`, `unistd.h`, `secontext.h`. Kernel/user ABI names observed in the full file include `chdir`, `fchdir`, `fcntl`, `name_to_handle_at`, `open_by_handle_at`. Prominent constants include `SPDX`, `GPL`, `ASSERT_NONE`, `ASSERT_SUCCESS`, `ASSERT_ERROR`, `MAX_HANDLE_SZ`, `MIN`, `TEST_SECONTEXT`, `NULL`, ... (31 total), `F8ILL_KULONG_MASK`, `O_WRONLY`, `ARRAY_SIZE`; prominent struct names include `file_handle`, `strval`.

Control flow: `main` builds deterministic arguments, invokes the target syscall or helper sequence, prints the expected strace line with `printf`/test helpers, and exits through the strace test harness. The main path first probes `name_to_handle_at` error behavior, then allocates several handle buffers to cover overflow, valid data, invalid pointers, and `open_by_handle_at` formatting.

State and persistence behavior: runtime state is intentionally temporary and test-local. The test may allocate tail buffers and/or create temporary files, directories, descriptors, sockets, eventfds, epoll instances, or mount/file handles, then relies on process exit or explicit cleanup for disposal. Opaque file handles and mount ids are kernel/filesystem outputs and are printed, not persisted.

Dependencies: strace test harness headers such as `tests.h`, `scno.h`, `print_utils.h`, `pidns.h`, `secontext.h`, local xlat tables, libc headers, and Linux UAPI headers provide syscall numbers, fallback structs, constants, and output helpers. This file directly includes `tests.h`, `scno.h`, `assert.h`, `errno.h`, `inttypes.h`, `fcntl.h`, `stdio.h`, `unistd.h`, `secontext.h`.

Integration points: the file participates in strace's testsuite as a compiled C test, AWK normalizer, header, or generator input. It integrates with generated xlat tables, syscall-number selection, test-driver `.test` scripts, and expected-output comparison.

Risks: file handles are filesystem-dependent and may require capabilities for open_by_handle_at; tests must preserve EOVERFLOW, EINVAL, and success distinctions without assuming stable opaque handle bytes.

Test signals: useful validation is the corresponding strace testsuite target under the same basename, comparison of stdout against expected decoder lines, successful compilation under the configured personality/time ABI, and skip behavior when the kernel lacks the syscall or permission. The source was read in full for this report: 408 lines, 11725 bytes, sha256 prefix `ba4eed4fcb9e`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/file_handle.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/file_setattr-P.c -->
# sources/test-tools/strace/tests/file_setattr-P.c

Purpose: `file_setattr-P.c` covers file attribute setting decoder output for mask/attribute flags, path/fd forms, and xlat verbosity.

Important APIs/types/functions: local functions include none detected; macros include `PATH_TRACING`, `SKIP_IF_PROC_IS_UNAVAILABLE`; included headers include `file_setattr.c`. Kernel/user ABI names observed in the full file include none detected. Prominent constants include `PATH_TRACING`, `SKIP_IF_PROC_IS_UNAVAILABLE`; prominent struct names include none detected.

Control flow: this file is a shared implementation or variant wrapper; compile-time macros select the syscall number, xlat style, fd/path mode, success behavior, or namespace mode before the included/shared test body runs. The path/fd variants allocate stable pathnames or descriptors, run failing and successful forms where possible, and print both symbolic flags and raw fallback bits.  This is a wrapper/variant file that reuses shared test implementation through local includes: `file_setattr.c`.

State and persistence behavior: runtime state is intentionally temporary and test-local. Most state lives in stack variables, tail-allocated buffers, compile-time macros, and errno/return-code snapshots.

Dependencies: strace test harness headers such as `tests.h`, `scno.h`, `print_utils.h`, `pidns.h`, `secontext.h`, local xlat tables, libc headers, and Linux UAPI headers provide syscall numbers, fallback structs, constants, and output helpers. This file directly includes `file_setattr.c`.

Integration points: the file participates in strace's testsuite as a compiled C test, AWK normalizer, header, or generator input. It integrates with generated xlat tables, syscall-number selection, test-driver `.test` scripts, and expected-output comparison. The variant also exercises path/fd decoding options such as `-P`, `-y`, `-yy`, or `--decode-fds`.

Risks: Primary risks are kernel/architecture feature availability, ABI-width differences, host header drift, permissions, namespace-dependent pid/fd/path rendering, and expected-output brittleness when symbolic constants change.

Test signals: useful validation is the corresponding strace testsuite target under the same basename, comparison of stdout against expected decoder lines, successful compilation under the configured personality/time ABI, and skip behavior when the kernel lacks the syscall or permission. The source was read in full for this report: 4 lines, 122 bytes, sha256 prefix `8ffa36a13a78`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/file_setattr-P.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/file_setattr-Xabbrev.c -->
# sources/test-tools/strace/tests/file_setattr-Xabbrev.c

Purpose: `file_setattr-Xabbrev.c` covers file attribute setting decoder output for mask/attribute flags, path/fd forms, and xlat verbosity.

Important APIs/types/functions: local functions include none detected; macros include none detected; included headers include `file_setattr.c`. Kernel/user ABI names observed in the full file include none detected. Prominent constants include none detected; prominent struct names include none detected.

Control flow: this file is a shared implementation or variant wrapper; compile-time macros select the syscall number, xlat style, fd/path mode, success behavior, or namespace mode before the included/shared test body runs. The path/fd variants allocate stable pathnames or descriptors, run failing and successful forms where possible, and print both symbolic flags and raw fallback bits.  This is a wrapper/variant file that reuses shared test implementation through local includes: `file_setattr.c`.

State and persistence behavior: runtime state is intentionally temporary and test-local. Most state lives in stack variables, tail-allocated buffers, compile-time macros, and errno/return-code snapshots.

Dependencies: strace test harness headers such as `tests.h`, `scno.h`, `print_utils.h`, `pidns.h`, `secontext.h`, local xlat tables, libc headers, and Linux UAPI headers provide syscall numbers, fallback structs, constants, and output helpers. This file directly includes `file_setattr.c`.

Integration points: the file participates in strace's testsuite as a compiled C test, AWK normalizer, header, or generator input. It integrates with generated xlat tables, syscall-number selection, test-driver `.test` scripts, and expected-output comparison. Its filename selects an xlat rendering mode, so the same syscall surface is compared under abbreviated, raw, or verbose symbolic output.

Risks: Primary risks are kernel/architecture feature availability, ABI-width differences, host header drift, permissions, namespace-dependent pid/fd/path rendering, and expected-output brittleness when symbolic constants change.

Test signals: useful validation is the corresponding strace testsuite target under the same basename, comparison of stdout against expected decoder lines, successful compilation under the configured personality/time ABI, and skip behavior when the kernel lacks the syscall or permission. The source was read in full for this report: 1 lines, 26 bytes, sha256 prefix `ed396ac93a3a`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/file_setattr-Xabbrev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/file_setattr-Xraw.c -->
# sources/test-tools/strace/tests/file_setattr-Xraw.c

Purpose: `file_setattr-Xraw.c` covers file attribute setting decoder output for mask/attribute flags, path/fd forms, and xlat verbosity.

Important APIs/types/functions: local functions include none detected; macros include `XLAT_RAW`; included headers include `file_setattr.c`. Kernel/user ABI names observed in the full file include none detected. Prominent constants include `XLAT_RAW`; prominent struct names include none detected.

Control flow: this file is a shared implementation or variant wrapper; compile-time macros select the syscall number, xlat style, fd/path mode, success behavior, or namespace mode before the included/shared test body runs. The path/fd variants allocate stable pathnames or descriptors, run failing and successful forms where possible, and print both symbolic flags and raw fallback bits.  This is a wrapper/variant file that reuses shared test implementation through local includes: `file_setattr.c`.

State and persistence behavior: runtime state is intentionally temporary and test-local. Most state lives in stack variables, tail-allocated buffers, compile-time macros, and errno/return-code snapshots.

Dependencies: strace test harness headers such as `tests.h`, `scno.h`, `print_utils.h`, `pidns.h`, `secontext.h`, local xlat tables, libc headers, and Linux UAPI headers provide syscall numbers, fallback structs, constants, and output helpers. This file directly includes `file_setattr.c`.

Integration points: the file participates in strace's testsuite as a compiled C test, AWK normalizer, header, or generator input. It integrates with generated xlat tables, syscall-number selection, test-driver `.test` scripts, and expected-output comparison. Its filename selects an xlat rendering mode, so the same syscall surface is compared under abbreviated, raw, or verbose symbolic output.

Risks: Primary risks are kernel/architecture feature availability, ABI-width differences, host header drift, permissions, namespace-dependent pid/fd/path rendering, and expected-output brittleness when symbolic constants change.

Test signals: useful validation is the corresponding strace testsuite target under the same basename, comparison of stdout against expected decoder lines, successful compilation under the configured personality/time ABI, and skip behavior when the kernel lacks the syscall or permission. The source was read in full for this report: 2 lines, 45 bytes, sha256 prefix `26f851691fbf`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/file_setattr-Xraw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/file_setattr-Xverbose.c -->
# sources/test-tools/strace/tests/file_setattr-Xverbose.c

Purpose: `file_setattr-Xverbose.c` covers file attribute setting decoder output for mask/attribute flags, path/fd forms, and xlat verbosity.

Important APIs/types/functions: local functions include none detected; macros include `XLAT_VERBOSE`; included headers include `file_setattr.c`. Kernel/user ABI names observed in the full file include none detected. Prominent constants include `XLAT_VERBOSE`; prominent struct names include none detected.

Control flow: this file is a shared implementation or variant wrapper; compile-time macros select the syscall number, xlat style, fd/path mode, success behavior, or namespace mode before the included/shared test body runs. The path/fd variants allocate stable pathnames or descriptors, run failing and successful forms where possible, and print both symbolic flags and raw fallback bits.  This is a wrapper/variant file that reuses shared test implementation through local includes: `file_setattr.c`.

State and persistence behavior: runtime state is intentionally temporary and test-local. Most state lives in stack variables, tail-allocated buffers, compile-time macros, and errno/return-code snapshots.

Dependencies: strace test harness headers such as `tests.h`, `scno.h`, `print_utils.h`, `pidns.h`, `secontext.h`, local xlat tables, libc headers, and Linux UAPI headers provide syscall numbers, fallback structs, constants, and output helpers. This file directly includes `file_setattr.c`.

Integration points: the file participates in strace's testsuite as a compiled C test, AWK normalizer, header, or generator input. It integrates with generated xlat tables, syscall-number selection, test-driver `.test` scripts, and expected-output comparison. Its filename selects an xlat rendering mode, so the same syscall surface is compared under abbreviated, raw, or verbose symbolic output.

Risks: Primary risks are kernel/architecture feature availability, ABI-width differences, host header drift, permissions, namespace-dependent pid/fd/path rendering, and expected-output brittleness when symbolic constants change.

Test signals: useful validation is the corresponding strace testsuite target under the same basename, comparison of stdout against expected decoder lines, successful compilation under the configured personality/time ABI, and skip behavior when the kernel lacks the syscall or permission. The source was read in full for this report: 2 lines, 49 bytes, sha256 prefix `9ca1bfa24e8d`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/file_setattr-Xverbose.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/file_setattr-y.c -->
# sources/test-tools/strace/tests/file_setattr-y.c

Purpose: `file_setattr-y.c` covers file attribute setting decoder output for mask/attribute flags, path/fd forms, and xlat verbosity.

Important APIs/types/functions: local functions include none detected; macros include `FD_PATH`, `SKIP_IF_PROC_IS_UNAVAILABLE`; included headers include `file_setattr.c`. Kernel/user ABI names observed in the full file include none detected. Prominent constants include `FD_PATH`, `SKIP_IF_PROC_IS_UNAVAILABLE`; prominent struct names include none detected.

Control flow: this file is a shared implementation or variant wrapper; compile-time macros select the syscall number, xlat style, fd/path mode, success behavior, or namespace mode before the included/shared test body runs. The path/fd variants allocate stable pathnames or descriptors, run failing and successful forms where possible, and print both symbolic flags and raw fallback bits.  This is a wrapper/variant file that reuses shared test implementation through local includes: `file_setattr.c`.

State and persistence behavior: runtime state is intentionally temporary and test-local. Most state lives in stack variables, tail-allocated buffers, compile-time macros, and errno/return-code snapshots.

Dependencies: strace test harness headers such as `tests.h`, `scno.h`, `print_utils.h`, `pidns.h`, `secontext.h`, local xlat tables, libc headers, and Linux UAPI headers provide syscall numbers, fallback structs, constants, and output helpers. This file directly includes `file_setattr.c`.

Integration points: the file participates in strace's testsuite as a compiled C test, AWK normalizer, header, or generator input. It integrates with generated xlat tables, syscall-number selection, test-driver `.test` scripts, and expected-output comparison. The variant also exercises path/fd decoding options such as `-P`, `-y`, `-yy`, or `--decode-fds`.

Risks: Primary risks are kernel/architecture feature availability, ABI-width differences, host header drift, permissions, namespace-dependent pid/fd/path rendering, and expected-output brittleness when symbolic constants change.

Test signals: useful validation is the corresponding strace testsuite target under the same basename, comparison of stdout against expected decoder lines, successful compilation under the configured personality/time ABI, and skip behavior when the kernel lacks the syscall or permission. The source was read in full for this report: 4 lines, 131 bytes, sha256 prefix `b1fd71b6c390`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/file_setattr-y.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/file_setattr-yy.c -->
# sources/test-tools/strace/tests/file_setattr-yy.c

Purpose: `file_setattr-yy.c` covers file attribute setting decoder output for mask/attribute flags, path/fd forms, and xlat verbosity.

Important APIs/types/functions: local functions include none detected; macros include `FD_PATH`, `SKIP_IF_PROC_IS_UNAVAILABLE`; included headers include `file_setattr.c`. Kernel/user ABI names observed in the full file include none detected. Prominent constants include `FD_PATH`, `SKIP_IF_PROC_IS_UNAVAILABLE`; prominent struct names include none detected.

Control flow: this file is a shared implementation or variant wrapper; compile-time macros select the syscall number, xlat style, fd/path mode, success behavior, or namespace mode before the included/shared test body runs. The path/fd variants allocate stable pathnames or descriptors, run failing and successful forms where possible, and print both symbolic flags and raw fallback bits.  This is a wrapper/variant file that reuses shared test implementation through local includes: `file_setattr.c`.

State and persistence behavior: runtime state is intentionally temporary and test-local. Most state lives in stack variables, tail-allocated buffers, compile-time macros, and errno/return-code snapshots.

Dependencies: strace test harness headers such as `tests.h`, `scno.h`, `print_utils.h`, `pidns.h`, `secontext.h`, local xlat tables, libc headers, and Linux UAPI headers provide syscall numbers, fallback structs, constants, and output helpers. This file directly includes `file_setattr.c`.

Integration points: the file participates in strace's testsuite as a compiled C test, AWK normalizer, header, or generator input. It integrates with generated xlat tables, syscall-number selection, test-driver `.test` scripts, and expected-output comparison. The variant also exercises path/fd decoding options such as `-P`, `-y`, `-yy`, or `--decode-fds`.

Risks: Primary risks are kernel/architecture feature availability, ABI-width differences, host header drift, permissions, namespace-dependent pid/fd/path rendering, and expected-output brittleness when symbolic constants change.

Test signals: useful validation is the corresponding strace testsuite target under the same basename, comparison of stdout against expected decoder lines, successful compilation under the configured personality/time ABI, and skip behavior when the kernel lacks the syscall or permission. The source was read in full for this report: 4 lines, 141 bytes, sha256 prefix `74d59b194ff1`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/file_setattr-yy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/file_setattr.c -->
# sources/test-tools/strace/tests/file_setattr.c

Purpose: `file_setattr.c` covers file attribute setting decoder output for mask/attribute flags, path/fd forms, and xlat verbosity.

Important APIs/types/functions: local functions include none detected; macros include `SYSCALL_NR`, `SYSCALL_NAME`, `SYSCALL_is_set`; included headers include `file_xetattr-common.c`. Kernel/user ABI names observed in the full file include none detected. Prominent constants include `SPDX`, `GPL`, `SYSCALL_NR`, `SYSCALL_NAME`; prominent struct names include none detected.

Control flow: this file is a shared implementation or variant wrapper; compile-time macros select the syscall number, xlat style, fd/path mode, success behavior, or namespace mode before the included/shared test body runs. The path/fd variants allocate stable pathnames or descriptors, run failing and successful forms where possible, and print both symbolic flags and raw fallback bits.  This is a wrapper/variant file that reuses shared test implementation through local includes: `file_xetattr-common.c`.

State and persistence behavior: runtime state is intentionally temporary and test-local. Most state lives in stack variables, tail-allocated buffers, compile-time macros, and errno/return-code snapshots.

Dependencies: strace test harness headers such as `tests.h`, `scno.h`, `print_utils.h`, `pidns.h`, `secontext.h`, local xlat tables, libc headers, and Linux UAPI headers provide syscall numbers, fallback structs, constants, and output helpers. This file directly includes `file_xetattr-common.c`.

Integration points: the file participates in strace's testsuite as a compiled C test, AWK normalizer, header, or generator input. It integrates with generated xlat tables, syscall-number selection, test-driver `.test` scripts, and expected-output comparison.

Risks: Primary risks are kernel/architecture feature availability, ABI-width differences, host header drift, permissions, namespace-dependent pid/fd/path rendering, and expected-output brittleness when symbolic constants change.

Test signals: useful validation is the corresponding strace testsuite target under the same basename, comparison of stdout against expected decoder lines, successful compilation under the configured personality/time ABI, and skip behavior when the kernel lacks the syscall or permission. The source was read in full for this report: 14 lines, 303 bytes, sha256 prefix `e650f8ebd8c4`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/file_setattr.c -->
