# sources/distributed-fs/openafs/src/WINNT/tests/torture/Source/WinThreads.c

## Purpose

`WinThreads.c` implements the per-thread execution engine for WinTorture. Each thread reads a dbench/netbench-style script file, substitutes client/locker variables, dispatches operations to `nb_*` filesystem functions, records per-command timing/error statistics, reacts to global pause/continue/shutdown events, and checks whether an AFS path is online after certain network-name failures.

## Important APIs, Types, and Functions

- Includes optional OpenAFS headers for `pioctl` and `VIOC_PATH_AVAILABILITY`; in `NO_AFS_SOURCE` mode it declares enough local types to dynamically call `pioctl`.
- Global named handles include `MutexHandle`, `FileMutexHandle`, `ShutDownEventHandle`, `PauseEventHandle`, `ContinueEventHandle`, and `OSMutexHandle`.
- Many thread-local (`__declspec(thread)`) values hold current command state: process number, log ID, buffer, locker paths, hostname, command stats, file table, event handle, exit status, and last error.
- `StressTestThread()` initializes thread-local state from `PARAMETERLIST`, opens its completion event, allocates the I/O buffer, creates/open named events and mutexes, repeatedly runs `run_netbench()`, and handles `ERROR_NETNAME_DELETED` recovery by polling `IsOnline()`.
- `run_netbench()` reads the script file, parses commands, performs substitutions, handles control events, dispatches operations such as `NTCreateX`, `Mkdir`, `Attach`, `CreateFile`, `WriteX`, `ReadX`, `LockingX`, and cleans up open handles.
- `IsOnline()` dynamically loads `afsauthent.dll`, gets `pioctl`, and calls `VIOC_PATH_AVAILABILITY` on the path.

## Control Flow

`StressTestThread()` receives a `PARAMETERLIST`, copies shared settings into thread-local variables, opens a uniquely named completion event created by `WinTorture.c`, allocates and fills `IoBuffer`, creates named control events/mutexes, and enters a retry loop. Before each run it resets shared and thread-local command counters. It calls `run_netbench()`. If `LastKnownError` is not `ERROR_NETNAME_DELETED`, the loop ends. Otherwise it logs recovery, clears exit status, marks the thread active, and calls `IsOnline()` up to four times with ten-second sleeps. Persistent offline or missing AFS DLL/pioctl marks the thread failed.

`run_netbench()` opens the client script, reads up to 128 bytes at a time, manually advances the file pointer by the consumed line length, strips CR/LF, handles pause and shutdown named events, skips blank/comment lines, substitutes `client1`, `clients`, `\\afs\\locker`, and optional second directory placeholders, tokenizes on spaces into `params`, updates benchmark state commands, and dispatches each recognized operation to its matching `nb_*` function. Any operation returning `-1` breaks execution. At exit it ends timing, closes all open file-table handles, deletes the local critical section, and returns.

`IsOnline()` serializes dynamic AFS DLL loading with `OSMutexHandle`, loads `afsauthent.dll`, resolves `pioctl`, invokes `VIOC_PATH_AVAILABILITY`, and maps specific `errno` values to offline versus online status. Missing DLL/function are distinct return statuses.

## State and Persistence

Per-thread state is held in TLS and in log files written through external `LogMessage()`/`LogStats()`. Threads create or open named Win32 events and mutexes shared across the process or processes. File operation state is in the TLS `ftable`. Persistent artifacts are thread logs and stats under the WinTorture log directory.

## Dependencies and Integration Points

This file is tightly coupled to `WinTorture.c` for thread creation and `PARAMETERLIST`, to `nbio.c` for operation implementations, to `output.c` for logging/statistics, and optionally to OpenAFS `afsauthent.dll`/`pioctl` for online checks. The script grammar is the dbench/netbench command stream plus OpenAFS-specific commands like `SetLocker`, `Attach`, `Detach`, and `Xrmdir`.

## Risks and Edge Cases

- Expressions such as `if (rc = WaitForSingleObject(...) == WAIT_OBJECT_0)` assign the boolean comparison result, not the raw wait status.
- Script reading in fixed 128-byte chunks can mishandle lines longer than the chunk size.
- Tokenization is space-only and does not handle quoted paths.
- Several string copies and `sprintf` calls use fixed buffers without bounds checks.
- `run_netbench()` initializes a local critical section per thread; it only protects that thread's verbose `printf`, not global console output.
- `IsOnline()` calls `pioctl` and then checks `errno` only when `code` is zero, which may reflect legacy OpenAFS semantics but is counterintuitive.
- Named control objects use fixed global names, so separate WinTorture runs can interfere.

## Test Signals

Signals include per-thread logs, command timing/error stats, exit status reasons, recovery logs after `ERROR_NETNAME_DELETED`, and online/offline statuses from `IsOnline()`. Script coverage should exercise every dispatched command, pause/continue/shutdown events, long paths, failure paths, and AFS DLL absence.
