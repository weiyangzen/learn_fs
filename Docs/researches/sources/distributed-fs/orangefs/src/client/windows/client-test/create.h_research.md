# sources/distributed-fs/orangefs/src/client/windows/client-test/create.h

## Purpose
`create.h` declares the creation-related test functions registered by `test-list.h`.

## Important APIs, Types, And Functions
It exposes `create_dir`, `create_subdir`, `create_dir_toolong`, `create_files`, `create_file_long`, `create_file_toolong`, and `create_files_many`, all with signature `int (global_options *options, int fatal)`.

## Control Flow
The header is declarative. `client-test.c` invokes these functions through `op_table`; each function reports results and returns `0`, an errno-style technical error, or `CODE_FATAL`.

## State And Persistence
State is owned by implementations in `create.c` and by the shared `global_options`.

## Dependencies And Integration Points
It includes `test-support.h` for `global_options` and result constants. It is consumed by `test-list.h`.

## Risks And Test Signals
The broad signature makes fatal policy caller-controlled. No direct compile-time relationship records which tests require `-tabfile`; that is enforced only at runtime in `create.c`.
