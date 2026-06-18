# sources/control-plane/csi-driver-nfs/charts/v4.9.0/csi-driver-nfs/Chart.yaml

## Purpose
Helm chart metadata for CSI NFS driver release v4.9.0.

## Important APIs, Types, And Functions
Declares Helm `apiVersion: v1`, `name: csi-driver-nfs`, description, `version: v4.9.0`, and `appVersion: v4.9.0`.

## Control Flow
Helm uses this metadata during chart loading, packaging, installation, upgrade, and release display. It does not directly render resources.

## State And Persistence
The metadata is persisted in packaged charts and Helm release records, identifying this release as v4.9.0.

## Dependencies And Integration Points
Should align with values defaults, particularly the NFS plugin image tag `v4.9.0`, and with release automation such as Cloud Build image publishing.

## Risks And Edge Cases
Version mismatch between chart metadata and image tags can make upgrades unclear. Chart API v1 metadata is simple but less expressive than v2 dependency metadata.

## Test Signals
Run `helm lint`, package the chart, and compare rendered image tags and release labels against this metadata.
