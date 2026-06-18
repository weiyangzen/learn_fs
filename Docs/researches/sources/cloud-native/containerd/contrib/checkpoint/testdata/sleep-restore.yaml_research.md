<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/contrib/checkpoint/testdata/sleep-restore.yaml -->
# sources/cloud-native/containerd/contrib/checkpoint/testdata/sleep-restore.yaml

## Purpose
Kubernetes pod manifest for restoring from a local checkpoint image.

## Important APIs, Types, And Functions
Pod `sleeper` with container image `localhost/checkpoint-image:latest` and `IfNotPresent` pull policy.

## Control Flow
Applied by Kubernetes checkpoint restore script after local image import/tagging.

## State And Persistence
Creates/updates a Kubernetes pod when applied.

## Dependencies And Integration Points
Kubernetes API and local image availability.

## Risks And Test Signals
Name collides with test pod; assumes image is present on node. Validated by script. Source size reviewed: 10 lines in the current workspace.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/contrib/checkpoint/testdata/sleep-restore.yaml -->
