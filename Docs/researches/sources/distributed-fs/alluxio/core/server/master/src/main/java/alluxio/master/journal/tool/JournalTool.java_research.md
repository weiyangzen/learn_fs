# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/journal/tool/JournalTool.java

## Purpose
`JournalTool` is the command-line entry point for converting Alluxio journals into human-readable files. It selects the UFS or embedded journal dumper from configuration and parses common dump options.

## Important APIs, types, and functions
`main(String[])` parses arguments, handles help, and calls `dumpJournal()`. CLI options are `help`, `master`, `start`, `end`, `inputDir`, and `outputDir`. `dumpJournal()` selects `UfsJournalDumper` for `JournalType.UFS` and `RaftJournalDumper` for `JournalType.EMBEDDED`. `parseInputArgs` fills static option fields. `usage()` prints Apache CLI help.

## Control flow
Argument parsing uses `DefaultParser`; parse failure prints usage and exits failed. Help exits successfully. The input directory defaults to `MASTER_JOURNAL_FOLDER`; output defaults to `journal_dump-${timestamp}`. Unsupported journal types print an error and return.

## State and persistence behavior
The tool stores parsed options in static fields for the process lifetime and writes dump output under `sOutputDir`. It reads but should not mutate journal state.

## Dependencies and integration points
It depends on Alluxio configuration, `JournalType`, Apache Commons CLI, runtime constants, and the two dumper implementations. Operators use it offline for debugging/recovery inspection.

## Risks
`main` catches `Exception` around dump but not all `Throwable` even though `dumpJournal` declares `Throwable`; serious errors may escape. Static parsed state makes repeated invocation in the same JVM awkward for tests. The tool relies on process configuration to decide journal type, so an incorrect config can select the wrong reader for an input dir.

## Test signals
Tests should cover option parsing defaults, help and parse failures, UFS/embedded dumper selection, unsupported type behavior, absolute path normalization, start/end parsing including `Long.MAX_VALUE`, and repeated parse invocations.
