# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/crypto/CryptoFSDataInputStream.java

## Purpose
FSDataInputStream wrapper that decrypts data through Hadoop CryptoInputStream while preserving FSDataInputStream API shape.

## Important APIs, Types, and Functions
Two constructors accept FSDataInputStream, CryptoCodec, key, IV, and optional buffer size.

## Control Flow
Constructor wraps the source stream in CryptoInputStream and passes it to FSDataInputStream super.

## State and Persistence Behavior
No added state; CryptoInputStream owns cipher position and delegates reads to the underlying stream.

## Dependencies and Integration Points
Depends on CryptoCodec, CryptoInputStream, and FSDataInputStream. Used by encryption-aware filesystems.

## Risks and Test Signals
Risks are cipher position/IV correctness and preserving seek/position behavior from the wrapped stream. Tests should read with/without explicit buffer size and verify close propagation.
