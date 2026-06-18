# sources/distributed-fs/openafs/src/procmgmt/redirect_nt.c

## Purpose
Redirects native Microsoft C runtime signals on Windows into the OpenAFS process-management signal system.

## Important APIs, Types, And Functions
Key functions are `NativeSignalHandler`, `pmgt_RedirectNativeSignals`, and `pmgt_RestoreNativeSignals`. The handler maps native `SIGINT`, `SIGILL`, `SIGFPE`, `SIGSEGV`, `SIGTERM`, and `SIGABRT` names into `pmgt_SignalRaiseLocalByName`. For abort, it exits with `PMGT_SIGSTATUS_ENCODE(libSigno)`.

## Control Flow
`pmgt_RedirectNativeSignals` installs `NativeSignalHandler` for supported CRT signals. The handler reinstalls itself because NT CRT signals are unreliable, translates the native signal to a string, raises the matching procmgmt signal, and handles abort specially so `waitpid` observes a signal-style termination rather than CRT exit code 3. `pmgt_RestoreNativeSignals` resets handlers to `SIG_DFL`.

## State And Persistence
Persistent runtime state is the process CRT signal-disposition table. `dummyDouble` exists to ensure floating-point support for `SIGFPE` trapping.

## Dependencies And Integration Points
Used by `procmgmt_nt.c` library initialization and cleanup. It deliberately avoids `procmgmt.h` because that header redefines signal-related APIs.

## Risks And Test Signals
Risks include incomplete native signal coverage, reentrant signal handling, comment typo naming restore as redirect, and reliance on CRT-specific behavior. Test signals are abort reporting as `SIGABRT`, native access violation/floating-point exceptions mapping to wait status, and restore-on-DLL-detach behavior.
