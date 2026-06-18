<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn/examples/block/crypto/storageclass-crypto-global.yaml -->
# sources/control-plane/longhorn/examples/block/crypto/storageclass-crypto-global.yaml

Purpose: StorageClass for globally keyed encrypted Longhorn block volumes.

Important APIs/types/functions: `storage.k8s.io/v1` `StorageClass` named `longhorn-crypto-global`, provisioner `driver.longhorn.io`, `allowVolumeExpansion: true`, `encrypted: "true"`, replica/timeout/fromBackup parameters, and CSI provisioner/node-publish/node-stage secret references.

Control flow: PVCs using this class trigger Longhorn CSI provisioning with encryption enabled and early secret validation. Node operations retrieve the same global Secret from `longhorn-system`.

State and persistence: class itself has no data; it controls encrypted Longhorn volume creation and secret lookup.

Dependencies/integration points: depends on `longhorn-crypto` Secret, CSI external provisioner/node plugins, and node crypto tooling.

Risks/test signals: all volumes share one passphrase in this example. Online expansion secret references are commented and require feature gates if enabled. Test signals are StorageClass validation, PVC provisioning, attach/mount, and expansion behavior if enabled.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn/examples/block/crypto/storageclass-crypto-global.yaml -->
