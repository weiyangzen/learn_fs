# sources/control-plane/rook/pkg/operator/ceph/object/cosi/spec.go

## Purpose
`cosi/spec.go` constructs the Kubernetes Deployment, Pod template, labels, containers, volumes, and defaults for the Ceph COSI driver.

## Important APIs, Types, and Functions
`createCephCOSIDriverDeployment()` creates a one-replica Recreate Deployment with Rook revision history, 30-second minimum readiness, and 600-second progress deadline. `getCOSILabels()` extends standard Rook app labels with COSI-specific `app.kubernetes.io` labels. `createCOSIPodSpec()` creates two containers, applies placement, sets the service account, host networking policy, emptyDir socket volume, and pod labels. `createCOSIDriverContainer()` selects the Ceph COSI image, passes `--driver-prefix=rook-ceph`, exposes `POD_NAMESPACE`, mounts `/var/lib/cosi`, and applies resource requirements. `createCOSISideCarContainer()` selects the objectstorage provisioner sidecar image and mounts the same socket.

## Control Flow, State, and Persistence
The file is pure object construction. Persistent state appears when the controller creates or updates the returned Deployment. The shared emptyDir socket is process-local to the pod and is the integration channel between driver and sidecar.

## Dependencies and Integration Points
It integrates CephCOSIDriver spec fields for images, placement, and resources; operator label helpers; host-network enforcement; Kubernetes Deployment/Pod APIs; and COSI sidecar socket conventions.

## Risks and Test Signals
Risks include hard-coded default images, no explicit probes, no owner reference in this constructor, service-account assumptions, and potential global host-network side effects. Tests in `controller_test.go` cover custom driver image indirectly; additional tests should verify sidecar image override, placement, resources, labels/selectors, volumes, and service account.
