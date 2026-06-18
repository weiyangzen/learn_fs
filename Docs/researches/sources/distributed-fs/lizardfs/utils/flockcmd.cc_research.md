# sources/distributed-fs/lizardfs/utils/flockcmd.cc

Purpose: interactive helper for testing BSD `flock()` behavior on a shared filesystem. It opens a file, takes a shared or exclusive advisory lock, prints state transitions, and waits for signals.

Important APIs/functions: global command maps translate `r` to `LOCK_SH` and `w` to `LOCK_EX`. Signal handlers: `SIGUSR1` unlocks, `SIGUSR2` reports interruption, and `SIGINT` closes the descriptor. `register_handler()` wraps `sigaction`.

Control flow: validates `path [r/w]`, opens the path read/write, prints `open`, calls blocking `flock(fd, cmd)`, prints `lock`, and then pauses. Signal handlers let tests orchestrate unlock/interrupt/close from another process.

State and persistence: holds a process-global fd and lock state. It does not write file data. Lock state is kernel/filesystem state and disappears on close/process exit.

Dependencies/integration: depends on `<sys/file.h>` and POSIX signals. It is used by shell/integration tests to observe flock semantics over LizardFS.

Risks and test signals: after an invalid command character it prints an error but does not immediately exit, so `commands[cmdno]` can default-insert zero. Signal handlers call non-async-signal-safe C++/stdio/string methods. Test signals are read/read compatibility, read/write and write/write exclusion, remote unlock via `SIGUSR1`, close via `SIGINT`, and behavior under signal interruption.
