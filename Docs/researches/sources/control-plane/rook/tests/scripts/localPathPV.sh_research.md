<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/tests/scripts/localPathPV.sh -->
# sources/control-plane/rook/tests/scripts/localPathPV.sh

Purpose: creates local PersistentVolumes and a manual StorageClass for Rook PVC-based integration tests, using host directories for monitors and block devices/partitions for OSDs, DB, and WAL.

Important APIs and control flow: it selects a scratch block device, validates it, labels the node, deletes previous `type=local` PVs, creates three filesystem monitor PVs under `/var/lib/rook/rook-integration-test`, optionally adds DB and WAL block PVs, chooses OSD count based on DB/WAL/LVM/test env, creates one or two OSD block PVs, then applies a `manual` no-provisioner StorageClass with `WaitForFirstConsumer`.

State, persistence, and integration: creates host directories, node labels, PVs, and a StorageClass. Dependencies include `kubectl`, `sudo`, `lsblk`, a valid block device, and local-path PV support. Risks include deleting all local-labeled PVs, fixed PV names, single-node assumption, and direct host path/block exposure. Test signals are `kubectl get pv -o wide` and subsequent PVC binding/OSD provisioning.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/tests/scripts/localPathPV.sh -->
