<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/test/env/beegfs-ubuntu/beegfs8-fs-2.yaml -->
# sources/control-plane/beegfs-csi-driver/test/env/beegfs-ubuntu/beegfs8-fs-2.yaml

Purpose: BeeGFS 8 test filesystem with TLS disabled and connection auth mounted from a Secret.
Important surface: Secret `conn-auth-secret` stores `conn.auth`; mgmtd starts with `--tls-disable=true`; meta and storage containers mount `/etc/beegfs` and use `connAuthFile=/etc/beegfs/conn.auth`.
Control flow/state: initializes a local mgmtd sqlite database plus metadata and two storage targets, using host networking and a NodePort Service for BeeGFS ports.
Dependencies/integration: templated `${BEEGFS_VERSION}` and `${BEEGFS_SECRET}`; paired with CSI test config to exercise BeeGFS 8 non-TLS auth layout.
Risks/test signals: Secret filename is version-specific; hostNetwork port collisions can prevent pod readiness; lack of durable storage means restart behavior may not mimic real clusters. Passing e2e mounts against this FS validates compatibility.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/test/env/beegfs-ubuntu/beegfs8-fs-2.yaml -->
