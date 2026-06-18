# sources/control-plane/ceph-csi/e2e/namespace.go

Purpose: provides namespace lifecycle and template namespace-replacement helpers for e2e-deployed CSI components and auxiliary resources.

Important APIs/types/functions: `createNamespace(c, name)` creates a Namespace if needed and polls until it can be retrieved. `deleteNamespace(c, name)` deletes a Namespace if present and polls until it disappears. `replaceNamespaceInTemplate(filePath)` reads a YAML file and rewrites `namespace: default` or `namespace: "default"` to the current `cephCSINamespace`.

Control flow: creation uses client-go `Namespaces().Create()` and ignores AlreadyExists, then polls with retryable API error handling. Deletion ignores NotFound and polls until the API returns NotFound. Template replacement is a simple read and two `strings.ReplaceAll()` passes.

State and persistence: creates and deletes Kubernetes namespaces. Template replacement does not persist to disk; it returns modified YAML content for kubectl input.

Dependencies and integration points: uses Kubernetes CoreV1 Namespace APIs, wait polling, API error helpers, framework logging, and global `deployTimeout`, `poll`, and `cephCSINamespace`. Deployment, Vault, NFS, CephFS, and NVMe-oF resource deployers call these helpers.

Risks: namespace deletion can block on finalizers from leaked resources. Template replacement only handles exact namespace lines and may miss embedded names or replace too little for new templates. It does not preserve quotes when replacing `"default"`.

Test signals: namespace reaches gettable state before resources are applied, disappears after teardown, and templated resources land in the intended Ceph-CSI namespace.
