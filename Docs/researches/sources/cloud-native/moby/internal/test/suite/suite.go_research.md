# sources/cloud-native/moby/internal/test/suite/suite.go

## Purpose
Implements a small reflection-based test suite runner as a lighter alternative to testify's suite package.

## Important APIs, Types, And Functions
- `TimeoutFlag` aliases the standard `-timeout` flag but is marked `DO NOT USE`.
- `Run(ctx, t, suite)` discovers suite methods and runs `Test*` methods as subtests.
- `getSetupAllSuite`, `getSetupTestSuite`, `getTearDownTestSuite`, and `getTeardownAllSuite` validate lifecycle hook signatures.
- `failOnPanic` converts panics into test failures with stack traces.
- `methodFilter` accepts methods named `Test*` with receiver plus `*testing.T`.

## Control Flow
`Run` starts a span, defers panic recovery and suite teardown, reflects over exported methods, filters test methods, and invokes each with `t.Run`. For each subtest it sets test context, lazily runs suite setup once before the first test, runs per-test setup, calls the reflected test method, and defers per-test teardown.

## State And Persistence
State is in-memory: `suiteSetupDone`, suite context, and testing context storage through `testutil.SetContext`/`CleanupContext`. No files or daemon state are modified directly.

## Dependencies And Integration Points
Uses `reflect`, `runtime/debug`, `strings`, `testing`, and `internal/testutil` tracing/context helpers. Intended for internal test suites that want lifecycle hooks without pulling in testify dependencies.

## Risks And Edge Cases
Reflection only sees exported methods. Suite setup runs lazily on the first matching test, so a suite with no tests will not run setup/teardown. Panic recovery calls `FailNow`, which aborts the current test goroutine. `TimeoutTestSuite` is not wired into timeout behavior.

## Test Signals
Expected behavior is subtests for each matching suite method, setup/teardown hook invocation with exact signatures, panic-to-failure conversion, and context availability during each test.
