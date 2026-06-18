# sources/cloud-native/containerd/integration/containerd_image_test.go

## Purpose

This file validates CRI image visibility and metadata when images are manipulated directly through the containerd client rather than CRI. It covers image import into the `k8s.io` namespace, namespace isolation, sandbox image pinning, and externally pulled pause images.

## Important APIs, Types, And Functions

- `TestContainerdImage` pulls BusyBox with `containerdClient.Pull`, waits for CRI visibility, checks labels/pinning, and starts a container by image ID.
- `TestContainerdImageInOtherNamespaces` verifies images in a non-CRI namespace are invisible until CRI pulls its own copy.
- `TestContainerdSandboxImage` checks the pause image exists and is pinned.
- `TestContainerdSandboxImagePulledOutsideCRI` removes/pulls the pause image outside CRI and verifies CRI marks it pinned.

## Control Flow

The main test removes preexisting CRI image state, pulls BusyBox directly with labels including the CRI pinned label, waits for `ImageStatus` by ref and ID, verifies repo tags and managed labels, then creates a container using the image ID. Deferred cleanup deletes both tag and ID references and verifies CRI visibility changes. Namespace isolation uses a `test` containerd namespace to prove CRI does not see images outside `k8s.io`.

## State And Persistence Behavior

These tests mutate containerd image store records and CRI image index state. They specifically check labels such as `io.cri-containerd.image` and pin metadata, and they validate reference deletion behavior.

## Dependencies And Integration Points

The file integrates containerd client image service, CRI image service, namespace scoping, CRI labels, errdefs not-found handling, and runtime container creation.

## Risks And Edge Cases

Tests rely on asynchronous CRI image-store reconciliation and therefore use `Eventually`/`Consistently`. Shared image references can interfere with parallel tests. Label semantics are tightly coupled to CRI image management internals.

## Test Signals

Passing shows containerd-side image changes in the CRI namespace are reflected in CRI, labels/pins are maintained, and namespace isolation is respected.
