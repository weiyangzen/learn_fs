<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/contrib/checkpoint/testdata/container_sleep.json -->
# sources/cloud-native/containerd/contrib/checkpoint/testdata/container_sleep.json

## Purpose
CRI container config fixture for checkpoint/restore tests.

## Important APIs, Types, And Functions
JSON describing container metadata, image, command loop, env, annotations, log path, TTY/stdin flags, and Linux resources/security.

## Control Flow
Consumed by `crictl create` in checkpoint scripts.

## State And Persistence
No execution by itself; controls created CRI container behavior.

## Dependencies And Integration Points
CRI runtime config schema and `ghcr.io/containerd/alpine` image.

## Risks And Test Signals
Image availability and resource/security fields affect portability. Validated by checkpoint scripts. Source size reviewed: 49 lines in the current workspace.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/contrib/checkpoint/testdata/container_sleep.json -->
