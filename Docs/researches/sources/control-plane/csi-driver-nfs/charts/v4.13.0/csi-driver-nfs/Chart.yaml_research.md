# sources/control-plane/csi-driver-nfs/charts/v4.13.0/csi-driver-nfs/Chart.yaml

## Purpose
This Helm metadata file identifies chart version 4.13.0 of the CSI NFS driver.

## APIs, Control Flow, and State
It declares `apiVersion: v1`, `name: csi-driver-nfs`, `description: CSI NFS Driver for Kubernetes`, `version: 4.13.0`, and `appVersion: 4.13.0`. There is no executable chart logic here; Helm uses it for packaging and chart repository metadata.

## Dependencies and Integration Points
The metadata should align with the directory, packaged tarball, and `values.yaml` NFS image tag. It marks the transition from 4.12.x to 4.13.0, where sidecar versions and template arguments change.

## Risks and Test Signals
Metadata mismatch affects upgrade automation and operator expectations. Test with `helm lint`, chart package inspection, and comparison to default image tags.
