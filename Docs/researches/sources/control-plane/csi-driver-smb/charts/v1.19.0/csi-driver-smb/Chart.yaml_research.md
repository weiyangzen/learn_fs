# sources/control-plane/csi-driver-smb/charts/v1.19.0/csi-driver-smb/Chart.yaml

## Purpose
This Helm `Chart.yaml` declares the SMB CSI Driver chart package for `v1.19.0`. It names the chart `csi-driver-smb`, describes it as the Kubernetes SMB CSI driver, and binds the chart release version to `1.19.0` with app version `1.19.0`.

## Important APIs, Types, And Functions
The file uses the Helm chart metadata API (`apiVersion: v1`) rather than a Kubernetes workload API. Its important fields are `name`, `description`, `version`, and `appVersion`; there are no templates, functions, dependencies, or exported objects in this file.

## Control Flow
There is no runtime control flow. Helm reads this metadata before rendering sibling templates, so this file influences chart identity, packaging, index entries, and upgrade/version selection but does not conditionally render resources.

## State And Persistence Behavior
The file is declarative metadata only. Persistent state is created by sibling templates such as `CSIDriver`, `Deployment`, `DaemonSet`, RBAC, and `StorageClass` resources, not by this descriptor.

## Dependencies And Integration Points
The chart integrates with Helm repositories and Kubernetes package installation tooling. Its version must stay aligned with image tags and values defaults in the same chart directory, otherwise users can install a package whose metadata and rendered controller/node image versions disagree.

## Risks And Test Signals
Primary risk is version drift between `appVersion`, `version`, packaged `.tgz` archives, and image tags. Test by running `helm lint`, `helm template`, and checking chart repository indexes for the expected `v1.19.0` package identity.
