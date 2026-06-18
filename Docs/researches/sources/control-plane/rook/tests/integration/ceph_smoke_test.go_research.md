# sources/control-plane/rook/tests/integration/ceph_smoke_test.go

Primary smoke suite for a manifest-installed Rook Ceph cluster. It validates core install, monitor failover, pool resize, client CRD updates, RBD mirror CR lifecycle, and basic NFS/block/file/object workflows.

`SmokeSuite` installs `smoke-cluster` in `smoke-ns` with three mons, encrypted/compressed connections, crash pruner, volume replication, NFS CSI testing, hostname changes, selected Ceph version, and CSI operator. Storage tests delegate to NFS/block/file/object helpers. `TestMonFailover` scales a non-canary mon to zero and accepts either replacement or original recreation. `TestPoolResize` creates a pool, resizes it to 2 and back to 1, and checks mirror bootstrap token Secret when applicable. `TestCreateClient` creates/updates/deletes Ceph client caps. `TestCreateRBDMirrorClient` creates/deletes an RBDMirror CR.

State includes the full Ceph cluster, delegated storage resources, monitor deployment scale, pools, optional mirror token Secret, Ceph client CR/user, and RBDMirror CR. Dependencies are shared helpers, Rook clients, Kubernetes deployment APIs, Ceph client admin info, and testify.

Risks: many subsystems in one namespace make failures cascade; mon failover validates recovery but not always replacement; pool resize assumes enough OSD capacity; object tests skip on OpenShift; fixed helper names limit parallelism. Signals include pod counts, mon recovery, pool list/size changes, mirror token Secret, client caps, RBDMirror lifecycle, and delegated storage signals.
