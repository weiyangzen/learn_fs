# Research: sources/cloud-native/buildkit/executor/oci/user.go

## Purpose
User/group resolution helpers for OCI process specs.

## Important APIs, Types, and Functions
`GetUser`, `ParseUIDGID`, `openUserFile`, `parseUID`, `WithUIDGID`, `setProcess`, `ensureAdditionalGids`.

## Control Flow
Reads passwd/group data in rootfs, parses numeric/user forms, and mutates OCI process user fields.

## State and Persistence
No durable state; reads rootfs and mutates in-memory specs.

## Dependencies and Integration Points
Depends on `moby/sys/user`, containerd OCI, and runtime-spec user fields. Used by runc/containerd run and exec process setup.

## Risks and Edge Cases
Rootfs path safety, malformed users, and missing group files are edge cases.

## Test Signals
Indirect executor coverage.
