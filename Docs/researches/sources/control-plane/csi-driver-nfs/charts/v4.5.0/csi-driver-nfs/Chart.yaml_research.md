# sources/control-plane/csi-driver-nfs/charts/v4.5.0/csi-driver-nfs/Chart.yaml

## Purpose

This is the Helm chart metadata for the v4.5.0 NFS CSI driver chart. It declares `apiVersion: v1`, chart `name: csi-driver-nfs`, description `CSI NFS Driver for Kubernetes`, `version: v4.5.0`, and `appVersion: v4.5.0`.

## APIs, control flow, and state

There is no executable control flow. Helm reads this file to identify the chart package and to expose chart/application versions in release metadata. The chart version should track the template/defaults bundled in `charts/v4.5.0`, while `appVersion` tracks the default NFS driver image version used by `values.yaml`.

## Dependencies and integration points

The metadata integrates with Helm packaging, dependency indexing, release history, chart repositories, and operators that inspect `.Chart.Name`, `.Chart.Version`, or `.Chart.AppVersion` through helper templates. It must remain consistent with the default `image.nfs.tag` and the source directory version.

## Risks and test signals

Version drift is the primary risk: if this file says v4.5.0 while values deploy another driver, release inventory becomes misleading. Test by running `helm lint`, `helm template`, and `helm show chart` for this directory, and by comparing `appVersion` with `values.yaml`'s NFS image tag.
