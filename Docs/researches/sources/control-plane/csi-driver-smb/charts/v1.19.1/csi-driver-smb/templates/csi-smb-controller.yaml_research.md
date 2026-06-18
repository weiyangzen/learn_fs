# sources/control-plane/csi-driver-smb/charts/v1.19.1/csi-driver-smb/templates/csi-smb-controller.yaml

## Purpose
This template renders the Linux controller `apps/v1` `Deployment` for the SMB CSI driver in chart `v1.19.1`. It runs the controller service account with the CSI sidecars and the SMB controller plugin that handles dynamic provisioning and, in newer versions, expansion.

## Important APIs, Types, And Functions
The resource is a `Deployment` named `.Values.controller.name`. It renders containers for csi-provisioner, csi-resizer, liveness-probe, and smb. The provisioner connects to `/csi/csi.sock` through `ADDRESS`; the SMB container receives `CSI_ENDPOINT`, `.Values.driver.name`, metrics and health ports, log level, and, in later charts, `--working-mount-dir`. Image references may use `.Values.image.baseRepo` when repositories start with `/`.

## Control Flow
Helm injects labels, pod labels, annotations, pull secrets, resources, node selectors, tolerations, and affinity from values. This version uses configurable `.Values.controller.dnsPolicy`. It uses `Recreate` rollout strategy to avoid overlapping controller pods sharing mount state. Control-plane scheduling is either explicitly set by affinity or synthesized from `runOnMaster`/`runOnControlPlane` in modern charts.

## State And Persistence Behavior
The controller stores its CSI socket in an `emptyDir`; authoritative state lives in Kubernetes PV/PVC/Lease objects and remote SMB shares. Leader election uses Leases, so RBAC and namespace alignment are required.

## Dependencies And Integration Points
It depends on the RBAC template, controller service account, CSI provisioner image, optional resizer image, liveness-probe image, and the SMB plugin image. It integrates with the `CSIDriver`, `StorageClass` provisioner name, and Kubernetes events.

## Risks And Test Signals
Risks include broken image path composition, insufficient RBAC for provisioning/resizing, controller scheduling to the wrong OS, and privileged SMB container requirements. Test with `helm template`, `helm lint`, rendered Deployment inspection, PVC create/delete, expansion where available, and liveness/metrics endpoint checks. Newer sidecars use localhost HTTP liveness endpoints and drop Linux capabilities where possible.
