# sources/cloud-native/cri-o/test/mocks/ocicni/types.go

## Purpose
Generated GoMock for `github.com/cri-o/ocicni/pkg/ocicni.CNIPlugin`.

## Important APIs, Types, And Functions
`MockCNIPlugin` mocks GC, default network name, pod network status, setup/teardown with and without context, plugin name, status, and shutdown.

## Control Flow
Each CNI operation delegates to GoMock expectations and returns configured network results or errors.

## State And Persistence
No real CNI state, network namespace changes, or IPAM persistence.

## Dependencies And Integration Points
Used by server tests for startup status checks, CNI garbage collection, sandbox networking, and cleanup behavior.

## Risks And Test Signals
Mocks call contracts only; actual CNI plugin config parsing, bridge setup, IPAM, and namespace cleanup require integration tests.
