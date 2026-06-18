# subset-b-000033 research

Grouped report for subset-b-000033. Each file section is delimited for reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/testutil/integration/pins.go -->
# sources/cloud-native/buildkit/util/testutil/integration/pins.go

## Purpose
implementation file in the adjacent Go package, contributing the symbols and behavior listed below.

## Important APIs, Types, Functions, Or Configuration
build constraints: !windows; package integration; package vars pins.

## Control Flow And Integration Points
The file is 19 lines in integration and participates in this package role: BuildKit integration-test harness code. It launches real daemons, registries, sockets/pipes, mirrors, and buildctl commands, so correctness depends on cleanup ordering, environment variables, external binaries, and platform-specific socket behavior. Control flow should be read through the listed functions and methods; notable exported or lifecycle symbols are included above. Integration points include buildkitd, buildctl, registry, containerd/dockerd/OCI worker factories, image mirrors, ConfigUpdater TOML fragments, testing.T cleanup, and feature skip helpers. Test signals are mostly downstream integration tests rather than narrow unit tests.

## State, Persistence, Dependencies, Risks, And Test Signals
State and persistence are inferred from symbols and dependencies: globals/types/functions listed above, filesystem/process/network state where the APIs call external daemons or stores, and in-memory closure/mutex/channel state where concurrency helpers are present. Dependencies: No imports or external package dependencies are declared in this file. Primary risks are package-specific integration coupling, platform/build-tag behavior where present, cleanup and cancellation boundaries for daemon/executor/tracing code, and stale assumptions in tests or constants. This is production/helper code; test signal comes from adjacent package tests and integration users.

<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/testutil/integration/pins.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/testutil/integration/registry.go -->
# sources/cloud-native/buildkit/util/testutil/integration/registry.go

## Purpose
implementation file in the adjacent Go package, contributing the symbols and behavior listed below.

## Important APIs, Types, Functions, Or Configuration
package integration; functions/methods NewRegistry, detectPort.

## Control Flow And Integration Points
The file is 117 lines in integration and participates in this package role: BuildKit integration-test harness code. It launches real daemons, registries, sockets/pipes, mirrors, and buildctl commands, so correctness depends on cleanup ordering, environment variables, external binaries, and platform-specific socket behavior. Control flow should be read through the listed functions and methods; notable exported or lifecycle symbols are included above. Integration points include buildkitd, buildctl, registry, containerd/dockerd/OCI worker factories, image mirrors, ConfigUpdater TOML fragments, testing.T cleanup, and feature skip helpers. Test signals are mostly downstream integration tests rather than narrow unit tests.

## State, Persistence, Dependencies, Risks, And Test Signals
State and persistence are inferred from symbols and dependencies: globals/types/functions listed above, filesystem/process/network state where the APIs call external daemons or stores, and in-memory closure/mutex/channel state where concurrency helpers are present. Dependencies: external packages: bufio, context, fmt, io, os, os/exec, path/filepath, regexp, time, github.com/pkg/errors. Primary risks are package-specific integration coupling, platform/build-tag behavior where present, cleanup and cancellation boundaries for daemon/executor/tracing code, and stale assumptions in tests or constants. This is production/helper code; test signal comes from adjacent package tests and integration users.

<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/testutil/integration/registry.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/testutil/integration/run.go -->
# sources/cloud-native/buildkit/util/testutil/integration/run.go

## Purpose
central integration test runner: registers workers, builds matrix subtests, mirrors images, creates sandboxes, enforces parallelism, and prints daemon logs on failure.

## Important APIs, Types, Functions, Or Configuration
package integration; types Backend, Sandbox, BackendConfig, Worker, ConfigUpdater, Test, testFunc, TestOpt, testConf, mirrorConfig, Mirror, matrixValue; functions/methods init, Name, Run, TestFuncs, Register, List, WithMatrix, WithMirroredImages, Run, getFunctionName, copyImagesLocal, resolveDefaultPlatform, OfficialImages, withMirrorConfig, UpdateConfigFile, WriteConfig, lazyMirrorRunnerFunc, lock, Close, AddImages, RunMirror, functionSuffix, newMatrixValue, prepareValueMatrix; package vars sandboxLimiter, defaultWorkers, localImageCache, localImageCacheMu; tests TestFuncs.

## Control Flow And Integration Points
The file is 599 lines in integration and participates in this package role: BuildKit integration-test harness code. It launches real daemons, registries, sockets/pipes, mirrors, and buildctl commands, so correctness depends on cleanup ordering, environment variables, external binaries, and platform-specific socket behavior. Control flow should be read through the listed functions and methods; notable exported or lifecycle symbols are included above. Integration points include buildkitd, buildctl, registry, containerd/dockerd/OCI worker factories, image mirrors, ConfigUpdater TOML fragments, testing.T cleanup, and feature skip helpers. Test signals are mostly downstream integration tests rather than narrow unit tests.

## State, Persistence, Dependencies, Risks, And Test Signals
State and persistence are inferred from symbols and dependencies: globals/types/functions listed above, filesystem/process/network state where the APIs call external daemons or stores, and in-memory closure/mutex/channel state where concurrency helpers are present. Dependencies: BuildKit packages: github.com/moby/buildkit/util/appcontext, github.com/moby/buildkit/util/contentutil; external packages: bytes, context, fmt, maps, math, math/rand, os, os/exec, path/filepath, reflect, runtime, slices. Primary risks are package-specific integration coupling, platform/build-tag behavior where present, cleanup and cancellation boundaries for daemon/executor/tracing code, and stale assumptions in tests or constants. Direct test functions in this file: TestFuncs.

<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/testutil/integration/run.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/testutil/integration/run_unix.go -->
# sources/cloud-native/buildkit/util/testutil/integration/run_unix.go

## Purpose
platform-specific helper for integration test image/reference or runtime behavior.

## Important APIs, Types, Functions, Or Configuration
build constraints: !windows; package integration; functions/methods officialImages.

## Control Flow And Integration Points
The file is 26 lines in integration and participates in this package role: BuildKit integration-test harness code. It launches real daemons, registries, sockets/pipes, mirrors, and buildctl commands, so correctness depends on cleanup ordering, environment variables, external binaries, and platform-specific socket behavior. Control flow should be read through the listed functions and methods; notable exported or lifecycle symbols are included above. Integration points include buildkitd, buildctl, registry, containerd/dockerd/OCI worker factories, image mirrors, ConfigUpdater TOML fragments, testing.T cleanup, and feature skip helpers. Test signals are mostly downstream integration tests rather than narrow unit tests.

## State, Persistence, Dependencies, Risks, And Test Signals
State and persistence are inferred from symbols and dependencies: globals/types/functions listed above, filesystem/process/network state where the APIs call external daemons or stores, and in-memory closure/mutex/channel state where concurrency helpers are present. Dependencies: external packages: runtime. Primary risks are package-specific integration coupling, platform/build-tag behavior where present, cleanup and cancellation boundaries for daemon/executor/tracing code, and stale assumptions in tests or constants. This is production/helper code; test signal comes from adjacent package tests and integration users.

<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/testutil/integration/run_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/testutil/integration/run_windows.go -->
# sources/cloud-native/buildkit/util/testutil/integration/run_windows.go

## Purpose
platform-specific helper for integration test image/reference or runtime behavior.

## Important APIs, Types, Functions, Or Configuration
package integration; functions/methods officialImages.

## Control Flow And Integration Points
The file is 14 lines in integration and participates in this package role: BuildKit integration-test harness code. It launches real daemons, registries, sockets/pipes, mirrors, and buildctl commands, so correctness depends on cleanup ordering, environment variables, external binaries, and platform-specific socket behavior. Control flow should be read through the listed functions and methods; notable exported or lifecycle symbols are included above. Integration points include buildkitd, buildctl, registry, containerd/dockerd/OCI worker factories, image mirrors, ConfigUpdater TOML fragments, testing.T cleanup, and feature skip helpers. Test signals are mostly downstream integration tests rather than narrow unit tests.

## State, Persistence, Dependencies, Risks, And Test Signals
State and persistence are inferred from symbols and dependencies: globals/types/functions listed above, filesystem/process/network state where the APIs call external daemons or stores, and in-memory closure/mutex/channel state where concurrency helpers are present. Dependencies: No imports or external package dependencies are declared in this file. Primary risks are package-specific integration coupling, platform/build-tag behavior where present, cleanup and cancellation boundaries for daemon/executor/tracing code, and stale assumptions in tests or constants. This is production/helper code; test signal comes from adjacent package tests and integration users.

<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/testutil/integration/run_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/testutil/integration/sandbox.go -->
# sources/cloud-native/buildkit/util/testutil/integration/sandbox.go

## Purpose
sandbox implementation wrapping a test backend with buildctl command helpers, CDI directory, per-test cleanup, registry creation, timeout cancellation, and feature compatibility checks.

## Important APIs, Types, Functions, Or Configuration
package integration; types sandbox; functions/methods Name, Context, CDISpecDir, Logs, PrintLogs, ClearLogs, NewRegistry, Cmd, Value, newSandbox, printBuildkitdDebugLogs, RootlessSupported, PrintLogs, FormatLogs, CheckFeatureCompat, HasFeatureCompat.

## Control Flow And Integration Points
The file is 248 lines in integration and participates in this package role: BuildKit integration-test harness code. It launches real daemons, registries, sockets/pipes, mirrors, and buildctl commands, so correctness depends on cleanup ordering, environment variables, external binaries, and platform-specific socket behavior. Control flow should be read through the listed functions and methods; notable exported or lifecycle symbols are included above. Integration points include buildkitd, buildctl, registry, containerd/dockerd/OCI worker factories, image mirrors, ConfigUpdater TOML fragments, testing.T cleanup, and feature skip helpers. Test signals are mostly downstream integration tests rather than narrow unit tests.

## State, Persistence, Dependencies, Risks, And Test Signals
State and persistence are inferred from symbols and dependencies: globals/types/functions listed above, filesystem/process/network state where the APIs call external daemons or stores, and in-memory closure/mutex/channel state where concurrency helpers are present. Dependencies: BuildKit packages: github.com/moby/buildkit/util/bklog; external packages: bufio, bytes, context, fmt, io, net, net/http, os, os/exec, path/filepath, strings, testing. Primary risks are package-specific integration coupling, platform/build-tag behavior where present, cleanup and cancellation boundaries for daemon/executor/tracing code, and stale assumptions in tests or constants. This is production/helper code; test signal comes from adjacent package tests and integration users.

<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/testutil/integration/sandbox.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/testutil/integration/util.go -->
# sources/cloud-native/buildkit/util/testutil/integration/util.go

## Purpose
shared integration utility layer for temp filesystems, process start/stop, socket polling, binary lookup, synchronized log capture, and LIFO cleanup.

## Important APIs, Types, Functions, Or Configuration
package integration; types TmpDirWithName, MultiCloser, lockingWriter; functions/methods String, Tmpdir, RunCmd, StartCmd, WaitSocket, LookupBinary, F, Append, setCmdLogs, Write; package vars ErrRequirements.

## Control Flow And Integration Points
The file is 208 lines in integration and participates in this package role: BuildKit integration-test harness code. It launches real daemons, registries, sockets/pipes, mirrors, and buildctl commands, so correctness depends on cleanup ordering, environment variables, external binaries, and platform-specific socket behavior. Control flow should be read through the listed functions and methods; notable exported or lifecycle symbols are included above. Integration points include buildkitd, buildctl, registry, containerd/dockerd/OCI worker factories, image mirrors, ConfigUpdater TOML fragments, testing.T cleanup, and feature skip helpers. Test signals are mostly downstream integration tests rather than narrow unit tests.

## State, Persistence, Dependencies, Risks, And Test Signals
State and persistence are inferred from symbols and dependencies: globals/types/functions listed above, filesystem/process/network state where the APIs call external daemons or stores, and in-memory closure/mutex/channel state where concurrency helpers are present. Dependencies: external packages: bytes, context, fmt, io, os, os/exec, strings, sync, syscall, testing, time, github.com/containerd/continuity/fs/fstest. Primary risks are package-specific integration coupling, platform/build-tag behavior where present, cleanup and cancellation boundaries for daemon/executor/tracing code, and stale assumptions in tests or constants. This is production/helper code; test signal comes from adjacent package tests and integration users.

<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/testutil/integration/util.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/testutil/integration/util_unix.go -->
# sources/cloud-native/buildkit/util/testutil/integration/util_unix.go

## Purpose
platform-specific utility companion for the adjacent package.

## Important APIs, Types, Functions, Or Configuration
build constraints: !windows; package integration; functions/methods dialPipe; package vars socketScheme.

## Control Flow And Integration Points
The file is 23 lines in integration and participates in this package role: BuildKit integration-test harness code. It launches real daemons, registries, sockets/pipes, mirrors, and buildctl commands, so correctness depends on cleanup ordering, environment variables, external binaries, and platform-specific socket behavior. Control flow should be read through the listed functions and methods; notable exported or lifecycle symbols are included above. Integration points include buildkitd, buildctl, registry, containerd/dockerd/OCI worker factories, image mirrors, ConfigUpdater TOML fragments, testing.T cleanup, and feature skip helpers. Test signals are mostly downstream integration tests rather than narrow unit tests.

## State, Persistence, Dependencies, Risks, And Test Signals
State and persistence are inferred from symbols and dependencies: globals/types/functions listed above, filesystem/process/network state where the APIs call external daemons or stores, and in-memory closure/mutex/channel state where concurrency helpers are present. Dependencies: external packages: net, github.com/pkg/errors. Primary risks are package-specific integration coupling, platform/build-tag behavior where present, cleanup and cancellation boundaries for daemon/executor/tracing code, and stale assumptions in tests or constants. This is production/helper code; test signal comes from adjacent package tests and integration users.

<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/testutil/integration/util_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/testutil/integration/util_windows.go -->
# sources/cloud-native/buildkit/util/testutil/integration/util_windows.go

## Purpose
Windows-specific utilities for named pipes, platform flags, user SID resolution, or worker address helpers depending on package path.

## Important APIs, Types, Functions, Or Configuration
package integration; functions/methods dialPipe; package vars socketScheme, windowsImagesMirrorMap.

## Control Flow And Integration Points
The file is 31 lines in integration and participates in this package role: BuildKit integration-test harness code. It launches real daemons, registries, sockets/pipes, mirrors, and buildctl commands, so correctness depends on cleanup ordering, environment variables, external binaries, and platform-specific socket behavior. Control flow should be read through the listed functions and methods; notable exported or lifecycle symbols are included above. Integration points include buildkitd, buildctl, registry, containerd/dockerd/OCI worker factories, image mirrors, ConfigUpdater TOML fragments, testing.T cleanup, and feature skip helpers. Test signals are mostly downstream integration tests rather than narrow unit tests.

## State, Persistence, Dependencies, Risks, And Test Signals
State and persistence are inferred from symbols and dependencies: globals/types/functions listed above, filesystem/process/network state where the APIs call external daemons or stores, and in-memory closure/mutex/channel state where concurrency helpers are present. Dependencies: BuildKit packages: github.com/moby/buildkit/client/connhelper/npipe; external packages: net, github.com/Microsoft/go-winio. Primary risks are package-specific integration coupling, platform/build-tag behavior where present, cleanup and cancellation boundaries for daemon/executor/tracing code, and stale assumptions in tests or constants. This is production/helper code; test signal comes from adjacent package tests and integration users.

<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/testutil/integration/util_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/testutil/tar.go -->
# sources/cloud-native/buildkit/util/testutil/tar.go

## Purpose
implementation file in the adjacent Go package, contributing the symbols and behavior listed below.

## Important APIs, Types, Functions, Or Configuration
package testutil; types TarItem; functions/methods ReadTarToMap.

## Control Flow And Integration Points
The file is 51 lines in testutil and participates in this package role: Source file in the researched subset. Control flow should be read through the listed functions and methods; notable exported or lifecycle symbols are included above. Integration points are inferred from imports, symbols, and adjacent package conventions.

## State, Persistence, Dependencies, Risks, And Test Signals
State and persistence are inferred from symbols and dependencies: globals/types/functions listed above, filesystem/process/network state where the APIs call external daemons or stores, and in-memory closure/mutex/channel state where concurrency helpers are present. Dependencies: external packages: archive/tar, bytes, compress/gzip, io, github.com/pkg/errors. Primary risks are package-specific integration coupling, platform/build-tag behavior where present, cleanup and cancellation boundaries for daemon/executor/tracing code, and stale assumptions in tests or constants. This is production/helper code; test signal comes from adjacent package tests and integration users.

<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/testutil/tar.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/testutil/workers/backend.go -->
# sources/cloud-native/buildkit/util/testutil/workers/backend.go

## Purpose
implementation file in the adjacent Go package, contributing the symbols and behavior listed below.

## Important APIs, Types, Functions, Or Configuration
package workers; types backend; functions/methods Address, DockerAddress, ContainerdAddress, DebugAddress, Rootless, NetNSDetached, Snapshotter, ExtraEnv, Supports.

## Control Flow And Integration Points
The file is 67 lines in workers and participates in this package role: BuildKit integration worker backend code. It registers selectable test backends and starts buildkitd against containerd, dockerd, or OCI/runc style workers. Control flow should be read through the listed functions and methods; notable exported or lifecycle symbols are included above. Integration points include the integration.Backend/Worker interfaces, external daemons, root/rootless setup, platform helpers, feature capability lists, and daemon config updaters. Risks cluster around privileged requirements, startup timeouts, environment overrides, and cleanup of temporary roots/sockets.

## State, Persistence, Dependencies, Risks, And Test Signals
State and persistence are inferred from symbols and dependencies: globals/types/functions listed above, filesystem/process/network state where the APIs call external daemons or stores, and in-memory closure/mutex/channel state where concurrency helpers are present. Dependencies: external packages: os, slices, strings. Primary risks are package-specific integration coupling, platform/build-tag behavior where present, cleanup and cancellation boundaries for daemon/executor/tracing code, and stale assumptions in tests or constants. This is production/helper code; test signal comes from adjacent package tests and integration users.

