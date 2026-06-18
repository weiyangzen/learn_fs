<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/net/ConnectTimeoutException.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/net/ConnectTimeoutException.java

## Purpose
`ConnectTimeoutException` distinguishes timeout during socket connection from other socket timeout operations.

## Important APIs and Types
It extends `SocketTimeoutException`, declares a stable serial version UID, and has a single message constructor.

## Control Flow
There is no custom flow. `NetUtils.connect` catches `SocketTimeoutException` from connection attempts and wraps it as this type.

## State and Persistence
State is the inherited exception message and stack trace.

## Dependencies and Integration Points
RPC and network clients can catch this specific subtype when connect timeout handling differs from read timeout handling.

## Risks and Test Signals
It does not preserve a cause because `SocketTimeoutException` lacks a cause constructor in this usage. Tests should cover `NetUtils.connect` producing this type on timeout and preserving a useful message.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/net/ConnectTimeoutException.java -->
