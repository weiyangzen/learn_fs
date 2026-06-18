# sources/control-plane/rook/deploy/examples/osd-purge.yaml

Purpose: runs the Rook OSD purge job to remove an OSD from a Ceph cluster.

Important APIs/types/functions: `batch/v1 Job/rook-ceph-purge-osd`, image `docker.io/rook/ceph:master`, args invoking OSD removal with an OSD ID placeholder, service account `rook-ceph-purge-osd`, Ceph admin secret and config volumes, and environment variables such as `ROOK_MON_ENDPOINTS`, `ROOK_CEPH_USERNAME`, `ROOK_FSID`, and `ROOK_LOG_LEVEL`.

Control flow: the job starts a container with Ceph/Rook config, authenticates to the cluster, and executes the purge command for the configured OSD.

State and persistence: modifies durable Ceph cluster state by removing OSD metadata/auth/CRUSH entries; Kubernetes job state records execution.

Dependencies/integration: requires admin credentials, monitor endpoints, correct FSID, and prior OSD drain/safe-to-destroy handling.

Risks: wrong OSD ID or FSID can destroy the wrong daemon metadata; image tag is mutable.

Test signals: job completes, `ceph osd tree` no longer lists the OSD, and Ceph health returns to expected state.