<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/testutil/workers/backend.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/testutil/workers/containerd.go -->
# sources/cloud-native/buildkit/util/testutil/workers/containerd.go

## Purpose
containerd-backed worker factory/startup path for both integration workers and production WorkerOpt wiring, depending on package path.

## Important APIs, Types, Functions, Or Configuration
package workers; types Containerd; functions/methods InitContainerdWorker, Name, Rootless, NetNSDetached, New, Close, runStargzSnapshotter.

## Control Flow And Integration Points
The file is 299 lines in workers and participates in this package role: BuildKit integration worker backend code. It registers selectable test backends and starts buildkitd against containerd, dockerd, or OCI/runc style workers. Control flow should be read through the listed functions and methods; notable exported or lifecycle symbols are included above. Integration points include the integration.Backend/Worker interfaces, external daemons, root/rootless setup, platform helpers, feature capability lists, and daemon config updaters. Risks cluster around privileged requirements, startup timeouts, environment overrides, and cleanup of temporary roots/sockets.

## State, Persistence, Dependencies, Risks, And Test Signals
State and persistence are inferred from symbols and dependencies: globals/types/functions listed above, filesystem/process/network state where the APIs call external daemons or stores, and in-memory closure/mutex/channel state where concurrency helpers are present. Dependencies: BuildKit packages: github.com/moby/buildkit/util/bklog, github.com/moby/buildkit/util/testutil/integration; external packages: context, fmt, log, os, os/exec, path/filepath, runtime, slices, strconv, strings, time, github.com/pkg/errors. Primary risks are package-specific integration coupling, platform/build-tag behavior where present, cleanup and cancellation boundaries for daemon/executor/tracing code, and stale assumptions in tests or constants. This is production/helper code; test signal comes from adjacent package tests and integration users.

<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/testutil/workers/containerd.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/testutil/workers/dockerd.go -->
# sources/cloud-native/buildkit/util/testutil/workers/dockerd.go

## Purpose
Docker daemon backed integration worker that starts a temporary dockerd and proxies its BuildKit gRPC endpoint.

## Important APIs, Types, Functions, Or Configuration
package workers; types Moby; functions/methods InitDockerdWorker, Name, Rootless, NetNSDetached, New, Close, waitForAPI, IsTestDockerd, IsTestDockerdMoby.

## Control Flow And Integration Points
The file is 285 lines in workers and participates in this package role: BuildKit integration worker backend code. It registers selectable test backends and starts buildkitd against containerd, dockerd, or OCI/runc style workers. Control flow should be read through the listed functions and methods; notable exported or lifecycle symbols are included above. Integration points include the integration.Backend/Worker interfaces, external daemons, root/rootless setup, platform helpers, feature capability lists, and daemon config updaters. Risks cluster around privileged requirements, startup timeouts, environment overrides, and cleanup of temporary roots/sockets.

## State, Persistence, Dependencies, Risks, And Test Signals
State and persistence are inferred from symbols and dependencies: globals/types/functions listed above, filesystem/process/network state where the APIs call external daemons or stores, and in-memory closure/mutex/channel state where concurrency helpers are present. Dependencies: BuildKit packages: github.com/moby/buildkit/cmd/buildkitd/config, github.com/moby/buildkit/util/testutil/dockerd, github.com/moby/buildkit/util/testutil/dockerd/client, github.com/moby/buildkit/util/testutil/integration; external packages: context, encoding/json, io, net, os, path/filepath, strings, time, github.com/pkg/errors, golang.org/x/sync/errgroup. Primary risks are package-specific integration coupling, platform/build-tag behavior where present, cleanup and cancellation boundaries for daemon/executor/tracing code, and stale assumptions in tests or constants. This is production/helper code; test signal comes from adjacent package tests and integration users.

<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/testutil/workers/dockerd.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/testutil/workers/features.go -->
# sources/cloud-native/buildkit/util/testutil/workers/features.go

## Purpose
implementation file in the adjacent Go package, contributing the symbols and behavior listed below.

## Important APIs, Types, Functions, Or Configuration
package workers; functions/methods CheckFeatureCompat, HasFeatureCompat; package vars features.

## Control Flow And Integration Points
The file is 72 lines in workers and participates in this package role: BuildKit integration worker backend code. It registers selectable test backends and starts buildkitd against containerd, dockerd, or OCI/runc style workers. Control flow should be read through the listed functions and methods; notable exported or lifecycle symbols are included above. Integration points include the integration.Backend/Worker interfaces, external daemons, root/rootless setup, platform helpers, feature capability lists, and daemon config updaters. Risks cluster around privileged requirements, startup timeouts, environment overrides, and cleanup of temporary roots/sockets.

## State, Persistence, Dependencies, Risks, And Test Signals
State and persistence are inferred from symbols and dependencies: globals/types/functions listed above, filesystem/process/network state where the APIs call external daemons or stores, and in-memory closure/mutex/channel state where concurrency helpers are present. Dependencies: BuildKit packages: github.com/moby/buildkit/util/testutil/integration; external packages: testing. Primary risks are package-specific integration coupling, platform/build-tag behavior where present, cleanup and cancellation boundaries for daemon/executor/tracing code, and stale assumptions in tests or constants. This is production/helper code; test signal comes from adjacent package tests and integration users.

<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/testutil/workers/features.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/testutil/workers/oci.go -->
# sources/cloud-native/buildkit/util/testutil/workers/oci.go

## Purpose
OCI buildkitd integration worker that enables oci-worker mode and optionally rootless/rootlesskit execution.

## Important APIs, Types, Functions, Or Configuration
package workers; types OCI; functions/methods InitOCIWorker, Name, Rootless, NetNSDetached, New, Close.

## Control Flow And Integration Points
The file is 103 lines in workers and participates in this package role: BuildKit integration worker backend code. It registers selectable test backends and starts buildkitd against containerd, dockerd, or OCI/runc style workers. Control flow should be read through the listed functions and methods; notable exported or lifecycle symbols are included above. Integration points include the integration.Backend/Worker interfaces, external daemons, root/rootless setup, platform helpers, feature capability lists, and daemon config updaters. Risks cluster around privileged requirements, startup timeouts, environment overrides, and cleanup of temporary roots/sockets.

## State, Persistence, Dependencies, Risks, And Test Signals
State and persistence are inferred from symbols and dependencies: globals/types/functions listed above, filesystem/process/network state where the APIs call external daemons or stores, and in-memory closure/mutex/channel state where concurrency helpers are present. Dependencies: BuildKit packages: github.com/moby/buildkit/util/testutil/integration; external packages: context, fmt, log, runtime, github.com/pkg/errors. Primary risks are package-specific integration coupling, platform/build-tag behavior where present, cleanup and cancellation boundaries for daemon/executor/tracing code, and stale assumptions in tests or constants. This is production/helper code; test signal comes from adjacent package tests and integration users.

<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/testutil/workers/oci.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/testutil/workers/oci_unix.go -->
# sources/cloud-native/buildkit/util/testutil/workers/oci_unix.go

## Purpose
implementation file in the adjacent Go package, contributing the symbols and behavior listed below.

## Important APIs, Types, Functions, Or Configuration
build constraints: !windows; package workers; functions/methods initOCIWorker.

## Control Flow And Integration Points
The file is 33 lines in workers and participates in this package role: BuildKit integration worker backend code. It registers selectable test backends and starts buildkitd against containerd, dockerd, or OCI/runc style workers. Control flow should be read through the listed functions and methods; notable exported or lifecycle symbols are included above. Integration points include the integration.Backend/Worker interfaces, external daemons, root/rootless setup, platform helpers, feature capability lists, and daemon config updaters. Risks cluster around privileged requirements, startup timeouts, environment overrides, and cleanup of temporary roots/sockets.

## State, Persistence, Dependencies, Risks, And Test Signals
State and persistence are inferred from symbols and dependencies: globals/types/functions listed above, filesystem/process/network state where the APIs call external daemons or stores, and in-memory closure/mutex/channel state where concurrency helpers are present. Dependencies: BuildKit packages: github.com/moby/buildkit/util/bklog, github.com/moby/buildkit/util/testutil/integration; external packages: fmt, os. Primary risks are package-specific integration coupling, platform/build-tag behavior where present, cleanup and cancellation boundaries for daemon/executor/tracing code, and stale assumptions in tests or constants. This is production/helper code; test signal comes from adjacent package tests and integration users.

<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/testutil/workers/oci_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/testutil/workers/oci_windows.go -->
# sources/cloud-native/buildkit/util/testutil/workers/oci_windows.go

## Purpose
implementation file in the adjacent Go package, contributing the symbols and behavior listed below.

## Important APIs, Types, Functions, Or Configuration
package workers; functions/methods initOCIWorker.

## Control Flow And Integration Points
The file is 8 lines in workers and participates in this package role: BuildKit integration worker backend code. It registers selectable test backends and starts buildkitd against containerd, dockerd, or OCI/runc style workers. Control flow should be read through the listed functions and methods; notable exported or lifecycle symbols are included above. Integration points include the integration.Backend/Worker interfaces, external daemons, root/rootless setup, platform helpers, feature capability lists, and daemon config updaters. Risks cluster around privileged requirements, startup timeouts, environment overrides, and cleanup of temporary roots/sockets.

## State, Persistence, Dependencies, Risks, And Test Signals
State and persistence are inferred from symbols and dependencies: globals/types/functions listed above, filesystem/process/network state where the APIs call external daemons or stores, and in-memory closure/mutex/channel state where concurrency helpers are present. Dependencies: BuildKit packages: github.com/moby/buildkit/util/bklog. Primary risks are package-specific integration coupling, platform/build-tag behavior where present, cleanup and cancellation boundaries for daemon/executor/tracing code, and stale assumptions in tests or constants. This is production/helper code; test signal comes from adjacent package tests and integration users.

<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/testutil/workers/oci_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/testutil/workers/util.go -->
# sources/cloud-native/buildkit/util/testutil/workers/util.go

## Purpose
shared integration utility layer for temp filesystems, process start/stop, socket polling, binary lookup, synchronized log capture, and LIFO cleanup.

## Important APIs, Types, Functions, Or Configuration
package workers; types otelSocketPath, cdiSpecDir; functions/methods withOTELSocketPath, UpdateConfigFile, withCDISpecDir, UpdateConfigFile, runBuildkitd.

## Control Flow And Integration Points
The file is 130 lines in workers and participates in this package role: BuildKit integration worker backend code. It registers selectable test backends and starts buildkitd against containerd, dockerd, or OCI/runc style workers. Control flow should be read through the listed functions and methods; notable exported or lifecycle symbols are included above. Integration points include the integration.Backend/Worker interfaces, external daemons, root/rootless setup, platform helpers, feature capability lists, and daemon config updaters. Risks cluster around privileged requirements, startup timeouts, environment overrides, and cleanup of temporary roots/sockets.

## State, Persistence, Dependencies, Risks, And Test Signals
State and persistence are inferred from symbols and dependencies: globals/types/functions listed above, filesystem/process/network state where the APIs call external daemons or stores, and in-memory closure/mutex/channel state where concurrency helpers are present. Dependencies: BuildKit packages: github.com/moby/buildkit/util/testutil/integration; external packages: bytes, context, fmt, os, os/exec, path/filepath, time. Primary risks are package-specific integration coupling, platform/build-tag behavior where present, cleanup and cancellation boundaries for daemon/executor/tracing code, and stale assumptions in tests or constants. This is production/helper code; test signal comes from adjacent package tests and integration users.

<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/testutil/workers/util.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/testutil/workers/util_unix.go -->
# sources/cloud-native/buildkit/util/testutil/workers/util_unix.go

## Purpose
platform-specific utility companion for the adjacent package.

## Important APIs, Types, Functions, Or Configuration
build constraints: !windows; package workers; functions/methods applyBuildkitdPlatformFlags, requireRoot, getSysProcAttr, getBuildkitdAddr, getBuildkitdDebugAddr, getTraceSocketPath, getContainerdSock, getContainerdDebugSock, mountInfo, chown, normalizeAddress, applyDockerdPlatformFlags, getBuildkitdNetworkAddr.

## Control Flow And Integration Points
The file is 89 lines in workers and participates in this package role: BuildKit integration worker backend code. It registers selectable test backends and starts buildkitd against containerd, dockerd, or OCI/runc style workers. Control flow should be read through the listed functions and methods; notable exported or lifecycle symbols are included above. Integration points include the integration.Backend/Worker interfaces, external daemons, root/rootless setup, platform helpers, feature capability lists, and daemon config updaters. Risks cluster around privileged requirements, startup timeouts, environment overrides, and cleanup of temporary roots/sockets.

## State, Persistence, Dependencies, Risks, And Test Signals
State and persistence are inferred from symbols and dependencies: globals/types/functions listed above, filesystem/process/network state where the APIs call external daemons or stores, and in-memory closure/mutex/channel state where concurrency helpers are present. Dependencies: BuildKit packages: github.com/moby/buildkit/util/testutil/integration; external packages: bufio, os, path/filepath, strings, syscall, github.com/pkg/errors. Primary risks are package-specific integration coupling, platform/build-tag behavior where present, cleanup and cancellation boundaries for daemon/executor/tracing code, and stale assumptions in tests or constants. This is production/helper code; test signal comes from adjacent package tests and integration users.

<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/testutil/workers/util_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/testutil/workers/util_windows.go -->
# sources/cloud-native/buildkit/util/testutil/workers/util_windows.go

## Purpose
Windows-specific integration worker helper functions for named-pipe addresses, TCP listener mode, no-op chown/root checks, and dockerd runtime flags.

## Important APIs, Types, Functions, Or Configuration
package workers; functions/methods applyBuildkitdPlatformFlags, requireRoot, getSysProcAttr, getBuildkitdAddr, getBuildkitdDebugAddr, getTraceSocketPath, getContainerdSock, getContainerdDebugSock, mountInfo, chown, normalizeAddress, applyDockerdPlatformFlags, getBuildkitdNetworkAddr.

## Control Flow And Integration Points
The file is 74 lines in workers and participates in this package role: BuildKit integration worker backend code. It registers selectable test backends and starts buildkitd against containerd, dockerd, or OCI/runc style workers. Control flow should be read through the listed functions and methods; notable exported or lifecycle symbols are included above. Integration points include the integration.Backend/Worker interfaces, external daemons, root/rootless setup, platform helpers, feature capability lists, and daemon config updaters. Risks cluster around privileged requirements, startup timeouts, environment overrides, and cleanup of temporary roots/sockets.

## State, Persistence, Dependencies, Risks, And Test Signals
State and persistence are inferred from symbols and dependencies: globals/types/functions listed above, filesystem/process/network state where the APIs call external daemons or stores, and in-memory closure/mutex/channel state where concurrency helpers are present. Dependencies: external packages: path/filepath, strings, syscall, github.com/containerd/containerd/v2/defaults. Primary risks are package-specific integration coupling, platform/build-tag behavior where present, cleanup and cancellation boundaries for daemon/executor/tracing code, and stale assumptions in tests or constants. This is production/helper code; test signal comes from adjacent package tests and integration users.

<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/testutil/workers/util_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/throttle/throttle.go -->
# sources/cloud-native/buildkit/util/throttle/throttle.go

## Purpose
implementation file in the adjacent Go package, contributing the symbols and behavior listed below.

## Important APIs, Types, Functions, Or Configuration
package throttle; functions/methods Throttle, After, throttle.

## Control Flow And Integration Points
The file is 59 lines in throttle and participates in this package role: Small timing utility package. It wraps callbacks so repeated calls collapse according to throttle or after-delay semantics. Control flow should be read through the listed functions and methods; notable exported or lifecycle symbols are included above. Integration points are any caller that needs coalesced callbacks. Risks are wall-clock sensitivity, goroutine lifetime, and absence of cancellation; tests use atomic counters and tolerant sleeps.

## State, Persistence, Dependencies, Risks, And Test Signals
State and persistence are inferred from symbols and dependencies: globals/types/functions listed above, filesystem/process/network state where the APIs call external daemons or stores, and in-memory closure/mutex/channel state where concurrency helpers are present. Dependencies: external packages: sync, time. Primary risks are package-specific integration coupling, platform/build-tag behavior where present, cleanup and cancellation boundaries for daemon/executor/tracing code, and stale assumptions in tests or constants. This is production/helper code; test signal comes from adjacent package tests and integration users.

<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/throttle/throttle.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/throttle/throttle_test.go -->
# sources/cloud-native/buildkit/util/throttle/throttle_test.go

## Purpose
test coverage for the adjacent package behavior, using table tests, integration sandboxes, or worker execution helpers depending on package.

## Important APIs, Types, Functions, Or Configuration
package throttle; functions/methods TestThrottle, TestAfter; tests TestThrottle, TestAfter.

## Control Flow And Integration Points
The file is 76 lines in throttle and participates in this package role: Small timing utility package. It wraps callbacks so repeated calls collapse according to throttle or after-delay semantics. Control flow should be read through the listed functions and methods; notable exported or lifecycle symbols are included above. Integration points are any caller that needs coalesced callbacks. Risks are wall-clock sensitivity, goroutine lifetime, and absence of cancellation; tests use atomic counters and tolerant sleeps.

## State, Persistence, Dependencies, Risks, And Test Signals
State and persistence are inferred from symbols and dependencies: globals/types/functions listed above, filesystem/process/network state where the APIs call external daemons or stores, and in-memory closure/mutex/channel state where concurrency helpers are present. Dependencies: external packages: sync/atomic, testing, time, github.com/stretchr/testify/require. Primary risks are package-specific integration coupling, platform/build-tag behavior where present, cleanup and cancellation boundaries for daemon/executor/tracing code, and stale assumptions in tests or constants. Direct test functions in this file: TestThrottle, TestAfter.

<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/throttle/throttle_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/tracing/childprocess/common.go -->
# sources/cloud-native/buildkit/util/tracing/childprocess/common.go

## Purpose
implementation file in the adjacent Go package, contributing the symbols and behavior listed below.

