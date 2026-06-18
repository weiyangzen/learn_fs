# Research: sources/cloud-native/buildkit/executor/oci/hosts.go

## Purpose
OCI `/etc/hosts` generator.

## Important APIs, Types, and Functions
`GetHostsFile`, `makeHostsFile`, `initHostsFile`.

## Control Flow
Writes localhost/default hostname plus `ExtraHosts`, applies idmapped ownership, and returns a cleanup function.

## State and Persistence
Temporary hosts file under executor root.

## Dependencies and Integration Points
Depends on `os.Root`, id mapping, and executor host metadata. Used before spec generation mounts `/etc/hosts`.

## Risks and Edge Cases
Hostname and extra-host formatting plus cleanup failures affect networking.

## Test Signals
Covered indirectly by executor tests.
