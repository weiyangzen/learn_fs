# sources/cloud-native/nydus/contrib/nydusify/pkg/backend/registry_test.go

## Purpose
This file tests registry backend upload behavior, helper methods, constructor behavior, and expected panics for unimplemented readers.

## Important APIs, Types, and Functions
Tests cover `Registry.Upload`, `Finalize`, `Check`, `Type`, `RangeReader`, `Reader`, `Size`, and `newRegistryBackend`. They use `gomonkey` to patch `remote.Remote.Push`.

## Control Flow
Upload tests create a temporary blob file, patch `Push` to validate descriptor and reader content, then assert returned descriptor metadata. Failure tests cover missing file and push error. Panic tests assert direct reader methods panic.

## State, Persistence, and Dependencies
Tests use temp files and monkeypatch the remote type. No network registry is contacted. Dependencies include digest, OCI descriptors, `testify/require`, and gomonkey.

## Integration Points
These tests guard the registry backend contract used by cache and converter code.

## Risks and Test Signals
The tests intentionally encode that read methods panic and `Check` is optimistic. They do not validate actual registry resolver behavior or retry semantics.
