# sources/distributed-fs/openafs/src/WINNT/tests/winflock/main.cpp

Purpose: entry point and orchestration for the Win32 file-locking test program. It runs coordinated parent/child processes to validate sharing, byte-range locks, wait locks, reads, writes, unlocks, and lock escalation.

Important APIs and functions: `parse_cmd_line` handles `-d`, `-nr`, `-child`, `-p`, `-wS`, `-wP`, and `-wC`. `spawn_kids` starts a child copy of the executable. `run_tests` sequences test routines with parent/child synchronization macros. `create_sync_objects` and `free_sync_objects` manage named events and a log mutex. `_tmain` wires setup, child spawning, test execution, and cleanup.

Control flow: parent parses options, creates synchronization objects, starts a child, waits for child readiness, then both processes run the same test sequence. `PC_CALL` wraps routines that should run in coordinated parent/child phases; `PCINT_CALL` invokes tests that manage their own synchronization.

State and persistence: global booleans select test modes. Named local events `WinFLockChildEvent` and `WinFLockParentEvent` coordinate phases; `WinFLockLogFileMutex` serializes log blocks. Test files are created under `test_dir`.

Dependencies and integration: depends on `winflock.h`, `sync.cpp`, and `tests.cpp`, plus Win32 process/event/mutex APIs.

Risks and test signals: command-line construction uses a `MAX_PATH` buffer and does not quote `-d` values. `parse_cmd_line` documents `-wP <dir>` but does not consume a directory argument. Console `TEST:* PASS/FAILED` lines and synchronized parent/child log blocks are primary signals.
