# sources/cloud-native/buildkit/worker/tests/common.go

## Purpose
implementation file in the adjacent Go package, contributing the symbols and behavior listed below.

## Important APIs, Types, Functions, Or Configuration
package tests; types mountable; functions/methods RunMirror, mirrorBusybox, NewBusyboxSourceSnapshot, NewCtx, TestWorkerExec, TestWorkerExecFailures, TestWorkerCancel, execMount, Mount; package vars mirrorOnce, mirror, mirrorMu; tests TestWorkerExec, TestWorkerExecFailures, TestWorkerCancel.

## Control Flow And Integration Points
The file is 366 lines in tests and participates in this package role: BuildKit worker core. These files define worker interfaces, local worker implementation, controller, cache result storage, WorkerRef results, concrete runc/containerd factories, labels, filters, and shared worker tests. Control flow should be read through the listed functions and methods; notable exported or lifecycle symbols are included above. Integration points include solver ops, cache manager, snapshots, content stores, lease managers, executors, source resolvers, exporters, netproviders, CDI, Windows layer wrappers, and client WorkerInfo. Risks center on ref ownership, persistent worker IDs, cleanup, privileged integration tests, and broad interface coupling.

## State, Persistence, Dependencies, Risks, And Test Signals
State and persistence are inferred from symbols and dependencies: globals/types/functions listed above, filesystem/process/network state where the APIs call external daemons or stores, and in-memory closure/mutex/channel state where concurrency helpers are present. Dependencies: BuildKit packages: github.com/moby/buildkit/cache, github.com/moby/buildkit/executor, github.com/moby/buildkit/identity, github.com/moby/buildkit/session, github.com/moby/buildkit/snapshot, github.com/moby/buildkit/source/containerimage, github.com/moby/buildkit/util/iohelper, github.com/moby/buildkit/util/testutil/integration, github.com/moby/buildkit/worker/base; external packages: bytes, context, io, sync, testing, time, github.com/containerd/containerd/v2/pkg/namespaces, github.com/pkg/errors, github.com/stretchr/testify/require, golang.org/x/sync/errgroup. Primary risks are package-specific integration coupling, platform/build-tag behavior where present, cleanup and cancellation boundaries for daemon/executor/tracing code, and stale assumptions in tests or constants. Direct test functions in this file: TestWorkerExec, TestWorkerExecFailures, TestWorkerCancel.
