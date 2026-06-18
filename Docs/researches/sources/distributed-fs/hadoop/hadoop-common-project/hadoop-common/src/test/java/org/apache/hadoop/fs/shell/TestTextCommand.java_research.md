# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/shell/TestTextCommand.java

Purpose: Tests `Display.Text`, the FS shell `-text` implementation, for supported binary/text formats: Avro object container files, Hadoop SequenceFiles with Java-serialized non-Writable keys/values, and plain text files. It also verifies the custom input streams obey `InputStream.read(byte[], int, int)` contracts and EOF consistency.

Important APIs/types/functions: `Display.Text.getInputStream(PathData)`, `PathData(URI, Configuration)`, `SequenceFile.createWriter`, `IOUtils.copy`, `IO_FILE_BUFFER_SIZE_KEY`, helpers `readUsingTextCommand`, `inputStreamToString`, `inputStreamSingleByteReadsToString`, `generateWeatherAvroBinaryData`, `generateEmptyAvroBinaryData`, `createEmptySequenceFile`, `createNonWritableSequenceFile`, and `getInputStream`.

Control flow: Tests create local files under `GenericTestUtils.getTestDir("testText")`, then read them through an anonymous `Display.Text` subclass exposing the protected `getInputStream`. Avro tests compare decoded JSON lines for a fixture with five weather records, exercise tiny multi-byte reads by setting buffer size to `2`, validate empty Avro output, enforce null/negative/too-long buffer failures, check zero-length reads return `0`, verify repeat EOF returns `-1`, and compare single-byte to multi-byte reads. Text tests check empty, one-byte, and two-byte pass-through. SequenceFile tests mirror the Avro stream contract and compare tab/newline formatted output for two string records.

State/persistence: Writes local files in the test directory and overwrites/reuses fixed filenames. SequenceFile tests mutate `Configuration` serialization setting to Java serialization. Streams are closed by try-with-resources or utility copy paths.

Dependencies/integration: Integrates shell display code with local FS, Avro decoding embedded in `Display.Text`, Hadoop SequenceFile reading, Java serialization configuration, commons-io copy logic, and Java `InputStream` semantics.

Risks: Large embedded binary byte arrays are opaque and hard to modify. Fixed filenames under a shared test root can collide if tests run concurrently without isolation. Expected JSON line separators use the platform line separator for Avro but hard-coded `\n` for SequenceFile, reflecting actual command behavior. The tests validate behavior but not cleanup of created files.

Test signals: Exact decoded Avro/SequenceFile/plain-text output, exception classes for invalid reads, zero-length read return values, EOF idempotence, and equality of single-byte and bulk-read streams under small buffer settings.
