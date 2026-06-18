# sources/control-plane/csi-driver-nfs/charts/v4.13.2/csi-driver-nfs/Chart.yaml

## Purpose
This Helm chart metadata file identifies the v4.13.2 NFS CSI driver chart and ties the chart package version to the driver application version.

## Important APIs, Types, and Functions
It uses Helm chart API `v1` with `name: csi-driver-nfs`, `description: CSI NFS Driver for Kubernetes`, `version: 4.13.2`, and `appVersion: 4.13.2`.

## Control Flow, State, and Persistence
The file has no templating logic or runtime state. Helm uses it for chart packaging, dependency metadata, release history, and display.

## Dependencies and Integration Points
The version should align with `values.yaml` image tag defaults, especially `image.nfs.tag: v4.13.2`. Consumers may depend on the unprefixed semver-style chart version introduced in later chart lines.

## Risks and Test Signals
Risks are chart/app version drift and tooling assumptions around earlier versions that used a leading `v`. Signals are `helm lint`, packaged chart metadata inspection, and verifying the rendered nfsplugin image tag matches the advertised app version.
