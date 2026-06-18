# sources/distributed-fs/orangefs/src/client/windows/client-test/find.c

## Purpose
`find.c` provides Windows-only tests for directory lookup and wildcard enumeration against the mounted client.

## Important APIs, Types, And Functions
Under `WIN32`, it implements `find_files` and `find_files_pattern`. It uses `_findfirst`, `_findnext`, `_findclose`, `struct _finddata_t`, `quick_create`, and reporting helpers.

## Control Flow
`find_files` creates ten random files and confirms each exact path can be found. `find_files_pattern` creates ten files with an `xyz` prefix, finds them using an `xyz*` pattern, then using `xyz?????`, and marks each generated name as found. Both tests clean up generated files.

## State And Persistence
Only temporary files under `options->root_dir` are created and removed. Search state is held in CRT find handles.

## Dependencies And Integration Points
It depends on Windows CRT find APIs and `test-support.h`. It directly exercises `PVFS_Dokan_find_files_with_pattern`, name conversion, wildcard matching, and directory paging through the mounted path.

## Risks And Test Signals
The non-Windows branch is not implemented. The pattern test does not reset `mark[]` between `*` and `?` checks, so the second check can pass based on first-pass marks. Error handling assumes `errno == ENOENT` after enumeration completion. The test is still valuable for confirming basic find callbacks and wildcard compatibility.
