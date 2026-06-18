# sources/distributed-fs/orangefs/src/client/windows/client-test/create.c

## Purpose
`create.c` contains client tests for directory creation, file creation, long path/name behavior, and repeated file creation.

## Important APIs, Types, And Functions
Public tests are `create_dir`, `create_subdir`, `create_dir_toolong`, `create_files`, `create_file_long`, `create_file_toolong`, and `create_files_many`. Helpers include `create_dir_cleanup`, `randchar`, `create_subdir_cleanup`, `create_subdir_int`, `create_files_cleanup`, `create_file_int`, and `create_file_long_int`.

## Control Flow
Tests generate random names under `options->root_dir`, perform `_mkdir`, `fopen`, or repeated create operations, report expected success/failure via `report_result`, and clean up artifacts. Long file tests require `-tabfile`, parse the first tabfile line to account for filesystem root length, then synthesize names near or beyond `MAX_FILE_NAME`.

## State And Persistence
Temporary directories and files are created under the test root and normally removed before return. `create_files_many` creates and immediately removes 1000 zero-byte files through `create_file_int`.

## Dependencies And Integration Points
It depends on CRT directory/file APIs, errno, `test-support.h`, and helper generators/reporters. These tests indirectly cover Dokany create disposition, mkdir, path length handling, and cleanup behavior.

## Risks And Test Signals
Cleanup is best effort. `create_subdir_cleanup` returns early without freeing `root_dir_int` if path equals root. Long-name tests depend on tabfile parsing assumptions and Windows path limits. Expected error code `2` is platform-specific (`ENOENT`/file not found), so results may vary across runtime layers. These tests are important signals for namespace creation and path conversion.
