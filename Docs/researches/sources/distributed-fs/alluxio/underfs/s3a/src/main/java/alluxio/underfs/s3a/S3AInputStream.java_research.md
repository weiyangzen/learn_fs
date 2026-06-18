# sources/distributed-fs/alluxio/underfs/s3a/src/main/java/alluxio/underfs/s3a/S3AInputStream.java

## Purpose
`S3AInputStream` wraps AWS SDK S3 object streams and implements efficient skip by reopening the object at a byte range.

## Important APIs, Types, And Functions
Constructors accept bucket, key, `AmazonS3` client, optional position, and retry policy. Public methods are `read`, `read(byte[])`, `read(byte[], int, int)`, `skip`, and `close`. Internals include `openStream`, `closeStream`, and `getClient`.

## Control Flow
Reads lazily open the S3 object at `mPos`; non-empty reads advance `mPos`. `skip` closes the current stream, increments `mPos`, and opens a new ranged request. `openStream` omits range when position is zero to avoid zero-length object issues.

## State And Persistence
State includes client, bucket, key, active `S3ObjectInputStream`, current position, and retry policy. No local persistence is used.

## Dependencies And Integration Points
It depends on AWS SDK v1 `AmazonS3` and `GetObjectRequest`. `S3AUnderFileSystem.openObject` constructs it.

## Risks
The retry loop immediately throws on the first `AmazonS3Exception`, so the retry policy is not actually used for those exceptions. `skip` always returns requested bytes even if beyond EOF.

## Test Signals
Behavior is indirectly covered through S3Proxy read tests and generic object open flows; this subset has no dedicated `S3AInputStreamTest`.
