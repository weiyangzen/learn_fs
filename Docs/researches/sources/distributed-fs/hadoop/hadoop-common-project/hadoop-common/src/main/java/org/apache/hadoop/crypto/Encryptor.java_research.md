# `sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/crypto/Encryptor.java`

## Purpose

`Encryptor` defines the direct-buffer encryption contract used by Hadoop crypto streams.

## Important APIs and Types

Methods are `init(byte[] key, byte[] iv)`, `isContextReset()`, and `encrypt(ByteBuffer inBuffer, ByteBuffer outBuffer)`. It mirrors the `Decryptor` interface for the encryption direction.

## Control Flow

Callers initialize the encryptor with key and IV, then repeatedly call `encrypt` with direct buffers. The method advances input and output positions and may need multiple calls to process all input depending on implementation. `isContextReset` allows wrappers to detect ciphers that reset internal state and require explicit reinitialization.

## State and Persistence

The interface is stateless, while implementations hold cipher context. There is no persistence beyond ciphertext emitted by stream wrappers.

## Dependencies and Integration Points

It is produced by `CryptoCodec.createEncryptor` and consumed by `CryptoOutputStream`. It depends on Java `ByteBuffer` and `IOException`.

## Risks

Partial processing, non-direct buffers, insufficient output space, and context resets must be handled consistently by stream wrappers and implementations. Incorrect position advancement can corrupt ciphertext alignment.

## Test Signals

Tests should cover init validation, encryption over exact and partial block-size ranges, context reset behavior, buffer position/limit preservation rules, and round-trip decryption with matching `Decryptor`.
