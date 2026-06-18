<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/tests/manifests/test-on-pvc-db.yaml -->
# sources/control-plane/rook/tests/manifests/test-on-pvc-db.yaml

Purpose: YAML fragment adding a BlueStore metadata device PVC template to a PVC-backed OSD device set. It is intended for composition into a larger cluster manifest.

Important structure: declares a volume claim template named `metadata` requesting 2Gi, `manual` StorageClass, block volume mode, and `ReadWriteOnce` access.

State, persistence, and integration: when inserted under `volumeClaimTemplates`, it provisions a separate block PVC used as BlueStore DB/metadata storage. Dependencies include a manual StorageClass and matching local PVs. Risks include fragment-only indentation sensitivity and insufficient 2Gi capacity if reused outside tests. Test signals are OSD prepare success and PVC binding for the metadata device.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/tests/manifests/test-on-pvc-db.yaml -->
