<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/contrib/checkpoint/testdata/sleep.yaml -->
# sources/cloud-native/containerd/contrib/checkpoint/testdata/sleep.yaml

## Purpose
Kubernetes source pod manifest used before checkpointing.

## Important APIs, Types, And Functions
Pod `sleeper` running `quay.io/adrianreber/counter:latest`.

## Control Flow
Applied by the Kubernetes checkpoint script to create a counter workload.

## State And Persistence
Creates a Kubernetes pod when applied.

## Dependencies And Integration Points
Kubernetes API and external image registry.

## Risks And Test Signals
External image availability can break tests; script validates readiness/output. Source size reviewed: 8 lines in the current workspace.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/contrib/checkpoint/testdata/sleep.yaml -->
