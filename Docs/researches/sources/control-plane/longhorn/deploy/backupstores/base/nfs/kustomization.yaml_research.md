# sources/control-plane/longhorn/deploy/backupstores/base/nfs/kustomization.yaml

Purpose: Kustomize entry point for the NFS backupstore base.

Important APIs/types/functions: `kustomize.config.k8s.io/v1beta1` `Kustomization` referencing `nfs-backupstore.yaml`.

Control flow: Kustomize builds or applies the adjacent NFS manifest as the base's resource set.

State and persistence: no runtime state is stored directly. It only controls inclusion of NFS test backupstore resources.

Dependencies/integration: depends on the adjacent NFS manifest and optional overlays for persistence, namespaces, or image pinning.

Risks: hard-coded namespaces and ephemeral storage from the resource file remain unless patched by overlays. Moving the manifest path breaks the base.

Test signals: run `kustomize build sources/control-plane/longhorn/deploy/backupstores/base/nfs` and verify the output includes the NFS deployment and service.
