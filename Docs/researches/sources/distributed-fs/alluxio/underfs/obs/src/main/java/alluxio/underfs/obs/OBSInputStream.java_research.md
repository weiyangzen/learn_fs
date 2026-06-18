## sources/distributed-fs/alluxio/underfs/obs/src/main/java/alluxio/underfs/obs/OBSInputStream.java

### Purpose
`OBSInputStream` implements ranged reads from Huawei OBS using Alluxio's `MultiRangeObjectInputStream`.

### Important APIs, Types, And Functions
Constructors record bucket/key/client/retry policy/chunk size and fetch object content length from OBS metadata. `createStream(long, long)` builds a `GetObjectRequest` with range start/end and returns a buffered object-content stream.

### Control Flow
Each range request copies the retry policy, attempts `mObsClient.getObject`, retries only 404 not-found responses, and converts non-404 `ObsException` to `IOException`. Range end is clamped to content length minus one.

### State, Persistence, And Dependencies
State includes bucket, key, OBS client, content length, retry policy, and inherited position. It depends on Huawei OBS SDK, HTTP status codes, and Alluxio multi-range stream logic.

### Integration Points
`OBSUnderFileSystem.openObject` creates this stream with the configured multi-range chunk size.

### Risks
The constructor metadata call can fail before read retries begin. A `System.out.println` of response code leaks logging to stdout. If content length is zero, computed range end can become `-1`, relying on caller behavior for empty objects.

### Test Signals
No direct tests are present. Useful tests would cover metadata failures, range clamping, 404 retry, non-404 propagation, empty objects, and stream close behavior.
