<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/create-remove.c -->
# sources/distributed-fs/openafs/src/tests/create-remove.c

## Purpose
Compiled helper that repeatedly creates and removes either one file or one directory name to stress metadata operations.

## Important APIs, Types, And Functions
Defines `creat_dir`, `remove_dir`, `creat_file`, `unlink_file`, `usage`, `creat_many`, and `main`. Uses `mkdir`, `rmdir`, `open`, `close`, `unlink`, `snprintf`, and `strtol`.

## Control Flow
Parses type (`file` or `dir`) and count. `creat_many` builds a process-specific name `foo-<num>-<pid>`, then loops count times calling the create and delete callbacks.

## State And Persistence
No persistent state on success; a failed iteration may leave the current test file/directory.

## Dependencies And Integration Points
Used by `create-remove-dirs` and `create-remove-files`.

## Risks And Test Signals
`creat_file` reports open failures as `mkdir` in the error message. The same name is reused each cycle, stressing cache invalidation and name reuse. Success means all cycles completed without POSIX errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/create-remove.c -->
