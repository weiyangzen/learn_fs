# sources/control-plane/rook/deploy/examples/nfs-test.yaml

Purpose: supplies a reduced-size NFS example for tests, including the `CephNFS` daemon and its backing built-in pool.

Important APIs/types/functions: `CephNFS/my-nfs` with `server.active: 1` and debug log level, plus `CephBlockPool/builtin-nfs` mapped to the Ceph pool `.nfs` with replica size 1 and `requireSafeReplicaSize: false`.

Control flow: Rook reconciles the pool, then starts one NFS server daemon using the built-in pool for NFS-Ganesha state.

State and persistence: NFS daemon state is stored in the `.nfs` Ceph pool; the CRs persist desired daemon count and pool properties.

Dependencies/integration: requires Rook Ceph CRDs, an active Ceph cluster, and clients or tests that create exports.

Risks: one-replica pool is unsafe outside test clusters; debug logging can be verbose.

Test signals: CephNFS status ready, `.nfs` pool exists, and test exports can be mounted.
