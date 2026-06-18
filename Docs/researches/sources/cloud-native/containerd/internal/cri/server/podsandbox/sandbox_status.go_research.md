# sources/cloud-native/containerd/internal/cri/server/podsandbox/sandbox_status.go

## Purpose

This file implements controller-level sandbox status and verbose CRI sandbox info construction.

## Important APIs, Types, and Functions

`Status` returns `sandbox.ControllerStatus` from the in-memory `PodSandbox` status. `toCRISandboxInfo` builds a JSON-encoded `types.SandboxInfo` map including PID, config, CNI result, task status, runtime spec, image, snapshot metadata, runtime options, and network namespace closed state. `getRuntimeOptions` unpacks runtime options from container metadata.

## Control Flow

Status lookup fails with not-found when the sandbox is absent. Verbose info optionally loads task status, spec, container info, and runtime options, tolerating task not-found as deleted status but propagating other errors.

## State and Persistence Behavior

The file reads in-memory sandbox status and containerd metadata/spec/task state. It does not mutate state.

## Dependencies and Integration Points

It integrates with containerd container/task APIs, typeurl runtime options, netns status checks, and CRI verbose `info` JSON expected by kubelet clients.

## Risks and Test Signals

Verbose status can fail if container spec/info retrieval fails or netns closed checks error. Tests cover basic non-verbose status; verbose behavior needs integration coverage.
