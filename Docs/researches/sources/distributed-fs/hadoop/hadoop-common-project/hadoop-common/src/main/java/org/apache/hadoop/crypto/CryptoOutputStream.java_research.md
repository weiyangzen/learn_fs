# `sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/crypto/CryptoOutputStream.java`

## Purpose

`CryptoOutputStream` wraps an output stream and encrypts plaintext into CTR-mode ciphertext with a one-to-one byte mapping. It tracks stream offset so encryption can start at arbitrary positions.

## Important APIs and Types

The class extends `FilterOutputStream` and implements `Syncable`, `CanSetDropBehind`, `StreamCapabilities`, and `IOStatisticsSource`. Constructors accept a wrapped stream, codec, optional buffer size, key, IV, stream offset, and a flag controlling whether closing this wrapper closes the underlying stream. Public methods include `write`, `flush`, `close`, `hflush`, `hsync`, `setDropBehind`, `hasCapability`, `getIOStatistics`, and `getWrappedStream`.

## Control Flow

Construction validates codec and buffer size, clones key/IV, allocates direct input/output buffers, creates an encryptor, and initializes it with IV derived from `streamOffset / blockSize` plus padding at `streamOffset % blockSize`. `write(byte[],off,len)` fills `inBuffer`; when full, `encrypt` flips it, encrypts to `outBuffer`, skips leading padding once, writes encrypted bytes to the underlying stream via a temporary heap array, advances `streamOffset`, and reinitializes if the encryptor reset its context. `flush` encrypts pending buffered data before flushing. `hflush` and `hsync` flush encryption state first, then delegate sync calls when supported.

## State and Persistence

State includes direct buffers, cloned key and initial/current IV, current stream offset, padding, one encryptor, optional heap temp buffer, closed flag, and `closeOutputStream`. There is no independent persistence; encrypted bytes are written to the wrapped stream.

## Dependencies and Integration Points

It integrates with `CryptoCodec`, `Encryptor`, `CryptoStreamUtils`, Hadoop `Syncable`, stream capabilities helpers, drop-behind support, and IO statistics. HDFS clients use this style of wrapper to encrypt file data while preserving file offsets.

## Risks

The class is not thread-safe despite synchronized core methods matching `DFSOutputStream` behavior. Any misalignment of stream offset, padding, or IV calculation corrupts ciphertext. When `closeOutputStream` is false, `close` does not close the codec either, which may be intentional for shared ownership but can leak codec resources. `setDropBehind` assumes the wrapped stream implements `CanSetDropBehind` and catches only `ClassCastException`. Temporary heap copying can be a performance bottleneck.

## Test Signals

Tests should cover writes across buffer and block boundaries, nonzero initial offset, flush of partial buffers, close with both `closeOutputStream` values, sync delegation, drop-behind unsupported behavior, encryptor context reset handling, IO statistics delegation, and round-trip compatibility with `CryptoInputStream`.
