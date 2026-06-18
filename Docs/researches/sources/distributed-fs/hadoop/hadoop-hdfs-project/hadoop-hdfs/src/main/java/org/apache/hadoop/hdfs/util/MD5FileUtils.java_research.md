<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/util/MD5FileUtils.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/util/MD5FileUtils.java

## Purpose
`MD5FileUtils` provides static helpers for md5sum-compatible sidecar files named `<data>.md5`, including compute, save, read, verify, and rename operations.

## APIs and Types
Public APIs are `verifySavedMD5`, `readStoredMd5ForFile`, `computeMd5ForFile`, `saveMD5File(File, MD5Hash)`, `renameMD5File`, and `getDigestFileForFile`. It uses `LINE_REGEX` to parse 32 lowercase hex digits plus filename.

## Control Flow
Reading opens the md5 file as UTF-8, reads and trims the first line, validates the regex, checks the referenced filename basename against the expected data file, and returns `MD5Hash`. Computing streams the data file through `DigestInputStream` into `IOUtils.NullOutputStream`. Saving writes `"<hex> *<name>\n"` through `AtomicFileOutputStream`. Renaming reads the old digest, writes a new sidecar for the new filename, then deletes the old sidecar.

## State and Persistence
The class is stateless. Persistence is the `.md5` sidecar, written atomically through `AtomicFileOutputStream`.

## Dependencies and Integration
It depends on Java security digest APIs, Hadoop `MD5Hash`, `IOUtils`, `StringUtils`, and `AtomicFileOutputStream`. It supports fsimage/editlog checksum workflows and other HDFS file sidecars.

## Risks
Only lowercase md5 hex matches. `verifySavedMD5` reports its `expectedMD5` as "computed" but does not compute internally. If no sidecar exists, `readStoredMd5ForFile` returns null and verify will fail by inequality. `renameMD5File` can leave both sidecars if old delete fails. The filename check ignores directories by comparing basename only.

## Test Signals
Tests should cover md5 computation, save/read round trip, missing sidecar, invalid format, uppercase hash rejection, wrong referenced filename, verify mismatch, atomic save content, and rename side effects when deletion fails.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/util/MD5FileUtils.java -->
