# sources/distributed-fs/openafs/src/rx/SOLARIS/rx_kmutex.c

Purpose: Solaris Rx condition-variable wait implementation.

Important APIs/types/functions: `afs_cv_wait`, with optional `RX_LOCKS_DB` file/line parameters.

Control flow: detects AFS global-lock ownership, drops it before waiting, optionally records lock-debug release/acquire, calls `cv_wait` or `cv_wait_sig`, maps signal interruption to `EINTR`, then restores global-lock ordering by dropping/reentering the Rx mutex around `AFS_GLOCK`.

State/persistence: no global state; operates on caller-provided Solaris `kcondvar_t`/`kmutex_t`.

Dependencies/integration: Solaris kernel CV/mutex APIs, Rx lock debugging, and OpenAFS global lock.

Risks: signal semantics and lock-debug accounting must remain consistent; global-lock restoration can deadlock if caller lock order changes. Test signals are Solaris CV wait/signal, signal-interruptible waits, and RX_LOCKS_DB builds.
