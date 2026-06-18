# sources/distributed-fs/openafs/src/WINNT/tests/torture/Source/WinTorture.c

## Purpose

`WinTorture.c` is the top-level Windows stress-test coordinator for OpenAFS. It parses command-line options, prepares log directories and named synchronization objects, starts worker threads implemented in `WinThreads.c`, aggregates per-thread statistics, loops by iteration count or runtime, and finalizes master logs when the last process in a job finishes.

## Important APIs, Types, and Functions

- Uses `includes.h`, `common.h`, PSAPI, optional Hesiod locker resolution, and external logging/stat functions from `output.c`.
- Globals hold option state (`ClientText`, `PathToSecondDir`, `verbose`, `BufferSize`, `UseLocker`, `EndOnError`, `AfsTrace`, `ChronLog`, `PrintStats`), thread status, named mutex/event handles, and `ExitStatus`.
- `create_procs()` allocates per-thread command-stat blocks and `PARAMETERLIST` structures, creates per-thread events, starts suspended worker threads, resumes them, optionally resolves/attaches lockers, waits for all thread events, logs completion reasons, and calls `show_results()`.
- `show_results()` aggregates `cmd_struct` counters across threads, writes process stats, and updates master logs.
- `main()` parses options, derives target/locker paths, creates mutexes/events/job object/directories, runs the main iteration/time loop, builds master logs, updates process/iteration counts, and performs final job-level cleanup/renaming.
- `FindProcessCount()` uses `QueryInformationJobObject()` to determine assigned process count.
- A local `getopt()` implementation supports Unix-like option parsing on Windows.

## Control Flow

`main()` initializes defaults, parses options such as script file, target hostname/log name, iteration count, runtime, thread count, locker/UNC target, second directory, stats, tracing, end-on-error, and verbose mode. It validates required target and locker inputs, reconstructs a command-line summary, normalizes slash direction, and optionally derives an AFS locker target from Hesiod data. It creates global named mutexes/events and a job object, creates log/test directories, removes the current host log directory, and then loops.

Each loop checks time/iteration/shutdown limits, increments the loop counter, logs start time, calls `create_procs()`, logs end/lapse time, updates a shared `IterationCount` file under a mutex, handles end-on-error and recovery sleep, then repeats. After the loop it builds a `Master.log` by concatenating thread logs, builds process/master stat logs, increments `ProcessCount`, and if this is the only process in the job, moves raw count/stat files, builds the final master stat log, renames `log#####` to a timestamped directory, resets and closes global events, and releases the exit mutex.

`create_procs()` starts up to `NumberOfThreads` worker threads. It skips inactive threads when `EndOnError` is set, creates named events keyed by process ID/host/thread, passes each thread a slice of the command stats array, resumes the thread, waits for all event handles, logs per-thread completion or failure reason, aggregates results, and frees per-thread allocations.

## State and Persistence

Persistent artifacts include `log#####` directories, host subdirectories, thread logs, process stats, master logs, raw/final stat logs, `IterationCount`, and `ProcessCount`. Runtime state is coordinated through named events/mutexes (`AfsShutdownEvent`, `AfsPauseEvent`, `AfsContinueEvent`, `WinTorture*Mutex`) and a Windows job object named from `LogID`.

## Dependencies and Integration Points

The file depends on `WinThreads.c` for `StressTestThread()`, `output.c` for stats/log aggregation, `nbio.c` indirectly through worker execution, and optional Hesiod/locker attach functions. It uses Windows process, job-object, event, mutex, directory, file, time, and PSAPI APIs. It is the central executable entry point for the WinTorture test suite.

## Risks and Edge Cases

- `MAX_THREADS` is 100 but arrays such as `ThreadStatus` are sized by `MAX_HANDLES` from shared headers; option validation for `-n` is not visible here.
- Several `sprintf`, `strcpy`, and shell `system("rmdir ...")` uses are unquoted and fixed-buffer.
- `CloseHandle(hEventHandle[i])` is called after handles were already closed and nulled in an earlier loop, which can produce invalid-handle calls.
- `grand_total += FinalCmdInfo[j].total_sec` in `show_results()` indexes by thread `j` instead of command `i`, suggesting a stats aggregation bug.
- `FindProcessCount()` returns immediately after `QueryInformationJobObject()`, leaving the PSAPI fallback dead code.
- Named global events/mutexes can collide across simultaneous test runs with different working directories.
- If the process exits early, log directory renaming and event cleanup may not run.

## Test Signals

Useful signals are iteration start/end console output, thread completion logs, per-thread and process stats, master stat logs, job-level final log directory rename, correct handling of `-i` versus `-m`, and recovery behavior when `ThreadStatus` marks errors. Integration testing requires a representative command script and AFS target path.