## Important APIs, Types, Functions, Or Configuration
package childprocess; types textMap; functions/methods Get, Set, Keys.

## Control Flow And Integration Points
The file is 44 lines in childprocess and participates in this package role: BuildKit tracing support. The files adapt OpenTelemetry propagation, exporters, gRPC stats, trace forwarding, resource detection, and protobuf-to-SDK span conversion. Control flow should be read through the listed functions and methods; notable exported or lifecycle symbols are included above. Integration points include OpenTelemetry SDK/exporters, environment variables, appcontext, child process env, gRPC stats handlers, HTTP instrumentation, and BuildKit client tracer delegates. Risks include global detector/resource state, exporter shutdown/deadlock behavior, and compatibility with deprecated Jaeger/env conventions.

## State, Persistence, Dependencies, Risks, And Test Signals
State and persistence are inferred from symbols and dependencies: globals/types/functions listed above, filesystem/process/network state where the APIs call external daemons or stores, and in-memory closure/mutex/channel state where concurrency helpers are present. Dependencies: No imports or external package dependencies are declared in this file. Primary risks are package-specific integration coupling, platform/build-tag behavior where present, cleanup and cancellation boundaries for daemon/executor/tracing code, and stale assumptions in tests or constants. This is production/helper code; test signal comes from adjacent package tests and integration users.

<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/tracing/childprocess/common.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/tracing/childprocess/traceenv.go -->
# sources/cloud-native/buildkit/util/tracing/childprocess/traceenv.go

## Purpose
implementation file in the adjacent Go package, contributing the symbols and behavior listed below.

## Important APIs, Types, Functions, Or Configuration
package childprocess; functions/methods init, initContext.

## Control Flow And Integration Points
The file is 37 lines in childprocess and participates in this package role: BuildKit tracing support. The files adapt OpenTelemetry propagation, exporters, gRPC stats, trace forwarding, resource detection, and protobuf-to-SDK span conversion. Control flow should be read through the listed functions and methods; notable exported or lifecycle symbols are included above. Integration points include OpenTelemetry SDK/exporters, environment variables, appcontext, child process env, gRPC stats handlers, HTTP instrumentation, and BuildKit client tracer delegates. Risks include global detector/resource state, exporter shutdown/deadlock behavior, and compatibility with deprecated Jaeger/env conventions.

## State, Persistence, Dependencies, Risks, And Test Signals
State and persistence are inferred from symbols and dependencies: globals/types/functions listed above, filesystem/process/network state where the APIs call external daemons or stores, and in-memory closure/mutex/channel state where concurrency helpers are present. Dependencies: BuildKit packages: github.com/moby/buildkit/util/appcontext; external packages: context, os, go.opentelemetry.io/otel/propagation. Primary risks are package-specific integration coupling, platform/build-tag behavior where present, cleanup and cancellation boundaries for daemon/executor/tracing code, and stale assumptions in tests or constants. This is production/helper code; test signal comes from adjacent package tests and integration users.

<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/tracing/childprocess/traceenv.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/tracing/childprocess/traceexec.go -->
# sources/cloud-native/buildkit/util/tracing/childprocess/traceexec.go

## Purpose
implementation file in the adjacent Go package, contributing the symbols and behavior listed below.

## Important APIs, Types, Functions, Or Configuration
package childprocess; functions/methods Environ.

## Control Flow And Integration Points
The file is 37 lines in childprocess and participates in this package role: BuildKit tracing support. The files adapt OpenTelemetry propagation, exporters, gRPC stats, trace forwarding, resource detection, and protobuf-to-SDK span conversion. Control flow should be read through the listed functions and methods; notable exported or lifecycle symbols are included above. Integration points include OpenTelemetry SDK/exporters, environment variables, appcontext, child process env, gRPC stats handlers, HTTP instrumentation, and BuildKit client tracer delegates. Risks include global detector/resource state, exporter shutdown/deadlock behavior, and compatibility with deprecated Jaeger/env conventions.

## State, Persistence, Dependencies, Risks, And Test Signals
State and persistence are inferred from symbols and dependencies: globals/types/functions listed above, filesystem/process/network state where the APIs call external daemons or stores, and in-memory closure/mutex/channel state where concurrency helpers are present. Dependencies: external packages: context, go.opentelemetry.io/otel/propagation. Primary risks are package-specific integration coupling, platform/build-tag behavior where present, cleanup and cancellation boundaries for daemon/executor/tracing code, and stale assumptions in tests or constants. This is production/helper code; test signal comes from adjacent package tests and integration users.

<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/tracing/childprocess/traceexec.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/tracing/delegated/delegated.go -->
# sources/cloud-native/buildkit/util/tracing/delegated/delegated.go

## Purpose
implementation file in the adjacent Go package, contributing the symbols and behavior listed below.

## Important APIs, Types, Functions, Or Configuration
package delegated; types Exporter; functions/methods ExportSpans, Shutdown, SetSpanExporter; package vars DefaultExporter.

## Control Flow And Integration Points
The file is 73 lines in delegated and participates in this package role: BuildKit tracing support. The files adapt OpenTelemetry propagation, exporters, gRPC stats, trace forwarding, resource detection, and protobuf-to-SDK span conversion. Control flow should be read through the listed functions and methods; notable exported or lifecycle symbols are included above. Integration points include OpenTelemetry SDK/exporters, environment variables, appcontext, child process env, gRPC stats handlers, HTTP instrumentation, and BuildKit client tracer delegates. Risks include global detector/resource state, exporter shutdown/deadlock behavior, and compatibility with deprecated Jaeger/env conventions.

## State, Persistence, Dependencies, Risks, And Test Signals
State and persistence are inferred from symbols and dependencies: globals/types/functions listed above, filesystem/process/network state where the APIs call external daemons or stores, and in-memory closure/mutex/channel state where concurrency helpers are present. Dependencies: BuildKit packages: github.com/moby/buildkit/client; external packages: context, sync, go.opentelemetry.io/otel/sdk/trace. Primary risks are package-specific integration coupling, platform/build-tag behavior where present, cleanup and cancellation boundaries for daemon/executor/tracing code, and stale assumptions in tests or constants. This is production/helper code; test signal comes from adjacent package tests and integration users.

<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/tracing/delegated/delegated.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/tracing/detect/detect.go -->
# sources/cloud-native/buildkit/util/tracing/detect/detect.go

## Purpose
OpenTelemetry exporter detector registry with env-var selection, priority fallback, and explicit none exporters.

## Important APIs, Types, Functions, Or Configuration
package detect; types ExporterDetector, detector, TraceExporterDetector, noneDetector, noneSpanExporter, noneMetricExporter; functions/methods Register, DetectTraceExporter, DetectMetricExporter, NewSpanExporter, NewMetricExporter, DetectTraceExporter, DetectMetricExporter, ExportSpans, Shutdown, IsNoneSpanExporter, Temporality, Aggregation, Export, ForceFlush, Shutdown, IsNoneMetricExporter, init; package vars detectors.

## Control Flow And Integration Points
The file is 159 lines in detect and participates in this package role: BuildKit tracing support. The files adapt OpenTelemetry propagation, exporters, gRPC stats, trace forwarding, resource detection, and protobuf-to-SDK span conversion. Control flow should be read through the listed functions and methods; notable exported or lifecycle symbols are included above. Integration points include OpenTelemetry SDK/exporters, environment variables, appcontext, child process env, gRPC stats handlers, HTTP instrumentation, and BuildKit client tracer delegates. Risks include global detector/resource state, exporter shutdown/deadlock behavior, and compatibility with deprecated Jaeger/env conventions.

## State, Persistence, Dependencies, Risks, And Test Signals
State and persistence are inferred from symbols and dependencies: globals/types/functions listed above, filesystem/process/network state where the APIs call external daemons or stores, and in-memory closure/mutex/channel state where concurrency helpers are present. Dependencies: external packages: context, os, slices, strconv, github.com/pkg/errors, go.opentelemetry.io/otel/sdk/metric, go.opentelemetry.io/otel/sdk/metric/metricdata, go.opentelemetry.io/otel/sdk/trace. Primary risks are package-specific integration coupling, platform/build-tag behavior where present, cleanup and cancellation boundaries for daemon/executor/tracing code, and stale assumptions in tests or constants. This is production/helper code; test signal comes from adjacent package tests and integration users.

<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/tracing/detect/detect.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/tracing/detect/jaeger/jaeger.go -->
# sources/cloud-native/buildkit/util/tracing/detect/jaeger/jaeger.go

## Purpose
implementation file in the adjacent Go package, contributing the symbols and behavior listed below.

## Important APIs, Types, Functions, Or Configuration
package jaeger; types threadSafeExporterWrapper; functions/methods init, jaegerExporter, envOr, ExportSpans, Shutdown.

## Control Flow And Integration Points
The file is 89 lines in jaeger and participates in this package role: BuildKit tracing support. The files adapt OpenTelemetry propagation, exporters, gRPC stats, trace forwarding, resource detection, and protobuf-to-SDK span conversion. Control flow should be read through the listed functions and methods; notable exported or lifecycle symbols are included above. Integration points include OpenTelemetry SDK/exporters, environment variables, appcontext, child process env, gRPC stats handlers, HTTP instrumentation, and BuildKit client tracer delegates. Risks include global detector/resource state, exporter shutdown/deadlock behavior, and compatibility with deprecated Jaeger/env conventions.

## State, Persistence, Dependencies, Risks, And Test Signals
State and persistence are inferred from symbols and dependencies: globals/types/functions listed above, filesystem/process/network state where the APIs call external daemons or stores, and in-memory closure/mutex/channel state where concurrency helpers are present. Dependencies: BuildKit packages: github.com/moby/buildkit/util/tracing/detect; external packages: context, net, os, strings, sync, go.opentelemetry.io/otel/exporters/jaeger, go.opentelemetry.io/otel/sdk/trace. Primary risks are package-specific integration coupling, platform/build-tag behavior where present, cleanup and cancellation boundaries for daemon/executor/tracing code, and stale assumptions in tests or constants. This is production/helper code; test signal comes from adjacent package tests and integration users.

<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/tracing/detect/jaeger/jaeger.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/tracing/detect/otlp.go -->
# sources/cloud-native/buildkit/util/tracing/detect/otlp.go

## Purpose
implementation file in the adjacent Go package, contributing the symbols and behavior listed below.

## Important APIs, Types, Functions, Or Configuration
package detect; types otlpExporterDetector; functions/methods init, DetectTraceExporter, DetectMetricExporter, deltaTemporality; package vars otlpExporter.

## Control Flow And Integration Points
The file is 87 lines in detect and participates in this package role: BuildKit tracing support. The files adapt OpenTelemetry propagation, exporters, gRPC stats, trace forwarding, resource detection, and protobuf-to-SDK span conversion. Control flow should be read through the listed functions and methods; notable exported or lifecycle symbols are included above. Integration points include OpenTelemetry SDK/exporters, environment variables, appcontext, child process env, gRPC stats handlers, HTTP instrumentation, and BuildKit client tracer delegates. Risks include global detector/resource state, exporter shutdown/deadlock behavior, and compatibility with deprecated Jaeger/env conventions.

## State, Persistence, Dependencies, Risks, And Test Signals
State and persistence are inferred from symbols and dependencies: globals/types/functions listed above, filesystem/process/network state where the APIs call external daemons or stores, and in-memory closure/mutex/channel state where concurrency helpers are present. Dependencies: external packages: context, os, github.com/pkg/errors, go.opentelemetry.io/otel/exporters/otlp/otlpmetric/otlpmetricgrpc, go.opentelemetry.io/otel/exporters/otlp/otlpmetric/otlpmetrichttp, go.opentelemetry.io/otel/exporters/otlp/otlptrace, go.opentelemetry.io/otel/exporters/otlp/otlptrace/otlptracegrpc, go.opentelemetry.io/otel/exporters/otlp/otlptrace/otlptracehttp, go.opentelemetry.io/otel/sdk/metric, go.opentelemetry.io/otel/sdk/metric/metricdata, go.opentelemetry.io/otel/sdk/trace. Primary risks are package-specific integration coupling, platform/build-tag behavior where present, cleanup and cancellation boundaries for daemon/executor/tracing code, and stale assumptions in tests or constants. This is production/helper code; test signal comes from adjacent package tests and integration users.

<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/tracing/detect/otlp.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/tracing/detect/recorder.go -->
# sources/cloud-native/buildkit/util/tracing/detect/recorder.go

## Purpose
in-memory trace recorder/exporter that stores spans by TraceID with listener tracking and background garbage collection.

## Important APIs, Types, Functions, Or Configuration
package detect; types TraceRecorder, stubs; functions/methods NewTraceRecorder, Record, gcLoop, gc, ExportSpans, Shutdown; package vars Recorder.

## Control Flow And Integration Points
The file is 165 lines in detect and participates in this package role: BuildKit tracing support. The files adapt OpenTelemetry propagation, exporters, gRPC stats, trace forwarding, resource detection, and protobuf-to-SDK span conversion. Control flow should be read through the listed functions and methods; notable exported or lifecycle symbols are included above. Integration points include OpenTelemetry SDK/exporters, environment variables, appcontext, child process env, gRPC stats handlers, HTTP instrumentation, and BuildKit client tracer delegates. Risks include global detector/resource state, exporter shutdown/deadlock behavior, and compatibility with deprecated Jaeger/env conventions.

## State, Persistence, Dependencies, Risks, And Test Signals
State and persistence are inferred from symbols and dependencies: globals/types/functions listed above, filesystem/process/network state where the APIs call external daemons or stores, and in-memory closure/mutex/channel state where concurrency helpers are present. Dependencies: external packages: context, sync, time, github.com/pkg/errors, go.opentelemetry.io/otel/sdk/trace, go.opentelemetry.io/otel/sdk/trace/tracetest, go.opentelemetry.io/otel/trace, golang.org/x/sync/semaphore. Primary risks are package-specific integration coupling, platform/build-tag behavior where present, cleanup and cancellation boundaries for daemon/executor/tracing code, and stale assumptions in tests or constants. This is production/helper code; test signal comes from adjacent package tests and integration users.

<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/tracing/detect/recorder.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/tracing/detect/resource.go -->
# sources/cloud-native/buildkit/util/tracing/detect/resource.go

## Purpose
implementation file in the adjacent Go package, contributing the symbols and behavior listed below.

## Important APIs, Types, Functions, Or Configuration
package detect; functions/methods Resource, OverrideResource, Detect, Detect.

## Control Flow And Integration Points
The file is 110 lines in detect and participates in this package role: BuildKit tracing support. The files adapt OpenTelemetry propagation, exporters, gRPC stats, trace forwarding, resource detection, and protobuf-to-SDK span conversion. Control flow should be read through the listed functions and methods; notable exported or lifecycle symbols are included above. Integration points include OpenTelemetry SDK/exporters, environment variables, appcontext, child process env, gRPC stats handlers, HTTP instrumentation, and BuildKit client tracer delegates. Risks include global detector/resource state, exporter shutdown/deadlock behavior, and compatibility with deprecated Jaeger/env conventions.

## State, Persistence, Dependencies, Risks, And Test Signals
State and persistence are inferred from symbols and dependencies: globals/types/functions listed above, filesystem/process/network state where the APIs call external daemons or stores, and in-memory closure/mutex/channel state where concurrency helpers are present. Dependencies: external packages: context, os, path/filepath, sync, go.opentelemetry.io/otel, go.opentelemetry.io/otel/attribute, go.opentelemetry.io/otel/sdk, go.opentelemetry.io/otel/sdk/resource. Primary risks are package-specific integration coupling, platform/build-tag behavior where present, cleanup and cancellation boundaries for daemon/executor/tracing code, and stale assumptions in tests or constants. This is production/helper code; test signal comes from adjacent package tests and integration users.

<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/tracing/detect/resource.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/tracing/detect/resource_test.go -->
# sources/cloud-native/buildkit/util/tracing/detect/resource_test.go

## Purpose
test coverage for the adjacent package behavior, using table tests, integration sandboxes, or worker execution helpers depending on package.

## Important APIs, Types, Functions, Or Configuration
package detect; functions/methods TestResource; tests TestResource.

## Control Flow And Integration Points
The file is 39 lines in detect and participates in this package role: BuildKit tracing support. The files adapt OpenTelemetry propagation, exporters, gRPC stats, trace forwarding, resource detection, and protobuf-to-SDK span conversion. Control flow should be read through the listed functions and methods; notable exported or lifecycle symbols are included above. Integration points include OpenTelemetry SDK/exporters, environment variables, appcontext, child process env, gRPC stats handlers, HTTP instrumentation, and BuildKit client tracer delegates. Risks include global detector/resource state, exporter shutdown/deadlock behavior, and compatibility with deprecated Jaeger/env conventions.

## State, Persistence, Dependencies, Risks, And Test Signals
State and persistence are inferred from symbols and dependencies: globals/types/functions listed above, filesystem/process/network state where the APIs call external daemons or stores, and in-memory closure/mutex/channel state where concurrency helpers are present. Dependencies: external packages: testing, github.com/stretchr/testify/require, go.opentelemetry.io/otel. Primary risks are package-specific integration coupling, platform/build-tag behavior where present, cleanup and cancellation boundaries for daemon/executor/tracing code, and stale assumptions in tests or constants. Direct test functions in this file: TestResource.

<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/tracing/detect/resource_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/tracing/forwarder/forwarder.go -->
# sources/cloud-native/buildkit/util/tracing/forwarder/forwarder.go

## Purpose
asynchronous span exporter that buffers export requests, drops expired/full-buffer batches, and drains on shutdown.

## Important APIs, Types, Functions, Or Configuration
package forwarder; types exportRequest, Exporter; functions/methods New, NewUnstarted, Start, ExportSpans, exportLoop, exportSpans, Shutdown; package vars _.

