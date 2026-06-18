# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/ReflectionUtils.java

## Purpose
`ReflectionUtils` provides shared reflection, configuration injection, thread dump logging, object creation, serialization-copy, and inherited-member discovery utilities.

## Important APIs, Types, And Functions
Key APIs are `setConf`, `newInstance`, `setContentionTracing`, `printThreadInfo`, `logThreadInfo`, `getClass`, `copy`, `cloneWritableInto`, `getDeclaredFieldsIncludingInherited`, and `getDeclaredMethodsIncludingInherited`. Static state includes constructor cache, serialization factory, thread MXBean, previous log time, and thread-local clone buffers.

## Control Flow
`newInstance` validates constructor argument arity, fetches or caches an accessible constructor by class, instantiates, then injects configuration. `setConf` calls `Configurable.setConf` and reflectively supports legacy `JobConfigurable.configure(JobConf)`. Thread dump methods collect MXBean thread info and throttle logging by `previousLogTime`. Copy methods serialize to a thread-local output buffer, reset an input buffer over the same bytes, then deserialize into the destination.

## State And Persistence
Constructor and serialization-factory caches persist for the process and can pin classes. Thread-local buffers persist per thread. No disk persistence exists.

## Dependencies And Integration Points
It depends on Hadoop `Configuration`, `Configurable`, Writable/serialization APIs, MXBeans, reflection, and SLF4J/commons logging. It bridges common code and optional mapred classes.

## Risks
Constructor cache keys ignore constructor argument types, so using multiple constructors for one class can be unsafe. Static serialization factory may not reflect later configurations. Caches can retain classes. Reflection exceptions are wrapped as runtime failures.

## Test Signals
Tests should cover constructor caching, non-default constructor behavior, configuration injection, legacy mapred configuration, thread dump throttling, serialization copy correctness, cache clearing, and inherited member ordering.
