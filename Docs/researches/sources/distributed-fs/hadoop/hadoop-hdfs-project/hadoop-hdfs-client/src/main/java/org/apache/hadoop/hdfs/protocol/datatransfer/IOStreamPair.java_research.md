# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/datatransfer/IOStreamPair.java

## Purpose
`IOStreamPair` is a small container for the input and output streams used by data transfer connections, especially after SASL or crypto wrapping.

## Important APIs, Types, and Functions
It exposes public final `InputStream in` and `OutputStream out` fields. The constructor stores both. `close` closes both streams via `IOUtils.closeStream`.

## Control Flow
No active control flow. SASL/client code returns either a raw stream pair or a wrapped pair, and callers use the fields directly.

## State and Persistence Behavior
The pair owns references to streams but not underlying sockets by itself. Closing is best-effort through `IOUtils.closeStream`, which suppresses/logs close exceptions rather than failing early.

## Dependencies and Integration Points
It depends on Java stream types and Hadoop `IOUtils`. It is used by `SaslDataTransferClient`, `DataTransferSaslUtil.createStreamPair`, `SaslParticipant.createStreamPair`, and `EncryptedPeer`.

## Risks and Edge Cases
Public fields make ownership simple but allow direct misuse. Close order is input then output; callers that need a flush should flush before closing. Null streams are tolerated only if `IOUtils.closeStream` handles nulls.

## Test Signals
SASL/encrypted transfer tests indirectly cover stream wrapping. Focused tests could assert close behavior and integration with `EncryptedPeer`.
