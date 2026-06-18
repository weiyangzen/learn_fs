# sources/cloud-native/containerd/internal/cri/labels/labels.go

## Purpose

This file defines label and extension keys used by the CRI plugin to mark images, containers, sandboxes, Kubernetes metadata, and stored CRI metadata extensions.

## Important APIs, Types, and Functions

Constants include the `io.cri-containerd` prefix, image management and pinned labels, container kind label and values, container/sandbox metadata extension names, Kubernetes pod name/namespace/UID/container name labels, and the infra container name `POD`.

## Control Flow

There is no executable control flow.

## State and Persistence Behavior

These constants become persisted labels and container extension keys in containerd metadata stores and image/container records. They are part of the compatibility surface for CRI metadata discovery.

## Dependencies and Integration Points

The labels are used by image management, container creation, checkpoint import metadata fixups, NRI wrappers, and store/index code. `ContainerMetadataExtension` is registered in container creation and read by NRI integration.

## Risks and Edge Cases

Changing string values would break lookup of existing images/containers or metadata extensions. Kubernetes label keys must remain aligned with kubelet expectations. The `PinnedImageLabelKey` comment says "label value" but the constant is a key; consumers should rely on the identifier, not the comment.

## Test Signals

Tests should verify labels are applied during image/container creation, extensions round-trip through containerd metadata, and checkpoint restore updates Kubernetes labels correctly.
