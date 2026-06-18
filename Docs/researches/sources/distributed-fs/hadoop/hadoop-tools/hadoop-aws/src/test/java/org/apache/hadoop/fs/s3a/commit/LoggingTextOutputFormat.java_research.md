# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/commit/LoggingTextOutputFormat.java

## Purpose
Test output format used by committer integration tests to expose and log the actual work-file destination while behaving like Hadoop `TextOutputFormat`.

## Important APIs, Types, and Functions
`LoggingTextOutputFormat<K,V>` extends `TextOutputFormat<K,V>`. `getRecordWriter()` reproduces the standard text output writer path, including compression support, but returns `LoggingLineRecordWriter`. The nested writer extends `LineRecordWriter<K,V>`, tracks `dest` and `lines`, overrides `write()`, exposes `getDest()` and `getLines()`, and logs close details. Static `bind(Configuration)` sets `MRJobConfig.OUTPUT_FORMAT_CLASS_ATTR`.

## Control Flow and Behavior
On writer creation the format resolves compression options, computes `getDefaultWorkFile()`, opens the target filesystem output stream, and wraps it in an optional codec stream. Each `write()` delegates to `LineRecordWriter` then increments a line counter. `close()` logs the target and count before closing the stream.

## State, Persistence, and Dependencies
Persistent state is the generated task output file, possibly compressed. In-memory state is limited to the destination path and line count. Dependencies include MR output-format APIs, `CompressionCodec`/`GzipCodec`, `ReflectionUtils`, `FileSystem`, and standard Hadoop text output constants such as `SEPARATOR`.

## Integration Points, Risks, and Test Signals
This helper is used by MR committer integration tests to validate task output paths and success marker file lists. It intentionally mirrors standard `TextOutputFormat`; risks are drift from upstream output behavior, compression edge cases, and `close()` bypassing superclass behavior by directly closing `out`.