## Control Flow And Integration Points
The file is 171 lines in forwarder and participates in this package role: BuildKit tracing support. The files adapt OpenTelemetry propagation, exporters, gRPC stats, trace forwarding, resource detection, and protobuf-to-SDK span conversion. Control flow should be read through the listed functions and methods; notable exported or lifecycle symbols are included above. Integration points include OpenTelemetry SDK/exporters, environment variables, appcontext, child process env, gRPC stats handlers, HTTP instrumentation, and BuildKit client tracer delegates. Risks include global detector/resource state, exporter shutdown/deadlock behavior, and compatibility with deprecated Jaeger/env conventions.

## State, Persistence, Dependencies, Risks, And Test Signals
State and persistence are inferred from symbols and dependencies: globals/types/functions listed above, filesystem/process/network state where the APIs call external daemons or stores, and in-memory closure/mutex/channel state where concurrency helpers are present. Dependencies: BuildKit packages: github.com/moby/buildkit/util/bklog; external packages: context, sync, time, github.com/pkg/errors, go.opentelemetry.io/otel, go.opentelemetry.io/otel/sdk/trace. Primary risks are package-specific integration coupling, platform/build-tag behavior where present, cleanup and cancellation boundaries for daemon/executor/tracing code, and stale assumptions in tests or constants. This is production/helper code; test signal comes from adjacent package tests and integration users.

<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/tracing/forwarder/forwarder.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/tracing/forwarder/forwarder_test.go -->
# sources/cloud-native/buildkit/util/tracing/forwarder/forwarder_test.go

## Purpose
test coverage for the adjacent package behavior, using table tests, integration sandboxes, or worker execution helpers depending on package.

## Important APIs, Types, Functions, Or Configuration
package forwarder; types testExporter; functions/methods ExportSpans, Shutdown, TestExportSpansDropsExpiredRequest, TestShutdownReturnsWhenExportBlocks, TestShutdownPassesContextToExporterShutdown, TestShutdownDrainsPendingExports, requireCloses; package vars testSpans; tests TestExportSpansDropsExpiredRequest, TestShutdownReturnsWhenExportBlocks, TestShutdownPassesContextToExporterShutdown, TestShutdownDrainsPendingExports.

## Control Flow And Integration Points
The file is 149 lines in forwarder and participates in this package role: BuildKit tracing support. The files adapt OpenTelemetry propagation, exporters, gRPC stats, trace forwarding, resource detection, and protobuf-to-SDK span conversion. Control flow should be read through the listed functions and methods; notable exported or lifecycle symbols are included above. Integration points include OpenTelemetry SDK/exporters, environment variables, appcontext, child process env, gRPC stats handlers, HTTP instrumentation, and BuildKit client tracer delegates. Risks include global detector/resource state, exporter shutdown/deadlock behavior, and compatibility with deprecated Jaeger/env conventions.

## State, Persistence, Dependencies, Risks, And Test Signals
State and persistence are inferred from symbols and dependencies: globals/types/functions listed above, filesystem/process/network state where the APIs call external daemons or stores, and in-memory closure/mutex/channel state where concurrency helpers are present. Dependencies: external packages: context, sync, sync/atomic, testing, time, github.com/stretchr/testify/require, go.opentelemetry.io/otel/sdk/trace. Primary risks are package-specific integration coupling, platform/build-tag behavior where present, cleanup and cancellation boundaries for daemon/executor/tracing code, and stale assumptions in tests or constants. Direct test functions in this file: TestExportSpansDropsExpiredRequest, TestShutdownReturnsWhenExportBlocks, TestShutdownPassesContextToExporterShutdown, TestShutdownDrainsPendingExports.

<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/tracing/forwarder/forwarder_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/tracing/grpcstats.go -->
# sources/cloud-native/buildkit/util/tracing/grpcstats.go

## Purpose
implementation file in the adjacent Go package, contributing the symbols and behavior listed below.

## Important APIs, Types, Functions, Or Configuration
package tracing; types contextKey, statsFilter; functions/methods ServerStatsHandler, ClientStatsHandler, TagRPC, HandleRPC, TagConn, HandleConn, defaultStatsFilter.

## Control Flow And Integration Points
The file is 62 lines in tracing and participates in this package role: BuildKit tracing support. The files adapt OpenTelemetry propagation, exporters, gRPC stats, trace forwarding, resource detection, and protobuf-to-SDK span conversion. Control flow should be read through the listed functions and methods; notable exported or lifecycle symbols are included above. Integration points include OpenTelemetry SDK/exporters, environment variables, appcontext, child process env, gRPC stats handlers, HTTP instrumentation, and BuildKit client tracer delegates. Risks include global detector/resource state, exporter shutdown/deadlock behavior, and compatibility with deprecated Jaeger/env conventions.

## State, Persistence, Dependencies, Risks, And Test Signals
State and persistence are inferred from symbols and dependencies: globals/types/functions listed above, filesystem/process/network state where the APIs call external daemons or stores, and in-memory closure/mutex/channel state where concurrency helpers are present. Dependencies: external packages: context, strings, go.opentelemetry.io/contrib/instrumentation/google.golang.org/grpc/otelgrpc, google.golang.org/grpc/stats. Primary risks are package-specific integration coupling, platform/build-tag behavior where present, cleanup and cancellation boundaries for daemon/executor/tracing code, and stale assumptions in tests or constants. This is production/helper code; test signal comes from adjacent package tests and integration users.

<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/tracing/grpcstats.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/tracing/multi_span_exporter.go -->
# sources/cloud-native/buildkit/util/tracing/multi_span_exporter.go

## Purpose
implementation file in the adjacent Go package, contributing the symbols and behavior listed below.

## Important APIs, Types, Functions, Or Configuration
package tracing; types MultiSpanExporter; functions/methods ExportSpans, Shutdown.

## Control Flow And Integration Points
The file is 31 lines in tracing and participates in this package role: BuildKit tracing support. The files adapt OpenTelemetry propagation, exporters, gRPC stats, trace forwarding, resource detection, and protobuf-to-SDK span conversion. Control flow should be read through the listed functions and methods; notable exported or lifecycle symbols are included above. Integration points include OpenTelemetry SDK/exporters, environment variables, appcontext, child process env, gRPC stats handlers, HTTP instrumentation, and BuildKit client tracer delegates. Risks include global detector/resource state, exporter shutdown/deadlock behavior, and compatibility with deprecated Jaeger/env conventions.

## State, Persistence, Dependencies, Risks, And Test Signals
State and persistence are inferred from symbols and dependencies: globals/types/functions listed above, filesystem/process/network state where the APIs call external daemons or stores, and in-memory closure/mutex/channel state where concurrency helpers are present. Dependencies: external packages: context, errors, go.opentelemetry.io/otel/sdk/trace. Primary risks are package-specific integration coupling, platform/build-tag behavior where present, cleanup and cancellation boundaries for daemon/executor/tracing code, and stale assumptions in tests or constants. This is production/helper code; test signal comes from adjacent package tests and integration users.

<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/tracing/multi_span_exporter.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/tracing/multispan.go -->
# sources/cloud-native/buildkit/util/tracing/multispan.go

## Purpose
implementation file in the adjacent Go package, contributing the symbols and behavior listed below.

## Important APIs, Types, Functions, Or Configuration
package tracing; types MultiSpan; functions/methods NewMultiSpan, Add.

## Control Flow And Integration Points
The file is 23 lines in tracing and participates in this package role: BuildKit tracing support. The files adapt OpenTelemetry propagation, exporters, gRPC stats, trace forwarding, resource detection, and protobuf-to-SDK span conversion. Control flow should be read through the listed functions and methods; notable exported or lifecycle symbols are included above. Integration points include OpenTelemetry SDK/exporters, environment variables, appcontext, child process env, gRPC stats handlers, HTTP instrumentation, and BuildKit client tracer delegates. Risks include global detector/resource state, exporter shutdown/deadlock behavior, and compatibility with deprecated Jaeger/env conventions.

## State, Persistence, Dependencies, Risks, And Test Signals
State and persistence are inferred from symbols and dependencies: globals/types/functions listed above, filesystem/process/network state where the APIs call external daemons or stores, and in-memory closure/mutex/channel state where concurrency helpers are present. Dependencies: external packages: go.opentelemetry.io/otel/trace. Primary risks are package-specific integration coupling, platform/build-tag behavior where present, cleanup and cancellation boundaries for daemon/executor/tracing code, and stale assumptions in tests or constants. This is production/helper code; test signal comes from adjacent package tests and integration users.

<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/tracing/multispan.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/tracing/otlptracegrpc/client.go -->
# sources/cloud-native/buildkit/util/tracing/otlptracegrpc/client.go

## Purpose
OTLP trace client implementation that exports ResourceSpans through a managed gRPC TraceService client.

## Important APIs, Types, Functions, Or Configuration
package otlptracegrpc; types client; functions/methods NewClient, handleNewConnection, Start, Stop, UploadTraces; package vars _.

## Control Flow And Integration Points
The file is 96 lines in otlptracegrpc and participates in this package role: BuildKit tracing support. The files adapt OpenTelemetry propagation, exporters, gRPC stats, trace forwarding, resource detection, and protobuf-to-SDK span conversion. Control flow should be read through the listed functions and methods; notable exported or lifecycle symbols are included above. Integration points include OpenTelemetry SDK/exporters, environment variables, appcontext, child process env, gRPC stats handlers, HTTP instrumentation, and BuildKit client tracer delegates. Risks include global detector/resource state, exporter shutdown/deadlock behavior, and compatibility with deprecated Jaeger/env conventions.

## State, Persistence, Dependencies, Risks, And Test Signals
State and persistence are inferred from symbols and dependencies: globals/types/functions listed above, filesystem/process/network state where the APIs call external daemons or stores, and in-memory closure/mutex/channel state where concurrency helpers are present. Dependencies: external packages: context, sync, time, github.com/pkg/errors, go.opentelemetry.io/otel/exporters/otlp/otlptrace, go.opentelemetry.io/proto/otlp/collector/trace/v1, go.opentelemetry.io/proto/otlp/trace/v1, google.golang.org/grpc. Primary risks are package-specific integration coupling, platform/build-tag behavior where present, cleanup and cancellation boundaries for daemon/executor/tracing code, and stale assumptions in tests or constants. This is production/helper code; test signal comes from adjacent package tests and integration users.

<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/tracing/otlptracegrpc/client.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/tracing/otlptracegrpc/connection.go -->
# sources/cloud-native/buildkit/util/tracing/otlptracegrpc/connection.go

## Purpose
OTLP gRPC connection manager for an existing ClientConn with disconnected state, reconnect loop, stop context, and shutdown handling.

## Important APIs, Types, Functions, Or Configuration
package otlptracegrpc; types Connection; functions/methods NewConnection, StartConnection, LastConnectError, saveLastConnectError, SetStateDisconnected, setStateConnected, Connected, indefiniteBackgroundConnection, connect, ContextWithMetadata, Shutdown, ContextWithStop.

## Control Flow And Integration Points
The file is 219 lines in otlptracegrpc and participates in this package role: BuildKit tracing support. The files adapt OpenTelemetry propagation, exporters, gRPC stats, trace forwarding, resource detection, and protobuf-to-SDK span conversion. Control flow should be read through the listed functions and methods; notable exported or lifecycle symbols are included above. Integration points include OpenTelemetry SDK/exporters, environment variables, appcontext, child process env, gRPC stats handlers, HTTP instrumentation, and BuildKit client tracer delegates. Risks include global detector/resource state, exporter shutdown/deadlock behavior, and compatibility with deprecated Jaeger/env conventions.

## State, Persistence, Dependencies, Risks, And Test Signals
State and persistence are inferred from symbols and dependencies: globals/types/functions listed above, filesystem/process/network state where the APIs call external daemons or stores, and in-memory closure/mutex/channel state where concurrency helpers are present. Dependencies: external packages: context, math/rand, sync, sync/atomic, time, unsafe, github.com/pkg/errors, google.golang.org/grpc, google.golang.org/grpc/metadata. Primary risks are package-specific integration coupling, platform/build-tag behavior where present, cleanup and cancellation boundaries for daemon/executor/tracing code, and stale assumptions in tests or constants. This is production/helper code; test signal comes from adjacent package tests and integration users.

<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/tracing/otlptracegrpc/connection.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/tracing/tracing.go -->
# sources/cloud-native/buildkit/util/tracing/tracing.go

## Purpose
implementation file in the adjacent Go package, contributing the symbols and behavior listed below.

## Important APIs, Types, Functions, Or Configuration
package tracing; functions/methods StartSpan, hasStacktrace, FinishWithError, ContextWithSpanFromContext, NewTransport; package vars DefaultTransport, DefaultClient.

## Control Flow And Integration Points
The file is 86 lines in tracing and participates in this package role: BuildKit tracing support. The files adapt OpenTelemetry propagation, exporters, gRPC stats, trace forwarding, resource detection, and protobuf-to-SDK span conversion. Control flow should be read through the listed functions and methods; notable exported or lifecycle symbols are included above. Integration points include OpenTelemetry SDK/exporters, environment variables, appcontext, child process env, gRPC stats handlers, HTTP instrumentation, and BuildKit client tracer delegates. Risks include global detector/resource state, exporter shutdown/deadlock behavior, and compatibility with deprecated Jaeger/env conventions.

## State, Persistence, Dependencies, Risks, And Test Signals
State and persistence are inferred from symbols and dependencies: globals/types/functions listed above, filesystem/process/network state where the APIs call external daemons or stores, and in-memory closure/mutex/channel state where concurrency helpers are present. Dependencies: BuildKit packages: github.com/moby/buildkit/util/bklog, github.com/moby/buildkit/util/stack; external packages: context, fmt, net/http, net/http/httptrace, github.com/pkg/errors, go.opentelemetry.io/contrib/instrumentation/net/http/httptrace/otelhttptrace, go.opentelemetry.io/contrib/instrumentation/net/http/otelhttp, go.opentelemetry.io/otel/attribute, go.opentelemetry.io/otel/codes, go.opentelemetry.io/otel/propagation, go.opentelemetry.io/otel/trace, go.opentelemetry.io/otel/trace/noop. Primary risks are package-specific integration coupling, platform/build-tag behavior where present, cleanup and cancellation boundaries for daemon/executor/tracing code, and stale assumptions in tests or constants. This is production/helper code; test signal comes from adjacent package tests and integration users.

<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/tracing/tracing.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/tracing/transform/attribute.go -->
# sources/cloud-native/buildkit/util/tracing/transform/attribute.go

## Purpose
implementation file in the adjacent Go package, contributing the symbols and behavior listed below.

## Important APIs, Types, Functions, Or Configuration
package transform; functions/methods Attributes, toValue, boolArray, intArray, doubleArray, stringArray, arrayValues.

## Control Flow And Integration Points
The file is 103 lines in transform and participates in this package role: BuildKit tracing support. The files adapt OpenTelemetry propagation, exporters, gRPC stats, trace forwarding, resource detection, and protobuf-to-SDK span conversion. Control flow should be read through the listed functions and methods; notable exported or lifecycle symbols are included above. Integration points include OpenTelemetry SDK/exporters, environment variables, appcontext, child process env, gRPC stats handlers, HTTP instrumentation, and BuildKit client tracer delegates. Risks include global detector/resource state, exporter shutdown/deadlock behavior, and compatibility with deprecated Jaeger/env conventions.

## State, Persistence, Dependencies, Risks, And Test Signals
State and persistence are inferred from symbols and dependencies: globals/types/functions listed above, filesystem/process/network state where the APIs call external daemons or stores, and in-memory closure/mutex/channel state where concurrency helpers are present. Dependencies: external packages: go.opentelemetry.io/otel/attribute, go.opentelemetry.io/proto/otlp/common/v1. Primary risks are package-specific integration coupling, platform/build-tag behavior where present, cleanup and cancellation boundaries for daemon/executor/tracing code, and stale assumptions in tests or constants. This is production/helper code; test signal comes from adjacent package tests and integration users.

<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/tracing/transform/attribute.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/tracing/transform/instrumentation.go -->
# sources/cloud-native/buildkit/util/tracing/transform/instrumentation.go

## Purpose
implementation file in the adjacent Go package, contributing the symbols and behavior listed below.

## Important APIs, Types, Functions, Or Configuration
package transform; functions/methods instrumentationScope.

## Control Flow And Integration Points
The file is 18 lines in transform and participates in this package role: BuildKit tracing support. The files adapt OpenTelemetry propagation, exporters, gRPC stats, trace forwarding, resource detection, and protobuf-to-SDK span conversion. Control flow should be read through the listed functions and methods; notable exported or lifecycle symbols are included above. Integration points include OpenTelemetry SDK/exporters, environment variables, appcontext, child process env, gRPC stats handlers, HTTP instrumentation, and BuildKit client tracer delegates. Risks include global detector/resource state, exporter shutdown/deadlock behavior, and compatibility with deprecated Jaeger/env conventions.

## State, Persistence, Dependencies, Risks, And Test Signals
State and persistence are inferred from symbols and dependencies: globals/types/functions listed above, filesystem/process/network state where the APIs call external daemons or stores, and in-memory closure/mutex/channel state where concurrency helpers are present. Dependencies: external packages: go.opentelemetry.io/proto/otlp/common/v1, go.opentelemetry.io/otel/sdk/instrumentation. Primary risks are package-specific integration coupling, platform/build-tag behavior where present, cleanup and cancellation boundaries for daemon/executor/tracing code, and stale assumptions in tests or constants. This is production/helper code; test signal comes from adjacent package tests and integration users.

<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/tracing/transform/instrumentation.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/tracing/transform/span.go -->
# sources/cloud-native/buildkit/util/tracing/transform/span.go

## Purpose
OTLP ResourceSpans to sdktrace.ReadOnlySpan adapter, including span context, parent, kind, attributes, links, events, status, resource, and dropped counts.

## Important APIs, Types, Functions, Or Configuration
package transform; types readOnlySpan; functions/methods Spans, Name, SpanContext, Parent, SpanKind, StartTime, EndTime, Attributes, Links, Events, Status, InstrumentationScope, InstrumentationLibrary, Resource, DroppedAttributes, DroppedLinks, DroppedEvents, ChildSpanCount, statusCode, links, spanEvents, spanKind; package vars _.

