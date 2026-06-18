<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn/examples/crypto/storageclass-crypto-per-volume-dedicated-namespace.yaml -->
# sources/control-plane/longhorn/examples/crypto/storageclass-crypto-per-volume-dedicated-namespace.yaml

Purpose: encrypted StorageClass pattern where each PVC uses a Secret named after the PVC, stored in `longhorn-system`.

Important APIs/types/functions: StorageClass `longhorn-secure-per-volume-ns-longhorn-system` uses `${pvc.name}` for CSI secret names and fixed secret namespace `longhorn-system`.

Control flow: CSI parameter substitution resolves each PVC's name to a Secret and uses that Secret for provision/node operations.

State and persistence: class defines lookup convention only; per-volume secrets and Longhorn volumes carry persistent state.

Dependencies/integration points: depends on PVC-name-based Secrets pre-created in `longhorn-system`, Longhorn CSI token substitution, and encryption tooling.

Risks/test signals: PVC names must be valid Secret names and must not collide across namespaces if centralized in `longhorn-system`. Test signals are per-PVC secret creation, provisioning success, attach in source namespace, and failure modes for missing secret.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn/examples/crypto/storageclass-crypto-per-volume-dedicated-namespace.yaml -->
