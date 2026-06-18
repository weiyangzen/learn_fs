
<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/images/image_remove.go -->
# sources/cloud-native/containerd/internal/cri/server/images/image_remove.go

## Purpose

This file implements CRI image removal. It resolves an image by reference or ID, deletes all known references from containerd's image store, and refreshes the CRI in-memory image index.

## Important APIs, Types, and Functions

`(*GRPCCRIImageService).RemoveImage` is the CRI gRPC handler. `(*CRIImageService).RemoveImage` performs resolution and deletion. It uses `LocalResolve`, `c.images.Delete`, `images.SynchronousDelete`, and `c.imageStore.Update`.

## Control Flow

The gRPC wrapper delegates to the service and suppresses `NotFound` as CRI success. The service resolves the image locally. Missing images are traced and treated as success. For each known reference, it deletes the reference from containerd; the last reference uses synchronous delete to trigger garbage collection. After successful or already-missing deletion, it updates the in-memory image store for that reference.

## State and Persistence Behavior

The function deletes containerd image metadata references and may trigger best-effort garbage collection on the last reference. It refreshes CRI image-store state to reflect removed references. It does not directly delete content blobs or snapshots.

## Dependencies and Integration Points

Dependencies include containerd core images store APIs, errdefs, tracing, and CRI runtime API. It integrates with `LocalResolve` and the image store maintained by pulls and image events.

## Risks and Edge Cases

Reference deletion can race with external image store changes. Synchronous deletion is best effort and only applied to the last reference known in the in-memory image object. If updating the CRI image store after a delete fails, removal returns an error even if containerd metadata changed.

## Test Signals

Useful tests would cover missing image success, partial reference deletion failures, `NotFound` during delete, synchronous option on last reference, image-store update failures, and concurrent reference removal.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/images/image_remove.go -->
