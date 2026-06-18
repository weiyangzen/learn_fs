# sources/cloud-native/cri-o/internal/lib/container_server_test.go

## Purpose
Tests `ContainerServer` construction, getters, sandbox/container restore from persisted specs, state persistence errors, name reservation, shutdown, in-memory state stores, and list/filter behavior.

## Important APIs, Types, And Functions
- Exercises `lib.New`, getters, `LoadSandbox`, `LoadContainer`, `ContainerStateToDisk`, `ReserveContainerName`, `ReservePodName`, `Shutdown`, `AddContainer`, `AddSandbox`, `RemoveContainer`, `RemoveSandbox`, `ListContainers`, `ListSandboxes`, `AddInfraContainer`, and `RemoveInfraContainer`.
- Uses shared helpers such as `beforeEach`, `createDummyState`, `mockDirs`, `testManifest`, `mySandbox`, and `myContainer`.

## Control Flow
Constructor tests mock config/store access and clean shutdown markers. LoadSandbox tests mutate a serialized manifest to produce valid and invalid annotations, metadata, namespace options, port mappings, labels, SELinux labels, pod resources, names, and storage directory errors. LoadContainer tests cover valid restore, bad manifests, storage directory failures, invalid annotations, and non-CRI-O manager rejection. Later blocks validate name reservation conflicts, storage shutdown errors, add/remove semantics, and list filtering.

## State And Persistence
Uses mocks for storage directories and state, creates temporary files for clean shutdown/config, and mutates in-memory server stores/indexes. `ContainerStateToDisk` failure is tested with an invalid state path.

## Dependencies And Integration Points
Integrates gomock storage/config mocks, CRI-O annotations/constants, OCI container creation, CRI API metadata, and the test framework. It documents the on-disk annotation contract used to restore sandboxes and containers.

## Risks And Edge Cases
Many tests depend on exact JSON fragments in `testManifest`; unrelated formatting changes can require updates. Some behavior labeled "should fail" intentionally returns a partially built sandbox plus error, so callers must inspect both. RemoveContainer behavior when sandbox is already missing leaves the container present, which the test documents.

## Test Signals
Very strong signal for persistence/restore robustness and server state invariants. It catches malformed persisted metadata and name/index lifecycle regressions.
