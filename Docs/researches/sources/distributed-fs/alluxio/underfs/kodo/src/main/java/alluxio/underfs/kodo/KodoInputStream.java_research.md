## sources/distributed-fs/alluxio/underfs/kodo/src/main/java/alluxio/underfs/kodo/KodoInputStream.java

### Purpose
`KodoInputStream` implements ranged object reads for Kodo through `MultiRangeObjectInputStream`.

### Important APIs, Types, And Functions
The constructor records key/client/position/retry policy, initializes multi-range chunk size, and fetches object size through `KodoClient.getFileInfo`. `createStream(long, long)` opens the requested byte range.

### Control Flow
For each range, the stream copies the retry policy and repeatedly calls `KodoClient.getObject`. `NotFoundException` is retried to handle eventual consistency. After retry exhaustion, it throws an `IOException` with the last not-found error.

### State, Persistence, And Dependencies
State includes key, Kodo client, current position inherited from the superclass, object length, and retry policy. It depends on Qiniu metadata exceptions and Alluxio multi-range stream support.

### Integration Points
`KodoUnderFileSystem.openObject` creates this stream with the configured object-store multi-range chunk size.

### Risks
Only not-found errors are retried by this class; other IO failures from `getObject` propagate. Constructor metadata lookup can fail before stream creation. The member name `mKodoclent` is misspelled but local.

### Test Signals
No direct tests are present. Useful tests would cover range boundaries, not-found retry, metadata failure, empty-object reads, and multi-range chunk behavior.
