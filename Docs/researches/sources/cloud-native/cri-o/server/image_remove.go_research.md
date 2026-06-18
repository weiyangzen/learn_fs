<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/server/image_remove.go -->
# sources/cloud-native/cri-o/server/image_remove.go

## Purpose

This file implements CRI `RemoveImage` for storage images and OCI artifacts, including CRI idempotency and protection for image volumes currently used by containers.

## Important APIs, Types, and Functions

`RemoveImage(ctx, req)` validates an image spec and delegates to `removeImage`. `removeImage(ctx, imageRef)` handles ID deletion, name untagging, artifact removal, and idempotent not-found behavior. `volumeInUse(digest)` scans container volumes to prevent removing images used as mounted image volumes.

## Control Flow

If the ref resolves as an image ID prefix, the code checks image volume usage and calls storage `DeleteImage`, treating unknown/not-an-image as success. Otherwise it resolves candidate names, looks up status, checks volume usage by image ID, un-tags the first candidate that succeeds, and handles concurrent deletion errors idempotently. It then checks the artifact store for the original ref; not-found is success, other status errors fail, and found artifacts are usage-checked by digest and removed.

## State and Persistence Behavior

The code mutates image storage by deleting or untagging images and mutates artifact storage by removing artifacts. It reads current containers and their volumes to avoid deleting mounted volume images.

## Dependencies and Integration Points

It depends on storage image server ID/name resolution, containers/storage error types, artifact store status/remove, container list state, CRI image spec, and internal `oci.ContainerVolume` image fields.

## Risks and Edge Cases

Only the first successfully untagged candidate is removed. If storage untag succeeds and artifact removal later fails, storage state has already changed. `volumeInUse` assumes `volume.Image` is non-nil; if any volume lacks an image pointer, this can panic. It does not check normal container rootfs image use because storage handles that case.

## Test Signals

Tests cover name removal, full-ID deletion, untag errors, name resolution errors, missing image spec, idempotency for unknown/not-an-image delete, and concurrent deletion during untag. Artifact and volume-in-use paths are not covered.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/server/image_remove.go -->
