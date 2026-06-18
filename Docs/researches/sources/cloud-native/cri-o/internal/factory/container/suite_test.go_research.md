# sources/cloud-native/cri-o/internal/factory/container/suite_test.go

## Purpose
Bootstraps the Ginkgo/Gomega test suite for `internal/factory/container` and provides shared test framework state plus a fresh container factory subject for each test.

## Important APIs, Types, And Functions
- `TestContainer(t *testing.T)` registers Gomega fail handling and runs framework specs.
- Package globals `t *TestFramework` and `sut container.Container` are used by tests.
- `BeforeSuite`, `AfterSuite`, and `BeforeEach` manage framework setup/teardown and recreate `sut` via `container.New()`.

## Control Flow
Before the suite, a CRI-O test framework is created with no-op setup/teardown callbacks and initialized. After the suite it is torn down. Before every spec, the shared `sut` is replaced with a newly constructed container.

## State And Persistence
Maintains package-global test state. Temporary files or directories are managed by `TestFramework` helpers in individual tests; this file itself does not persist state.

## Dependencies And Integration Points
Integrates ONSI Ginkgo/Gomega with CRI-O's `test/framework` and the factory container constructor.

## Risks And Edge Cases
All tests rely on `sut` being fresh per test; if a test mutates package-level external state such as CDI configuration, this suite setup alone may not reset it.

## Test Signals
Failure here would prevent the whole factory container test suite from running. It provides no product assertions itself.
