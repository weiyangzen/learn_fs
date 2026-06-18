<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn/examples/block/crypto/secret-crypto-global.yaml -->
# sources/control-plane/longhorn/examples/block/crypto/secret-crypto-global.yaml

Purpose: global crypto Secret for block-mode encrypted Longhorn examples.

Important APIs/types/functions: Kubernetes `Secret` named `longhorn-crypto` in `longhorn-system` with `stringData` keys `CRYPTO_KEY_VALUE` and optional `CRYPTO_KEY_PROVIDER`.

Control flow: CSI secret references in encrypted StorageClasses resolve this Secret during provision/node stage/publish operations.

State and persistence: stores encryption passphrase material in Kubernetes Secret storage.

Dependencies/integration points: depends on Kubernetes Secret access by Longhorn CSI components and matching StorageClass secret names/namespaces.

Risks/test signals: example passphrase is insecure and rotation affects volume accessibility. Test signals are secret existence, CSI permission to read it, and successful encrypted block volume provisioning.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn/examples/block/crypto/secret-crypto-global.yaml -->
