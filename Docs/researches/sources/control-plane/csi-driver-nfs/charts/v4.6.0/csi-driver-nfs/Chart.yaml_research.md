# sources/control-plane/csi-driver-nfs/charts/v4.6.0/csi-driver-nfs/Chart.yaml

## Purpose

This is the Helm metadata file for chart v4.6.0. It declares the chart as `csi-driver-nfs`, describes it as `CSI NFS Driver for Kubernetes`, and sets both `version` and `appVersion` to `v4.6.0`.

## APIs, control flow, and state

There is no runtime control flow. Helm uses the file for packaging, chart repository indexes, release history, and chart metadata inspection. The `appVersion` should match the default NFS plugin image tag in `values.yaml`; the `version` should match the templates under the v4.6.0 directory.

## Dependencies and integration points

Helper templates and release tooling can read `.Chart.Name`, `.Chart.Version`, and `.Chart.AppVersion`. Operators use these fields to audit installed chart/application versions and compare them against rendered images.

## Risks and test signals

Metadata drift is the main risk. Test with `helm lint`, `helm show chart`, and a comparison between this `appVersion` and `values.yaml`'s `image.nfs.tag`. Package tests should ensure the directory name, chart version, and app version all remain coherent.
