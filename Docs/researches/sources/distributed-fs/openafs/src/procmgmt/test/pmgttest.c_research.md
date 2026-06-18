# sources/distributed-fs/openafs/src/procmgmt/test/pmgttest.c

## Purpose
Provides an end-to-end test program for the process-management library. It self-spawns into parent and child modes to validate signal set manipulation, signal handler semantics, process spawning, wait/waitpid behavior, WNOHANG, signal termination, abort handling, environment passing, and NT-only spawn data buffers.

## Important APIs, Types, And Functions
Important helpers are `TimedSleep`, `Bailout`, `ChildTableLookup`, `ChildTableClear`, `SignalCatcher`, `BasicAPITest`, `SingleThreadMgmtTest`, `BehaveLikeAParent`, `BehaveLikeAChild`, and `main`. It uses `spawnprocve`, `spawnprocv`, NT-only `spawnprocveb`, `wait`, `waitpid`, `sigaction`, `signal`, `raise`, `kill`, `WIFEXITED`, `WEXITSTATUS`, `WIFSIGNALED`, and `WTERMSIG`.

## Control Flow
Without arguments the program acts as parent: it runs API-only signal tests, then repeatedly spawns children with special argv markers for spawn, wait, WNOHANG, signal, and abort scenarios. Children validate argv/env/data buffer contents or sleep forever until signaled, then exit with expected statuses. The parent records pids, kills lingering children on bailout, and checks exact wait statuses.

## State And Persistence
State is in volatile signal-catcher flags, a fixed child pid table, environment variable `PMGT_SPAWNTEST`, and NT-only `spawnDatap`/`spawnDataLen`. No disk state is written except possible core/crash artifacts.

## Dependencies And Integration Points
Depends on public `afs/procmgmt.h` and platform runtime behavior. It is the primary behavioral signal for both Unix wrappers and NT emulation.

## Risks And Test Signals
Risks include timing sleeps hiding races, interactive/debug dialogs on NT abort tests, fixed `TEST_CHILD_MAX`, and no multithreaded stress coverage. Passing output `All tests completed successfully.` is the key signal; failures identify API, signal, spawn, or wait-status regressions.
