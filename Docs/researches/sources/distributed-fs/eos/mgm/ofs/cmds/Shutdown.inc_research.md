## sources/distributed-fs/eos/mgm/ofs/cmds/Shutdown.inc

Purpose: signal handler for orderly MGM shutdown.

Important APIs and types: `xrdmgmofs_shutdown`, POSIX `signal`, global `gOFS`, `XrdMgmOfs::Shutdown`, `OrderlyShutdown`, logging, and `std::quick_exit`.

Control flow: ignores `SIGINT`, `SIGTERM`, and `SIGQUIT`, logs shutdown start, returns immediately if shutdown is already in progress, sets `gOFS->Shutdown`, calls `gOFS->OrderlyShutdown()`, logs completion, and exits the process with status 0 via `quick_exit`.

State and persistence behavior: mutates the in-memory shutdown flag and delegates all persistent/service cleanup to `OrderlyShutdown()`. It intentionally exits without normal stack unwinding.

Dependencies and integration points: registered as a process signal handler by the MGM process. Commented design indicates `OrderlyShutdown()` handles namespace follower and sub-service shutdown depending on role.

Risks: the handler calls logging and complex shutdown code from a signal context, which is generally not async-signal-safe. `quick_exit` bypasses normal destructors. If `gOFS` is invalid during signal delivery, the handler has no guard.

Test signals: idempotent second signal return, signal ignore setup, `Shutdown` flag set before cleanup, `OrderlyShutdown()` called once, and process exit behavior in integration tests rather than unit tests.
