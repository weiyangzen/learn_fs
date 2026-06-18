# sources/cloud-native/moby/integration/container/exec_linux_test.go

Purpose: Linux-specific exec behavior tests for initial console size and standard failed-exec exit codes.

Important APIs and flow: `TestExecConsoleSize` requires API v1.42, runs busybox, creates an exec with TTY and `ConsoleSize{Height:57, Width:123}`, runs `stty size`, and expects `57 123`. `TestFailedExecExitCode` runs invalid commands and checks exit codes 127 for executable not found and 126 for invoking a non-executable directory.

State and dependencies: Uses running containers and exec sessions only; no persistent state beyond containers cleaned by helpers. Depends on Linux TTY behavior and busybox utilities.

Risks and signals: It guards API-to-runtime terminal sizing and POSIX-compatible exit-code mapping. Failures may point to runtime exec setup regressions or changed error handling for failed process creation.
