<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/server/container_restore.go -->
# sources/cloud-native/cri-o/server/container_restore.go

## Purpose

This file implements container creation from checkpoint archives or checkpoint OCI images. It is used when `CreateContainer` detects an image input that represents checkpoint data and prepares an `oci.Container` flagged for later restore in `StartContainer`.

## Important APIs, Types, and Functions

`checkIfCheckpointOCIImage(ctx, input)` resolves an image and checks for CRI-O checkpoint annotations. `CRImportCheckpoint(ctx, createConfig, sb, sandboxUID)` imports checkpoint metadata, reconstructs a CRI container config, validates required bind mounts, reserves name/ID state, calls the normal `createSandboxContainer`, and marks the new container as restore-capable.

## Control Flow

Restore import validates image and metadata fields. If input resolves to a checkpoint OCI image, it rejects namespace-specific signature policy, mounts the image through the storage image server, and defers unmount. Otherwise it opens a checkpoint archive, extracts selected metadata files into a temp directory, and defers cleanup. It reads `spec.dump` and `config.dump`, unmarshals original annotations from the dumped spec, updates pod UID and container hash where applicable, checks sandbox stop state, creates a new factory container, chooses the rootfs image from `RootfsImageRef` or `RootfsImageName`, applies incoming resources/security context and dumped masked/readonly paths, verifies every non-ignored bind mount in the dump is present in the new CRI request, creates sandbox config, reserves the name, sets restore mode, invokes common creation, adds indexes and in-memory state, marks created/restore, records archive path or storage image ID and checkpoint time, and returns the new ID.

## State and Persistence Behavior

It may mount/unmount a checkpoint OCI image, create/remove a temp extraction directory, reserve/release container names, create storage/runtime bundle state via `createSandboxContainer`, add/remove in-memory containers and ID indexes on failure, and set restore metadata on the `oci.Container`. Context cancellation returns an error after construction but does not use the same resource-store handoff pattern as normal create.

## Dependencies and Integration Points

The code depends on checkpointctl metadata file names, containers/storage archive extraction, internal annotations, image status and storage image mount APIs, signature policy namespace context, sandbox state, the factory container and shared creation pipeline, kubelet pod UID labels, and runtime restore in `StartContainer`.

## Risks and Edge Cases

Security-sensitive behavior includes refusing undeclared bind mounts from checkpoint data and rejecting namespaced signature policies for OCI checkpoint restores. Archive parsing trusts checkpoint metadata structure and fails on missing or malformed JSON. Ignored mounts are recreated for the new environment. Cleanup is defer-heavy; missing cleanup can leave mounted images, temp dirs, name reservations, storage containers, or ID indexes. The typo in a comment is harmless.

## Test Signals

Restore tests cover missing archives, empty/non-tar archives, broken `spec.dump`/`config.dump`, empty metadata, successful archive restore with rootfs image by name or ID, bind mount preservation, annotation hash/pod UID update, and OCI checkpoint image mount failure behavior. CRIU availability and rootless mode gate some tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/server/container_restore.go -->
