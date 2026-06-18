<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/test/env/beegfs-ubuntu/beegfs-fs-2.yaml -->
# sources/control-plane/beegfs-csi-driver/test/env/beegfs-ubuntu/beegfs-fs-2.yaml

Purpose: second BeeGFS 7-style test filesystem, exercising connection auth delivered through a Kubernetes Secret volume instead of env-only data.
Important surface: `conn-auth-secret` Opaque Secret stores `connAuthFile`; StatefulSet `beegfs-fs-2` mounts it at `/etc/beegfs` and passes `connAuthFile=/etc/beegfs/connAuthFile` to mgmtd, meta, and storage containers.
Control flow/state: initializes one management target, one metadata target, and two storage targets, then exposes standard BeeGFS ports with a NodePort Service. Runtime state is container-local unless external storage is attached.
Dependencies/integration: templated `${BEEGFS_VERSION}` and `${BEEGFS_SECRET}` values; CSI config must match this auth file layout.
Risks/test signals: Secret key name differs from BeeGFS 8 manifests (`connAuthFile` versus `conn.auth`), so version-specific wiring matters; hostNetwork and NodePort increase environment coupling. Successful driver mounting across multiple FS configs validates it.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/test/env/beegfs-ubuntu/beegfs-fs-2.yaml -->
