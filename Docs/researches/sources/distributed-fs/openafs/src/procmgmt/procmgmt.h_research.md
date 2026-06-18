# sources/distributed-fs/openafs/src/procmgmt/procmgmt.h

## Purpose
Provides OpenAFS portable process spawning, waiting, and signal APIs. On Windows NT it emulates a Unix-like `pid_t`, `wait`, `waitpid`, `signal`, `sigaction`, `raise`, `kill`, signal sets, and wait-status macros; on Unix it maps spawn wrappers to native fork/exec semantics and includes native signal/wait headers.

## Important APIs, Types, And Functions
Windows definitions include `pid_t`, `WIFEXITED`, `WIFSIGNALED`, `WEXITSTATUS`, `WTERMSIG`, `WNOHANG`, `SIGHUP` through `SIGTSTP`, `NSIG`, `sigset_t`, `struct sigaction`, `pmgt_ProcessSpawnVEB`, `pmgt_ProcessWaitPid`, `pmgt_SigactionSet`, `pmgt_SignalSet`, `pmgt_SignalRaiseLocal`, and `pmgt_SignalRaiseRemote`. Public spawn macros include `spawnprocveb`, `spawnprocve`, `spawnprocve_sig`, and `spawnprocv`. Unix exposes `pmgt_ProcessSpawnVE`.

## Control Flow
Consumers include this header and use familiar Unix names. On NT, macros redirect calls into the process-management DLL/library. On Unix, only spawn helpers are wrapped while native wait/signal behavior remains intact.

## State And Persistence
Declares NT exported `pmgt_spawnData` and `pmgt_spawnDataLen`, a buffer delivered from parent to spawned child. Wait status encodings are part of the cross-process contract.

## Dependencies And Integration Points
Central integration header for `afskill`, procmgmt implementations, and OpenAFS code needing portable process handling. On Windows it must be included before `signal.h`, which it deliberately blocks.

## Risks And Test Signals
Risks include macro substitution surprises, incompatible Windows signal semantics, `NSIG <= 33` assumptions in bitsets, and public ABI drift. Test signals include compiling consumers on Unix and NT, spawn/wait tests, signal handler install/reinstall behavior, and child data buffer delivery.