## Control Flow And Integration Points
The file is 272 lines in transform and participates in this package role: BuildKit tracing support. The files adapt OpenTelemetry propagation, exporters, gRPC stats, trace forwarding, resource detection, and protobuf-to-SDK span conversion. Control flow should be read through the listed functions and methods; notable exported or lifecycle symbols are included above. Integration points include OpenTelemetry SDK/exporters, environment variables, appcontext, child process env, gRPC stats handlers, HTTP instrumentation, and BuildKit client tracer delegates. Risks include global detector/resource state, exporter shutdown/deadlock behavior, and compatibility with deprecated Jaeger/env conventions.

## State, Persistence, Dependencies, Risks, And Test Signals
State and persistence are inferred from symbols and dependencies: globals/types/functions listed above, filesystem/process/network state where the APIs call external daemons or stores, and in-memory closure/mutex/channel state where concurrency helpers are present. Dependencies: external packages: time, go.opentelemetry.io/otel/attribute, go.opentelemetry.io/otel/codes, go.opentelemetry.io/otel/sdk/instrumentation, go.opentelemetry.io/otel/sdk/resource, go.opentelemetry.io/otel/sdk/trace, go.opentelemetry.io/otel/trace, go.opentelemetry.io/proto/otlp/common/v1, go.opentelemetry.io/proto/otlp/resource/v1, go.opentelemetry.io/proto/otlp/trace/v1. Primary risks are package-specific integration coupling, platform/build-tag behavior where present, cleanup and cancellation boundaries for daemon/executor/tracing code, and stale assumptions in tests or constants. This is production/helper code; test signal comes from adjacent package tests and integration users.

<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/tracing/transform/span.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/urlutil/redact.go -->
# sources/cloud-native/buildkit/util/urlutil/redact.go

## Purpose
implementation file in the adjacent Go package, contributing the symbols and behavior listed below.

## Important APIs, Types, Functions, Or Configuration
package urlutil; functions/methods RedactCredentials.

## Control Flow And Integration Points
The file is 34 lines in urlutil and participates in this package role: URL safety helper package for redacting credentials before logging or display. Control flow should be read through the listed functions and methods; notable exported or lifecycle symbols are included above. Integration points are callers that log user-provided URLs. Risks are net/url parsing edge cases and credential forms; table tests cover core cases.

## State, Persistence, Dependencies, Risks, And Test Signals
State and persistence are inferred from symbols and dependencies: globals/types/functions listed above, filesystem/process/network state where the APIs call external daemons or stores, and in-memory closure/mutex/channel state where concurrency helpers are present. Dependencies: external packages: net/url. Primary risks are package-specific integration coupling, platform/build-tag behavior where present, cleanup and cancellation boundaries for daemon/executor/tracing code, and stale assumptions in tests or constants. This is production/helper code; test signal comes from adjacent package tests and integration users.

<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/urlutil/redact.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/urlutil/redact_test.go -->
# sources/cloud-native/buildkit/util/urlutil/redact_test.go

## Purpose
test coverage for the adjacent package behavior, using table tests, integration sandboxes, or worker execution helpers depending on package.

## Important APIs, Types, Functions, Or Configuration
package urlutil; functions/methods TestRedactCredentials; tests TestRedactCredentials.

## Control Flow And Integration Points
The file is 45 lines in urlutil and participates in this package role: URL safety helper package for redacting credentials before logging or display. Control flow should be read through the listed functions and methods; notable exported or lifecycle symbols are included above. Integration points are callers that log user-provided URLs. Risks are net/url parsing edge cases and credential forms; table tests cover core cases.

## State, Persistence, Dependencies, Risks, And Test Signals
State and persistence are inferred from symbols and dependencies: globals/types/functions listed above, filesystem/process/network state where the APIs call external daemons or stores, and in-memory closure/mutex/channel state where concurrency helpers are present. Dependencies: external packages: testing. Primary risks are package-specific integration coupling, platform/build-tag behavior where present, cleanup and cancellation boundaries for daemon/executor/tracing code, and stale assumptions in tests or constants. Direct test functions in this file: TestRedactCredentials.

<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/urlutil/redact_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/wildcard/wildcard.go -->
# sources/cloud-native/buildkit/util/wildcard/wildcard.go

## Purpose
implementation file in the adjacent Go package, contributing the symbols and behavior listed below.

## Important APIs, Types, Functions, Or Configuration
package wildcard; types Wildcard, Match; functions/methods New, Wildcard2Regexp, String, Match, String, Format.

## Control Flow And Integration Points
The file is 88 lines in wildcard and participates in this package role: Wildcard matching helper that translates BuildKit wildcard strings into anchored regular expressions and exposes captured substitutions. Control flow should be read through the listed functions and methods; notable exported or lifecycle symbols are included above. Integration points are matching/formatting callers that use * captures. Risks include greedy regexp behavior, invalid ** handling, and replacement semantics; unit tests cover escaping and formatting.

## State, Persistence, Dependencies, Risks, And Test Signals
State and persistence are inferred from symbols and dependencies: globals/types/functions listed above, filesystem/process/network state where the APIs call external daemons or stores, and in-memory closure/mutex/channel state where concurrency helpers are present. Dependencies: external packages: regexp, strings, github.com/pkg/errors. Primary risks are package-specific integration coupling, platform/build-tag behavior where present, cleanup and cancellation boundaries for daemon/executor/tracing code, and stale assumptions in tests or constants. This is production/helper code; test signal comes from adjacent package tests and integration users.

<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/wildcard/wildcard.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/wildcard/wildcard_test.go -->
# sources/cloud-native/buildkit/util/wildcard/wildcard_test.go

## Purpose
test coverage for the adjacent package behavior, using table tests, integration sandboxes, or worker execution helpers depending on package.

## Important APIs, Types, Functions, Or Configuration
package wildcard; functions/methods TestWildcard, TestWildcardInvalid, TestWildcardEscape, TestWildcardParentheses; tests TestWildcard, TestWildcardInvalid, TestWildcardEscape, TestWildcardParentheses.

## Control Flow And Integration Points
The file is 52 lines in wildcard and participates in this package role: Wildcard matching helper that translates BuildKit wildcard strings into anchored regular expressions and exposes captured substitutions. Control flow should be read through the listed functions and methods; notable exported or lifecycle symbols are included above. Integration points are matching/formatting callers that use * captures. Risks include greedy regexp behavior, invalid ** handling, and replacement semantics; unit tests cover escaping and formatting.

## State, Persistence, Dependencies, Risks, And Test Signals
State and persistence are inferred from symbols and dependencies: globals/types/functions listed above, filesystem/process/network state where the APIs call external daemons or stores, and in-memory closure/mutex/channel state where concurrency helpers are present. Dependencies: external packages: testing, github.com/stretchr/testify/assert, github.com/stretchr/testify/require. Primary risks are package-specific integration coupling, platform/build-tag behavior where present, cleanup and cancellation boundaries for daemon/executor/tracing code, and stale assumptions in tests or constants. Direct test functions in this file: TestWildcard, TestWildcardInvalid, TestWildcardEscape, TestWildcardParentheses.

<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/wildcard/wildcard_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/windows/util_windows.go -->
# sources/cloud-native/buildkit/util/windows/util_windows.go

## Purpose
Windows-specific utilities for named pipes, platform flags, user SID resolution, or worker address helpers depending on package path.

## Important APIs, Types, Functions, Or Configuration
package windows; types bytesReadWriteCloser, snapshotMountable, executorMountable; functions/methods ResolveUsernameToSID, GetUserIdentFromContainer, Write, Close, Mount, IdentityMapping, Mount, newStubMountable.

## Control Flow And Integration Points
The file is 167 lines in windows and participates in this package role: Windows container utility code. It resolves users to SIDs, including container built-ins, host well-known SIDs, and an executor fallback inside the container filesystem. Control flow should be read through the listed functions and methods; notable exported or lifecycle symbols are included above. Integration points include executor.Executor, container root mounts, get-user-info helper, Windows syscall SID APIs, and JSON stdout. Risks include localized account names, helper availability, and root mount assumptions.

## State, Persistence, Dependencies, Risks, And Test Signals
State and persistence are inferred from symbols and dependencies: globals/types/functions listed above, filesystem/process/network state where the APIs call external daemons or stores, and in-memory closure/mutex/channel state where concurrency helpers are present. Dependencies: BuildKit packages: github.com/moby/buildkit/executor, github.com/moby/buildkit/snapshot; external packages: bytes, context, encoding/json, strings, syscall, github.com/containerd/containerd/v2/core/mount, github.com/moby/sys/user, github.com/pkg/errors. Primary risks are package-specific integration coupling, platform/build-tag behavior where present, cleanup and cancellation boundaries for daemon/executor/tracing code, and stale assumptions in tests or constants. This is production/helper code; test signal comes from adjacent package tests and integration users.

<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/windows/util_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/winlayers/applier.go -->
# sources/cloud-native/buildkit/util/winlayers/applier.go

## Purpose
Windows layer aware diff applier wrapper that can strip Windows Files/ layout and apply it as an OCI filesystem layer on non-Windows hosts.

## Important APIs, Types, Functions, Or Configuration
package winlayers; types winApplier, readCounter, readCanceler; functions/methods NewFileSystemApplierWithWindows, Apply, Read, filter, Read, cancel.

## Control Flow And Integration Points
The file is 192 lines in winlayers and participates in this package role: Windows layer compatibility code. It converts between OCI filesystem diffs and Windows layer tar layout when a context flag enables that mode. Control flow should be read through the listed functions and methods; notable exported or lifecycle symbols are included above. Integration points include containerd diff appliers/comparers, content store writers/readers, archive.Apply/WriteDiff, compression, optional nydus unpacking, and Windows PAX/security metadata. Risks include stream cancellation, descriptor/digest correctness, and fidelity of synthetic Windows metadata.

## State, Persistence, Dependencies, Risks, And Test Signals
State and persistence are inferred from symbols and dependencies: globals/types/functions listed above, filesystem/process/network state where the APIs call external daemons or stores, and in-memory closure/mutex/channel state where concurrency helpers are present. Dependencies: external packages: archive/tar, context, io, runtime, strings, sync, github.com/containerd/containerd/v2/core/content, github.com/containerd/containerd/v2/core/diff, github.com/containerd/containerd/v2/core/images, github.com/containerd/containerd/v2/core/mount, github.com/containerd/containerd/v2/pkg/archive, github.com/containerd/containerd/v2/pkg/archive/compression. Primary risks are package-specific integration coupling, platform/build-tag behavior where present, cleanup and cancellation boundaries for daemon/executor/tracing code, and stale assumptions in tests or constants. This is production/helper code; test signal comes from adjacent package tests and integration users.

<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/winlayers/applier.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/winlayers/apply.go -->
# sources/cloud-native/buildkit/util/winlayers/apply.go

## Purpose
implementation file in the adjacent Go package, contributing the symbols and behavior listed below.

## Important APIs, Types, Functions, Or Configuration
build constraints: !nydus; package winlayers; functions/methods apply.

## Control Flow And Integration Points
The file is 16 lines in winlayers and participates in this package role: Windows layer compatibility code. It converts between OCI filesystem diffs and Windows layer tar layout when a context flag enables that mode. Control flow should be read through the listed functions and methods; notable exported or lifecycle symbols are included above. Integration points include containerd diff appliers/comparers, content store writers/readers, archive.Apply/WriteDiff, compression, optional nydus unpacking, and Windows PAX/security metadata. Risks include stream cancellation, descriptor/digest correctness, and fidelity of synthetic Windows metadata.

## State, Persistence, Dependencies, Risks, And Test Signals
State and persistence are inferred from symbols and dependencies: globals/types/functions listed above, filesystem/process/network state where the APIs call external daemons or stores, and in-memory closure/mutex/channel state where concurrency helpers are present. Dependencies: external packages: context, github.com/containerd/containerd/v2/core/diff, github.com/containerd/containerd/v2/core/mount, github.com/opencontainers/image-spec/specs-go/v1. Primary risks are package-specific integration coupling, platform/build-tag behavior where present, cleanup and cancellation boundaries for daemon/executor/tracing code, and stale assumptions in tests or constants. This is production/helper code; test signal comes from adjacent package tests and integration users.

<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/winlayers/apply.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/winlayers/apply_nydus.go -->
# sources/cloud-native/buildkit/util/winlayers/apply_nydus.go

## Purpose
implementation file in the adjacent Go package, contributing the symbols and behavior listed below.

## Important APIs, Types, Functions, Or Configuration
build constraints: nydus; package winlayers; functions/methods isNydusBlob, apply.

## Control Flow And Integration Points
The file is 73 lines in winlayers and participates in this package role: Windows layer compatibility code. It converts between OCI filesystem diffs and Windows layer tar layout when a context flag enables that mode. Control flow should be read through the listed functions and methods; notable exported or lifecycle symbols are included above. Integration points include containerd diff appliers/comparers, content store writers/readers, archive.Apply/WriteDiff, compression, optional nydus unpacking, and Windows PAX/security metadata. Risks include stream cancellation, descriptor/digest correctness, and fidelity of synthetic Windows metadata.

## State, Persistence, Dependencies, Risks, And Test Signals
State and persistence are inferred from symbols and dependencies: globals/types/functions listed above, filesystem/process/network state where the APIs call external daemons or stores, and in-memory closure/mutex/channel state where concurrency helpers are present. Dependencies: external packages: context, io, github.com/containerd/containerd/v2/core/diff, github.com/containerd/containerd/v2/core/mount, github.com/containerd/containerd/v2/pkg/archive, github.com/opencontainers/go-digest, github.com/opencontainers/image-spec/specs-go/v1, github.com/pkg/errors, github.com/containerd/nydus-snapshotter/pkg/converter. Primary risks are package-specific integration coupling, platform/build-tag behavior where present, cleanup and cancellation boundaries for daemon/executor/tracing code, and stale assumptions in tests or constants. This is production/helper code; test signal comes from adjacent package tests and integration users.

<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/winlayers/apply_nydus.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/winlayers/context.go -->
# sources/cloud-native/buildkit/util/winlayers/context.go

## Purpose
implementation file in the adjacent Go package, contributing the symbols and behavior listed below.

## Important APIs, Types, Functions, Or Configuration
package winlayers; types contextKeyT; functions/methods UseWindowsLayerMode, hasWindowsLayerMode; package vars contextKey.

## Control Flow And Integration Points
The file is 17 lines in winlayers and participates in this package role: Windows layer compatibility code. It converts between OCI filesystem diffs and Windows layer tar layout when a context flag enables that mode. Control flow should be read through the listed functions and methods; notable exported or lifecycle symbols are included above. Integration points include containerd diff appliers/comparers, content store writers/readers, archive.Apply/WriteDiff, compression, optional nydus unpacking, and Windows PAX/security metadata. Risks include stream cancellation, descriptor/digest correctness, and fidelity of synthetic Windows metadata.

## State, Persistence, Dependencies, Risks, And Test Signals
State and persistence are inferred from symbols and dependencies: globals/types/functions listed above, filesystem/process/network state where the APIs call external daemons or stores, and in-memory closure/mutex/channel state where concurrency helpers are present. Dependencies: external packages: context. Primary risks are package-specific integration coupling, platform/build-tag behavior where present, cleanup and cancellation boundaries for daemon/executor/tracing code, and stale assumptions in tests or constants. This is production/helper code; test signal comes from adjacent package tests and integration users.

<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/winlayers/context.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/winlayers/differ.go -->
# sources/cloud-native/buildkit/util/winlayers/differ.go

## Purpose
Windows layer aware diff comparer that emits Windows-compatible tar layout with PAX attributes and security descriptors.

## Important APIs, Types, Functions, Or Configuration
package winlayers; types winDiffer; functions/methods NewWalkingDiffWithWindows, Compare, uniqueRef, prepareWinHeader, addSecurityDescriptor, makeWindowsLayer; package vars emptyDesc.

## Control Flow And Integration Points
The file is 273 lines in winlayers and participates in this package role: Windows layer compatibility code. It converts between OCI filesystem diffs and Windows layer tar layout when a context flag enables that mode. Control flow should be read through the listed functions and methods; notable exported or lifecycle symbols are included above. Integration points include containerd diff appliers/comparers, content store writers/readers, archive.Apply/WriteDiff, compression, optional nydus unpacking, and Windows PAX/security metadata. Risks include stream cancellation, descriptor/digest correctness, and fidelity of synthetic Windows metadata.

## State, Persistence, Dependencies, Risks, And Test Signals
State and persistence are inferred from symbols and dependencies: globals/types/functions listed above, filesystem/process/network state where the APIs call external daemons or stores, and in-memory closure/mutex/channel state where concurrency helpers are present. Dependencies: BuildKit packages: github.com/moby/buildkit/util/bklog; external packages: archive/tar, context, crypto/rand, encoding/base64, fmt, io, time, github.com/containerd/containerd/v2/core/content, github.com/containerd/containerd/v2/core/diff, github.com/containerd/containerd/v2/core/mount, github.com/containerd/containerd/v2/pkg/archive, github.com/containerd/containerd/v2/pkg/archive/compression. Primary risks are package-specific integration coupling, platform/build-tag behavior where present, cleanup and cancellation boundaries for daemon/executor/tracing code, and stale assumptions in tests or constants. This is production/helper code; test signal comes from adjacent package tests and integration users.

<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/winlayers/differ.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/version/ua.go -->
# sources/cloud-native/buildkit/version/ua.go

## Purpose
implementation file in the adjacent Go package, contributing the symbols and behavior listed below.

## Important APIs, Types, Functions, Or Configuration
package version; functions/methods UserAgent, SetUserAgentProduct.

## Control Flow And Integration Points
The file is 50 lines in version and participates in this package role: BuildKit version metadata and User-Agent construction. Control flow should be read through the listed functions and methods; notable exported or lifecycle symbols are included above. Integration points include linker-populated Package/Version/Revision variables and user-agent product callbacks. Risks include global mutable state and map iteration order; unit tests pin common version normalization.

