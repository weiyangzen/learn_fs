<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/examples/k8s/static-ro/static-ro-app.yaml -->
# sources/control-plane/beegfs-csi-driver/examples/k8s/static-ro/static-ro-app.yaml

Purpose: standalone Pod that verifies read-only mounting of a static BeeGFS volume.

Important APIs and flow: Alpine Pod mounts `csi-beegfs-static-ro-pvc` at `/mnt/static-ro` with `readOnly: true` and sleeps. Comments describe using `touch` to verify write failure.

State and persistence: Pod has no write path by design; underlying BeeGFS data is external and retained.

Dependencies and integration points: depends on static read-only PV/PVC manifests and the CSI node driver enforcing read-only mount semantics.

Risks and test signals: PV/PVC `ReadOnlyMany` does not itself enforce read-only access; the Pod claim's `readOnly: true` is essential. Test with a failed write attempt.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/examples/k8s/static-ro/static-ro-app.yaml -->
