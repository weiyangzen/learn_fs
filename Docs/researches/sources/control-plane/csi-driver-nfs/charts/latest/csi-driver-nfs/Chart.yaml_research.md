# sources/control-plane/csi-driver-nfs/charts/latest/csi-driver-nfs/Chart.yaml

Purpose: Helm chart metadata for the latest NFS CSI driver chart.

Important APIs and types: chart `apiVersion: v1`, `appVersion: latest`, description, name `csi-driver-nfs`, and version `v0.0.0`.

Control flow: Helm reads this metadata during packaging, linting, dependency resolution, and install display.

State and persistence: static chart metadata.

Dependencies and integration: used by Makefile E2E Helm install and chart index packaging.

Risks: `v0.0.0` latest chart version is suitable for moving latest but not immutable release installs. App version `latest` can obscure the exact driver image version unless values override image tags.

Test signals: Helm lint/package/install behavior.
