<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/winutils/chmod.c -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/winutils/chmod.c

## Purpose
`chmod.c` implements the Windows `winutils chmod` subcommand. It parses octal and symbolic Unix-style permission modes, optionally recurses through directory trees, converts each target path to a Windows long-path form, computes the resulting Unix permission mask, and delegates actual ACL mutation to shared winutils permission helpers.

## Important APIs, Types, And Functions
The exported command entry point is `int Chmod(int argc, wchar_t *argv[])`, with `ChmodUsage()` printing supported syntax. Internal enums model symbolic mode grammar: `CHMOD_WHO_*` maps user/group/other/all bit fields, `CHMOD_OP_*` models `+`, `-`, and `=`, and `CHMOD_PERM_*` models `r`, `w`, `x`, and capital `X`. `MODE_CHANGE_ACTION` is a linked-list node holding one parsed symbolic action (`who`, `op`, `perm`, `ref`, `next_action`). Core helpers are `ParseCommandLineArguments`, `ParseOctalMode`, `ParseMode`, `ComputeNewMode`, `ConvertActionsToMask`, `ChangeFileModeByActions`, `ChangeFileMode`, `ChangeFileModeRecursively`, and `FreeActions`.

## Control Flow
`Chmod` validates arguments, parses either `[OPTION] OCTAL-MODE FILE` or `[OPTION] MODE FILE`, converts the target with `ConvertToLongPath`, then calls either `ChangeFileMode` or `ChangeFileModeRecursively`. `ParseCommandLineArguments` accepts only three or four arguments; the four-argument path must use `-R`, and recursion is enabled only when `GetFileInformationByName(..., followLink=FALSE)` and `IsDirFileInfo` identify the input as a directory. Mode parsing tries octal first; four-digit octal modes ignore the leading setuid/setgid/sticky digit because Windows has no direct equivalent.

Symbolic mode parsing is a state machine over `[ugoa]*([-+=]([rwxX]*|[ugo]))+` clauses. Each completed action is appended to a linked list; missing `who` defaults to all, and chained operations without a comma inherit the last `who`. `ComputeNewMode` applies literal permissions or references another class's bits, expands capital `X` only for directories or files with an existing execute bit, and then applies plus/minus/equal. Recursive chmod walks children with `FindFirstFile`/`FindNextFileW`, skips `.` and `..`, converts child paths to long-path form, recurses into non-symlink directories, and applies the change after children.

## State And Persistence Behavior
The command persists only filesystem ACL/mode changes through `ChangeFileModeByMask`; all parser state is temporary heap allocation via `LocalAlloc`. Recursive mode can change many descendants before failing on a later entry, and there is no rollback. Symlinks and junctions are not traversed as directories by the documented recursion rule; symlink targets are not followed by permission discovery calls using `followLink=FALSE`.

## Dependencies And Integration Points
This file depends on `winutils.h` for path conversion, file information, directory/symlink checks, Unix mask constants, owner/permission lookup, ACL mutation, error reporting, and Windows headers. It integrates with the main winutils command dispatcher through `Chmod`, and with Hadoop Java code that shells out to `winutils.exe chmod` on Windows for POSIX-like permission behavior.

## Risks
Recursive chmod is partial on failure and can leave a tree in mixed permission state. The parser accepts only a subset of POSIX chmod semantics and intentionally drops special mode bits, so parity with Unix chmod is approximate. In `ParseMode`, failed parsing calls `FreeActions(*pActions)` but does not clear the caller's pointer, so a caller that later frees again could double-free if it reused the same pointer after failure; the current `Chmod` path returns immediately on parse failure, limiting practical exposure. `FindFirstFile` handles are not closed in `ChangeFileModeRecursively`, which can leak handles during large recursive walks. Symbolic `X` depends on mode bits returned by `FindFileOwnerAndPermission`, so incorrect Windows-to-Unix mapping propagates into recursive behavior.

## Test Signals
Tests should cover octal modes with three and four digits, invalid octal values, symbolic clauses with comma and inherited `who`, references such as `g=u`, capital `X` on files vs directories, `-R` on files and directories, symlink/junction non-traversal, long paths, permission-denied failures, and partial-recursion behavior. Windows integration tests should verify the resulting ACLs through `FindFileOwnerAndPermission` and Hadoop filesystem permission APIs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/winutils/chmod.c -->
