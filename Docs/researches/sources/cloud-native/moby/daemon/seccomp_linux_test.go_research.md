# sources/cloud-native/moby/daemon/seccomp_linux_test.go

## Purpose
Tests Linux seccomp OCI spec mutation across privilege, daemon profile, container profile, and kernel-support combinations.

## Important APIs, Types, And Functions
`TestWithSeccomp` builds table cases with `Daemon`, `container.Container`, input/output `coci.Spec`, and expected errors. It calls `WithSeccomp` and compares against specs built from `oci.DefaultLinuxSpec` and Moby seccomp profiles.

## Control Flow
Each case constructs a daemon sysinfo and container host config, invokes the returned `SpecOpts`, then asserts the mutated spec and error. Cases verify unconfined, privileged custom profile, privileged default, privileged daemon profile ignored, disabled kernel custom error, default profile, container profile, daemon profile, and container-over-daemon priority.

## State And Persistence
Only in-memory specs and container structs are mutated. No seccomp files are loaded from disk; custom profiles are inline JSON strings.

## Dependencies And Integration Points
Depends on containerd OCI spec types, daemon OCI helper defaults, sysinfo, Moby profiles/seccomp, and gotest assertions.

## Risks And Edge Cases
Spec equality depends on default profile generation remaining stable. The tests focus on JSON minimal profiles and do not cover profile file paths or malformed profile strings.

## Test Signals
Passing tests confirm profile precedence, privileged-mode semantics, error behavior when kernel seccomp is unavailable, and default profile attachment.
