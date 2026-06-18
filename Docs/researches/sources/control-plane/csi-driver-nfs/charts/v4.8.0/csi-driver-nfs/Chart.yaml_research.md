# sources/control-plane/csi-driver-nfs/charts/v4.8.0/csi-driver-nfs/Chart.yaml

## Purpose
Helm chart metadata for CSI NFS driver release v4.8.0.

## Important APIs, Types, And Functions
Uses Helm chart API `apiVersion: v1`, `name: csi-driver-nfs`, `description: CSI NFS Driver for Kubernetes`, `version: v4.8.0`, and `appVersion: v4.8.0`.

## Control Flow
Helm reads this metadata when packaging, installing, listing releases, and resolving chart identity. It does not render Kubernetes resources itself.

## State And Persistence
The metadata is stored in Helm release records and chart archives, identifying the chart and application version used for an installation.

## Dependencies And Integration Points
Integrates with values and templates under the same chart directory. The `appVersion` should align with `.Values.image.nfs.tag` and release artifacts.

## Risks And Edge Cases
Version drift between `Chart.yaml`, image tags, and source code can confuse upgrades and provenance. Since this is Helm v1 chart metadata, compatibility depends on the consuming Helm tooling.

## Test Signals
`helm lint`, `helm package`, and comparing rendered image tags against `appVersion` are the main signals.
