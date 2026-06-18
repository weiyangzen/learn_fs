<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/chunk_connector.h -->
# sources/distributed-fs/lizardfs/src/common/chunk_connector.h

## Purpose

This header declares connector abstractions and an RAII connection wrapper for chunkserver TCP connections.

## Important APIs, Types, and Functions

`ChunkConnector` exposes virtual `startUsingConnection()`/`endUsingConnection()` plus RTT/source-IP setters. `Connection` opens in its constructor, closes in `destroy()`, returns to connector in `endUsing()`, and closes in its destructor if still owned. `ChunkConnectorUsingPool` integrates a `ConnectionPool`.

## Control Flow

Callers create `Connection`, use `fd()`, then either call `endUsing()` to return it to connector/pool or let destruction close it. The pool subclass changes end behavior from close to timed pool insertion.

## State and Persistence Behavior

The RAII object owns one descriptor at a time and marks it `-1` after destroy/end. The connector stores connection tuning only.

## Dependencies and Integration Points

It depends on socket wrappers, network address, connection pool, and timeout utilities. Chunk readers/writers use this abstraction for chunkserver IO.

## Risks and Edge Cases

`Connection::endUsing()` does not set `fd_ = -1`, so the destructor will also call `destroy()` and close the descriptor after returning it to the pool. That is a serious ownership hazard unless callers avoid letting returned connections destruct normally or the code path is otherwise unused. The move constructor transfers the descriptor and invalidates the source.

## Test Signals

Tests should validate RAII close, move semantics, pool return without double close, and exception safety on failed connects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/chunk_connector.h -->
