# sources/control-plane/csi-driver-nfs/charts/v4.12.1/csi-driver-nfs/Chart.yaml

## Purpose
This Helm metadata file identifies chart version 4.12.1 of `csi-driver-nfs`.

## APIs, Control Flow, and State
It uses Helm chart `apiVersion: v1`, declares `name: csi-driver-nfs`, `description: CSI NFS Driver for Kubernetes`, `version: 4.12.1`, and `appVersion: 4.12.1`. It has no template logic, dependencies, maintainers, or values itself; Helm uses it as chart package metadata.

## Dependencies and Integration Points
The version and appVersion should match the packaged tarball and default NFS driver image tag in `values.yaml`. Consumers and automation can use these fields for chart repository indexes, upgrade detection, and compatibility reporting.

## Risks and Test Signals
Metadata drift between `Chart.yaml`, the package name, and `values.yaml` image tag can mislead upgrade tooling. Test with `helm lint`, package metadata inspection, and comparison to the chart directory and tarball version.
