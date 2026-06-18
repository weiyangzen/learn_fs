# sources/distributed-fs/alluxio/core/server/common/src/test/java/alluxio/master/ExecutorServiceBuilderTest.java

## Purpose
`ExecutorServiceBuilderTest` verifies master RPC executor configuration validation and construction for supported executor variants.

## Important APIs, Types, and Functions
Tests cover zero/negative FJP parallelism, zero/negative keepalive, TPE creation, TPE core thread timeout, and every `ThreadPoolExecutorQueueType`. They exercise `ExecutorServiceBuilder.buildExecutorService()`, `RpcExecutorType`, `ThreadPoolExecutorQueueType`, and master RPC executor property keys.

## Control Flow, State, and Persistence
Each test reloads configuration first. Invalid tests set bad values and expect `IllegalArgumentException` with specific messages. Valid tests set executor type/options and call the builder. The tests do not persist data; they mutate global configuration during the test.

## Dependencies and Integration Points
It depends on Alluxio configuration and executor builder code used by master gRPC services.

## Risks and Test Signals
Risks covered include accepting unusable thread-pool parameters and queue type regressions. Signals are exact error messages and successful executor construction for valid TPE configurations.
