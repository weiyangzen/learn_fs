# sources/cloud-native/moby/daemon/containerd/fake_service_test.go

## Purpose
Provides reusable test fixtures for the containerd-backed image service: a fake `ImageService`, a read-only blob-directory content store, a no-op leases manager, and a delay wrapper for content-store benchmarks.

## Important APIs, Types, And Functions
- `fakeImageService` wires metadata image store, content store, snapshotter service, event service, memory container store, and a containerd client with injected services.
- `noopLeasesManager` satisfies containerd leases APIs without retaining resources.
- `blobsDirContentStore` implements content store reads, info, walk, and delete against files in a `blobs/sha256` directory.
- `delayedStore` wraps content operations with a constant sleep.

## Control Flow
Tests call `fakeImageService` with a content store, then exercise image service methods without an external containerd daemon. Blob reads map descriptor digest encodings to filenames. Walk enumerates files and constructs content info from stat data. Delay wrapper forwards all calls after sleeping.

## State And Persistence
State lives in temporary metadata databases, in-memory snapshotter fixtures, and test blob directories. `blobsDirContentStore.Delete` removes files, while writes/status updates are intentionally unsupported or read-only.

## Dependencies And Integration Points
Depends on containerd client service injection, metadata DB, snapshotter service test doubles, daemon events, and Moby container memory store. It underpins tests for image identity, deletion, import/export, and manifest walking.

## Risks And Edge Cases
The blob content store is intentionally incomplete; tests using it must not expect writes, status tracking, label updates, or real lease semantics. Digest construction in `Walk` uses file names as digest inputs and is only suitable for controlled fixtures.

## Test Signals
This file is test infrastructure. Failures in dependent tests can indicate fake service drift from containerd service interfaces or fixture behavior insufficient for new image-service code paths.
