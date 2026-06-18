# sources/cloud-native/buildkit/util/testutil/integration/util_windows.go

## Purpose
Windows-specific utilities for named pipes, platform flags, user SID resolution, or worker address helpers depending on package path.

## Important APIs, Types, Functions, Or Configuration
package integration; functions/methods dialPipe; package vars socketScheme, windowsImagesMirrorMap.

## Control Flow And Integration Points
The file is 31 lines in integration and participates in this package role: BuildKit integration-test harness code. It launches real daemons, registries, sockets/pipes, mirrors, and buildctl commands, so correctness depends on cleanup ordering, environment variables, external binaries, and platform-specific socket behavior. Control flow should be read through the listed functions and methods; notable exported or lifecycle symbols are included above. Integration points include buildkitd, buildctl, registry, containerd/dockerd/OCI worker factories, image mirrors, ConfigUpdater TOML fragments, testing.T cleanup, and feature skip helpers. Test signals are mostly downstream integration tests rather than narrow unit tests.

## State, Persistence, Dependencies, Risks, And Test Signals
State and persistence are inferred from symbols and dependencies: globals/types/functions listed above, filesystem/process/network state where the APIs call external daemons or stores, and in-memory closure/mutex/channel state where concurrency helpers are present. Dependencies: BuildKit packages: github.com/moby/buildkit/client/connhelper/npipe; external packages: net, github.com/Microsoft/go-winio. Primary risks are package-specific integration coupling, platform/build-tag behavior where present, cleanup and cancellation boundaries for daemon/executor/tracing code, and stale assumptions in tests or constants. This is production/helper code; test signal comes from adjacent package tests and integration users.
