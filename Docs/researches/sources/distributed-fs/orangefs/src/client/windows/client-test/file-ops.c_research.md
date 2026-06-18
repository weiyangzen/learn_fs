# sources/distributed-fs/orangefs/src/client/windows/client-test/file-ops.c

## Purpose
`file-ops.c` tests deletion, directory removal, rename, and move behavior through ordinary CRT filesystem APIs against the mounted client root.

## Important APIs, Types, And Functions
Tests include `delete_file`, `delete_file_notexist`, `delete_dir_empty`, `delete_dir_notempty`, `rename_file`, `rename_file_exist`, `move_file`, `move_file_baddir`, and `move_file_exist`. `lookup_file_int` wraps `_stat` to check whether a path exists.

## Control Flow
Each test creates random files/directories as needed, performs `_unlink`, `_rmdir`, or `rename`, reports expected results, and removes remaining artifacts. Move tests build destination paths under newly created or intentionally missing directories.

## State And Persistence
Temporary files and directories are created under `options->root_dir`. Cleanup generally removes final artifacts, though some paths omit unlink of moved files before removing directories, depending on target behavior.

## Dependencies And Integration Points
The module depends on CRT stat/rename/remove APIs, errno constants, `test-support.h`, and `file-ops.h`. It exercises Dokany delete-on-close, directory empty checks, and `fs_rename`.

## Risks And Test Signals
`delete_dir_notempty` reports expected `ENOTEMPTY` but fatal logic checks `code != 0`, so a correct `ENOTEMPTY` result can be treated as fatal if fatal were enabled. `rename_file_exist` comments that OrangeFS overwrites, reports success expected, but fatal logic checks `code != EACCES`, which conflicts with the report expectation. These inconsistencies reduce reliability of fatal-mode signal. Still, the tests are useful for namespace mutation and error propagation.
