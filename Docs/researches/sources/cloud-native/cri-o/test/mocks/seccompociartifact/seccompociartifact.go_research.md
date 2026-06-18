# sources/cloud-native/cri-o/test/mocks/seccompociartifact/seccompociartifact.go

## Purpose
Generated GoMock for seccomp OCI artifact pulling implementation.

## Important APIs, Types, And Functions
`MockImpl` provides `PullData(ctx, ref, *datastore.PullOptions)` returning artifact data.

## Control Flow
Single mocked method delegates to GoMock.

## State And Persistence
No real network or artifact persistence.

## Dependencies And Integration Points
Used by tests for seccomp profile loading from OCI artifacts. Depends on CRI-O datastore artifact data types.

## Risks And Test Signals
Only verifies call behavior and returned artifact data handling; does not test registry auth, digest selection, or profile parsing.