## State, Persistence, Dependencies, Risks, And Test Signals
State and persistence are inferred from symbols and dependencies: globals/types/functions listed above, filesystem/process/network state where the APIs call external daemons or stores, and in-memory closure/mutex/channel state where concurrency helpers are present. Dependencies: external packages: fmt, regexp, strings, sync. Primary risks are package-specific integration coupling, platform/build-tag behavior where present, cleanup and cancellation boundaries for daemon/executor/tracing code, and stale assumptions in tests or constants. This is production/helper code; test signal comes from adjacent package tests and integration users.

<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/version/ua.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/version/ua_test.go -->
# sources/cloud-native/buildkit/version/ua_test.go

## Purpose
test coverage for the adjacent package behavior, using table tests, integration sandboxes, or worker execution helpers depending on package.

## Important APIs, Types, Functions, Or Configuration
package version; functions/methods TestUserAgent; tests TestUserAgent.

## Control Flow And Integration Points
The file is 50 lines in version and participates in this package role: BuildKit version metadata and User-Agent construction. Control flow should be read through the listed functions and methods; notable exported or lifecycle symbols are included above. Integration points include linker-populated Package/Version/Revision variables and user-agent product callbacks. Risks include global mutable state and map iteration order; unit tests pin common version normalization.

## State, Persistence, Dependencies, Risks, And Test Signals
State and persistence are inferred from symbols and dependencies: globals/types/functions listed above, filesystem/process/network state where the APIs call external daemons or stores, and in-memory closure/mutex/channel state where concurrency helpers are present. Dependencies: external packages: testing. Primary risks are package-specific integration coupling, platform/build-tag behavior where present, cleanup and cancellation boundaries for daemon/executor/tracing code, and stale assumptions in tests or constants. Direct test functions in this file: TestUserAgent.

<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/version/ua_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/version/version.go -->
# sources/cloud-native/buildkit/version/version.go

## Purpose
implementation file in the adjacent Go package, contributing the symbols and behavior listed below.

## Important APIs, Types, Functions, Or Configuration
package version.

## Control Flow And Integration Points
The file is 35 lines in version and participates in this package role: BuildKit version metadata and User-Agent construction. Control flow should be read through the listed functions and methods; notable exported or lifecycle symbols are included above. Integration points include linker-populated Package/Version/Revision variables and user-agent product callbacks. Risks include global mutable state and map iteration order; unit tests pin common version normalization.

## State, Persistence, Dependencies, Risks, And Test Signals
State and persistence are inferred from symbols and dependencies: globals/types/functions listed above, filesystem/process/network state where the APIs call external daemons or stores, and in-memory closure/mutex/channel state where concurrency helpers are present. Dependencies: No imports or external package dependencies are declared in this file. Primary risks are package-specific integration coupling, platform/build-tag behavior where present, cleanup and cancellation boundaries for daemon/executor/tracing code, and stale assumptions in tests or constants. This is production/helper code; test signal comes from adjacent package tests and integration users.

<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/version/version.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/worker/base/worker.go -->
# sources/cloud-native/buildkit/worker/base/worker.go

## Purpose
base local worker implementation that wires cache manager, source manager, image writer, exporters, solver op resolution, source metadata, remote imports, and persistent worker ID.

## Important APIs, Types, Functions, Or Configuration
package base; types WorkerOpt, Worker, proxyPolicyExecutor; functions/methods NewWorker, GarbageCollect, Close, ContentStore, LeaseManager, CDIManager, ID, Labels, Platforms, GCPolicy, BuildkitVersion, LoadRef, Executor, CacheManager, Run, Exec, proxyPolicy, ResolveOp, PruneCacheMounts, ResolveSourceMetadata, DiskUsage, Prune, Exporter, FromRemote.

## Control Flow And Integration Points
The file is 739 lines in base and participates in this package role: BuildKit worker core. These files define worker interfaces, local worker implementation, controller, cache result storage, WorkerRef results, concrete runc/containerd factories, labels, filters, and shared worker tests. Control flow should be read through the listed functions and methods; notable exported or lifecycle symbols are included above. Integration points include solver ops, cache manager, snapshots, content stores, lease managers, executors, source resolvers, exporters, netproviders, CDI, Windows layer wrappers, and client WorkerInfo. Risks center on ref ownership, persistent worker IDs, cleanup, privileged integration tests, and broad interface coupling.

## State, Persistence, Dependencies, Risks, And Test Signals
State and persistence are inferred from symbols and dependencies: globals/types/functions listed above, filesystem/process/network state where the APIs call external daemons or stores, and in-memory closure/mutex/channel state where concurrency helpers are present. Dependencies: BuildKit packages: github.com/moby/buildkit/cache, github.com/moby/buildkit/cache/metadata, github.com/moby/buildkit/client, github.com/moby/buildkit/client/llb/sourceresolver, github.com/moby/buildkit/executor, github.com/moby/buildkit/executor/resources, github.com/moby/buildkit/executor/resources/types, github.com/moby/buildkit/exporter, github.com/moby/buildkit/exporter/containerimage, github.com/moby/buildkit/exporter/local; external packages: context, errors, fmt, os, path/filepath, slices, sync, time, github.com/containerd/containerd/v2/core/content, github.com/containerd/containerd/v2/core/diff, github.com/containerd/containerd/v2/core/images, github.com/containerd/containerd/v2/core/remotes/docker. Primary risks are package-specific integration coupling, platform/build-tag behavior where present, cleanup and cancellation boundaries for daemon/executor/tracing code, and stale assumptions in tests or constants. This is production/helper code; test signal comes from adjacent package tests and integration users.

<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/worker/base/worker.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/worker/base/worker_test.go -->
# sources/cloud-native/buildkit/worker/base/worker_test.go

## Purpose
test coverage for the adjacent package behavior, using table tests, integration sandboxes, or worker execution helpers depending on package.

## Important APIs, Types, Functions, Or Configuration
package base; functions/methods TestID; tests TestID.

## Control Flow And Integration Points
The file is 31 lines in base and participates in this package role: BuildKit worker core. These files define worker interfaces, local worker implementation, controller, cache result storage, WorkerRef results, concrete runc/containerd factories, labels, filters, and shared worker tests. Control flow should be read through the listed functions and methods; notable exported or lifecycle symbols are included above. Integration points include solver ops, cache manager, snapshots, content stores, lease managers, executors, source resolvers, exporters, netproviders, CDI, Windows layer wrappers, and client WorkerInfo. Risks center on ref ownership, persistent worker IDs, cleanup, privileged integration tests, and broad interface coupling.

## State, Persistence, Dependencies, Risks, And Test Signals
State and persistence are inferred from symbols and dependencies: globals/types/functions listed above, filesystem/process/network state where the APIs call external daemons or stores, and in-memory closure/mutex/channel state where concurrency helpers are present. Dependencies: external packages: os, testing, github.com/stretchr/testify/require. Primary risks are package-specific integration coupling, platform/build-tag behavior where present, cleanup and cancellation boundaries for daemon/executor/tracing code, and stale assumptions in tests or constants. Direct test functions in this file: TestID.

<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/worker/base/worker_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/worker/cacheresult.go -->
# sources/cloud-native/buildkit/worker/cacheresult.go

## Purpose
solver cache-result storage that persists worker-ref IDs and reloads refs/remotes through the Worker Controller.

## Important APIs, Types, Functions, Or Configuration
package worker; types cacheResultStorage; functions/methods NewCacheResultStorage, Save, Load, getWorkerRef, load, LoadRemotes, Exists, parseWorkerRef.

## Control Flow And Integration Points
The file is 114 lines in worker and participates in this package role: BuildKit worker core. These files define worker interfaces, local worker implementation, controller, cache result storage, WorkerRef results, concrete runc/containerd factories, labels, filters, and shared worker tests. Control flow should be read through the listed functions and methods; notable exported or lifecycle symbols are included above. Integration points include solver ops, cache manager, snapshots, content stores, lease managers, executors, source resolvers, exporters, netproviders, CDI, Windows layer wrappers, and client WorkerInfo. Risks center on ref ownership, persistent worker IDs, cleanup, privileged integration tests, and broad interface coupling.

## State, Persistence, Dependencies, Risks, And Test Signals
State and persistence are inferred from symbols and dependencies: globals/types/functions listed above, filesystem/process/network state where the APIs call external daemons or stores, and in-memory closure/mutex/channel state where concurrency helpers are present. Dependencies: BuildKit packages: github.com/moby/buildkit/cache/config, github.com/moby/buildkit/session, github.com/moby/buildkit/solver, github.com/moby/buildkit/util/compression; external packages: context, strings, time, github.com/pkg/errors. Primary risks are package-specific integration coupling, platform/build-tag behavior where present, cleanup and cancellation boundaries for daemon/executor/tracing code, and stale assumptions in tests or constants. This is production/helper code; test signal comes from adjacent package tests and integration users.

<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/worker/cacheresult.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/worker/containerd/containerd.go -->
# sources/cloud-native/buildkit/worker/containerd/containerd.go

## Purpose
production containerd WorkerOpt factory that connects to containerd and builds base.WorkerOpt with executor, snapshotter, content store, leases, labels, GC, and Windows-aware differ/applier.

## Important APIs, Types, Functions, Or Configuration
package containerd; types RuntimeInfo, WorkerOptions; functions/methods NewWorkerOpt, newContainerd.

## Control Flow And Integration Points
The file is 179 lines in containerd and participates in this package role: BuildKit worker core. These files define worker interfaces, local worker implementation, controller, cache result storage, WorkerRef results, concrete runc/containerd factories, labels, filters, and shared worker tests. Control flow should be read through the listed functions and methods; notable exported or lifecycle symbols are included above. Integration points include solver ops, cache manager, snapshots, content stores, lease managers, executors, source resolvers, exporters, netproviders, CDI, Windows layer wrappers, and client WorkerInfo. Risks center on ref ownership, persistent worker IDs, cleanup, privileged integration tests, and broad interface coupling.

## State, Persistence, Dependencies, Risks, And Test Signals
State and persistence are inferred from symbols and dependencies: globals/types/functions listed above, filesystem/process/network state where the APIs call external daemons or stores, and in-memory closure/mutex/channel state where concurrency helpers are present. Dependencies: BuildKit packages: github.com/moby/buildkit/cache/metadata, github.com/moby/buildkit/executor/containerdexecutor, github.com/moby/buildkit/executor/oci, github.com/moby/buildkit/snapshot/containerd, github.com/moby/buildkit/solver/llbsolver/cdidevices, github.com/moby/buildkit/util/leaseutil, github.com/moby/buildkit/util/network/netproviders, github.com/moby/buildkit/util/winlayers, github.com/moby/buildkit/worker/base, github.com/moby/buildkit/worker/label; external packages: context, maps, os, path/filepath, strconv, strings, github.com/containerd/containerd/v2/client, github.com/containerd/containerd/v2/core/leases, github.com/containerd/containerd/v2/pkg/gc, github.com/containerd/platforms, github.com/opencontainers/image-spec/specs-go/v1, github.com/pkg/errors. Primary risks are package-specific integration coupling, platform/build-tag behavior where present, cleanup and cancellation boundaries for daemon/executor/tracing code, and stale assumptions in tests or constants. This is production/helper code; test signal comes from adjacent package tests and integration users.

<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/worker/containerd/containerd.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/worker/containerd/containerd_test.go -->
# sources/cloud-native/buildkit/worker/containerd/containerd_test.go

## Purpose
test coverage for the adjacent package behavior, using table tests, integration sandboxes, or worker execution helpers depending on package.

## Important APIs, Types, Functions, Or Configuration
build constraints: !windows; package containerd; functions/methods TestMain, init, TestContainerdWorkerIntegration, newWorkerOpt, testContainerdWorkerExec, testContainerdWorkerExecFailures, testContainerdWorkerCancel; tests TestMain, TestContainerdWorkerIntegration.

## Control Flow And Integration Points
The file is 91 lines in containerd and participates in this package role: BuildKit worker core. These files define worker interfaces, local worker implementation, controller, cache result storage, WorkerRef results, concrete runc/containerd factories, labels, filters, and shared worker tests. Control flow should be read through the listed functions and methods; notable exported or lifecycle symbols are included above. Integration points include solver ops, cache manager, snapshots, content stores, lease managers, executors, source resolvers, exporters, netproviders, CDI, Windows layer wrappers, and client WorkerInfo. Risks center on ref ownership, persistent worker IDs, cleanup, privileged integration tests, and broad interface coupling.

## State, Persistence, Dependencies, Risks, And Test Signals
State and persistence are inferred from symbols and dependencies: globals/types/functions listed above, filesystem/process/network state where the APIs call external daemons or stores, and in-memory closure/mutex/channel state where concurrency helpers are present. Dependencies: BuildKit packages: github.com/moby/buildkit/util/network/netproviders, github.com/moby/buildkit/util/testutil/integration, github.com/moby/buildkit/util/testutil/workers, github.com/moby/buildkit/worker/base, github.com/moby/buildkit/worker/tests; external packages: context, testing, github.com/stretchr/testify/require. Primary risks are package-specific integration coupling, platform/build-tag behavior where present, cleanup and cancellation boundaries for daemon/executor/tracing code, and stale assumptions in tests or constants. Direct test functions in this file: TestMain, TestContainerdWorkerIntegration.

<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/worker/containerd/containerd_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/worker/containerd/containerd_test_unix.go -->
# sources/cloud-native/buildkit/worker/containerd/containerd_test_unix.go

## Purpose
implementation file in the adjacent Go package, contributing the symbols and behavior listed below.

## Important APIs, Types, Functions, Or Configuration
build constraints: !windows; package containerd; functions/methods checkRequirement.

## Control Flow And Integration Points
The file is 15 lines in containerd and participates in this package role: BuildKit worker core. These files define worker interfaces, local worker implementation, controller, cache result storage, WorkerRef results, concrete runc/containerd factories, labels, filters, and shared worker tests. Control flow should be read through the listed functions and methods; notable exported or lifecycle symbols are included above. Integration points include solver ops, cache manager, snapshots, content stores, lease managers, executors, source resolvers, exporters, netproviders, CDI, Windows layer wrappers, and client WorkerInfo. Risks center on ref ownership, persistent worker IDs, cleanup, privileged integration tests, and broad interface coupling.

## State, Persistence, Dependencies, Risks, And Test Signals
State and persistence are inferred from symbols and dependencies: globals/types/functions listed above, filesystem/process/network state where the APIs call external daemons or stores, and in-memory closure/mutex/channel state where concurrency helpers are present. Dependencies: external packages: os, testing. Primary risks are package-specific integration coupling, platform/build-tag behavior where present, cleanup and cancellation boundaries for daemon/executor/tracing code, and stale assumptions in tests or constants. This is production/helper code; test signal comes from adjacent package tests and integration users.

<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/worker/containerd/containerd_test_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/worker/containerd/containerd_test_windows.go -->
# sources/cloud-native/buildkit/worker/containerd/containerd_test_windows.go

## Purpose
implementation file in the adjacent Go package, contributing the symbols and behavior listed below.

## Important APIs, Types, Functions, Or Configuration
package containerd; functions/methods checkRequirement.

## Control Flow And Integration Points
The file is 9 lines in containerd and participates in this package role: BuildKit worker core. These files define worker interfaces, local worker implementation, controller, cache result storage, WorkerRef results, concrete runc/containerd factories, labels, filters, and shared worker tests. Control flow should be read through the listed functions and methods; notable exported or lifecycle symbols are included above. Integration points include solver ops, cache manager, snapshots, content stores, lease managers, executors, source resolvers, exporters, netproviders, CDI, Windows layer wrappers, and client WorkerInfo. Risks center on ref ownership, persistent worker IDs, cleanup, privileged integration tests, and broad interface coupling.

## State, Persistence, Dependencies, Risks, And Test Signals
State and persistence are inferred from symbols and dependencies: globals/types/functions listed above, filesystem/process/network state where the APIs call external daemons or stores, and in-memory closure/mutex/channel state where concurrency helpers are present. Dependencies: external packages: testing. Primary risks are package-specific integration coupling, platform/build-tag behavior where present, cleanup and cancellation boundaries for daemon/executor/tracing code, and stale assumptions in tests or constants. This is production/helper code; test signal comes from adjacent package tests and integration users.

<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/worker/containerd/containerd_test_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/worker/filter.go -->
# sources/cloud-native/buildkit/worker/filter.go

## Purpose
implementation file in the adjacent Go package, contributing the symbols and behavior listed below.

## Important APIs, Types, Functions, Or Configuration
package worker; functions/methods adaptWorker, checkMap.

## Control Flow And Integration Points
The file is 34 lines in worker and participates in this package role: BuildKit worker core. These files define worker interfaces, local worker implementation, controller, cache result storage, WorkerRef results, concrete runc/containerd factories, labels, filters, and shared worker tests. Control flow should be read through the listed functions and methods; notable exported or lifecycle symbols are included above. Integration points include solver ops, cache manager, snapshots, content stores, lease managers, executors, source resolvers, exporters, netproviders, CDI, Windows layer wrappers, and client WorkerInfo. Risks center on ref ownership, persistent worker IDs, cleanup, privileged integration tests, and broad interface coupling.

## State, Persistence, Dependencies, Risks, And Test Signals
State and persistence are inferred from symbols and dependencies: globals/types/functions listed above, filesystem/process/network state where the APIs call external daemons or stores, and in-memory closure/mutex/channel state where concurrency helpers are present. Dependencies: external packages: strings, github.com/containerd/containerd/v2/pkg/filters. Primary risks are package-specific integration coupling, platform/build-tag behavior where present, cleanup and cancellation boundaries for daemon/executor/tracing code, and stale assumptions in tests or constants. This is production/helper code; test signal comes from adjacent package tests and integration users.

<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/worker/filter.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/worker/label/label.go -->
# sources/cloud-native/buildkit/worker/label/label.go

## Purpose
implementation file in the adjacent Go package, contributing the symbols and behavior listed below.

## Important APIs, Types, Functions, Or Configuration
package label.

