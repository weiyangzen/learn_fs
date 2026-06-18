<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/compress/bzip2/BZip2TextFileWriter.java -->
## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/compress/bzip2/BZip2TextFileWriter.java

Purpose: Test utility for generating BZip2-compressed text data with predictable block boundaries.

Important APIs/types/functions: public constant `BLOCK_SIZE` derives from `CBZip2OutputStream.getAllowableBlockSize(MIN_BLOCKSIZE) + 1`. Constructors accept a Hadoop `Path`/`Configuration` or raw `OutputStream`. Public methods are `writeManyRecords`, `writeRecord`, `write(String)`, `write(byte[])`, and `close`.

Control flow: the raw-output constructor writes the Hadoop BZip2 header via `BZip2Codec.writeHeader`, then wraps the stream in `CBZip2OutputStream` with minimum block size. If construction fails, it closes the raw stream and rethrows. `writeManyRecords` validates record count and delimiter, divides total size evenly, and writes all records with any remainder in the last record. `writeRecord` writes alternating `'a'` and `'b'` bytes until delimiter space remains, then writes the delimiter. Alternation prevents run-length encoding from collapsing the intended block-boundary size.

State and persistence behavior: owns a single `CBZip2OutputStream` and writes compressed data to caller-provided file/stream. No static mutable state beyond constants.

Dependencies and integration points: used by `TestBZip2Codec` and `TestBZip2TextFileWriter`. Integrates with Hadoop `Path`/`FileSystem`, `BZip2Codec`, and low-level `CBZip2OutputStream`.

Risks and edge cases: the block-size logic depends on CBZip2 internals and comments document that the extra byte is required by allowable-block offset checks. It closes only the compressed wrapper in `close`, which should close the underlying stream through wrapper semantics.

Test signals: enables precise tests around BZip2 block marker offsets and split stream behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/compress/bzip2/BZip2TextFileWriter.java -->
