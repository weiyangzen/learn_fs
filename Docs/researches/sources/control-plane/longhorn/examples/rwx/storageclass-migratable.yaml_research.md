<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn/examples/rwx/storageclass-migratable.yaml -->
# sources/control-plane/longhorn/examples/rwx/storageclass-migratable.yaml

Purpose: StorageClass enabling Longhorn migratable volumes.

Important APIs/types/functions: StorageClass `longhorn-migratable`, provisioner `driver.longhorn.io`, expansion enabled, replica/timeout/fromBackup parameters, and `migratable: "true"`.

Control flow: PVCs using this class create Longhorn volumes marked for migration/live-migration capable behavior.

State and persistence: StorageClass policy influences Longhorn volume spec; volume data persists in created PVCs.

Dependencies/integration points: depends on Longhorn migration support and consumer workloads that use compatible attach semantics.

Risks/test signals: migratable behavior has scheduling and attachment constraints; not every workload should use it. Test signals are PVC provisioning, migration workflow, attach/detach events, and workload continuity during migration.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn/examples/rwx/storageclass-migratable.yaml -->
