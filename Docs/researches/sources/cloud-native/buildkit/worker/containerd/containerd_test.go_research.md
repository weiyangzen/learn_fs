# sources/cloud-native/buildkit/worker/containerd/containerd_test.go

## Purpose
test coverage for the adjacent package behavior, using table tests, integration sandboxes, or worker execution helpers depending on package.

## Important APIs, Types, Functions, Or Configuration
build constraints: !windows; package containerd; functions/methods TestMain, init, TestContainerdWorkerIntegration, newWorkerOpt, testContainerdWorkerExec, testContainerdWorkerExecFailures, testContainerdWorkerCancel; tests TestMain, TestContainerdWorkerIntegration.

## Control Flow And Integration Points
The file is 91 lines in containerd and participates in this package role: BuildKit worker core. These files define worker interfaces, local worker implementation, controller, cache result storage, WorkerRef results, concrete runc/containerd factories, labels, filters, and shared worker tests. Control flow should be read through the listed functions and methods; notable exported or lifecycle symbols are included above. Integration points include solver ops, cache manager, snapshots, content stores, lease managers, executors, source resolvers, exporters, netproviders, CDI, Windows layer wrappers, and client WorkerInfo. Risks center on ref ownership, persistent worker IDs, cleanup, privileged integration tests, and broad interface coupling.

## State, Persistence, Dependencies, Risks, And Test Signals
State and persistence are inferred from symbols and dependencies: globals/types/functions listed above, filesystem/process/network state where the APIs call external daemons or stores, and in-memory closure/mutex/channel state where concurrency helpers are present. Dependencies: BuildKit packages: github.com/moby/buildkit/util/network/netproviders, github.com/moby/buildkit/util/testutil/integration, github.com/moby/buildkit/util/testutil/workers, github.com/moby/buildkit/worker/base, github.com/moby/buildkit/worker/tests; external packages: context, testing, github.com/stretchr/testify/require. Primary risks are package-specific integration coupling, platform/build-tag behavior where present, cleanup and cancellation boundaries for daemon/executor/tracing code, and stale assumptions in tests or constants. Direct test functions in this file: TestMain, TestContainerdWorkerIntegration.
