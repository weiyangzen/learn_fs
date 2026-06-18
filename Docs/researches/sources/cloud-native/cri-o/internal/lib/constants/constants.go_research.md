# sources/cloud-native/cri-o/internal/lib/constants/constants.go

## Purpose
Defines the CRI-O container manager annotation value used to identify containers managed by CRI-O.

## Important APIs, Types, And Functions
- `ContainerManagerCRIO = "cri-o"`.

## Control Flow
Declaration only. Runtime behavior occurs in code that compares annotation values.

## State And Persistence
No state is held. The value is persisted elsewhere as an OCI annotation, typically under `io.container.manager`.

## Dependencies And Integration Points
Used by factory annotation code and `ContainerServer.LoadContainer` to distinguish CRI-O-managed containers from other managers such as libpod.

## Risks And Edge Cases
Changing the value would break compatibility with persisted container specs and load filtering.

## Test Signals
`container_test.go` validates generated annotations include this value, and `container_server_test.go` validates non-CRI-O manager annotations are rejected.
