## sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/test/java/org/apache/hadoop/hdfs/web/TestOffsetUrlInputStream.java

Purpose: this small test verifies `WebHdfsFileSystem.removeOffsetParam(URL)`, which removes byte-range offset parameters when building follow-up/resolved URLs.

Important APIs and types: it uses `URL`, `WebHdfsFileSystem.removeOffsetParam()`, and JUnit equality assertions.

Control flow: the test feeds URLs with no query, queries without offset, offset as first/middle/last parameter, mixed-case `OFFset`, and offset as the only parameter. It asserts the resulting URL string preserves all non-offset parameters and removes dangling separators.

State and persistence: no persistent state. The only state is URL parsing and string reconstruction.

Dependencies and integration points: supports WebHDFS/byte-range stream behavior by ensuring an existing offset parameter does not conflict with a newly requested range offset.

Risks: assertions compare exact URL strings, so parameter ordering and encoding behavior are part of the contract.

Test signals: confirms case-insensitive offset removal and correct query cleanup for first, middle, last, and only parameter positions.
