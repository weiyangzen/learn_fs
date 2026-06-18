# sources/distributed-fs/orangefs/src/client/windows/client-test/file-ops.h

## Purpose
`file-ops.h` declares namespace mutation tests for delete, rename, and move operations.

## Important APIs, Types, And Functions
It declares delete tests (`delete_file`, `delete_file_notexist`, `delete_dir_empty`, `delete_dir_notempty`), rename tests (`rename_file`, `rename_file_exist`), and move tests (`move_file`, `move_file_baddir`, `move_file_exist`).

## Control Flow
The header is consumed by `test-list.h`, which registers these tests for the runner. All functions follow the shared `global_options`/`fatal` signature.

## State And Persistence
State is in implementation-created temporary filesystem objects under the configured root.

## Dependencies And Integration Points
It includes `test-support.h` for shared test types. It is implemented by `file-ops.c`.

## Risks And Test Signals
The header gives no metadata about expected success/failure or fatal defaults; those live separately in `test-list.h` and implementation logic, where some inconsistencies exist.
