# sources/cloud-native/buildkit/worker/cacheresult.go

## Purpose
solver cache-result storage that persists worker-ref IDs and reloads refs/remotes through the Worker Controller.

## Important APIs, Types, Functions, Or Configuration
package worker; types cacheResultStorage; functions/methods NewCacheResultStorage, Save, Load, getWorkerRef, load, LoadRemotes, Exists, parseWorkerRef.

## Control Flow And Integration Points
The file is 114 lines in worker and participates in this package role: BuildKit worker core. These files define worker interfaces, local worker implementation, controller, cache result storage, WorkerRef results, concrete runc/containerd factories, labels, filters, and shared worker tests. Control flow should be read through the listed functions and methods; notable exported or lifecycle symbols are included above. Integration points include solver ops, cache manager, snapshots, content stores, lease managers, executors, source resolvers, exporters, netproviders, CDI, Windows layer wrappers, and client WorkerInfo. Risks center on ref ownership, persistent worker IDs, cleanup, privileged integration tests, and broad interface coupling.

## State, Persistence, Dependencies, Risks, And Test Signals
State and persistence are inferred from symbols and dependencies: globals/types/functions listed above, filesystem/process/network state where the APIs call external daemons or stores, and in-memory closure/mutex/channel state where concurrency helpers are present. Dependencies: BuildKit packages: github.com/moby/buildkit/cache/config, github.com/moby/buildkit/session, github.com/moby/buildkit/solver, github.com/moby/buildkit/util/compression; external packages: context, strings, time, github.com/pkg/errors. Primary risks are package-specific integration coupling, platform/build-tag behavior where present, cleanup and cancellation boundaries for daemon/executor/tracing code, and stale assumptions in tests or constants. This is production/helper code; test signal comes from adjacent package tests and integration users.
