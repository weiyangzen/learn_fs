<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/file/tfile/TFile.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/file/tfile/TFile.java

## Purpose
`TFile` is Hadoop's byte-oriented sorted or unsorted key/value container built on `BCFile`. It exposes public `Writer` and `Reader` APIs for appending records, writing named metadata blocks, scanning by full file, byte range, key range, or record number, and retrieving TFile metadata/index structures. Keys are raw bytes limited to 64 KiB; values are raw bytes with chunked encoding so large values do not need full buffering.

## Important APIs and Types
Top-level constants define supported compression names (`gz`, `lzo`, `none`), comparator names (`memcmp`, `jclass:`), `API_VERSION`, and configuration keys for chunk and filesystem buffering. `Writer` owns `prepareAppendKey`, `prepareAppendValue`, `append`, `prepareMetaBlock`, and `close`. `Reader` owns metadata access, comparator access, `getFirstKey`, `getLastKey`, `getKeyNear`, record-number mapping, and scanner creation. `Reader.Scanner` owns cursor movement (`advance`, `rewind`, `seekToEnd`, `lowerBound`, `upperBound`) and `Scanner.Entry` owns key/value extraction and comparison. Internal persisted metadata is modeled by `TFileMeta`, `TFileIndex`, and `TFileIndexEntry`.

## Control Flow
Writing is a strict state machine: `READY -> IN_KEY -> END_KEY -> IN_VALUE -> READY`, with `CLOSED` terminal. A key stream close writes a varint key length and key bytes, checks sorted order when a comparator is configured, and records first/last keys. A value stream close finalizes chunk encoding, increments per-block and whole-file record counts, and may close the current BCFile data block once compressed size reaches the configured minimum. `close` forces the last data block closed, writes `TFile.meta`, writes `TFile.index`, then closes/cleans BCFile resources.

Reading constructs a `BCFile.Reader`, loads `TFile.meta`, and lazily loads `TFile.index` on first indexed operation. Scanners convert byte/key/record ranges into `Location(blockIndex, recordIndex)` bounds. Cursor movement opens data blocks on demand, parses each key length/key/value chunk decoder, and consumes value streams before skipping to the next record. Sorted-key seeks binary-search the block index, then scan within the candidate block.

## State and Persistence
Persistent state lives in BCFile data blocks plus two TFile metadata blocks. `TFile.meta` stores version, total record count, and comparator name. `TFile.index` stores the first key, then one `TFileIndexEntry` per data block containing that block's last key and record count. In-memory reader state includes the lazy index, reusable key/value buffers, current block reader, and scanner bounds. `Scanner.Entry` values are single-use because the value stream is not cached.

## Dependencies and Integration Points
The class integrates with `BCFile`, `Chunk`, `CompareUtils`, Hadoop `FSDataInputStream`/`FSDataOutputStream`, Hadoop raw comparators, `BytesWritable`, `DataInputBuffer`, `DataOutputBuffer`, and Java serialization comparators by class name. Configuration keys control chunk buffer size and TFile-layer I/O buffering. The `main` method delegates to `TFileDumper`.

## Risks and Edge Cases
Writer errors increment `errorCount`; after an append failure the writer is intentionally inconsistent and close only cleans resources. Sorted files rely on comparator correctness and default constructor availability for `jclass:` comparators. Scanners throw if values are examined multiple times. Key lengths from corrupt files can exceed the fixed 64 KiB scanner buffer. Multi-threaded reading shares seek/read behavior in the underlying stream and is not designed for true parallel scanner I/O. Version compatibility only checks major version.

## Test Signals
Useful tests should cover append state errors, sorted-order enforcement, fixed and unknown value lengths, metadata block writing after data blocks, scanner ranges by byte/key/record, lower/upper-bound duplicate-key behavior, lazy index loading, corrupt/truncated varint/key/value handling, and comparator instantiation failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/file/tfile/TFile.java -->
