# Research: sources/cloud-native/buildkit/executor/containerdexecutor/executor_unix.go

## Purpose
Unix-specific containerd executor environment setup.

## Important APIs, Types, and Functions
`getUserSpec`, `prepareExecutionEnv`, `ensureCWD`, `createOCISpec`, `getTaskOpts`, `setArgs`.

## Control Flow
Mounts root snapshot, writes hosts/resolv, creates CWD with mapped ownership, resolves user/group, calls `oci.GenerateSpec`, applies rootfs and TTY settings.

## State and Persistence
Transient mount state and generated host resolver files under executor root.

## Dependencies and Integration Points
Depends on containerd mounts, BuildKit OCI helpers, user identity mapping, and Unix FS semantics. Provides the Unix half of containerd executor execution.

## Risks and Edge Cases
Mount release, CWD creation, and user lookup inside rootfs are sensitive.

## Test Signals
Covered by integration more than unit tests.
