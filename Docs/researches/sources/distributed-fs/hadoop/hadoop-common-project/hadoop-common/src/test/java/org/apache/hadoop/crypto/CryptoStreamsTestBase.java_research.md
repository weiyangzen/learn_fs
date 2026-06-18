# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/crypto/CryptoStreamsTestBase.java

## Purpose

`CryptoStreamsTestBase` is an abstract compliance suite for Hadoop crypto input/output streams. Concrete subclasses provide encrypted output and input streams; the base verifies that encryption/decryption preserves generated data across sequential reads, writes, IV offsets, sync operations, positioned reads, ByteBuffer reads, seek/skip/position behavior, enhanced ByteBuffer access, and unbuffering.

## Important APIs and types

- Abstract factories: `getOutputStream(int, byte[], byte[])` and `getInputStream(int, byte[], byte[])`.
- Shared crypto state: static `CryptoCodec codec`, fixed 16-byte key/IV, record count, and buffer sizes.
- Data generation: `RandomDatum.Generator` writes deterministic key/value pairs into `DataOutputBuffer`.
- Stream contracts under test: `Syncable`, `Seekable`, `PositionedReadable`, `ByteBufferReadable`, `ByteBufferPositionedReadable`, `HasEnhancedByteBufferAccess`, and `CanUnbuffer`.
- Helper methods: `readAll`, `preadAll`, `byteBufferPreadAll`, `readCheck`, `positionedReadCheck`, `readFullyCheck`, `seekCheck`, `byteBufferReadCheck`, `byteBufferPreadCheck`, and `verify`.

## Control flow

`setUp` regenerates a random dataset for every test. `testRead` writes all data then reads it back with default and small buffers. `testWrite` writes with both buffer sizes and checks `FSDataOutputStream` position when applicable. `testCryptoIV` rewrites the counter portion of IVs with boundary values and verifies round trips.

`testSyncable` writes one third of the data, calls `hflush`, reads the visible prefix, writes the rest, calls `hsync`, and verifies full data. Positioned-read tests verify byte-array and ByteBuffer reads from fractional offsets without disturbing normal stream state. Read-fully tests verify exact data and EOF failures. Seek, get-position, available, and skip tests validate stateful stream positioning and error messages for invalid offsets. ByteBuffer tests cover heap/direct buffers and nonzero positions. `testCombinedOp` mixes sequential reads, seeks, skips, positioned reads, and ByteBuffer reads to validate position accounting. Enhanced ByteBuffer access uses a direct `ByteBufferPool`. `testUnbuffer` verifies buffered reads, positioned reads, and ByteBuffer positioned reads still work after unbuffering.

## State and persistence behavior

The base stores generated plaintext data in instance fields. Concrete subclasses decide where encrypted bytes are stored. Stream state under test includes crypto buffer positions, cipher counter alignment, underlying stream position, flushed visibility, and unbuffered buffer lifecycle. No files are written by the base itself.

## Dependencies and integration points

The class integrates crypto streams with Hadoop filesystem stream interfaces, random writable test data, direct buffer pools, `ReadOption.SKIP_CHECKSUMS`, `FSExceptionMessages`, AssertJ, JUnit timeouts, and `GenericTestUtils` exception checks. It is intended to be reused by multiple crypto stream implementations.

## Risks and edge cases

- Random seeds vary each run, increasing coverage but making failures less directly reproducible unless logs capture enough context.
- Tests assume 16-byte key/IV and counter semantics suitable for AES/CTR-like codecs.
- Positioned read helpers use accumulated total as the next position for some paths, so they mainly validate full sequential pread from zero rather than arbitrary sparse ranges.
- Enhanced ByteBuffer access requires correct buffer ownership/release behavior; the dummy pool does not validate returned buffers.
- Timeout values protect against hangs but may hide performance regressions until they cross a large threshold.

## Test signals

The base provides broad behavioral signals for crypto stream correctness: plaintext round trip, EOF handling, flush/sync visibility, IV counter boundaries, positioned-read consistency, direct/heap ByteBuffer correctness, seek/skip error handling, position accounting, enhanced buffer access, and unbuffer idempotence.
