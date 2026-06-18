<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn/examples/crypto/storageclass-crypto-global.yaml -->
# sources/control-plane/longhorn/examples/crypto/storageclass-crypto-global.yaml

Purpose: encrypted Longhorn StorageClass using a single global Secret in `longhorn-system`.

Important APIs/types/functions: `StorageClass` `longhorn-crypto-global`, provisioner `driver.longhorn.io`, expansion enabled, `encrypted: "true"`, replica/timeout/fromBackup parameters, and CSI secret parameters for provisioner, node publish, and node stage.

Control flow: PVC creation invokes Longhorn CSI with encryption enabled and secret checks; node staging/publishing uses the global Secret to unlock the volume.

State and persistence: controls encrypted volume provisioning; stores no runtime data itself.

Dependencies/integration points: depends on companion `longhorn-crypto` Secret and CSI secret parameter substitution.

Risks/test signals: global key blast radius is high. Test signals are provisioning failure when Secret is absent, success when present, mount after restart, and optional expansion tests with node-expand secrets if feature gates are enabled.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn/examples/crypto/storageclass-crypto-global.yaml -->
