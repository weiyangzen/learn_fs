# sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/file/meta/UfsAbsentPathCacheTest.java

## Purpose
This file tests factory selection for absent UFS path caching based on the configured async thread count.

## Important APIs, Types, and Functions
It exercises `UfsAbsentPathCache.Factory.create` and checks returned implementations `AsyncUfsAbsentPathCache` and `NoopUfsAbsentPathCache`.

## Control Flow, State, and Persistence
Tests set or leave `MASTER_UFS_PATH_CACHE_THREADS`, create a cache with a system clock, assert implementation type, and reload configuration after each test.

## Dependencies and Integration Points
The test depends on Alluxio global configuration and clock injection. The mount table argument is `null`, showing that factory selection is independent from mount behavior.

## Risks
Factory behavior changes can silently disable async absent-path caching. Configuration cleanup is important because this test mutates global properties.

## Test Signals
Signals include default async cache creation, zero-thread fallback to noop, and negative-thread fallback to noop.
