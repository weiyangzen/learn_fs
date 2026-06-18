# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/router/TestPoolAlignmentContext.java

## Purpose

`TestPoolAlignmentContext` validates per-connection-pool state-id behavior used by Router observer reads. It ensures request headers carry only pool-local client state while last-seen namenode state is shared through `RouterStateIdContext`.

## Important APIs, types, and functions

The file constructs `RouterStateIdContext` and `PoolAlignmentContext`, then directly manipulates `RpcRequestHeaderProto.Builder` and `RpcResponseHeaderProto`. Helpers are `assertRequestHeaderStateId()` and `getRpcResponseHeader()`.

## Control flow

`testNamenodeRequestsOnlyUsePoolLocalStateID()` seeds namespace state id `20` in the shared Router context, creates two pool contexts for the same namespace, and verifies both initially send `Long.MIN_VALUE` in request headers while seeing last-seen state `20`. Advancing client state id on one pool to `30` affects only that pool's request header, not the other pool.

`testWhenNamenodeStopsSendingStateId()` receives a response with state id `10`, advances client state to `10`, then receives a response with state id `0`. A zero state id represents a namenode with state context disabled, so the pool resets last-seen and request state to `Long.MIN_VALUE`.

## State and persistence behavior

State is strictly in-memory. The test distinguishes shared namespace state in `RouterStateIdContext` from pool-local client state in `PoolAlignmentContext`. There is no state-store or filesystem dependency.

## Dependencies and integration points

This file protects the RPC header alignment contract between Router connection pools, clients, and observer namenodes. It is closely related to `TestObserverWithRouter` but isolates the state machine without a mini-cluster.

## Risks and test signals

Failures indicate potential stale state-id leakage across connection pools or continued observer state use after a namenode stops sending state ids. The test does not exercise concurrent updates, but it is a precise unit signal for header values.