## Control Flow And Integration Points
The file is 17 lines in label and participates in this package role: BuildKit worker core. These files define worker interfaces, local worker implementation, controller, cache result storage, WorkerRef results, concrete runc/containerd factories, labels, filters, and shared worker tests. Control flow should be read through the listed functions and methods; notable exported or lifecycle symbols are included above. Integration points include solver ops, cache manager, snapshots, content stores, lease managers, executors, source resolvers, exporters, netproviders, CDI, Windows layer wrappers, and client WorkerInfo. Risks center on ref ownership, persistent worker IDs, cleanup, privileged integration tests, and broad interface coupling.

## State, Persistence, Dependencies, Risks, And Test Signals
State and persistence are inferred from symbols and dependencies: globals/types/functions listed above, filesystem/process/network state where the APIs call external daemons or stores, and in-memory closure/mutex/channel state where concurrency helpers are present. Dependencies: No imports or external package dependencies are declared in this file. Primary risks are package-specific integration coupling, platform/build-tag behavior where present, cleanup and cancellation boundaries for daemon/executor/tracing code, and stale assumptions in tests or constants. This is production/helper code; test signal comes from adjacent package tests and integration users.

<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/worker/label/label.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/worker/result.go -->
# sources/cloud-native/buildkit/worker/result.go

## Purpose
worker result wrapper that ties cache ImmutableRef ownership to the originating Worker and solver.Result semantics.

## Important APIs, Types, Functions, Or Configuration
package worker; types WorkerRef, workerRefResult; functions/methods NewWorkerRefResult, ID, Release, GetRemotes, Release, Sys, Clone.

## Control Flow And Integration Points
The file is 77 lines in worker and participates in this package role: BuildKit worker core. These files define worker interfaces, local worker implementation, controller, cache result storage, WorkerRef results, concrete runc/containerd factories, labels, filters, and shared worker tests. Control flow should be read through the listed functions and methods; notable exported or lifecycle symbols are included above. Integration points include solver ops, cache manager, snapshots, content stores, lease managers, executors, source resolvers, exporters, netproviders, CDI, Windows layer wrappers, and client WorkerInfo. Risks center on ref ownership, persistent worker IDs, cleanup, privileged integration tests, and broad interface coupling.

## State, Persistence, Dependencies, Risks, And Test Signals
State and persistence are inferred from symbols and dependencies: globals/types/functions listed above, filesystem/process/network state where the APIs call external daemons or stores, and in-memory closure/mutex/channel state where concurrency helpers are present. Dependencies: BuildKit packages: github.com/moby/buildkit/cache, github.com/moby/buildkit/cache/config, github.com/moby/buildkit/session, github.com/moby/buildkit/solver; external packages: context. Primary risks are package-specific integration coupling, platform/build-tag behavior where present, cleanup and cancellation boundaries for daemon/executor/tracing code, and stale assumptions in tests or constants. This is production/helper code; test signal comes from adjacent package tests and integration users.

<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/worker/result.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/worker/result_test.go -->
# sources/cloud-native/buildkit/worker/result_test.go

## Purpose
test coverage for the adjacent package behavior, using table tests, integration sandboxes, or worker execution helpers depending on package.

## Important APIs, Types, Functions, Or Configuration
package worker; types stubImmutableRef; functions/methods ID, Clone, TestWorkerRefResultCloneOwnership, TestWorkerRefResultCloneNilRef; tests TestWorkerRefResultCloneOwnership, TestWorkerRefResultCloneNilRef.

## Control Flow And Integration Points
The file is 89 lines in worker and participates in this package role: BuildKit worker core. These files define worker interfaces, local worker implementation, controller, cache result storage, WorkerRef results, concrete runc/containerd factories, labels, filters, and shared worker tests. Control flow should be read through the listed functions and methods; notable exported or lifecycle symbols are included above. Integration points include solver ops, cache manager, snapshots, content stores, lease managers, executors, source resolvers, exporters, netproviders, CDI, Windows layer wrappers, and client WorkerInfo. Risks center on ref ownership, persistent worker IDs, cleanup, privileged integration tests, and broad interface coupling.

## State, Persistence, Dependencies, Risks, And Test Signals
State and persistence are inferred from symbols and dependencies: globals/types/functions listed above, filesystem/process/network state where the APIs call external daemons or stores, and in-memory closure/mutex/channel state where concurrency helpers are present. Dependencies: BuildKit packages: github.com/moby/buildkit/cache; external packages: testing, github.com/stretchr/testify/require. Primary risks are package-specific integration coupling, platform/build-tag behavior where present, cleanup and cancellation boundaries for daemon/executor/tracing code, and stale assumptions in tests or constants. Direct test functions in this file: TestWorkerRefResultCloneOwnership, TestWorkerRefResultCloneNilRef.

<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/worker/result_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/worker/runc/runc.go -->
# sources/cloud-native/buildkit/worker/runc/runc.go

## Purpose
Linux runc/OCI WorkerOpt factory that creates snapshotter/content/metadata stores, executor, network providers, labels, and resource monitor.

## Important APIs, Types, Functions, Or Configuration
build constraints: linux; package runc; types SnapshotterFactory; functions/methods NewWorkerOpt.

## Control Flow And Integration Points
The file is 163 lines in runc and participates in this package role: BuildKit worker core. These files define worker interfaces, local worker implementation, controller, cache result storage, WorkerRef results, concrete runc/containerd factories, labels, filters, and shared worker tests. Control flow should be read through the listed functions and methods; notable exported or lifecycle symbols are included above. Integration points include solver ops, cache manager, snapshots, content stores, lease managers, executors, source resolvers, exporters, netproviders, CDI, Windows layer wrappers, and client WorkerInfo. Risks center on ref ownership, persistent worker IDs, cleanup, privileged integration tests, and broad interface coupling.

## State, Persistence, Dependencies, Risks, And Test Signals
State and persistence are inferred from symbols and dependencies: globals/types/functions listed above, filesystem/process/network state where the APIs call external daemons or stores, and in-memory closure/mutex/channel state where concurrency helpers are present. Dependencies: BuildKit packages: github.com/moby/buildkit/cache/metadata, github.com/moby/buildkit/executor/oci, github.com/moby/buildkit/executor/resources, github.com/moby/buildkit/executor/runcexecutor, github.com/moby/buildkit/snapshot/containerd, github.com/moby/buildkit/solver/llbsolver/cdidevices, github.com/moby/buildkit/util/leaseutil, github.com/moby/buildkit/util/network/netproviders, github.com/moby/buildkit/util/winlayers, github.com/moby/buildkit/worker/base; external packages: context, maps, os, path/filepath, strconv, github.com/containerd/containerd/v2/core/diff/apply, github.com/containerd/containerd/v2/core/metadata, github.com/containerd/containerd/v2/core/snapshots, github.com/containerd/containerd/v2/plugins/content/local, github.com/containerd/containerd/v2/plugins/diff/walking, github.com/containerd/platforms, github.com/moby/sys/user. Primary risks are package-specific integration coupling, platform/build-tag behavior where present, cleanup and cancellation boundaries for daemon/executor/tracing code, and stale assumptions in tests or constants. This is production/helper code; test signal comes from adjacent package tests and integration users.

<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/worker/runc/runc.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/worker/runc/runc_test.go -->
# sources/cloud-native/buildkit/worker/runc/runc_test.go

## Purpose
test coverage for the adjacent package behavior, using table tests, integration sandboxes, or worker execution helpers depending on package.

## Important APIs, Types, Functions, Or Configuration
build constraints: linux; package runc; types mountable; functions/methods TestMain, newWorkerOpt, checkRequirement, TestRuncWorker, formatDiskUsage, TestRuncWorkerNoProcessSandbox, TestRuncWorkerExec, TestRuncWorkerExecFailures, TestRuncWorkerCancel, execMount, Mount; tests TestMain, TestRuncWorker, TestRuncWorkerNoProcessSandbox, TestRuncWorkerExec, TestRuncWorkerExecFailures, TestRuncWorkerCancel.

## Control Flow And Integration Points
The file is 258 lines in runc and participates in this package role: BuildKit worker core. These files define worker interfaces, local worker implementation, controller, cache result storage, WorkerRef results, concrete runc/containerd factories, labels, filters, and shared worker tests. Control flow should be read through the listed functions and methods; notable exported or lifecycle symbols are included above. Integration points include solver ops, cache manager, snapshots, content stores, lease managers, executors, source resolvers, exporters, netproviders, CDI, Windows layer wrappers, and client WorkerInfo. Risks center on ref ownership, persistent worker IDs, cleanup, privileged integration tests, and broad interface coupling.

## State, Persistence, Dependencies, Risks, And Test Signals
State and persistence are inferred from symbols and dependencies: globals/types/functions listed above, filesystem/process/network state where the APIs call external daemons or stores, and in-memory closure/mutex/channel state where concurrency helpers are present. Dependencies: BuildKit packages: github.com/moby/buildkit/cache, github.com/moby/buildkit/client, github.com/moby/buildkit/executor, github.com/moby/buildkit/executor/oci, github.com/moby/buildkit/session, github.com/moby/buildkit/snapshot, github.com/moby/buildkit/util/iohelper, github.com/moby/buildkit/util/network/netproviders, github.com/moby/buildkit/worker/base, github.com/moby/buildkit/worker/tests; external packages: bytes, context, fmt, os, os/exec, path/filepath, testing, time, github.com/containerd/containerd/v2/core/snapshots, github.com/containerd/containerd/v2/plugins/snapshots/overlay, github.com/stretchr/testify/require. Primary risks are package-specific integration coupling, platform/build-tag behavior where present, cleanup and cancellation boundaries for daemon/executor/tracing code, and stale assumptions in tests or constants. Direct test functions in this file: TestMain, TestRuncWorker, TestRuncWorkerNoProcessSandbox, TestRuncWorkerExec, TestRuncWorkerExecFailures, TestRuncWorkerCancel.

<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/worker/runc/runc_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/worker/tests/common.go -->
# sources/cloud-native/buildkit/worker/tests/common.go

## Purpose
implementation file in the adjacent Go package, contributing the symbols and behavior listed below.

## Important APIs, Types, Functions, Or Configuration
package tests; types mountable; functions/methods RunMirror, mirrorBusybox, NewBusyboxSourceSnapshot, NewCtx, TestWorkerExec, TestWorkerExecFailures, TestWorkerCancel, execMount, Mount; package vars mirrorOnce, mirror, mirrorMu; tests TestWorkerExec, TestWorkerExecFailures, TestWorkerCancel.

## Control Flow And Integration Points
The file is 366 lines in tests and participates in this package role: BuildKit worker core. These files define worker interfaces, local worker implementation, controller, cache result storage, WorkerRef results, concrete runc/containerd factories, labels, filters, and shared worker tests. Control flow should be read through the listed functions and methods; notable exported or lifecycle symbols are included above. Integration points include solver ops, cache manager, snapshots, content stores, lease managers, executors, source resolvers, exporters, netproviders, CDI, Windows layer wrappers, and client WorkerInfo. Risks center on ref ownership, persistent worker IDs, cleanup, privileged integration tests, and broad interface coupling.

## State, Persistence, Dependencies, Risks, And Test Signals
State and persistence are inferred from symbols and dependencies: globals/types/functions listed above, filesystem/process/network state where the APIs call external daemons or stores, and in-memory closure/mutex/channel state where concurrency helpers are present. Dependencies: BuildKit packages: github.com/moby/buildkit/cache, github.com/moby/buildkit/executor, github.com/moby/buildkit/identity, github.com/moby/buildkit/session, github.com/moby/buildkit/snapshot, github.com/moby/buildkit/source/containerimage, github.com/moby/buildkit/util/iohelper, github.com/moby/buildkit/util/testutil/integration, github.com/moby/buildkit/worker/base; external packages: bytes, context, io, sync, testing, time, github.com/containerd/containerd/v2/pkg/namespaces, github.com/pkg/errors, github.com/stretchr/testify/require, golang.org/x/sync/errgroup. Primary risks are package-specific integration coupling, platform/build-tag behavior where present, cleanup and cancellation boundaries for daemon/executor/tracing code, and stale assumptions in tests or constants. Direct test functions in this file: TestWorkerExec, TestWorkerExecFailures, TestWorkerCancel.

<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/worker/tests/common.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/worker/worker.go -->
# sources/cloud-native/buildkit/worker/worker.go

## Purpose
core BuildKit worker interface or base implementation depending on package path, connecting solver operations to cache, sources, executors, and exporters.

## Important APIs, Types, Functions, Or Configuration
package worker; types ProxyOpt, Worker, Infos.

## Control Flow And Integration Points
The file is 58 lines in worker and participates in this package role: BuildKit worker core. These files define worker interfaces, local worker implementation, controller, cache result storage, WorkerRef results, concrete runc/containerd factories, labels, filters, and shared worker tests. Control flow should be read through the listed functions and methods; notable exported or lifecycle symbols are included above. Integration points include solver ops, cache manager, snapshots, content stores, lease managers, executors, source resolvers, exporters, netproviders, CDI, Windows layer wrappers, and client WorkerInfo. Risks center on ref ownership, persistent worker IDs, cleanup, privileged integration tests, and broad interface coupling.

## State, Persistence, Dependencies, Risks, And Test Signals
State and persistence are inferred from symbols and dependencies: globals/types/functions listed above, filesystem/process/network state where the APIs call external daemons or stores, and in-memory closure/mutex/channel state where concurrency helpers are present. Dependencies: BuildKit packages: github.com/moby/buildkit/cache, github.com/moby/buildkit/client, github.com/moby/buildkit/client/llb/sourceresolver, github.com/moby/buildkit/executor, github.com/moby/buildkit/exporter, github.com/moby/buildkit/frontend, github.com/moby/buildkit/session, github.com/moby/buildkit/snapshot/containerd, github.com/moby/buildkit/solver, github.com/moby/buildkit/solver/llbsolver/cdidevices; external packages: context, io, github.com/opencontainers/image-spec/specs-go/v1. Primary risks are package-specific integration coupling, platform/build-tag behavior where present, cleanup and cancellation boundaries for daemon/executor/tracing code, and stale assumptions in tests or constants. This is production/helper code; test signal comes from adjacent package tests and integration users.

<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/worker/worker.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/worker/workercontroller.go -->
# sources/cloud-native/buildkit/worker/workercontroller.go

## Purpose
implementation file in the adjacent Go package, contributing the symbols and behavior listed below.

## Important APIs, Types, Functions, Or Configuration
package worker; types Controller, infosController; functions/methods Close, Add, List, GetDefault, Get, WorkerInfos, Infos, DefaultCacheManager, WorkerInfos; package vars _.

## Control Flow And Integration Points
The file is 108 lines in worker and participates in this package role: BuildKit worker core. These files define worker interfaces, local worker implementation, controller, cache result storage, WorkerRef results, concrete runc/containerd factories, labels, filters, and shared worker tests. Control flow should be read through the listed functions and methods; notable exported or lifecycle symbols are included above. Integration points include solver ops, cache manager, snapshots, content stores, lease managers, executors, source resolvers, exporters, netproviders, CDI, Windows layer wrappers, and client WorkerInfo. Risks center on ref ownership, persistent worker IDs, cleanup, privileged integration tests, and broad interface coupling.

## State, Persistence, Dependencies, Risks, And Test Signals
State and persistence are inferred from symbols and dependencies: globals/types/functions listed above, filesystem/process/network state where the APIs call external daemons or stores, and in-memory closure/mutex/channel state where concurrency helpers are present. Dependencies: BuildKit packages: github.com/moby/buildkit/cache, github.com/moby/buildkit/client; external packages: errors, github.com/containerd/containerd/v2/pkg/filters, github.com/pkg/errors. Primary risks are package-specific integration coupling, platform/build-tag behavior where present, cleanup and cancellation boundaries for daemon/executor/tracing code, and stale assumptions in tests or constants. This is production/helper code; test signal comes from adjacent package tests and integration users.

<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/worker/workercontroller.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/composefs-rs/.config/nextest.toml -->
# sources/cloud-native/composefs-rs/.config/nextest.toml

## Purpose
cargo-nextest profile configuration for default and VM-heavy integration tests.

## Important APIs, Types, Functions, Or Configuration
TOML sections: [store], [profile.default], [[profile.default.overrides]], [profile.integration], [profile.integration.junit], [[profile.integration.overrides]].

## Control Flow And Integration Points
This .toml file is 47 lines and belongs to this workflow area: composefs-rs repository configuration, CI, container build, devcontainer, packaging, and Cargo manifest material. Integration points include GitHub Actions, cargo/nextest/just, bootc VM tooling, Podman/skopeo, distro package managers, devcontainer tooling, crates.io trusted publishing, and workspace lint/dependency policy. Risks include privileged/KVM/fs-verity assumptions, external image/action availability, distro differences, and publication workflow scope.

## State, Persistence, Dependencies, Risks, And Test Signals
State is held in the consuming tool: GitHub Actions runner state, Cargo workspace resolution, container image layers, package-manager databases, devcontainer runtime settings, or automation review settings depending on file type. Risks include drift between CI/devcontainer/container images and source requirements, privileged or networked runtime assumptions, external action/image/package availability, and release/publish blast radius for workflow files.

<!-- END_FILE_RESEARCH: sources/cloud-native/composefs-rs/.config/nextest.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/composefs-rs/.devcontainer/debian/devcontainer.json -->
# sources/cloud-native/composefs-rs/.devcontainer/debian/devcontainer.json

## Purpose
configuration or script file supporting the adjacent project workflow.

## Important APIs, Types, Functions, Or Configuration
JSON top-level keys: name, image, customizations, features, privileged, postCreateCommand, remoteEnv.

## Control Flow And Integration Points
This .json file is 31 lines and belongs to this workflow area: composefs-rs repository configuration, CI, container build, devcontainer, packaging, and Cargo manifest material. Integration points include GitHub Actions, cargo/nextest/just, bootc VM tooling, Podman/skopeo, distro package managers, devcontainer tooling, crates.io trusted publishing, and workspace lint/dependency policy. Risks include privileged/KVM/fs-verity assumptions, external image/action availability, distro differences, and publication workflow scope.

