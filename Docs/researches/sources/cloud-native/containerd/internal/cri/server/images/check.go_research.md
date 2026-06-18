
<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/images/check.go -->
# sources/cloud-native/containerd/internal/cri/server/images/check.go

## Purpose

This file implements startup-style image readiness checking for the CRI image service. It scans containerd images, verifies content readiness and unpack status, and refreshes the CRI in-memory image store for usable images.

## Important APIs, Types, and Functions

The primary function is `(*CRIImageService).CheckImages`. It uses `c.client.ListImages`, `images.Check`, `containerd.Image.IsUnpacked`, and `c.UpdateImage`.

## Control Flow

`CheckImages` lists images from the containerd client. For each image, it starts a wait-group goroutine that checks content availability for the default platform, warns and skips if content is incomplete, checks whether the image is unpacked for the configured snapshotter, warns if not unpacked, and calls `UpdateImage` to reconcile CRI image metadata. Per-image errors are logged but do not cause `CheckImages` to fail after the initial list succeeds.

## State and Persistence Behavior

The function can update the CRI image store through `UpdateImage`, which may create CRI-managed references and refresh in-memory metadata. It does not pull missing content or unpack images; it only logs readiness problems.

## Dependencies and Integration Points

Dependencies include containerd image checks, platform matching, logging, and the CRI image service's client and config. It integrates with image-service startup recovery, image event reconciliation, and the in-memory `imagestore`.

## Risks and Edge Cases

The implementation currently checks only the default snapshotter and default platform. It logs but does not repair incomplete content or missing unpacked snapshots. Running checks concurrently can amplify load on content and metadata stores. The use of `sync.WaitGroup.Go` depends on the Go version/library in this tree.

## Test Signals

Useful tests would cover list failure, content check errors, content incomplete, unpack check errors, unpack missing, successful `UpdateImage`, and per-image error isolation.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/images/check.go -->
