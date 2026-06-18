<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/TestSequenceFileSync.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/TestSequenceFileSync.java

## Purpose
Tests sequence-file sync marker intervals and `Reader.sync(offset)` behavior for default and low sync intervals.

## Important APIs, Types, and Functions
Uses `SequenceFile.Writer` options `file`, `compression(NONE)`, `keyClass`, `valueClass`, and `syncInterval`; `SequenceFile.Reader` file and stream constructors; `Reader.sync`; `Reader.next`; `FSDataInputStream`; `IntWritable`; and `Text`.

## Control Flow and State
`writeSequenceFile()` writes numbered records with deterministic prefix text and random digit padding. `forOffset()` calls `sync(off)`, reads the next key/value, and asserts expected record id and prefix. `testDefaultSyncInterval()` writes 8000 records and verifies offsets 0, 65, 2000, and 0 across both reader construction styles, expecting offset 2000 to jump to record 1101 under default sync. `testLowSyncpoint()` sets sync interval 2000 bytes, writes 2000 records, and expects offset 2000 to jump to record 21.

## Dependencies and Integration Points
Integrates sequence-file sync marker generation, reader seek/sync semantics, local filesystem file and stream access, and record layout sizing.

## Risks and Test Signals
Risks include sensitivity to record size changes, default sync interval changes, random payload not affecting prefix, and resource cleanup through manual delete. Signals are exact expected record ids for offsets and writer `syncInterval` field equality.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/TestSequenceFileSync.java -->
