# sources/distributed-fs/openafs/src/procmgmt/afskill.c

## Purpose
Implements an AFS-aware `kill` command front-end that uses the process-management `kill` abstraction. It is intended especially for Windows NT, where non-`SIGKILL` signaling works only for processes linked with the OpenAFS process-management library.

## Important APIs, Types, And Functions
Defines `signal_map_t`, static `signalMap`, `PrintSignalList`, `SignalArgToNumber`, `PrintUsage`, and `main`. It recognizes names such as `HUP`, `INT`, `TERM`, `KILL`, `USR1`, `CHLD`, and `TSTP`, plus numeric signals parsed by `strtol`.

## Control Flow
`main` derives the program basename, handles no-argument usage, `-l` signal listing, or signal delivery. A leading `-signal` argument changes the default signal from `SIGTERM`. Remaining arguments are parsed as positive pids and passed to `kill((pid_t)pid, signo)`. Errors are mapped to user-facing diagnostics for invalid signal, no such process, permission, or generic errno.

## State And Persistence
No persistent state. The only external effect is process signaling or termination through the platform `kill` implementation.

## Dependencies And Integration Points
Depends on `procmgmt.h` for portable signal constants and `kill` macro/function behavior. On NT this routes to named-pipe or `TerminateProcess`; on Unix it is the native signal API.

## Risks And Test Signals
Risks include sending unintended signals, platform-specific support gaps for non-AFS Windows processes, and accepting numeric signals outside the named table until lower layers reject them. Test signals include `-l`, invalid pid handling, self-signal tests, non-existent pid mapping, and SIGKILL fallback behavior on Windows.
