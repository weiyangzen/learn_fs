# sources/control-plane/rook/deploy/examples/pool.yaml

Purpose: standard replicated Ceph block pool example.

Important APIs/types/functions: `CephBlockPool/replicapool` with failure domain `host`, replicated size 3, safe replica requirement, compression disabled, mirroring disabled in image mode, and status check settings.

Control flow: Rook creates or updates the pool and its mirroring/status configuration.

State and persistence: RBD or other data in the pool is replicated across OSD failure domains.

Dependencies/integration: often consumed by RBD storage class examples and volume replication examples.

Risks: requires enough OSDs for size 3; changing pool parameters after use can affect data placement and health.

Test signals: pool status ready, `ceph osd pool get replicapool size`, and successful PVC provisioning.
