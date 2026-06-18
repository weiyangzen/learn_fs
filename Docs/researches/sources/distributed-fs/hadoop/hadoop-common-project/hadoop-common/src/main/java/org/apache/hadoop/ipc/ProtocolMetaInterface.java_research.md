# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/ProtocolMetaInterface.java

## Purpose
`ProtocolMetaInterface` is implemented by client-side protocol translators that can report whether a server supports a method.

## Important APIs, Types, and Functions
The single API is `isMethodSupported(String methodName)`, returning a boolean and throwing `IOException` for RPC or lookup failures.

## Control Flow
Implementations usually delegate to `RpcClientUtil.isMethodSupported`, which queries the server's `ProtocolMetaInfoPB` service and caches signatures.

## State and Persistence Behavior
The interface has no state. Implementations may cache server method signatures in memory.

## Dependencies and Integration Points
It integrates with generated client translators for Hadoop services and with `RpcClientUtil`/`ProtocolMetaInfoPB`.

## Risks and Test Signals
Risks include assuming method names are unique and stale caches after server upgrades. Tests should cover positive and negative method support checks.
