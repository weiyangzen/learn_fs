# sources/control-plane/longhorn/deploy/backupstores/base/cifs/kustomization.yaml

Purpose: Kustomize entry point for the CIFS backupstore base.

Important APIs/types/functions: `kustomize.config.k8s.io/v1beta1` `Kustomization` referencing `cifs-backupstore.yaml`.

Control flow: Kustomize includes the single CIFS manifest when building or applying this base.

State and persistence: no runtime state is stored directly. It controls resource inclusion for the CIFS test backupstore.

Dependencies/integration: depends on the adjacent CIFS manifest. Overlays can patch image, namespaces, secrets, service type, or persistence.

Risks: hard-coded namespaces in the included resource remain unless overlays patch them. Moving the resource file breaks the kustomization.

Test signals: run `kustomize build` for the directory and ensure the output includes both secrets, the Samba deployment, and the headless service.
