# `sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/crypto/Decryptor.java`

## Purpose

`Decryptor` defines the direct-buffer decryption contract used by Hadoop crypto streams.

## Important APIs and Types

Methods are `init(byte[] key, byte[] iv)`, `isContextReset()`, and `decrypt(ByteBuffer inBuffer, ByteBuffer outBuffer)`. Implementations are private/evolving and typically also share code with encryptors in CTR mode.

## Control Flow

Callers initialize with key and IV before decrypting. Each `decrypt` call consumes bytes from a direct input buffer and writes plaintext to a direct output buffer, advancing positions but not limits. If the implementation reset its internal context, `isContextReset` tells stream wrappers to recalculate IV/padding and reinitialize.

## State and Persistence

The interface owns no state, but implementations generally hold cipher objects and context-reset flags. There is no persistence.

## Dependencies and Integration Points

It is produced by `CryptoCodec.createDecryptor` and consumed by `CryptoInputStream`. It depends on Java `ByteBuffer` and `IOException`.

## Risks

Implementations may not process all input in one call, so callers must be prepared for partial progress. The contract expects direct buffers and positive remaining space, but enforcement is implementation-specific. Incorrect position handling breaks stream offset alignment.

## Test Signals

Tests should verify init failure behavior, full and partial buffer processing, direct-buffer requirements, position advancement, context reset reporting, and compatibility with `CryptoInputStream` padding and seek paths.
