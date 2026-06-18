# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/journal/tool/AbstractJournalDumper.java

## Purpose
`AbstractJournalDumper` is the base for offline journal dump tools. It owns common input/output paths and converts checkpoint streams into human-readable files, including compound and RocksDB-backed inode checkpoints.

## Important APIs, types, and functions
The constructor captures master name, sequence range, input/output dirs, checkpoint output prefix, and edits file path, and creates the output directory. Subclasses implement `dumpJournal()`. `readCheckpoint(CheckpointInputStream, Path)` dispatches to compound, Rocks single, or regular checkpoint readers. `readCompoundCheckpoint`, `readRocksCheckpoint`, and `readRegularCheckpoint` perform the concrete conversions.

## Control flow
Compound checkpoints are recursively expanded by reading named entries and resolving child paths. Rocks checkpoints restore into a temporary `RocksInodeStore`, iterate inode views, and print proto forms separated by a dashed line. Regular checkpoints delegate to the checkpoint type's human-readable parser. Temporary Rocks DB directories are removed in `finally`.

## State and persistence behavior
This tool reads persisted journal/checkpoint state and writes text output under the requested output directory. It does not mutate the source journal, except for creating and deleting a temporary local Rocks database during conversion.

## Dependencies and integration points
It depends on checkpoint formats, `RocksInodeStore`, `CloseableIterator`, path/file utilities, and Java I/O. `UfsJournalDumper` and `RaftJournalDumper` subclass it.

## Risks
Large Rocks checkpoints can be expensive to restore and dump. Output files are overwritten if paths collide. Cleanup failure could leave temporary `*-rocks-db` directories. Recursive compound checkpoint handling must preserve names to avoid overwriting nested outputs.

## Test signals
Tests should cover regular checkpoint parsing, compound recursion, Rocks checkpoint restore/dump/cleanup, output directory creation, malformed checkpoint errors, and path collision scenarios.
