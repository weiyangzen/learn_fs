# sources/control-plane/csi-driver-nfs/charts/index.yaml

Purpose: Helm chart repository index for published `csi-driver-nfs` chart versions.

Important APIs and types: `apiVersion: v1`, entries under `csi-driver-nfs`, each with chart API version, appVersion, created timestamp, description, digest, name, URL to packaged chart tarball, and chart version. Includes current `latest` packaged as `v0.0.0`.

Control flow: Helm clients read this file to resolve chart versions and download packages from raw GitHub URLs.

State and persistence: persistent chart release metadata generated at `2026-04-17T13:22:50.057996816Z`.

Dependencies and integration: consumed by Helm repositories and Artifact Hub.

Risks: appVersion formatting changes across versions (`4.13.x` without `v`, older versions with `v`). URLs point at the `master` branch raw content, so branch rewrite or file removal would break installs.

Test signals: `helm repo update`, `helm search repo`, and chart install from each URL.
