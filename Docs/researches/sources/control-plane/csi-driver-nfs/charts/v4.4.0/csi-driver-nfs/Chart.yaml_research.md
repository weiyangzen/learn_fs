# sources/control-plane/csi-driver-nfs/charts/v4.4.0/csi-driver-nfs/Chart.yaml

## Purpose
This metadata file identifies the v4.4.0 NFS CSI Helm chart.

## Important APIs, Types, and Functions
It uses Helm chart API `v1`, with `name: csi-driver-nfs`, description `CSI NFS Driver for Kubernetes`, `version: v4.4.0`, and `appVersion: v4.4.0`.

## Control Flow, State, and Persistence
The file has no runtime control flow or persisted cluster state. Helm uses it for chart packaging and release metadata.

## Dependencies and Integration Points
The version should align with the v4.4.0 chart directory's values and image defaults. It retains the leading-`v` version style used by v4.2.0 and v4.3.0.

## Risks and Test Signals
Risks are version drift and compatibility with semver parsers that reject a leading `v`. Signals are `helm lint`, chart package inspection, and rendered image tag checks.
