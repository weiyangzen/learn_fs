# sources/cloud-native/containerd/internal/cri/server/podsandbox/sandbox_run_test.go

## Purpose

This shared test file validates platform-neutral sandbox spec behavior and typeurl metadata round-tripping.

## Important APIs, Types, and Functions

`TestEmpty` registers the root-required flag for all platforms. `TestSandboxContainerSpec` checks empty entrypoint/cmd errors and OCI passthrough annotation filtering, including wildcard matching. `TestTypeurlMarshalUnmarshalSandboxMeta` verifies `sandboxstore.Metadata` can be marshaled and unmarshaled through typeurl with original and Linux-enriched configs.

## Control Flow

The spec test obtains platform-specific baseline config from `getRunPodSandboxTestData`, applies case mutations, calls `sandboxContainerSpec`, then runs shared and case-specific assertions.

## State and Persistence Behavior

No real sandbox state is created. Metadata serialization exercises in-memory protobuf/typeurl representation that is also used for persisted container extensions.

## Dependencies and Integration Points

It integrates with platform-specific test helper files, CRI annotations, sandbox metadata, and typeurl registration.

## Risks and Test Signals

The tests catch annotation pass-through and metadata compatibility regressions. They skip some unsupported OSes and do not start real tasks.
