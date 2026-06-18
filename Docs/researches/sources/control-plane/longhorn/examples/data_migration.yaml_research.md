<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn/examples/data_migration.yaml -->
# sources/control-plane/longhorn/examples/data_migration.yaml

Purpose: one-shot Job for copying data from one PVC to another.

Important APIs/types/functions: `batch/v1` Job `volume-migration`, one completion, `backoffLimit: 3`, container `registry.suse.com/bci/golang:1.24`, command `cp -r -v /mnt/old/. /mnt/new`, and two PVC volumes.

Control flow: Kubernetes mounts source and target PVCs, runs the copy command once, and marks the Job complete or retries on failure.

State and persistence: mutates target PVC contents; source PVC is read/write mounted by default and not explicitly protected.

Dependencies/integration points: depends on both PVCs being in the selected namespace and attachable to the same pod/node under their access modes.

Risks/test signals: `cp -r` may not preserve all metadata, sparse files, hard links, ownership, or live-write consistency. Test signals are Job completion, copied file counts/checksums, application quiescence, and target workload validation.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn/examples/data_migration.yaml -->
