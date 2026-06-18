<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/examples/k8s/all/static-ro-pvc.yaml -->
# sources/control-plane/beegfs-csi-driver/examples/k8s/all/static-ro-pvc.yaml

Purpose: PVC that binds to the combined example's static read-only BeeGFS PV.

Important APIs and flow: requests `ReadOnlyMany`, `5Gi`, disables dynamic provisioning with `storageClassName: ""`, and pins `volumeName: csi-beegfs-static-ro-pv`.

State and persistence: binding state is stored in Kubernetes; underlying BeeGFS content is externally managed and retained.

Dependencies and integration points: requires the named static read-only PV and a Pod volume reference with `readOnly: true` for enforcement.

Risks and test signals: the manifest comment highlights that capacity is required by Kubernetes even though semantically arbitrary. Test PVC binding and read-only Pod behavior.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/examples/k8s/all/static-ro-pvc.yaml -->
