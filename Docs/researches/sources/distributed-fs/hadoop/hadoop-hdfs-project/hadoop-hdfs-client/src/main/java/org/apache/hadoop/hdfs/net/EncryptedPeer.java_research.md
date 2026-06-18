# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/net/EncryptedPeer.java

## Purpose
`EncryptedPeer` wraps an existing `Peer` with encrypted input/output streams from an `IOStreamPair`, while preserving peer metadata and timeout behavior through delegation.

## Important APIs, types, and functions
The constructor stores the enclosed peer, encrypted streams, and an encrypted channel if the input stream implements `ReadableByteChannel`. Timeout, receive-buffer, TCP_NODELAY, close-state, address, locality, and domain-socket methods delegate to the enclosed peer. `getInputStream` and `getOutputStream` return encrypted streams. `hasSecureChannel()` always returns true.

## Control flow
Close attempts to close the encrypted input, then encrypted output, then the enclosed peer in nested finally blocks. Other methods are direct delegation or stream access.

## State and persistence behavior
State is a wrapper around the enclosed peer and encrypted stream pair. No persistence occurs.

## Dependencies and integration points
It depends on `Peer`, `IOStreamPair`, `DomainSocket`, and Java stream/channel types. It is used by HDFS data-transfer encryption layers to keep the rest of the block-reader pipeline using `Peer`.

## Risks and test signals
Tests should verify encrypted stream use, close ordering under exceptions, channel null/non-null behavior depending on stream type, delegated timeout/address/locality behavior, `hasSecureChannel=true`, and no accidental exposure of unencrypted enclosed streams.
