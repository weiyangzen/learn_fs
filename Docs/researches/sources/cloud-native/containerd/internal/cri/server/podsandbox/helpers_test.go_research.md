# sources/cloud-native/containerd/internal/cri/server/podsandbox/helpers_test.go

## Purpose

This cross-platform test file covers generic OCI environment deduplication behavior and basic sandbox directory removal behavior.

## Important APIs, Types, and Functions

`TestEnvDeduplication` applies repeated `oci.WithEnv` options and verifies later values override earlier ones while preserving stable order. `TestEnsureRemoveAllNotExist`, `TestEnsureRemoveAllWithDir`, and `TestEnsureRemoveAllWithFile` validate that `ensureRemoveAll` tolerates missing paths and removes directories or files.

## Control Flow

The environment test constructs a runtime spec, applies options in sequence, and compares the final `Process.Env`. Removal tests call the platform-specific `ensureRemoveAll` through the common symbol.

## State and Persistence Behavior

Only temporary files and directories are created and removed. No containerd state is used.

## Dependencies and Integration Points

It depends on OCI spec options and the platform-selected `ensureRemoveAll` implementation.

## Risks and Test Signals

The tests catch regressions in env override semantics and basic cleanup behavior. They do not cover Linux mount-specific cleanup except through the Linux-only test.
