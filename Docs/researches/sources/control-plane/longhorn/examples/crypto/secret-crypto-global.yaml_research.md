<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn/examples/crypto/secret-crypto-global.yaml -->
# sources/control-plane/longhorn/examples/crypto/secret-crypto-global.yaml

Purpose: basic global crypto Secret for encrypted filesystem-volume examples.

Important APIs/types/functions: Kubernetes Secret `longhorn-crypto` in `longhorn-system` with passphrase `CRYPTO_KEY_VALUE` and provider `CRYPTO_KEY_PROVIDER`.

Control flow: encrypted StorageClasses reference this Secret for CSI provision, node stage, and node publish operations.

State and persistence: Kubernetes stores the passphrase; encrypted Longhorn volumes depend on it for access.

Dependencies/integration points: integrates with Longhorn CSI and encrypted StorageClass examples.

Risks/test signals: static shared passphrase is only an example. Test signals are secret readability by CSI and successful encrypted PVC lifecycle.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn/examples/crypto/secret-crypto-global.yaml -->
