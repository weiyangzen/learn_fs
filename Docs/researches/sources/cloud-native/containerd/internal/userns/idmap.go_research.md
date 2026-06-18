# sources/cloud-native/containerd/internal/userns/idmap.go

## Purpose
Handles user-namespace UID/GID mapping translation and string serialization.

## Important APIs, Types, And Functions
`User` stores UID/GID. `IDMap` stores OCI `LinuxIDMapping` slices. `RootPair`, `ToHost`, `Marshal`, and `Unmarshal` are methods. Helpers include `toHost`, `safeSum`, `serializeLinuxIDMapping`, and `deserializeLinuxIDMapping`.

## Control Flow
Mapping translation finds the mapping range containing a container ID, checks overflow, and computes host ID. Nil maps mean identity mapping. Marshal joins `container:host:size` entries; Unmarshal splits comma-separated strings and appends parsed mappings.

## State And Persistence
`IDMap` holds in-memory mapping slices that can be serialized to strings for metadata/config storage.

## Dependencies And Integration Points
Uses OCI runtime spec Linux ID mappings. It is copied/customized from Moby idtools.

## Risks
`Unmarshal` appends to existing slices rather than clearing them. Zero-size mappings deserialize successfully but map no IDs. Overflow handling returns sentinel invalid IDs.

## Test Signals
`idmap_test.go` covers root mapping, host translation, overflow, marshal/unmarshal, invalid strings, and identity mapping.
