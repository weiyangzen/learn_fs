<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/examples/k8s/static/static-app.yaml -->
# sources/control-plane/beegfs-csi-driver/examples/k8s/static/static-app.yaml

Purpose: standalone Pod demonstrating read/write access to a statically provisioned BeeGFS directory.

Important APIs and flow: Alpine Pod mounts `csi-beegfs-static-pvc` at `/mnt/static`, writes a marker file including the Pod UID and a cluster name placeholder, then sleeps. Optional OpenShift nodeSelector comments address RHEL/RHCOS placement.

State and persistence: marker file persists in the pre-existing BeeGFS directory after Pod deletion. Kubernetes does not create/delete the static target path.

Dependencies and integration points: depends on `static-pv.yaml`, `static-pvc.yaml`, node plugin mount support, and pre-created BeeGFS path.

Risks and test signals: cluster-name placeholder should be customized to avoid collisions. Test by exec listing `/mnt/static` and checking PV/PVC events.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/examples/k8s/static/static-app.yaml -->
