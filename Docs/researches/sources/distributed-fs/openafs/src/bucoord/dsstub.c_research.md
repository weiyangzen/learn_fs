# sources/distributed-fs/openafs/src/bucoord/dsstub.c

## Purpose
Provides a local flat-file stub for backup dump/tape metadata scanning. It names and opens local `T<tapename>.db` and `D<dumpid>.db` files under the server backup directory, parses dump headers and volume records, finds clone times, and recursively deletes local dump files by parent-child relationships.

## Important APIs, Types, And Functions
Important functions are `OpenTape`, `tailCompPtr`, `ScanDumpHdr`, `ScanTapeVolume`, and `ScanVolClone`. Private helpers `TapeName`, `DumpName`, `OpenDump`, `ScanForChildren`, and `DeleteDump` construct paths, open files, and remove dump trees.

## Control Flow
`TapeName` and `DumpName` allocate canonical local metadata paths with `asprintf`. `OpenTape` and `OpenDump` open those files in caller-specified modes. `ScanDumpHdr` reads the first dump line, parses magic, version, dump name, dump path, parent id, incremental time, create time, and level, then validates magic/version. `ScanTapeVolume` reads one volume-record line and distinguishes success, EOF, and parse/error. `ScanVolClone` scans records until it finds a matching volume name. `DeleteDump` unlinks the dump file and then calls `ScanForChildren`, which scans the backup directory for dump files whose header parent matches the deleted id.

## State And Persistence
State is persistent local metadata in `AFSDIR_SERVER_BACKUP_DIRPATH`, with a text format described in comments. Functions allocate path strings transiently and leave file lifecycle mostly to callers. Deletion removes local dump files and recursively removes child dump metadata.

## Dependencies And Integration Points
Depends on OpenAFS directory constants, BUDB/bubasics/volser headers for constants and types, standard directory and file APIs, and `bc.h`. `tailCompPtr` is reused by display and command code to print the final component of dump schedule paths.

## Risks And Test Signals
The parser uses fixed-size line buffers and whitespace-delimited fields, so names with whitespace cannot be represented and long lines are truncated. Several `sscanf` calls cast `afs_int32 *` to `long int *`, which is ABI-sensitive. Recursive deletion is based on scanning live directory contents and ignores unreadable child headers. Test signals include parsing valid/invalid magic/version headers, EOF and malformed volume lines, clone lookup hits/misses, local tape/dump open failures, child dump recursive deletion, and long-name boundary cases.
