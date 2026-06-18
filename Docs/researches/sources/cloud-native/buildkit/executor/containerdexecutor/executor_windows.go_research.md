# Research: sources/cloud-native/buildkit/executor/containerdexecutor/executor_windows.go

## Purpose
Windows-specific containerd executor support.

## Important APIs, Types, and Functions
Windows variants of user lookup, environment prep, CWD check, spec creation, task opts, and argument setting.

## Control Flow
Stores root mounts, adapts command-line process fields, and delegates to Windows OCI spec helpers.

## State and Persistence
Transient containerd/root mount state.

## Dependencies and Integration Points
Depends on Windows containerd task/spec semantics. Allows the executor interface to support Windows containers.

## Risks and Edge Cases
Path, command-line quoting, and user identity differences are key risks.

## Test Signals
Windows integration/build tests are required.
