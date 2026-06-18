<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/test/env/beegfs-ubuntu/beegfs-fs-1.yaml -->
# sources/control-plane/beegfs-csi-driver/test/env/beegfs-ubuntu/beegfs-fs-1.yaml

Purpose: Kubernetes test environment manifest for a BeeGFS 7-style single-node filesystem named `beegfs-fs-1`.
Important surface: StatefulSet with `beegfs-mgmtd`, `beegfs-meta`, and `beegfs-storage` containers using `${BEEGFS_VERSION}` images; initialization is driven by `beegfs_setup_*` env vars; connection auth is injected through `CONN_AUTH_FILE_DATA=${BEEGFS_SECRET}`.
Control flow/state: the containers initialize management, metadata, and two storage targets under `/mnt/*` paths, run with `hostNetwork: true`, and expose management/meta/storage TCP and UDP ports through a NodePort Service.
Dependencies/integration: consumed by test environment templating that substitutes BeeGFS version and secret; integrates with CSI config that points at the management host.
Risks/test signals: no persistent volume claims are declared, so data lifetime follows pod/container storage; hostNetwork can collide with ports on shared nodes; typo-prone setup target names affect filesystem initialization. Service readiness and CSI mount success are the signals.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/test/env/beegfs-ubuntu/beegfs-fs-1.yaml -->
