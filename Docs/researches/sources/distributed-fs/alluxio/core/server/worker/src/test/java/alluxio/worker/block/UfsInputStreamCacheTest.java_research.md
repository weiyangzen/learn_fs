## sources/distributed-fs/alluxio/core/server/worker/src/test/java/alluxio/worker/block/UfsInputStreamCacheTest.java

**Purpose:** Tests `UfsInputStreamCache`, which reuses seekable UFS input streams and closes non-reusable or expired streams.

**Important APIs:** Exercises `acquire`, `release`, UFS `isSeekable`, `openExistingFile`, `SeekableUnderFileInputStream.seek`, cache expiration property, and concurrent checkout/checkin behavior.

**Control flow:** Setup creates a mocked UFS that is seekable and returns a sequence of mocked seekable streams. Tests cover non-seekable streams closing on release, same-file reuse with seek to requested offset, multiple simultaneous checkouts opening multiple streams, expiration-triggered close, release after expiration for same/different file, and concurrent repeated acquire/release loops.

**State and persistence:** State is in-memory cache entries keyed by file identity/path and stream checkout status. No real files are read.

**Dependencies and integration:** Uses `ConfigurationRule` for expiration time, Mockito invocation introspection, `ConcurrencyUtils`, and UFS open options. This cache is consumed by under-file-system block readers.

**Risks:** Stream reuse is concurrency-sensitive. Incorrect expiration or release handling can leak file descriptors, close in-use streams, or seek a stream for the wrong file.

**Test signals:** Covers reuse, non-reuse, expiration cleanup, release-after-expire races, and concurrent seek counts under no-expiration and expiration settings.
