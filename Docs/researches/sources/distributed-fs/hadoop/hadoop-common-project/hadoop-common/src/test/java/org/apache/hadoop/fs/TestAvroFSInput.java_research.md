# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/TestAvroFSInput.java

## Purpose
`TestAvroFSInput` validates Hadoop's `AvroFSInput` adapter over a local file. It checks length reporting, initial position, sequential read position advancement, seeking, and close behavior.

## Important APIs, Types, And Functions
The test uses `FileSystem.getLocal(Configuration)`, `FileContext.getFileContext(Configuration)`, `AvroFSInput`, `FSDataOutputStream`, `BufferedWriter`, and `Path`. `getInputPath()` returns a temp path under `GenericTestUtils.getTempPath("AvroFSInput")`.

## Control Flow
The test ensures the input directory exists, deletes any old `foo`, writes `0123456789`, then constructs `AvroFSInput(fc, filePath)`. It asserts length `10`, `tell() == 0`, reads one byte and checks `tell() == 1` plus byte `'0'`, seeks to offset `4`, reads one byte, and verifies byte `'4'` and final position `5`.

## State And Persistence Behavior
The test writes one local filesystem file under a temp directory. It deletes only the target file before writing and closes both writer and Avro input. The directory may persist across runs.

## Dependencies And Integration Points
This test connects the local `FileSystem` writer path to the `FileContext`-based `AvroFSInput` reader. It verifies the adapter contract expected by Avro-style seekable input consumers.

## Risks
Coverage is minimal: it does not validate EOF, bulk reads, negative or out-of-range seeks, repeated close, or non-local filesystems. The writer uses platform default encoding through `OutputStreamWriter`, though the content is ASCII-only.

## Test Signals
Passing confirms that `AvroFSInput` reports file length and stream position correctly and delegates seek/read operations to Hadoop filesystem streams.
