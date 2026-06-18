<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/examples/k8s/all/all-app.yaml -->
# sources/control-plane/beegfs-csi-driver/examples/k8s/all/all-app.yaml

Purpose: combined demo Pod that mounts dynamic, generic ephemeral, static read/write, and static read-only BeeGFS volumes at once.

Important APIs and flow: a single Alpine Pod mounts four volumes at `/mnt/dyn`, `/mnt/ge`, `/mnt/static`, and `/mnt/static-ro`. Its command creates UID-named marker files in writable mounts and sleeps for seven days. The generic ephemeral volume embeds a PVC template using `csi-beegfs-ge-sc`; the others reference named PVCs.

State and persistence: writes marker files into BeeGFS-backed volumes; read-only mount should reject writes. Pod state is ephemeral, storage state depends on backing PV/PVC reclaim behavior.

Dependencies and integration points: integrates all example StorageClasses, PVCs, and PVs; depends on the CSI provisioner, node plugin, and BeeGFS management host replacement.

Risks and test signals: `localhost` and `name` placeholders must be replaced. Test with `kubectl exec` listing/touching each mount and verifying read-only failure.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/examples/k8s/all/all-app.yaml -->
