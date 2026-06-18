# sources/cloud-native/buildkit/util/testutil/integration/run.go

## Purpose
central integration test runner: registers workers, builds matrix subtests, mirrors images, creates sandboxes, enforces parallelism, and prints daemon logs on failure.

## Important APIs, Types, Functions, Or Configuration
package integration; types Backend, Sandbox, BackendConfig, Worker, ConfigUpdater, Test, testFunc, TestOpt, testConf, mirrorConfig, Mirror, matrixValue; functions/methods init, Name, Run, TestFuncs, Register, List, WithMatrix, WithMirroredImages, Run, getFunctionName, copyImagesLocal, resolveDefaultPlatform, OfficialImages, withMirrorConfig, UpdateConfigFile, WriteConfig, lazyMirrorRunnerFunc, lock, Close, AddImages, RunMirror, functionSuffix, newMatrixValue, prepareValueMatrix; package vars sandboxLimiter, defaultWorkers, localImageCache, localImageCacheMu; tests TestFuncs.

## Control Flow And Integration Points
The file is 599 lines in integration and participates in this package role: BuildKit integration-test harness code. It launches real daemons, registries, sockets/pipes, mirrors, and buildctl commands, so correctness depends on cleanup ordering, environment variables, external binaries, and platform-specific socket behavior. Control flow should be read through the listed functions and methods; notable exported or lifecycle symbols are included above. Integration points include buildkitd, buildctl, registry, containerd/dockerd/OCI worker factories, image mirrors, ConfigUpdater TOML fragments, testing.T cleanup, and feature skip helpers. Test signals are mostly downstream integration tests rather than narrow unit tests.

## State, Persistence, Dependencies, Risks, And Test Signals
State and persistence are inferred from symbols and dependencies: globals/types/functions listed above, filesystem/process/network state where the APIs call external daemons or stores, and in-memory closure/mutex/channel state where concurrency helpers are present. Dependencies: BuildKit packages: github.com/moby/buildkit/util/appcontext, github.com/moby/buildkit/util/contentutil; external packages: bytes, context, fmt, maps, math, math/rand, os, os/exec, path/filepath, reflect, runtime, slices. Primary risks are package-specific integration coupling, platform/build-tag behavior where present, cleanup and cancellation boundaries for daemon/executor/tracing code, and stale assumptions in tests or constants. Direct test functions in this file: TestFuncs.
