<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn/examples/crypto/storageclass-crypto-per-volume.yaml -->
# sources/control-plane/longhorn/examples/crypto/storageclass-crypto-per-volume.yaml

Purpose: encrypted StorageClass pattern where each PVC references a same-namespace Secret named after the PVC.

Important APIs/types/functions: StorageClass `longhorn-crypto-per-volume` uses `${pvc.name}` and `${pvc.namespace}` in CSI secret parameters for provisioner, node publish, and node stage.

Control flow: on PVC creation, CSI resolves the Secret in the claim namespace, enabling per-volume/per-namespace key isolation.

State and persistence: class stores policy; each namespace stores its own Secret and Longhorn stores encrypted volume data.

Dependencies/integration points: depends on Kubernetes CSI secret template substitution, namespace-local Secret management, and Longhorn encryption.

Risks/test signals: Secret lifecycle must be coordinated with PVC lifecycle; deleting the Secret can make data inaccessible. Test signals are provisioning with namespace-local Secret, cross-namespace isolation, and attach after pod reschedule.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn/examples/crypto/storageclass-crypto-per-volume.yaml -->
