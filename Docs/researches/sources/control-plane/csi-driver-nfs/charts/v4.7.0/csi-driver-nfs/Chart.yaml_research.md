# sources/control-plane/csi-driver-nfs/charts/v4.7.0/csi-driver-nfs/Chart.yaml

## Purpose

This is the Helm chart metadata for the v4.7.0 NFS CSI driver chart. It declares `apiVersion: v1`, `name: csi-driver-nfs`, description `CSI NFS Driver for Kubernetes`, and sets both `version` and `appVersion` to `v4.7.0`.

## APIs, control flow, and state

The file has no runtime control flow. Helm consumes it for chart packaging, repository indexes, release metadata, and display through commands such as `helm show chart`. It is the metadata anchor for the v4.7.0 chart directory, whose templates and values may evolve beyond v4.6.0.

## Dependencies and integration points

The chart metadata integrates with Helm release history, helper templates that reference `.Chart.*`, and operator inventory tooling. `appVersion` should stay aligned with the default NFS plugin image tag in the same chart version's `values.yaml`.

## Risks and test signals

The primary risk is version skew between metadata, directory name, and default driver image. Test with `helm lint`, `helm show chart`, `helm template`, and a comparison against the v4.7.0 `values.yaml` NFS image tag. Packaging checks should ensure downstream chart repositories expose this version correctly.
