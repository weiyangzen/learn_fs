# sources/control-plane/csi-driver-nfs/charts/v3.1.0/csi-driver-nfs/templates/csi-nfs-controller.yaml

Purpose: v3.1.0 controller Deployment, extending v3.0.0 with mount permission and working mount directory controls.

Important APIs/types/functions: `Deployment`; sidecars `csi-provisioner` and `liveness-probe`; NFS driver args `--mount-permissions` and `--working-mount-dir`; controller values and resources.

Control flow: Renders host-networked controller pods on Linux with optional master toleration. Sidecars share `/csi/csi.sock`; NFS container mounts kubelet pods and serves the CSI endpoint with configured driver and permission behavior.

State and persistence: HostPath pod mounts plus emptyDir socket. Dynamic state appears as PV/PVCs, events, and leader-election leases.

Dependencies and integration points: Integrates with RBAC, CSIDriver, external-provisioner, and kubelet pod directories.

Risks: Privileged hostPath mount with configurable permissions can over-open NFS directories if set broadly. Test signals: PVC lifecycle and permission checks on created subdirectories.
