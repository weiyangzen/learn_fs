# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/RpcConstants.java

## Purpose
`RpcConstants` centralizes wire-level Hadoop RPC constants: special call ids, dummy client id, retry sentinel, header bytes, header length, and protocol version.

## Important APIs, Types, and Functions
Constants include `AUTHORIZATION_FAILED_CALL_ID`, `INVALID_CALL_ID`, `CONNECTION_CONTEXT_CALL_ID`, `PING_CALL_ID`, `DUMMY_CLIENT_ID`, `INVALID_RETRY_COUNT`, `HEADER` (`hrpc`), `HEADER_LEN_AFTER_HRPC_PART`, and `CURRENT_VERSION = 9`.

## Control Flow
There is no runtime flow. Client and server connection code reference these constants while parsing/writing headers and classifying special calls.

## State and Persistence Behavior
Only immutable constants exist. The wire protocol version affects compatibility of persisted clients/servers only through network negotiation.

## Dependencies and Integration Points
It integrates with `Client`, `Server`, `RetryCache`, SASL negotiation, ping handling, and connection context processing.

## Risks and Test Signals
Changing these constants breaks wire compatibility. Tests should cover connection header validation, special call ids, dummy client id skip in retry cache, and current-version negotiation.
