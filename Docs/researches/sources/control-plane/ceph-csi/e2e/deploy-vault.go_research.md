# sources/control-plane/ceph-csi/e2e/deploy-vault.go

Purpose: deploys the HashiCorp Vault example stack and tenant service-account setup used by encryption/KMS e2e tests.

Important APIs/types/functions: path globals identify Vault example YAMLs. `deployVault(c, deployTimeout)` clears any helm-created KMS ConfigMap, applies Vault resources, and waits for the Vault pod. `deleteVault()` removes those resources. `createORDeleteVault(action)` applies service/statefulset, RBAC, and KMS config templates with namespace replacements. `createTenantServiceAccount(c, ns)`, `deleteTenantServiceAccount(ns)`, and `createORDeleteTenantServiceAccount(action, ns)` create/delete tenant service account resources and the admin Job that configures Vault policy.

Control flow: Vault deployment deletes `ceph-csi-encryption-kms-config` if present, applies templated YAML through kubectl input, lists pods with `app=vault`, asserts exactly one pod, and waits for it to run. Template processing replaces default namespace references and Vault service DNS with `cephCSINamespace`. Tenant setup creates the tenant SA in the tenant namespace, applies an admin job in the Ceph-CSI namespace with `TENANT_NAMESPACE` and Vault URL rewritten, then waits for the job to complete.

State and persistence: creates Vault workload/RBAC/ConfigMap objects in `cephCSINamespace`, tenant SAs in test namespaces, and Vault-side policy/kv setup through the admin job. Cleanup is kubectl-driven and assumes example labels/names remain stable.

Dependencies and integration points: uses `replaceNamespaceInTemplate()`, `retryKubectlArgs()`, `retryKubectlInput()`, `retryKubectlFile()`, pod wait/job wait helpers, Kubernetes client-go, and Gomega expectations. CephFS fscrypt tests and KMS helpers use the resulting Vault service and token/tenant configurations.

Risks: string replacement is broad (`default`, `vault.default`, `value: default`) and can mis-edit templates if content changes. The helper assumes one Vault pod and a fixed root token. Failure cleanup is limited when `logAndFail()` aborts. Tenant deletion expects both tenant and admin resources to still exist.

Test signals: Vault pod reaches Running, tenant admin job completes, KMS config exists in the CSI namespace, encrypted volume tests can read passphrases from Vault, and deletion removes the Vault resources without blocking subsequent tests.
