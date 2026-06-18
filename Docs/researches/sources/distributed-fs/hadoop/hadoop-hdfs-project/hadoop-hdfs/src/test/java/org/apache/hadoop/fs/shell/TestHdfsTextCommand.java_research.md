# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/shell/TestHdfsTextCommand.java

## Purpose

`TestHdfsTextCommand` validates the HDFS shell `-text` display path for Avro container files. It writes a small binary Avro weather-record file into a `MiniDFSCluster`, invokes the protected `Display.Text.getInputStream(PathData)` method, and asserts that the decoded text stream exactly matches the expected JSON-record lines.

## Important APIs, types, and functions

The test uses `MiniDFSCluster`, `FileSystem`, `FSDataOutputStream`, `PathData`, `Display.Text`, Java reflection `Method`, `InputStream`, `StringWriter`, and Commons IO copy helpers. Local helpers are `createAvroFile`, `inputStreamToString`, and `generateWeatherAvroBinaryData`, the latter embedding a complete Avro binary object container payload.

## Control flow, state, and persistence

Each test starts a fresh cluster in `setUp`, creates `/test/data/testText/weather.avro`, and shuts the cluster down in `tearDown`. `testDisplayForAvroFiles` writes the byte array, constructs `PathData` from the HDFS path and configuration, makes `getInputStream` accessible by reflection, reads the decoded stream as UTF-8, and compares all five output rows including platform line separators. State is transient HDFS file content only.

## Dependencies and integration points

The test touches the FsShell display implementation, Avro input detection/decoding in `Display.Text`, HDFS stream opening through `PathData`, and UTF-8 conversion. It depends on the Avro codec/schema embedded in the byte array and on shell output formatting remaining stable.

## Risks and test signals

Risks are brittle reflection against a protected method, embedded binary fixture opacity, platform line-separator sensitivity, and exact-output coupling to Avro JSON rendering. A passing test signals that HDFS `-text` can detect Avro data and produce record-oriented text rather than raw binary.
