# sources/cloud-native/nydus/smoke/tests/tool/test/suite.go

## Purpose
This package implements a lightweight reflection-based test-suite runner with static test methods, dynamic generators, and optional synchronous execution.

## Important APIs, Types, And Functions
`Option`, `options`, `Sync`, `Case`, and `Generator` define the mini-framework. `Run` validates that the suite is a pointer, applies options, reflects over exported methods whose names start with `Test`, and dispatches either static methods with signature `func(*testing.T)` or dynamic methods returning `Generator`. `runTest` wraps `t.Run` and calls `t.Parallel` unless sync is requested. `runDynamicTest` pulls generated cases until nil and names unnamed cases with a counter.

## Control Flow
Every suite entrypoint calls `test.Run(t, &Suite{})`. Reflection scans methods once. Dynamic generators produce one subtest at a time, enabling Cartesian matrices without registering all cases manually.

## State And Persistence
The framework stores only per-run option flags and generator counters. Test state lives in suite structs or closures.

## Dependencies And Integration Points
It integrates with Go's `testing` package and all smoke-test suites in this subset. It avoids external test frameworks while supporting parallelism.

## Risks
Reflection signature matching is strict and silent for unsupported methods. Parallel execution means suite fields shared across cases must be concurrency-safe; several suites cache prepared images and rely on external command serialization implicitly. Dynamic generators may perform expensive setup before returning the subtest closure.

## Test Signals
Subtest names and parallel/sync behavior are the visible outputs. Failures are reported through normal Go testing subtests.
