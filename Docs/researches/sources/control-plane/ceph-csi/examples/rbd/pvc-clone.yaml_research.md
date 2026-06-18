## sources/control-plane/ceph-csi/examples/rbd/pvc-clone.yaml

Purpose: Example filesystem PVC cloned from another RBD PVC.

Important API surface: PVC `rbd-pvc-clone`, `storageClassName: csi-rbd-sc`, data source `PersistentVolumeClaim` named `rbd-pvc`, `ReadWriteOnce`, and `1Gi` size.

Control flow and state: Kubernetes translates the data source into a CSI volume clone request. The RBD controller creates a cloned RBD image and records normal PV/PVC binding state.

Dependencies and risks: Requires source `rbd-pvc` to exist, be compatible, and not exceed requested target size. Clone behavior depends on RBD image features such as layering. Test by mounting source, writing data, creating clone, and mounting `pod-clone.yaml`.
