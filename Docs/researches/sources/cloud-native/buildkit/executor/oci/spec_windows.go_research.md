# Research: sources/cloud-native/buildkit/executor/oci/spec_windows.go

## Purpose
Windows OCI spec helper implementation.

## Important APIs, Types, and Functions
Windows process command-line, user-info mount, platform stubs, tracing mount, submount, and mount type normalization helpers.

## Control Flow
Adapts common spec generation to Windows command-line and mount semantics.

## State and Persistence
Transient spec/mount state only.

## Dependencies and Integration Points
Depends on containerd OCI and Windows runtime-spec fields. Used by Windows containerd executor.

## Risks and Edge Cases
Command-line quoting and Linux-feature omissions are key risks.

## Test Signals
Windows build/integration tests.
