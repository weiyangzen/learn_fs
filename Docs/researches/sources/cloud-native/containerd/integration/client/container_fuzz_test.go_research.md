<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/integration/client/container_fuzz_test.go -->
# sources/cloud-native/containerd/integration/client/container_fuzz_test.go

## Purpose
Defines integration fuzzers that exercise containerd daemon startup, OCI image import, image metadata operations, unpacking, and container creation through the public Go client. The fuzzers are aimed at OSS-Fuzz and compare two daemon lifecycle modes: keeping one daemon across iterations versus tearing the daemon down after each iteration.

## APIs, Types, And Functions
The key helpers are `downloadFile`, `initInSteps`, `updatePathEnv`, `startDaemon`, `tearDown`, `checkIfShouldRestart`, `deleteSocket`, `checkAndDoUnpack`, `getImage`, `newContainer`, and `doFuzz`. The exported fuzz entry points are `FuzzIntegNoTearDownWithDownload`, `FuzzIntegCreateContainerNoTearDown`, and `FuzzIntegCreateContainerWithTearDown`. They depend on `github.com/AdaLogics/go-fuzz-headers` for bounded generation of tar archives, strings, integers, booleans, and OCI specs.

## Control Flow And State
Initialization state is held in package booleans that gate download, extraction, and PATH mutation. `doFuzz` starts the package-level `ctrd` daemon if needed, opens a client on `defaultAddress`, imports up to 30 fuzz-generated tar streams, lists images, and creates up to 50 fuzz-selected containers from either a fuzzed spec alone, an image plus fuzzed spec, or an image alone. Successful containers are deferred for deletion with snapshot cleanup. The download fuzzer spreads binary download, extraction, and PATH setup across iterations to avoid OSS-Fuzz iteration timeouts.

## Persistence And Integration Points
The fuzzer mutates `/tmp/containerd-2.0.1-linux-amd64.tar.gz`, `/tmp/containerd-binaries`, `/out/containerd-binaries`, `defaultRoot`, `defaultState`, and the containerd socket. It exercises containerd import, image listing, image size, unpack, and `NewContainer` paths against a live daemon launched with the shim debug config.

## Risks And Test Signals
The main risks are global process state, stale sockets, network-dependent binary download, unchecked generated OCI structures, and daemon data accumulation when teardown is disabled. Failures that mention a dead daemon trigger socket deletion so later iterations can recover. Useful signals are panics, fatal daemon-start errors, crashes in import/unpack/container creation, and behavioral differences between teardown modes.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/integration/client/container_fuzz_test.go -->
