# sources/cloud-native/containerd/internal/cri/server/container_status_test.go

## Purpose
This test file validates CRI status conversion, image reference behavior, verbose-info disabling, stop-signal conversion, and supporting fakes for container/image services.

## Important APIs, Types, and Functions
Tests include `TestToCRIContainerStatus`, `TestToCRIContainerInfo`, `TestContainerStatus`, and `TestToCRISignal`. Helpers/fakes include `getContainerStatusTestData`, `fakeImageService`, `patchExceptedWithState`, and `fakeSpecOnlyContainer`.

## Control Flow, State, and Persistence
The tests create fake container metadata/status, fake image references with both tag and digest, and fake container specs. They call conversion functions and the `ContainerStatus` RPC wrapper, then compare exact CRI status output. `TestToCRISignal` covers standard and real-time signal names, plus fallback for unknown strings.

## Dependencies and Integration Points
It exercises container store, image store, runtime-spec fakes, snapshot/image service interface shape, CRI status fields, and stop-signal conversion used by status responses.

## Risks and Test Signals
Signals are exact state/timestamp/reason mapping, image tag/digest/config-digest semantics, and broad signal name coverage. Gaps include verbose true JSON serialization and live containerd spec/info failures.
