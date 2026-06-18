<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/admin/list_defective_files_command.cc -->
# sources/distributed-fs/lizardfs/src/admin/list_defective_files_command.cc

## Purpose
Implements `lizardfs-admin list-defective-files`, listing files or directories with unavailable chunks, under-goal chunks, or structure errors.

## Important APIs, Types, and Functions
Defines `kDefaultEntriesLimit`, `NodeErrorFlag` bits, `flagToString`, and command methods. Supported options are `--porcelain`, `--unavailable`, `--undergoal`, `--structure-error`, and valued `--limit=`.

## Control Flow, State, and Persistence
`run` validates host/port, ORs selected error flags or defaults to all, gets an entry limit, then pages through `cltoma::listDefectiveFiles::build(flags, entry_index, entries_left)`. Responses update `entry_index` and return `DefectiveFileInfo` records until the master reports index zero or the limit is exhausted. It prints raw quoted filename plus numeric flags in porcelain mode or labeled flag text otherwise. No persistent state is changed.

## Dependencies and Integration Points
Depends on `ServerConnection`, `protocol/cltoma.h`, `protocol/matocl.h`, and the master's defective-file scan/list implementation.

## Risks and Test Signals
Risks include including `registered_admin_connection.h` without using it, direct `exit(1)` on oversized responses instead of throwing, simplistic porcelain quoting that does not escape filenames, and large limits driving repeated master work. Test signals are each flag combination, default all-flags behavior, pagination with nonzero continuation index, limit exhaustion, empty result output, malformed oversized response handling, and filenames with spaces/quotes/newlines.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/admin/list_defective_files_command.cc -->
