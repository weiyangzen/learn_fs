# sources/distributed-fs/ceph-client/tools/testing/selftests/mm/pkey_util.c

Purpose: small syscall wrapper translation unit for pkey selftests, isolating direct kernel calls behind names used by shared helpers.

Important APIs and functions: `sys_pkey_alloc()` calls `SYS_pkey_alloc`; `sys_pkey_free()` calls `SYS_pkey_free`; `sys_mprotect_pkey()` calls `__NR_pkey_mprotect`, clears `errno`, logs details through `dprintf`, and returns the raw syscall result.

Control flow and state: no standalone entrypoint. The wrappers are linked into pkey binaries and called by `protection_keys.c`, `pkey_sighandler_tests.c`, and helper routines. It creates no state except kernel pkey allocation/freeing and VMA protection changes requested by callers.

Dependencies and risks: depends on `pkey-helpers.h`, syscall-number definitions, and Linux pkey syscall support. Any syscall-number mismatch would cause all higher-level pkey tests to fail or skip incorrectly.
