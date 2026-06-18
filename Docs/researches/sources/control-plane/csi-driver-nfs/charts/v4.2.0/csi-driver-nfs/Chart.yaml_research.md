# sources/control-plane/csi-driver-nfs/charts/v4.2.0/csi-driver-nfs/Chart.yaml

## Purpose
This metadata file identifies the v4.2.0 NFS CSI Helm chart.

## Important APIs, Types, and Functions
It uses Helm chart API `v1`, with `name: csi-driver-nfs`, description `CSI NFS Driver for Kubernetes`, and both `version` and `appVersion` set to `v4.2.0`.

## Control Flow, State, and Persistence
There is no templating or runtime state. Helm uses this file for package identity, release metadata, and chart version selection.

## Dependencies and Integration Points
The chart version should align with `values.yaml` defaults, especially the NFS plugin image tag `v4.2.0`. The leading `v` differs from later 4.13 chart metadata.

## Risks and Test Signals
Risks are version drift and automation that expects strict semver without a leading `v`. Signals are `helm lint`, package inspection, and rendered image tag comparison.