## State, Persistence, Dependencies, Risks, And Test Signals
State is held in the consuming tool: GitHub Actions runner state, Cargo workspace resolution, container image layers, package-manager databases, devcontainer runtime settings, or automation review settings depending on file type. Risks include drift between CI/devcontainer/container images and source requirements, privileged or networked runtime assumptions, external action/image/package availability, and release/publish blast radius for workflow files.

<!-- END_FILE_RESEARCH: sources/cloud-native/composefs-rs/.devcontainer/debian/devcontainer.json -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/composefs-rs/.devcontainer/devcontainer.json -->
# sources/cloud-native/composefs-rs/.devcontainer/devcontainer.json

## Purpose
configuration or script file supporting the adjacent project workflow.

## Important APIs, Types, Functions, Or Configuration
JSON top-level keys: name, image, customizations, features, privileged, postCreateCommand, remoteEnv.

## Control Flow And Integration Points
This .json file is 31 lines and belongs to this workflow area: composefs-rs repository configuration, CI, container build, devcontainer, packaging, and Cargo manifest material. Integration points include GitHub Actions, cargo/nextest/just, bootc VM tooling, Podman/skopeo, distro package managers, devcontainer tooling, crates.io trusted publishing, and workspace lint/dependency policy. Risks include privileged/KVM/fs-verity assumptions, external image/action availability, distro differences, and publication workflow scope.

## State, Persistence, Dependencies, Risks, And Test Signals
State is held in the consuming tool: GitHub Actions runner state, Cargo workspace resolution, container image layers, package-manager databases, devcontainer runtime settings, or automation review settings depending on file type. Risks include drift between CI/devcontainer/container images and source requirements, privileged or networked runtime assumptions, external action/image/package availability, and release/publish blast radius for workflow files.

<!-- END_FILE_RESEARCH: sources/cloud-native/composefs-rs/.devcontainer/devcontainer.json -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/composefs-rs/.devcontainer/ubuntu/devcontainer.json -->
# sources/cloud-native/composefs-rs/.devcontainer/ubuntu/devcontainer.json

## Purpose
configuration or script file supporting the adjacent project workflow.

## Important APIs, Types, Functions, Or Configuration
JSON top-level keys: name, image, customizations, features, privileged, postCreateCommand, remoteEnv.

## Control Flow And Integration Points
This .json file is 31 lines and belongs to this workflow area: composefs-rs repository configuration, CI, container build, devcontainer, packaging, and Cargo manifest material. Integration points include GitHub Actions, cargo/nextest/just, bootc VM tooling, Podman/skopeo, distro package managers, devcontainer tooling, crates.io trusted publishing, and workspace lint/dependency policy. Risks include privileged/KVM/fs-verity assumptions, external image/action availability, distro differences, and publication workflow scope.

## State, Persistence, Dependencies, Risks, And Test Signals
State is held in the consuming tool: GitHub Actions runner state, Cargo workspace resolution, container image layers, package-manager databases, devcontainer runtime settings, or automation review settings depending on file type. Risks include drift between CI/devcontainer/container images and source requirements, privileged or networked runtime assumptions, external action/image/package availability, and release/publish blast radius for workflow files.

<!-- END_FILE_RESEARCH: sources/cloud-native/composefs-rs/.devcontainer/ubuntu/devcontainer.json -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/composefs-rs/.gemini/config.yaml -->
# sources/cloud-native/composefs-rs/.gemini/config.yaml

## Purpose
configuration or script file supporting the adjacent project workflow.

## Important APIs, Types, Functions, Or Configuration
Workflow/config keys include jobs or sections: pull_request_opened.

## Control Flow And Integration Points
This .yaml file is 20 lines and belongs to this workflow area: composefs-rs repository configuration, CI, container build, devcontainer, packaging, and Cargo manifest material. Integration points include GitHub Actions, cargo/nextest/just, bootc VM tooling, Podman/skopeo, distro package managers, devcontainer tooling, crates.io trusted publishing, and workspace lint/dependency policy. Risks include privileged/KVM/fs-verity assumptions, external image/action availability, distro differences, and publication workflow scope.

## State, Persistence, Dependencies, Risks, And Test Signals
State is held in the consuming tool: GitHub Actions runner state, Cargo workspace resolution, container image layers, package-manager databases, devcontainer runtime settings, or automation review settings depending on file type. Risks include drift between CI/devcontainer/container images and source requirements, privileged or networked runtime assumptions, external action/image/package availability, and release/publish blast radius for workflow files.

<!-- END_FILE_RESEARCH: sources/cloud-native/composefs-rs/.gemini/config.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/composefs-rs/.github/workflows/bootc-revdep.yml -->
# sources/cloud-native/composefs-rs/.github/workflows/bootc-revdep.yml

## Purpose
configuration or script file supporting the adjacent project workflow.

## Important APIs, Types, Functions, Or Configuration
Workflow/config keys include jobs or sections: push, pull_request, merge_group, bootc-test.

## Control Flow And Integration Points
This .yml file is 52 lines and belongs to this workflow area: composefs-rs repository configuration, CI, container build, devcontainer, packaging, and Cargo manifest material. Integration points include GitHub Actions, cargo/nextest/just, bootc VM tooling, Podman/skopeo, distro package managers, devcontainer tooling, crates.io trusted publishing, and workspace lint/dependency policy. Risks include privileged/KVM/fs-verity assumptions, external image/action availability, distro differences, and publication workflow scope.

## State, Persistence, Dependencies, Risks, And Test Signals
State is held in the consuming tool: GitHub Actions runner state, Cargo workspace resolution, container image layers, package-manager databases, devcontainer runtime settings, or automation review settings depending on file type. Risks include drift between CI/devcontainer/container images and source requirements, privileged or networked runtime assumptions, external action/image/package availability, and release/publish blast radius for workflow files.

<!-- END_FILE_RESEARCH: sources/cloud-native/composefs-rs/.github/workflows/bootc-revdep.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/composefs-rs/.github/workflows/ci.yml -->
# sources/cloud-native/composefs-rs/.github/workflows/ci.yml

## Purpose
main composefs-rs CI workflow covering package checks, Fedora checks, smoke tests, fuzzing, VM integration, examples, and a required sentinel job.

## Important APIs, Types, Functions, Or Configuration
Workflow/config keys include jobs or sections: push, pull_request, merge_group, nightly, fedora, smoke, fuzz, integration, examples, required-checks.

## Control Flow And Integration Points
This .yml file is 231 lines and belongs to this workflow area: composefs-rs repository configuration, CI, container build, devcontainer, packaging, and Cargo manifest material. Integration points include GitHub Actions, cargo/nextest/just, bootc VM tooling, Podman/skopeo, distro package managers, devcontainer tooling, crates.io trusted publishing, and workspace lint/dependency policy. Risks include privileged/KVM/fs-verity assumptions, external image/action availability, distro differences, and publication workflow scope.

## State, Persistence, Dependencies, Risks, And Test Signals
State is held in the consuming tool: GitHub Actions runner state, Cargo workspace resolution, container image layers, package-manager databases, devcontainer runtime settings, or automation review settings depending on file type. Risks include drift between CI/devcontainer/container images and source requirements, privileged or networked runtime assumptions, external action/image/package availability, and release/publish blast radius for workflow files.

<!-- END_FILE_RESEARCH: sources/cloud-native/composefs-rs/.github/workflows/ci.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/composefs-rs/.github/workflows/mirror-fixture-images.yml -->
# sources/cloud-native/composefs-rs/.github/workflows/mirror-fixture-images.yml

## Purpose
configuration or script file supporting the adjacent project workflow.

## Important APIs, Types, Functions, Or Configuration
Workflow/config keys include jobs or sections: push, mirror.

## Control Flow And Integration Points
This .yml file is 40 lines and belongs to this workflow area: composefs-rs repository configuration, CI, container build, devcontainer, packaging, and Cargo manifest material. Integration points include GitHub Actions, cargo/nextest/just, bootc VM tooling, Podman/skopeo, distro package managers, devcontainer tooling, crates.io trusted publishing, and workspace lint/dependency policy. Risks include privileged/KVM/fs-verity assumptions, external image/action availability, distro differences, and publication workflow scope.

## State, Persistence, Dependencies, Risks, And Test Signals
State is held in the consuming tool: GitHub Actions runner state, Cargo workspace resolution, container image layers, package-manager databases, devcontainer runtime settings, or automation review settings depending on file type. Risks include drift between CI/devcontainer/container images and source requirements, privileged or networked runtime assumptions, external action/image/package availability, and release/publish blast radius for workflow files.

<!-- END_FILE_RESEARCH: sources/cloud-native/composefs-rs/.github/workflows/mirror-fixture-images.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/composefs-rs/.github/workflows/publish.yml -->
# sources/cloud-native/composefs-rs/.github/workflows/publish.yml

## Purpose
configuration or script file supporting the adjacent project workflow.

## Important APIs, Types, Functions, Or Configuration
Workflow/config keys include jobs or sections: push, publish.

## Control Flow And Integration Points
This .yml file is 20 lines and belongs to this workflow area: composefs-rs repository configuration, CI, container build, devcontainer, packaging, and Cargo manifest material. Integration points include GitHub Actions, cargo/nextest/just, bootc VM tooling, Podman/skopeo, distro package managers, devcontainer tooling, crates.io trusted publishing, and workspace lint/dependency policy. Risks include privileged/KVM/fs-verity assumptions, external image/action availability, distro differences, and publication workflow scope.

## State, Persistence, Dependencies, Risks, And Test Signals
State is held in the consuming tool: GitHub Actions runner state, Cargo workspace resolution, container image layers, package-manager databases, devcontainer runtime settings, or automation review settings depending on file type. Risks include drift between CI/devcontainer/container images and source requirements, privileged or networked runtime assumptions, external action/image/package availability, and release/publish blast radius for workflow files.

<!-- END_FILE_RESEARCH: sources/cloud-native/composefs-rs/.github/workflows/publish.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/composefs-rs/Cargo.toml -->
# sources/cloud-native/composefs-rs/Cargo.toml

## Purpose
Cargo manifest defining either the composefs-rs workspace or a crate dependency/lint contract.

## Important APIs, Types, Functions, Or Configuration
TOML sections: [workspace], [workspace.package], [workspace.lints.rust], [workspace.dependencies], [profile.dev.package.sha2], [profile.profiling], [workspace.metadata.vendor-filter].

## Control Flow And Integration Points
This .toml file is 62 lines and belongs to this workflow area: composefs-rs repository configuration, CI, container build, devcontainer, packaging, and Cargo manifest material. Integration points include GitHub Actions, cargo/nextest/just, bootc VM tooling, Podman/skopeo, distro package managers, devcontainer tooling, crates.io trusted publishing, and workspace lint/dependency policy. Risks include privileged/KVM/fs-verity assumptions, external image/action availability, distro differences, and publication workflow scope.

## State, Persistence, Dependencies, Risks, And Test Signals
State is held in the consuming tool: GitHub Actions runner state, Cargo workspace resolution, container image layers, package-manager databases, devcontainer runtime settings, or automation review settings depending on file type. Risks include drift between CI/devcontainer/container images and source requirements, privileged or networked runtime assumptions, external action/image/package availability, and release/publish blast radius for workflow files.

<!-- END_FILE_RESEARCH: sources/cloud-native/composefs-rs/Cargo.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/composefs-rs/Containerfile -->
# sources/cloud-native/composefs-rs/Containerfile

## Purpose
multi-stage bootc-compatible composefs-rs test image build that compiles cfsctl/integration tests and installs runtime VM test dependencies.

## Important APIs, Types, Functions, Or Configuration
Container stages: scratch AS src, ${base_image} AS build, ${base_image}; RUN instructions: 4..

## Control Flow And Integration Points
This Containerfile file is 59 lines and belongs to this workflow area: composefs-rs repository configuration, CI, container build, devcontainer, packaging, and Cargo manifest material. Integration points include GitHub Actions, cargo/nextest/just, bootc VM tooling, Podman/skopeo, distro package managers, devcontainer tooling, crates.io trusted publishing, and workspace lint/dependency policy. Risks include privileged/KVM/fs-verity assumptions, external image/action availability, distro differences, and publication workflow scope.

## State, Persistence, Dependencies, Risks, And Test Signals
State is held in the consuming tool: GitHub Actions runner state, Cargo workspace resolution, container image layers, package-manager databases, devcontainer runtime settings, or automation review settings depending on file type. Risks include drift between CI/devcontainer/container images and source requirements, privileged or networked runtime assumptions, external action/image/package availability, and release/publish blast radius for workflow files.

<!-- END_FILE_RESEARCH: sources/cloud-native/composefs-rs/Containerfile -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/composefs-rs/contrib/packaging/install-build-deps.sh -->
# sources/cloud-native/composefs-rs/contrib/packaging/install-build-deps.sh

## Purpose
configuration or script file supporting the adjacent project workflow.

## Important APIs, Types, Functions, Or Configuration
Shell functions: none; distro case labels: centos|fedora|rhel, debian|ubuntu.

## Control Flow And Integration Points
This .sh file is 34 lines and belongs to this workflow area: composefs-rs repository configuration, CI, container build, devcontainer, packaging, and Cargo manifest material. Integration points include GitHub Actions, cargo/nextest/just, bootc VM tooling, Podman/skopeo, distro package managers, devcontainer tooling, crates.io trusted publishing, and workspace lint/dependency policy. Risks include privileged/KVM/fs-verity assumptions, external image/action availability, distro differences, and publication workflow scope.

## State, Persistence, Dependencies, Risks, And Test Signals
State is held in the consuming tool: GitHub Actions runner state, Cargo workspace resolution, container image layers, package-manager databases, devcontainer runtime settings, or automation review settings depending on file type. Risks include drift between CI/devcontainer/container images and source requirements, privileged or networked runtime assumptions, external action/image/package availability, and release/publish blast radius for workflow files.

<!-- END_FILE_RESEARCH: sources/cloud-native/composefs-rs/contrib/packaging/install-build-deps.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/composefs-rs/contrib/packaging/install-test-deps.sh -->
# sources/cloud-native/composefs-rs/contrib/packaging/install-test-deps.sh

## Purpose
configuration or script file supporting the adjacent project workflow.

## Important APIs, Types, Functions, Or Configuration
Shell functions: none; distro case labels: centos|fedora|rhel, debian|ubuntu.

## Control Flow And Integration Points
This .sh file is 52 lines and belongs to this workflow area: composefs-rs repository configuration, CI, container build, devcontainer, packaging, and Cargo manifest material. Integration points include GitHub Actions, cargo/nextest/just, bootc VM tooling, Podman/skopeo, distro package managers, devcontainer tooling, crates.io trusted publishing, and workspace lint/dependency policy. Risks include privileged/KVM/fs-verity assumptions, external image/action availability, distro differences, and publication workflow scope.

## State, Persistence, Dependencies, Risks, And Test Signals
State is held in the consuming tool: GitHub Actions runner state, Cargo workspace resolution, container image layers, package-manager databases, devcontainer runtime settings, or automation review settings depending on file type. Risks include drift between CI/devcontainer/container images and source requirements, privileged or networked runtime assumptions, external action/image/package availability, and release/publish blast radius for workflow files.

<!-- END_FILE_RESEARCH: sources/cloud-native/composefs-rs/contrib/packaging/install-test-deps.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/composefs-rs/contrib/packaging/lib.sh -->
# sources/cloud-native/composefs-rs/contrib/packaging/lib.sh

## Purpose
configuration or script file supporting the adjacent project workflow.

## Important APIs, Types, Functions, Or Configuration
Shell functions: debian_apt_init, pkg_install; distro case labels: centos|fedora|rhel, debian|ubuntu.

## Control Flow And Integration Points
This .sh file is 51 lines and belongs to this workflow area: composefs-rs repository configuration, CI, container build, devcontainer, packaging, and Cargo manifest material. Integration points include GitHub Actions, cargo/nextest/just, bootc VM tooling, Podman/skopeo, distro package managers, devcontainer tooling, crates.io trusted publishing, and workspace lint/dependency policy. Risks include privileged/KVM/fs-verity assumptions, external image/action availability, distro differences, and publication workflow scope.

## State, Persistence, Dependencies, Risks, And Test Signals
State is held in the consuming tool: GitHub Actions runner state, Cargo workspace resolution, container image layers, package-manager databases, devcontainer runtime settings, or automation review settings depending on file type. Risks include drift between CI/devcontainer/container images and source requirements, privileged or networked runtime assumptions, external action/image/package availability, and release/publish blast radius for workflow files.

<!-- END_FILE_RESEARCH: sources/cloud-native/composefs-rs/contrib/packaging/lib.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/composefs-rs/crates/composefs-boot/Cargo.toml -->
# sources/cloud-native/composefs-rs/crates/composefs-boot/Cargo.toml

## Purpose
Cargo manifest defining either the composefs-rs workspace or a crate dependency/lint contract.

## Important APIs, Types, Functions, Or Configuration
TOML sections: [package], [dependencies], [dev-dependencies], [lints].

## Control Flow And Integration Points
This .toml file is 30 lines and belongs to this workflow area: composefs-rs repository configuration, CI, container build, devcontainer, packaging, and Cargo manifest material. Integration points include GitHub Actions, cargo/nextest/just, bootc VM tooling, Podman/skopeo, distro package managers, devcontainer tooling, crates.io trusted publishing, and workspace lint/dependency policy. Risks include privileged/KVM/fs-verity assumptions, external image/action availability, distro differences, and publication workflow scope.

## State, Persistence, Dependencies, Risks, And Test Signals
State is held in the consuming tool: GitHub Actions runner state, Cargo workspace resolution, container image layers, package-manager databases, devcontainer runtime settings, or automation review settings depending on file type. Risks include drift between CI/devcontainer/container images and source requirements, privileged or networked runtime assumptions, external action/image/package availability, and release/publish blast radius for workflow files.

<!-- END_FILE_RESEARCH: sources/cloud-native/composefs-rs/crates/composefs-boot/Cargo.toml -->
