# sources/distributed-fs/openafs/src/procmgmt/procmgmt_nt.c

## Purpose
Implements the Windows NT process-management library that emulates Unix process spawning, waiting, and software signals for OpenAFS processes.

## Important APIs, Types, And Functions
Major public functions are `pmgt_SigactionSet`, `pmgt_SignalSet`, `pmgt_SignalInit`, `pmgt_SignalRegister`, `pmgt_SignalRaiseLocal`, `pmgt_SignalRaiseLocalByName`, `pmgt_SignalRaiseRemote`, `pmgt_ProcessSpawnVEB`, and `pmgt_ProcessWaitPid`. Important private helpers include `SignalIsDefined`, `DefaultActionHandler`, `ProcessSignal`, `RemoteSignalListenerThread`, `StringArrayToString`, `StringArrayToMultiString`, `ComputeWaitStatus`, `CreateChildDataBuffer`, `ReadChildDataBuffer`, `ChildMonitorThread`, `PmgtLibraryInitialize`, and `DllMain`. Global state includes a signal disposition table, child process table, mutexes, condition variable, named signal pipe, and exported spawn data.

## Control Flow
DLL attach initializes locks, default signal dispositions, child-process table, optional parent-provided spawn data, a per-process named pipe for remote signals, a listener thread, and native signal redirection. Local signals run through `ProcessSignal`; remote signals are delivered with `CallNamedPipe`, ACKed, and executed on a new thread so `SIGKILL` is not blocked behind a stuck handler. Spawning converts argv/envp to Windows command-line/environment strings, optionally creates shared memory for spawn data, starts the child suspended, registers a process-table entry, starts a monitor thread, resumes the child, and waits briefly for data consumption. `waitpid` blocks on `childTermEvent` or returns `0` for `WNOHANG`, then converts Windows exit/exception/signal status to Unix wait status.

## State And Persistence
Runtime persistence is in process-global tables, named pipes (`TransarcAfsSignalPipe<PID>`), named shared memory/events for spawn data, child process handles, and encoded exit statuses. No disk state is written.

## Dependencies And Integration Points
Depends on Win32 process, pipe, event, shared-memory, and signal APIs; pthread mutex/cond wrappers; NT error mapping; security utility ACL updates; and private status encoding in `pmgtprivate.h`. It backs `procmgmt.h` macros and `afskill`.

## Risks And Test Signals
Risks include command-line quoting that rejects embedded quotes, fixed `PMGT_CHILD_MAX`, signal serialization not fully matching POSIX masks, races before a child creates its signal pipe, named-pipe ACL/security behavior, and 10-second spawn-data timeout. Test signals are the `pmgttest` suite, remote/local signal delivery, `SIGKILL` fallback to `TerminateProcess`, exception-to-signal wait decoding, spawn with env/data, and wait/waitpid `ECHILD`/`WNOHANG` behavior.
