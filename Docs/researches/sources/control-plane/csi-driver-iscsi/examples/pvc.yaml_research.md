## sources/control-plane/csi-driver-iscsi/examples/pvc.yaml

Purpose: example claim that binds to the static iSCSI PV.

Control flow declares a `ReadWriteOnce` 1Gi PVC in storage class `manual` with a selector matching label `name=data-iscsiplugin`. State is Kubernetes PVC binding state.

Dependencies are the PV example's label and storage class, and the default namespace unless applied elsewhere. Risks include static binding only, no dynamic provisioning despite StorageClass presence, and hard-coded name expected by the pod example. Test signal is PVC Bound status and yamllint.
