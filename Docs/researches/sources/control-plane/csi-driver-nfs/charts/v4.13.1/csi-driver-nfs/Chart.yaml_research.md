# sources/control-plane/csi-driver-nfs/charts/v4.13.1/csi-driver-nfs/Chart.yaml

## Purpose
This Helm metadata file identifies chart version 4.13.1 of `csi-driver-nfs`.

## APIs, Control Flow, and State
It declares Helm chart `apiVersion: v1`, `name: csi-driver-nfs`, description, `version: 4.13.1`, and `appVersion: 4.13.1`. It has no runtime control flow or state beyond chart packaging metadata.

## Dependencies and Integration Points
The metadata should match the chart directory, packaged `csi-driver-nfs-4.13.1.tgz`, and the 4.13.1 default NFS driver image tag in `values.yaml`. In this work item only `Chart.yaml` is mapped for v4.13.1, but repository diffs show the adjacent values file differs from 4.13.0 as part of the patch release.

## Risks and Test Signals
If appVersion or version drift from packaged contents, chart repository consumers can select or report the wrong release. Test with `helm lint`, package metadata inspection, and version consistency checks.
