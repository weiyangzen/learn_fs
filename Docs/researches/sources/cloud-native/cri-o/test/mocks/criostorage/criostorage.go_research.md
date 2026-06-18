# sources/cloud-native/cri-o/test/mocks/criostorage/criostorage.go

## Purpose
Generated GoMock implementations for CRI-O internal storage interfaces.

## Important APIs, Types, And Functions
Defines `MockImageServer`, `MockRuntimeServer`, and `MockStorageTransport`. Image server methods cover pull/list/status/delete/untag/pinned-images/name resolution. Runtime server methods cover pod/container creation, start/stop/delete, metadata, and work/run directories. Storage transport mocks `ResolveReference`.

## Control Flow
Standard GoMock delegation and recorder setup for each interface method.

## State And Persistence
No real storage persistence. Expectations model storage behavior in memory.

## Dependencies And Integration Points
Used widely by server tests to isolate CRI-O runtime service behavior from containers/storage and containers/image.

## Risks And Test Signals
Good for asserting CRI-O calls the storage layer correctly, but not for validating image policy, transport behavior, or storage durability. Regeneration needed on interface change.
