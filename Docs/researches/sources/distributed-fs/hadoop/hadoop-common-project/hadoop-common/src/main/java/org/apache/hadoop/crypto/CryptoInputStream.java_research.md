# `sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/crypto/CryptoInputStream.java`

## Purpose

`CryptoInputStream` wraps an input stream and decrypts CTR-mode ciphertext into plaintext while preserving a one-to-one byte mapping between encrypted and clear data. It supports sequential reads, seeks, positioned reads, byte-buffer reads, enhanced byte-buffer access, unbuffering, stream capabilities, and IO statistics delegation.

## Important APIs and Types

The class extends `FilterInputStream` and implements `Seekable`, `PositionedReadable`, `ByteBufferReadable`, `HasFileDescriptor`, `CanSetDropBehind`, `CanSetReadahead`, `HasEnhancedByteBufferAccess`, `ReadableByteChannel`, `CanUnbuffer`, `StreamCapabilities`, `ByteBufferPositionedReadable`, and `IOStatisticsSource`. It owns a `CryptoCodec`, main `Decryptor`, direct `inBuffer` and `outBuffer`, stream offset, padding, cloned key and IV material, and pools for direct buffers and decryptors used by positioned reads.

## Control Flow

Construction validates that the codec is AES/CTR or SM4/CTR, floors buffer size to a block multiple, clones key/IV, allocates direct buffers, creates a decryptor, and initializes it for the current stream offset. Sequential `read(byte[],off,len)` drains `outBuffer` if possible; otherwise it reads ciphertext into `inBuffer` using byte-buffer-capable APIs when supported, updates `streamOffset`, decrypts, handles padding, and returns plaintext from `outBuffer`. `seek` either repositions within already decrypted buffered data or seeks the wrapped stream and resets decryptor state. Positioned reads delegate to wrapped positioned APIs, then decrypt the returned range using local buffers/decryptors without changing the main stream offset. Byte-buffer read paths decrypt in place over the bytes just read.

## State and Persistence

State is in-memory stream state only: offset, padding, decryptor context, direct buffers, cached temporary heap buffer, and pools. Key and IV arrays are cloned at construction. `close` closes the wrapped stream through `super.close`, frees direct buffers, closes the codec, and marks closed. `unbuffer` frees pooled buffers/decryptors and delegates unbuffering.

## Dependencies and Integration Points

It integrates with Hadoop filesystem stream interfaces, `CryptoCodec`, `Decryptor`, `CryptoStreamUtils`, direct buffer cleaner utilities, `StreamCapabilitiesPolicy`, and IO statistics support. It can wrap HDFS or local streams and preserve enhanced capabilities when the underlying stream exposes them.

## Risks

The class is documented as not thread-safe except positioned read helpers. Offset, padding, and decryptor context must remain exactly aligned; off-by-one errors corrupt all following bytes. `setDropBehind` checks `CanSetReadahead` before casting to `CanSetDropBehind`, which appears suspicious and should be covered by tests. Direct buffers require explicit cleanup and may leak until GC if close is missed. Positioned byte-buffer decryption updates local padding using `filePosition + length` in one branch, which deserves careful tests over multi-chunk partial reads. `close` closes the codec, so sharing codec instances across streams can be risky unless callers manage lifecycle.

## Test Signals

Tests should cover sequential reads across block boundaries, nonzero initial stream offsets, seek within/outside buffered plaintext, skip semantics, positioned read and readFully for byte arrays and byte buffers, direct and heap `ByteBuffer` reads, enhanced buffer read/release, EOF behavior with unread decrypted data, unbuffer cleanup, capability delegation, direct-buffer cleanup on close, and AES/SM4 compatibility.
