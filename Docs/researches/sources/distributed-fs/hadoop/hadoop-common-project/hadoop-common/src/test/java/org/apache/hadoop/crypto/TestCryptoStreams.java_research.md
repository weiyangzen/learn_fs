# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/crypto/TestCryptoStreams.java

## Purpose

`TestCryptoStreams` is the concrete in-memory implementation of `CryptoStreamsTestBase` for Hadoop `CryptoInputStream` and `CryptoOutputStream`. It supplies fake underlying streams implementing Hadoop filesystem stream interfaces and adds capability-advertising tests.

## Important APIs and types

- `getOutputStream` wraps a `DataOutputBuffer` in `FakeOutputStream`, then in `CryptoOutputStream`.
- `getInputStream` wraps stored encrypted bytes in `DataInputBuffer`, then `FakeInputStream`, then `CryptoInputStream`.
- `FakeOutputStream` implements `OutputStream`, `Syncable`, `CanSetDropBehind`, and `StreamCapabilities`.
- `FakeInputStream` implements `InputStream`, `Seekable`, `PositionedReadable`, `ByteBufferReadable`, `ByteBufferPositionedReadable`, `HasFileDescriptor`, `CanSetDropBehind`, `CanSetReadahead`, `HasEnhancedByteBufferAccess`, `CanUnbuffer`, and `StreamCapabilities`.
- `testHasCapability` uses `ContractTestUtils.assertCapabilities`.

## Control flow

`init` creates the default `CryptoCodec`. Output creation uses an anonymous `DataOutputBuffer` whose `flush` and `close` snapshot the backing encrypted byte array and length. `FakeOutputStream` validates write arguments, rejects writes after close, forwards bytes to the buffer, implements `hflush`/`hsync` as flushes, and advertises `hflush`, `hsync`, and `dropbehind`.

`FakeInputStream` stores a byte array and cursor. It implements sequential reads, ByteBuffer reads, `available`, `skip`, `seek`, `seekToNewSource`, positioned byte-array and ByteBuffer reads, `readFully` variants with EOF checks, enhanced ByteBuffer reads via a supplied pool, no-op release/readahead/dropbehind/unbuffer, and capability advertising for readahead/dropbehind/unbuffer/ByteBuffer read/pread. Boundary checks reject negative positions and reads/seeks beyond EOF.

Inherited tests from `CryptoStreamsTestBase` run against these fake streams. `testHasCapability` specifically verifies that crypto wrappers delegate or expose the expected stream capabilities from the underlying fake streams.

## State and persistence behavior

The concrete test stores encrypted output in instance fields `buf` and `bufLen`. Fake streams maintain in-memory cursor and closed flags. No filesystem persistence occurs.

## Dependencies and integration points

This file integrates crypto streams with many Hadoop stream capability interfaces. The fake streams are also reused by `TestCryptoCodec` for seeked decryption. Capability behavior connects to Hadoop filesystem contract testing.

## Risks and edge cases

- Fake streams model Hadoop stream interfaces but are not full filesystem streams; real filesystem buffering, checksums, descriptors, and resource ownership may differ.
- `FakeInputStream.getFileDescriptor` returns null while advertising `HasFileDescriptor`; consumers must tolerate that in tests.
- Enhanced ByteBuffer read obtains direct buffers but `releaseBuffer` is a no-op, so pool lifecycle bugs are not caught.
- `hasCapability` lowercases input without a null guard; null capability behavior is not covered.
- `FakeOutputStream.close` snapshots data and marks closed but does not check close errors from an external resource.

## Test signals

The inherited suite verifies data correctness, positioning, ByteBuffer operations, sync, unbuffer, and IV behavior. This class adds concrete capability checks for crypto wrappers, ensuring expected capability pass-through for input and output streams.
