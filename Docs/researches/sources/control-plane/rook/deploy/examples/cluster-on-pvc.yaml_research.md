
# sources/control-plane/rook/deploy/examples/cluster-on-pvc.yaml

Purpose: demonstrates a production-style cloud deployment where mons and OSDs are backed by dynamically provisioned PVCs, using `gp2-csi` as the sample storage class.

Important APIs/types/functions: Rook `CephCluster`, mon PVC template, `cephVersion` v20.2.1, two mgrs, dashboard SSL, monitoring options, log collector, `storageClassDeviceSets` with portable OSDs, topology spread constraints, prepare pod anti-affinity, optional metadata/WAL PVC templates, priority classes, disruption management, and commented KMS/key rotation configuration.

Control flow: the operator creates mon PVCs and OSD PVCs from the storage class, spreads OSD pods by hostname/zone where possible, tunes device class behavior for cloud disks, and manages PDBs during disruptions.

State and persistence: Ceph data persists in dynamically provisioned PVs plus host metadata under `/var/lib/rook`. Optional KMS secrets/config affect encryption key state when enabled.

Dependencies/integration: depends on a working `gp2-csi` or replacement storage class, topology labels, Rook common/operator manifests, Ceph image availability, and optional Vault/KMS resources if uncommented.

Risks: sample storage class and zone topology may not match the cluster. Portable OSD behavior relies on storage that can attach across nodes. Misconfigured KMS blocks encrypted OSD startup. Cloud disk performance affects Ceph health.

Test signals: render/apply with a real storage class, verify PVC provisioning, OSD spread, mgr failover, log collection, PDB creation, and optional KMS secret validation.
