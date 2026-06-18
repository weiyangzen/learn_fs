## sources/control-plane/csi-driver-iscsi/examples/pv.yaml

Purpose: example static PersistentVolume for an external iSCSI target.

Control flow declares a 1Gi `ReadWriteOnce` PV using CSI driver `iscsi.csi.k8s.io`, `volumeHandle: iscsi-data-id`, selector label `name=data-iscsiplugin`, and volume attributes consumed by `getISCSIInfo`: `targetPortal`, `portals`, `iqn`, `lun`, interface, discovery, and CHAP flags.

State is Kubernetes PV binding state and external iSCSI target state. Dependencies include a real target at the hard-coded portal, matching PVC selector, and driver node publish code. Risks include placeholder IP/IQN, `discoveryCHAPAuth: true` without secret attributes, `portals` encoded as JSON string, and no Secret object. Test signal is manual bind/publish success and yamllint.
