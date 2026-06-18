# sources/distributed-fs/moosefs/mfsmaster/restore.c

## Purpose
`restore.c` is the MooseFS master changelog replay interpreter. It parses textual changelog operations, validates separators and encoded fields, dispatches to `*_mr_*` metadata mutation APIs, enforces metadata-version sequencing, and supports both network replication replay and merged changelog-file restore.

## Important APIs, Types, And Functions
The parser is macro-heavy. `EAT` validates exact separators. `GETNAME`, `GETPATH`, `GETDATA`, `GETARRAYU32`, and `GETHEX` decode escaped names, paths, arbitrary binary blobs, integer arrays, and hex label expressions. `GETU8/16/32/64` and `GETX32` parse numeric values with basic range checks.

There is one `do_*` handler for each changelog operation family: filesystem mutations (`do_create`, `do_link`, `do_move`, `do_unlink`, `do_attr`, `do_length`, `do_write`, `do_trunc`, `do_snapshot`, trash operations), chunks (`do_chunkadd`, `do_chunkdel`, `do_setversion`, `do_nextchunkid`), open files (`do_acquire`, `do_release`), locks (`do_flock`, `do_posixlock`), sessions (`do_sesadd`, `do_seschanged`, `do_sesdel`, connect/disconnect), patterns, storage classes, quotas, xattrs, ACLs, and metadata id changes.

The exported functions are `restore_net()` and `restore_file()`. `restore_line()` is the central dispatcher and uses a four-byte hash of the operation prefix before confirming exact strings.

## Control Flow
Each changelog line starts with a timestamp, `|`, an operation name, parenthesized arguments, and often a `:` result section. `restore_line()` parses the timestamp, selects a handler, and returns the handler status. Unknown entries log a warning and return mismatch.

Handlers parse only their operation syntax and delegate actual state changes to other modules. For example, `do_setacl()` validates ACL blob length and calls `fs_mr_setacl()`, `do_posixlock()` calls `posix_lock_mr_change()`, `do_sesadd()` calls `sessions_mr_sesadd()`, and `do_scset()` builds four `storagemode` values before calling `sclass_mr_set_entry()`.

`restore_net()` is strict for live replication: the incoming changelog version must equal `meta_version()`, the operation must parse and return `MFS_STATUS_OK`, and the metadata version must increase exactly once.

`restore_file()` is merge-oriented. It tracks static `v`, `lastv`, and `lastshfn` state, ignores older entries, tolerates exact duplicates, reports holes with `-2`, applies new entries, and verifies that each applied line advances metadata version by one. It retains the last filename through the shared-pointer helper.

## State, Persistence, And Dependencies
The file itself persists no metadata. It reconstructs metadata by calling module-specific replay APIs that increment metadata version. Several handlers keep static reusable buffers for variable-length decoded fields, so the parser is not reentrant.

Dependencies include `sharedpointer.h`, `filesystem.h`, `sessions.h`, `openfiles.h`, `flocklocks.h`, `posixlocks.h`, `csdb.h`, `chunks.h`, `storageclass.h`, `patterns.h`, `metadata.h`, `mfsstrerr.h`, and logging/assertion helpers.

## Integration Points
`merger.c` calls `restore_file()` while merging changelog files. Master replication code calls `restore_net()` for live changelog packets. Every `*_mr_*` callee is part of the metadata consistency surface: filesystem, chunk database, chunk placement, sessions, open files, locks, storage classes, patterns, and csdb.

## Risks
The parser uses macros that return from the enclosing function; any added handler must follow the same error convention carefully. `GETU32` and `GETU64` rely on `strtoul/strtoull` and do not check that at least one digit was consumed in every call.

Static buffers and static merge state make the implementation single-threaded. Concurrent restores would corrupt parse buffers and version tracking.

`restore_file()` ignores parse errors (`status < 0`) but stops on positive operation errors. This is intentional for corrupted lines but can hide repeated syntax problems during low-verbosity restores.

Storage-class parsing supports several historic formats, so changes to `sclass_make_changelog()` or `do_scset()` must stay in lockstep.

## Test Signals
Good tests include one changelog line per `do_*` handler, malformed separator and escape handling, missing line/hole detection, duplicate changelog entries, version-not-incremented and incremented-more-than-once detection, strict `restore_net()` desync behavior, ACL blob length mismatch, session syntax variants with and without export checksum/umask/disables, storage-class legacy and current formats, and snapshot GID formats.
