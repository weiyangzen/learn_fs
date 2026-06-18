# sources/control-plane/csi-driver-nfs/charts/v4.0.0/csi-driver-nfs/templates/csi-nfs-controller.yaml

Purpose: v4.0.0 controller Deployment with configurable `kubeletDir` and DNS policy.

Important APIs/types/functions: `Deployment`; Helm values `.Values.kubeletDir`, `.Values.controller.dnsPolicy`, `.Values.driver.mountPermissions`, resources, and images.

Control flow: Renders a host-networked Linux controller using a value-driven service account and DNS policy. Provisioner and liveness sidecars share the CSI socket; the NFS container mounts `${kubeletDir}/pods` and uses working mount directory and mount permission args.

State and persistence: HostPath pod mount and emptyDir socket; cluster state through sidecars.

Dependencies and integration points: Controller RBAC, CSIDriver, external-provisioner, livenessprobe, and kubelet pod directory.

Risks: `hostNetwork` with configurable DNS requires correct `dnsPolicy`; wrong `kubeletDir` breaks mounts. Test signals: render with non-default kubeletDir and run PVC provisioning on target node layout.
