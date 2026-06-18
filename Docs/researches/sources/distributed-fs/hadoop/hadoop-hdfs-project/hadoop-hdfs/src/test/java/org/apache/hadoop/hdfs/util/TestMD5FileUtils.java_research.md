# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/util/TestMD5FileUtils.java

Purpose: tests file digest computation and sidecar `.md5` verification utilities.

Important APIs/types/functions: `MD5FileUtils.computeMd5ForFile`, `saveMD5File`, `verifySavedMD5`, `getDigestFileForFile`, `MD5Hash.digest`, `DFSTestUtil.generateSequentialBytes`.

Control flow: `setup` deletes and recreates a class-specific test directory, writes a 128 KiB deterministic byte sequence to `testMd5File.dat`, and stores the expected MD5. Tests verify computed digest equality, successful save-and-verify, failure when the digest file is missing, failure when the digest file contains the wrong digest, and failure when the digest sidecar has invalid text format.

State and persistence behavior: persists a temporary data file and `.md5` sidecar under `PathUtils.getTestDir`. Each test gets clean disk state from `FileUtil.fullyDelete`.

Dependencies and integration points: validates HDFS utility behavior used by image/edit-log/checkpoint style file integrity workflows; relies on Hadoop `MD5Hash` and local filesystem I/O.

Risks: bad-digest and bad-format tests catch broad `IOException` without asserting message/type, so they verify failure but not precise diagnostics. File streams are manually closed rather than try-with-resources.

Test signals: positive digest round trip and three negative verification cases: missing, mismatched digest, malformed sidecar.
