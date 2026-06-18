# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/TestLocalFsFCStatistics.java

Purpose: specializes `FCStatisticsBaseTest` for local `FileContext` statistics and expected checksum sidecar byte accounting.

Important APIs/types/functions: `FileContext.getLocalFSFileContext`, `FileSystem.Statistics`, inherited `blockSize`, and `getFsUri`.

Control flow/state/persistence: setup creates a local test root through `FileContext`; teardown deletes it. Overrides assert that reads count two block-size reads for read and positional-read, while writes count `blockSize + 12` to include CRC bytes. The URI under test is `file:///tmp/test`.

Dependencies/integration points: depends on local `FileContext`, file-scheme statistics sharing, and checksum sidecar size assumptions.

Risks/test signals: catches statistics regressions where FileContext local reads/writes stop including checksum IO or count a different number of bytes.
