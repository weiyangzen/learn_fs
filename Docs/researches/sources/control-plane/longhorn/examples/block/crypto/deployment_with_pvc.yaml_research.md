<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn/examples/block/crypto/deployment_with_pvc.yaml -->
# sources/control-plane/longhorn/examples/block/crypto/deployment_with_pvc.yaml

Purpose: example encrypted Longhorn raw block PVC consumed by a Deployment.

Important APIs/types/functions: creates block-mode PVC `longhorn-block-pvc` with StorageClass `longhorn-crypto-global`, then a single-replica `apps/v1` Deployment mounting it via `volumeDevices`.

Control flow: CSI validates crypto secrets from the StorageClass, provisions an encrypted block volume, and exposes the mapped block device to nginx at `/dev/longhorn/testblk`.

State and persistence: encrypted block data persists in the Longhorn volume; key material lives in the referenced `longhorn-crypto` Secret from companion manifests.

Dependencies/integration points: depends on Longhorn encryption support, dm-crypt/cryptsetup on nodes, CSI secret references, and `storageclass-crypto-global.yaml`.

Risks/test signals: missing or changed crypto secrets can prevent attach or make data inaccessible. Test signals are successful provisioning, node stage/publish events, device presence, and encrypted volume attach after pod restart.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn/examples/block/crypto/deployment_with_pvc.yaml -->
