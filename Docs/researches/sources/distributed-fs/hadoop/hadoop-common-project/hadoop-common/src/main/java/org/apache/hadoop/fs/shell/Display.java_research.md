# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/shell/Display.java

Purpose: implements display commands `cat`, `text`, and `checksum`, plus stream adapters for SequenceFile and Avro-to-text rendering.

Important APIs and types: nested `Cat`, `Text`, `Checksum`, `TextRecordInputStream`, `AvroFileInputStream`, and `validateInputStreamReadArguments()`. `Cat` handles checksum verification and stdout copy; `Text` detects gzip, SequenceFile, codec-compressed streams, and Avro data files; `Checksum` prints algorithm/hash and optionally block size.

Control flow: `Cat.processPath()` rejects directories, configures checksum verification, opens sequential input via `PathData.openForSequentialIO()`, and copies to `out`. `Text.getInputStream()` reads lead bytes, seeks back as needed, and wraps the stream with gzip/codec readers or container readers. `TextRecordInputStream` converts SequenceFile key/value records into tab-separated text lines. `AvroFileInputStream` serializes Avro records through a JSON encoder into a byte buffer consumed by `read()`.

State and persistence: no filesystem mutation occurs. Stream classes keep reader state, buffers, and current positions until close.

Dependencies and integration: uses Hadoop compression codecs, `SequenceFile.Reader`, Avro `DataFileReader`, `AvroFSInput`, `FileContext`, `FileChecksum`, and `PathData`.

Risks: `Text.getInputStream()` must close or rewind correctly after probing lead bytes; SequenceFile and Avro detection is magic-byte based. `AvroFileInputStream` creates a new default `Configuration` for `FileContext`, not the command's configuration. Large records are buffered fully in memory for each record. `read(byte[],...)` validation intentionally mirrors `InputStream` contract but throws unchecked exceptions for null/range issues.

Test signals: cover directory rejection, `-ignoreCrc`, gzip and codec detection, short/empty files, SequenceFile text conversion, Avro JSON conversion including empty and final newline behavior, checksum null and verbose output, and buffer read argument validation.
