<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/tests/manifests/test-on-pvc-wal.yaml -->
# sources/control-plane/rook/tests/manifests/test-on-pvc-wal.yaml

Purpose: YAML fragment adding a BlueStore WAL PVC template to a PVC-backed OSD device set. It complements the metadata/DB fragment for WAL-specific tests.

Important structure: declares a `wal` volume claim template requesting 2Gi, using `manual` StorageClass, block volume mode, and `ReadWriteOnce`.

State, persistence, and integration: when merged into a cluster storage device set, it provisions a separate WAL block PVC. Dependencies include local manual PV preparation and Rook OSD PVC orchestration. Risks include fragment-only YAML context and small fixed size. Test signals are bound WAL PVCs and successful OSD provisioning with WAL device assignment.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/tests/manifests/test-on-pvc-wal.yaml -->
