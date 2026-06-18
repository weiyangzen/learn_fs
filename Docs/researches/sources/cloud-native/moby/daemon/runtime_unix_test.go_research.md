# sources/cloud-native/moby/daemon/runtime_unix_test.go

## Purpose
Tests non-Windows runtime configuration, runtime resolution, preflight behavior, and wrapper-script stability.

## Important APIs, Types, And Functions
Tests call `config.New`, `initRuntimesDir`, `setupRuntimes`, `runtimes.Get`, and inspect `runcoptions.Options`/runtime option protobufs. `mergo` overlays test configs onto defaults.

## Control Flow
`TestSetupRuntimes` runs invalid and valid configuration cases. `TestGetRuntime` builds configured path, args, shim, shim-by-path, and gVisor option runtimes, then verifies resolved shim/options or invalid-argument errors. `TestGetRuntime_PreflightCheck` asserts only wrapper-script runtimes check binary existence. `TestRuntimeWrapping` records wrapper scripts, changes runtime config, reruns setup, and verifies old wrappers remain untouched.

## State And Persistence
Tests create temporary daemon roots and runtime script directories. Wrapper files are written and read from disk to verify content and immutability.

## Dependencies And Integration Points
Uses containerd runtime option types, Moby system runtime API types, protobuf cloning, filesystem errors, and gotest/cmp assertions. It validates behavior consumed by daemon start and reload paths.

## Risks And Edge Cases
The tests intentionally allow configured runtime names with slashes while rejecting path-like implicit runtime names. They depend on `/bin/true` and `/bin/false` for wrapper content cases.

## Test Signals
Passing tests confirm reserved runtime protection, argument/type/options compatibility rules, shim option decoding, invalid runtime name rejection, wrapper hashing, and persistence of wrapper scripts for existing containers.
