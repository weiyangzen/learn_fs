# sources/control-plane/longhorn/deploy/backupstores/base/azurite/kustomization.yaml

Purpose: Kustomize entry point for the Azurite backupstore base.

Important APIs/types/functions: `kustomize.config.k8s.io/v1beta1` `Kustomization` with one resource, `azurite-backupstore.yaml`.

Control flow: `kubectl apply -k` or `kustomize build` reads this file and includes the Azurite manifest as the complete resource set for the base.

State and persistence: no runtime state is stored here; it determines which resources Kustomize emits.

Dependencies/integration: depends on the adjacent Azurite manifest path. It can be overlaid by higher-level Kustomize directories for namespace, patches, or secret data.

Risks: with only a single resource and no namespace transformer, the hard-coded namespaces in the resource file remain authoritative. Renaming or moving the manifest breaks the base.

Test signals: run `kustomize build sources/control-plane/longhorn/deploy/backupstores/base/azurite` and verify it emits the secret, deployment, and service from the resource file.
