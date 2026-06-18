# sources/control-plane/rook/deploy/examples/sqlitevfs-client.yaml

Purpose: demonstrates a Ceph client and helper deployment for SQLite VFS integration with Ceph.

Important APIs/types/functions: `CephClient/sqlitevfs` with caps, `ServiceAccount/sqlitevfs-setup`, ClusterRole/Binding for reading secrets/configmaps and patching deployment state, and `Deployment/sqlitevfs` with init/setup behavior plus an Alpine runtime container.

Control flow: Rook creates a Ceph client secret; the setup container uses Kubernetes API access to retrieve config/credentials and prepare `/libsqliteceph`; the main container runs with those artifacts mounted.

State and persistence: client identity persists in Ceph auth and Kubernetes Secret; deployment volume state is pod-local.

Dependencies/integration: requires Rook Ceph client controller, kubectl image, and Ceph config secrets.

Risks: broad cluster RBAC for setup should not be copied blindly; old image versions are examples.

Test signals: client secret created, setup completes, and the application can open SQLite data through Ceph VFS.
