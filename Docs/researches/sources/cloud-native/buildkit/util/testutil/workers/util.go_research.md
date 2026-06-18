# sources/cloud-native/buildkit/util/testutil/workers/util.go

## Purpose
shared integration utility layer for temp filesystems, process start/stop, socket polling, binary lookup, synchronized log capture, and LIFO cleanup.

## Important APIs, Types, Functions, Or Configuration
package workers; types otelSocketPath, cdiSpecDir; functions/methods withOTELSocketPath, UpdateConfigFile, withCDISpecDir, UpdateConfigFile, runBuildkitd.

## Control Flow And Integration Points
The file is 130 lines in workers and participates in this package role: BuildKit integration worker backend code. It registers selectable test backends and starts buildkitd against containerd, dockerd, or OCI/runc style workers. Control flow should be read through the listed functions and methods; notable exported or lifecycle symbols are included above. Integration points include the integration.Backend/Worker interfaces, external daemons, root/rootless setup, platform helpers, feature capability lists, and daemon config updaters. Risks cluster around privileged requirements, startup timeouts, environment overrides, and cleanup of temporary roots/sockets.

## State, Persistence, Dependencies, Risks, And Test Signals
State and persistence are inferred from symbols and dependencies: globals/types/functions listed above, filesystem/process/network state where the APIs call external daemons or stores, and in-memory closure/mutex/channel state where concurrency helpers are present. Dependencies: BuildKit packages: github.com/moby/buildkit/util/testutil/integration; external packages: bytes, context, fmt, os, os/exec, path/filepath, time. Primary risks are package-specific integration coupling, platform/build-tag behavior where present, cleanup and cancellation boundaries for daemon/executor/tracing code, and stale assumptions in tests or constants. This is production/helper code; test signal comes from adjacent package tests and integration users.
