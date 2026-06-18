# `sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/crypto/CryptoStreamUtils.java`

## Purpose

`CryptoStreamUtils` contains shared helpers for crypto stream buffer management, codec validation, buffer-size normalization, and input stream offset discovery.

## Important APIs and Types

Public static methods are `freeDB(ByteBuffer)`, `getBufferSize(Configuration)`, `checkCodec(CryptoCodec)`, `checkBufferSize(CryptoCodec,int)`, and `getInputStreamOffset(InputStream)`. `MIN_BUFFER_SIZE` is 512.

## Control Flow

`freeDB` uses `CleanerUtil` when unmapping/freeing direct buffers is supported and logs failures. `getBufferSize` reads `hadoop.security.crypto.buffer.size` with its default. `checkCodec` permits only `AES_CTR_NOPADDING` and `SM4_CTR_NOPADDING`. `checkBufferSize` rejects values under 512 and floors the result to a multiple of the cipher block size. `getInputStreamOffset` returns `Seekable.getPos()` when available or zero otherwise.

## State and Persistence

The class is stateless apart from constants and logger. There is no persistence.

## Dependencies and Integration Points

It is used by `CryptoInputStream` and `CryptoOutputStream`. It depends on Hadoop config constants, `CleanerUtil`, `Seekable`, `Preconditions`, and crypto suite metadata.

## Risks

Flooring buffer size can return a value smaller than the configured value; tests should ensure it never drops below useful block multiples after the minimum check. Codec validation must be updated when new CTR-compatible suites are introduced. Direct-buffer freeing is platform/JDK-sensitive and may silently no-op with trace logging.

## Test Signals

Tests should cover minimum buffer rejection, block-size flooring, AES/SM4 acceptance, unsupported suite rejection, seekable and non-seekable offset discovery, and direct-buffer free behavior on supported and unsupported JDKs.
