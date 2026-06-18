# sources/control-plane/longhorn/deploy/backupstores/base/minio/kustomization.yaml

Purpose: Kustomize entry point for the MinIO backupstore base.

Important APIs/types/functions: `kustomize.config.k8s.io/v1beta1` `Kustomization` referencing `minio-backupstore.yaml`.

Control flow: Kustomize includes the MinIO manifest as the entire base output.

State and persistence: no runtime state is stored here. Resource inclusion determines whether MinIO test backupstore objects are emitted.

Dependencies/integration: depends on the adjacent MinIO manifest and any overlays that populate secrets or persistence.

Risks: the base inherits hard-coded namespaces and empty secrets from the resource file. Renames or path changes require updating the kustomization.

Test signals: run `kustomize build sources/control-plane/longhorn/deploy/backupstores/base/minio` and verify the output includes the MinIO secrets, deployment, and service.
