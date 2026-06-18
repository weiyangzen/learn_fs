# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/crypto/CryptoFSDataOutputStream.java

## Purpose
FSDataOutputStream wrapper that encrypts writes with CryptoOutputStream and delegates position reporting to the original FSDataOutputStream.

## Important APIs, Types, and Functions
Constructors accept FSDataOutputStream, CryptoCodec, key/IV, optional buffer size, and closeOutputStream flag; getPos() returns fsOut.getPos().

## Control Flow
Constructors seed CryptoOutputStream with the current underlying output position and pass the same start position to FSDataOutputStream super. getPos bypasses wrapper counters.

## State and Persistence Behavior
Stores a strong reference to the underlying fsOut. Persistent effect is encrypted bytes written to the delegate stream.

## Dependencies and Integration Points
Depends on CryptoCodec, CryptoOutputStream, FSDataOutputStream. Used by encryption layers over filesystem output streams.

## Risks and Test Signals
Risks include mismatched position when appending, close propagation when closeOutputStream=false, and getPos accuracy after buffered crypto writes. Tests should cover append offsets, flush/close, and position reporting.
