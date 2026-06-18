# sources/distributed-fs/openafs/src/procmgmt/procmgmt_unix.c

## Purpose
Implements the Unix process-spawn wrapper used by `procmgmt.h`, giving OpenAFS code a consistent `spawnprocve`/`spawnprocv` API.

## Important APIs, Types, And Functions
Exports `pmgt_ProcessSpawnVE(const char *spath, char *sargv[], char *senvp[], int estatus, sigset_t *mask)`. It depends on native `fork`, `execv`, `execve`, `sigprocmask`, `close`, and `exit`.

## Control Flow
The function forks. In the child, it closes file descriptors 3 through 63, applies the supplied signal mask with `SIG_SETMASK`, executes `spath` with either explicit environment or inherited environment, and exits with `estatus` if exec fails. The parent returns the child pid or `-1` from failed `fork`.

## State And Persistence
No in-process persistent state is retained. External state is the spawned child process and inherited stdio descriptors.

## Dependencies And Integration Points
Used by Unix `procmgmt.h` spawn macros and any OpenAFS code needing child process creation with controlled environment and signal mask.

## Risks And Test Signals
Risks include hard-coded closure of only descriptors below 64, calling `sigprocmask` with a possibly NULL mask, lack of close-on-exec awareness above fd 63, and silent child `exec` failure represented only by `estatus`. Test signals are spawning with/without environment, signal-mask inheritance, exec failure exit status, and descriptor inheritance checks.
