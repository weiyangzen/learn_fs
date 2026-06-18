# File Research: sources/block-storage/util-linux/sys-utils/choom.c

## Scope

Implements `choom`, a small utility to inspect or change Linux OOM killer scoring, or run a command under a selected `oom_score_adj`.

## Public And Internal APIs Covered

- Main command-line entry point.
- `/proc` helpers: `get_score()`, `get_score_adj()`, `set_score_adj()`.

## Control Flow And Behavior

- Supports three modes:
  - `-p PID` with no adjust value prints `oom_score` and `oom_score_adj`.
  - `-p PID -n VALUE` changes an existing process's `oom_score_adj`.
  - `-n VALUE COMMAND ...` changes the current process's `oom_score_adj` then `execvp()`s the command.
- Validates that PID mode and command mode are not mixed.
- Uses `/proc/<pid>` path context, with `getpid()` for command-launch mode.
- Prints old and new adjustment values when changing an existing PID.

## Dependencies

- Linux `/proc/<pid>/oom_score` and `/proc/<pid>/oom_score_adj`.
- util-linux path, PID/int parsing, closestream, i18n, and exec error helpers.

## Risks And Invariants

- Running a command requires an explicit adjust value.
- Setting `oom_score_adj` may fail due to permissions or kernel constraints.
- In command mode, the path context must be released before replacing the process image.
