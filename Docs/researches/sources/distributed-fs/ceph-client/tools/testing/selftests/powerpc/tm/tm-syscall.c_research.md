# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/tm/tm-syscall.c

Purpose: verifies syscalls from active transactions abort persistently with syscall failure code, while syscalls from suspended transactions succeed, for both `sc` and optional `scv`.

Important APIs/types/functions: `getppid_tm()` wraps assembly helpers with retry/failure-code logic; `tm_syscall()` runs for `TEST_DURATION` seconds and checks failure helpers from `tm.h`.

Control flow: each iteration calls suspended getppid and expects success, then active getppid and expects -1 plus persistent syscall failure. If `PPC_FEATURE2_SCV` is present, it repeats the same checks with `scv`.

State and persistence behavior: global `retries` counts temporary TM aborts. No external state.

Dependencies and integration points: requires `PPC_FEATURE2_HTM_NOSC`, non-synthetic TM, `tm-syscall-asm.S`, and powerpc failure-code builtins.

Risks and test signals: temporary aborts are retried up to `TM_RETRIES`; exceeding that prints TEXASR/TFIAR and exits. Test duration is time-based.
