# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/cache_shape/Makefile

## Purpose
Builds the `cache_shape` PowerPC selftest binary.

## Important APIs, Types, and Functions
`TEST_GEN_PROGS := cache_shape`; includes kselftest lib.mk and PowerPC flags.mk.

## Control Flow
No custom flow beyond common build/install/run rules.

## State and Persistence
No persistent state except build output.

## Dependencies and Integration Points
Integrates the cache auxiliary-vector validation test into the PowerPC target.

## Risks and Test Signals
Risk is only build integration; runtime semantics live in `cache_shape.c`.
