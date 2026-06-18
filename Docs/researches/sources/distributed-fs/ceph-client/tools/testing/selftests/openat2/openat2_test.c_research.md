# sources/distributed-fs/ceph-client/tools/testing/selftests/openat2/openat2_test.c

Purpose: validates the openat2 syscall ABI: extensible `struct open_how` sizing/zero-extension behavior, pointer misalignment handling, open flag validation, mode validation, resolve flag conflicts, and unknown bit rejection.

Important APIs/types/functions: `struct open_how_ext` simulates future ABI extensions; `struct struct_test` drives size/trailing-data cases; `struct flag_test` drives flag/mode/resolve cases. `test_openat2_struct()` uses `raw_openat2()` with 13 deliberate alignment offsets. `test_openat2_flags()` uses `sys_openat2()`, `fcntl(F_GETFL/F_GETFD)`, and kselftest result functions.

Control flow: `main()` sets a plan of `13 * 7 + 25` tests. The struct suite checks normal, larger zero-padded, too-small, zero-sized, and larger nonzero-tail arguments against expected success, `-EINVAL`, or `-E2BIG`. The flag suite checks combinations such as `O_TMPFILE` conflicts, `O_PATH` allowed/disallowed companions, valid and invalid `how.mode`, `RESOLVE_BENEATH | RESOLVE_IN_ROOT`, invalid resolve bits, and high unknown flag bits. Unsupported `openat2` skips tests; filesystem-specific `-EOPNOTSUPP` for valid `O_TMPFILE` combinations is skipped.

State and persistence: may create/unlink `/tmp/ksft.openat2_tmpfile` for `O_CREAT` cases. Otherwise state is transient fds and allocations.

Dependencies/integration: linked with `helpers.c`; relies on openat2 syscall support and kselftest output. Sanitizers are enabled by the directory Makefile.

Risks: architecture-specific `O_LARGEFILE` fallback is acknowledged as wrong for some architectures, so related flag validation may be fragile there. Misalignment tests rely on malloc and usercopy behavior rather than kernel-internal visibility.

Test signals: kselftest TAP-style pass/skip/fail lines for each struct variation and flag case; nonzero fail/error counts cause `ksft_exit_fail()`.
