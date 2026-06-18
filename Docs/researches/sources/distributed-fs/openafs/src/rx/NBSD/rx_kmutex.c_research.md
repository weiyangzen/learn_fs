# sources/distributed-fs/openafs/src/rx/NBSD/rx_kmutex.c

Purpose: NetBSD 5+ implementation for Rx condition-variable waits.

Important APIs/types/functions: `afs_cv_wait`.

Control flow: drops the AFS global lock if held, waits using NetBSD `cv_wait` or `cv_wait_sig`, maps interrupted signal waits to `EINTR`, then restores global-lock ordering by temporarily dropping and reacquiring the Rx mutex around `AFS_GLOCK`.

State/persistence: no global state; operates on caller-provided `kcondvar_t` and `kmutex_t`.

Dependencies/integration: NetBSD 5+ mutex/CV primitives, OpenAFS global lock, and `rx_kmutex.h` macros.

Risks: return-value interpretation for `cv_wait_sig` must match NetBSD semantics; global-lock restoration ordering is subtle. Test signals are signal-interruptible waits and lock-order assertions.
