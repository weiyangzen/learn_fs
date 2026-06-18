<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/chunk_connector.cc -->
# sources/distributed-fs/lizardfs/src/common/chunk_connector.cc

## Purpose

This file implements TCP connection creation/reuse for communication with chunkservers.

## Important APIs, Types, and Functions

Implemented functions are `timeoutTime()`, `ChunkConnector::ChunkConnector()`, `startUsingConnection()`, `endUsingConnection()`, `ChunkConnectorUsingPool::ChunkConnectorUsingPool()`, `startUsingConnection()`, and `endUsingConnection()`.

## Control Flow

`startUsingConnection()` loops until the caller's `Timeout` expires: create socket, optionally bind source IP, compute retry timeout from RTT and retry count capped by remaining time, attempt `tcpnumtoconnect()`, and retry on connection failure. On success it sets `TCP_NODELAY`. The pool subclass first asks `ConnectionPool` for an existing descriptor, otherwise falls back to creating one; returning a connection puts it back into the pool.

## State and Persistence Behavior

Base connector stores source IP and RTT estimate. The pool connector references external pool state. No persistent state is used.

## Dependencies and Integration Points

It integrates sockets wrappers, `NetworkAddress`, `Timeout`, `ConnectionPool`, logging, and `ChunkserverConnectionException`.

## Risks and Edge Cases

Connection failures throw exceptions after closing descriptors. RTT backoff uses bit shifting on retry count and can grow quickly. Pool reuse assumes descriptors are still valid and protocol-clean. Source-IP bind failure stops retries immediately.

## Test Signals

Signals include successful connect, timeout behavior, bind failure, `TCP_NODELAY` warning-only behavior, pool hit/miss, and put-back expiration. No direct unit test is present here.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/chunk_connector.cc -->
