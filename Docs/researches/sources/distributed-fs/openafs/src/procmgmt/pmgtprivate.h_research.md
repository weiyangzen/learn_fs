# sources/distributed-fs/openafs/src/procmgmt/pmgtprivate.h

## Purpose
Declares private process-management support that should not be exported through public `procmgmt.h`, primarily for Windows NT signal emulation internals.

## Important APIs, Types, And Functions
For `AFS_NT40_ENV`, defines `PMGT_SIGSTATUS_ENCODE`, `PMGT_IS_SIGSTATUS`, and `PMGT_SIGSTATUS_DECODE`, which encode a Unix-like signal termination into a Windows process exit status. Declares `pmgt_SignalRaiseLocalByName`, `pmgt_RedirectNativeSignals`, and `pmgt_RestoreNativeSignals`.

## Control Flow
The macros are used by NT signal/default-action code to translate process exit codes back into wait statuses. Native signal redirection code raises library signals by name to avoid including `procmgmt.h` where it would redefine `signal`/`raise`.

## State And Persistence
The header declares no storage. It defines an exit-status encoding contract that persists across parent/child process boundaries until `waitpid` decodes it.

## Dependencies And Integration Points
Integrated by `procmgmt_nt.c` and `redirect_nt.c`. It is intentionally separated from public headers to avoid exposing NT implementation details.

## Risks And Test Signals
Risks are encoding collisions with real process exit codes and drift between encoder/decoder users. Test signals are Windows `waitpid` reporting `WIFSIGNALED`/`WTERMSIG` correctly for default signal actions and abort/native signal redirection.
