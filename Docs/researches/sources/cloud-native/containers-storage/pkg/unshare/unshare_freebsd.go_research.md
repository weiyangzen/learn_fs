# sources/cloud-native/containers-storage/pkg/unshare/unshare_freebsd.go

Purpose: FreeBSD Go wrapper for starting reexec commands with early C-side synchronization and optional session/process group setup.

Important APIs/types/functions: `Cmd` struct, `Command`, `Start`, `Run`, unsupported `CombinedOutput`/`Output`, `Runnable`, and `ExecRunnable`.

Control flow: `Start` locks the OS thread, sets environment instructions, creates PID and continue pipes, starts the reexec command, reads the child's C-reported PID, runs an optional hook, and returns so closing the continue pipe lets the child proceed. `Run` waits, and `ExecRunnable` exits with the child status or signal-derived status.

State/persistence: starts child processes, manipulates environment/extra files, and may change child session/process group/controlling terminal through C code.

Dependencies/integration: uses `pkg/reexec`, `logrus`, and the FreeBSD C constructor. Provides an API parallel to Linux for callers that do not need user namespace mappings.

Risks: if hook fails, the error is written to the child continue pipe but cleanup/kill behavior is less defensive than Linux. Output capture methods are intentionally unimplemented.

Test signals: FreeBSD tests should cover hook failure propagation, PID parsing, session and pgrp options, and exit-code preservation.
