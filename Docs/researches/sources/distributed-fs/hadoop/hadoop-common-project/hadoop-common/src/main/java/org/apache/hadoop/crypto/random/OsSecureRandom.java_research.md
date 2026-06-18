# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/crypto/random/OsSecureRandom.java

## Purpose
`OsSecureRandom` is a configurable `Random` implementation that reads random bytes directly from an operating-system device file such as `/dev/urandom`. It buffers data in an internal reservoir for efficient repeated calls.

## Important APIs and types
The class extends `Random` and implements `Closeable` and `Configurable`. Important methods are `setConf()`, `getConf()`, `nextBytes()`, protected `next(int)`, `close()`, visible-for-testing `isClosed()`, and private `fillReservoir(int)`.

## Control flow
`setConf()` records configuration, reads the random device path from `HADOOP_SECURITY_SECURE_RANDOM_DEVICE_FILE_PATH_KEY` with default fallback, and closes any open stream so the next read uses the new path. `nextBytes()` loops until the output is filled, calling `fillReservoir(0)` and copying from the reservoir. `next(int)` ensures at least four bytes are available, consumes four bytes, and masks to the requested bit count. `fillReservoir()` opens the device lazily and reads a full reservoir when the current position is too close to the end for the requested minimum.

## State and persistence
State is configuration, device path, open input stream, fixed 8192-byte reservoir, and current reservoir position. No random data is persisted. `close()` releases the stream and `finalize()` calls `close()`.

## Dependencies and integration points
It depends on Hadoop configuration keys, `IOUtils`, Java NIO `Files`, and `Random`. It can be selected via `hadoop.security.secure.random.impl`.

## Risks
Device-file reads can block or fail depending on platform/path. `fillReservoir()` converts I/O failures to runtime exceptions, so callers of `Random` APIs do not see checked exceptions. `next(int)` does not validate `nbits`; it assumes `Random` caller conventions. Finalization-based cleanup is best-effort only.

## Test signals
Tests should use a temporary deterministic byte file to validate reservoir refill, `nextBytes()` spanning reservoir boundaries, `next(int)` masking, `setConf()` path switching and stream close, `isClosed()`, and error behavior for missing device paths.
