## sources/control-plane/csi-driver-iscsi/examples/storageclass.yaml

Purpose: minimal StorageClass named `manual` for the static iSCSI example.

Control flow is declarative and sets `provisioner: manual`, indicating no CSI dynamic provisioning. State is Kubernetes StorageClass resource state.

Dependencies are PVC/PV examples that both reference `manual`. Risks include confusing users who expect dynamic provisioning through the iSCSI CSI driver; the driver controller CreateVolume is unimplemented. Test signal is successful apply and PVC binding to the static PV.
