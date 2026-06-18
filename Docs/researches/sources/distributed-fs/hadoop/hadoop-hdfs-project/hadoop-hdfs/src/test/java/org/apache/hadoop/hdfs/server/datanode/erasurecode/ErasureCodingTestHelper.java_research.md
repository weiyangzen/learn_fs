# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/erasurecode/ErasureCodingTestHelper.java

Purpose: This tiny helper exposes the erasure-coding DataNode reconstructor buffer pool to tests.

Important APIs/types/functions: `ErasureCodingTestHelper.getBufferPool`, `StripedReconstructor.getBufferPool`, and `ByteBufferPool`.

Control flow: The class is `final` with a private constructor and one static method that delegates directly to `StripedReconstructor.getBufferPool()`.

State and persistence behavior: No state is owned here. The returned pool is whatever static/shared buffer pool the reconstructor uses, so consumers may observe shared allocation/reuse behavior outside this helper.

Dependencies and integration points: It gives tests in or near the erasure-coding package access to internal reconstruction buffer-pool state without widening production APIs.

Risks and test signals: There are no local assertions. Risk is that this helper couples tests to `StripedReconstructor` internals; if buffer-pool ownership changes, tests using the helper may need updates.
