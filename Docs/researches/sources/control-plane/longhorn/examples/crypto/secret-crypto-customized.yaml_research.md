<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn/examples/crypto/secret-crypto-customized.yaml -->
# sources/control-plane/longhorn/examples/crypto/secret-crypto-customized.yaml

Purpose: customized crypto Secret example for encrypted Longhorn volumes using explicit cipher, hash, size, and PBKDF.

Important APIs/types/functions: Secret keys include `CRYPTO_KEY_VALUE`, `CRYPTO_KEY_PROVIDER`, `CRYPTO_KEY_CIPHER: aes-xts-plain64`, `CRYPTO_KEY_HASH: sha256`, `CRYPTO_KEY_SIZE: 256`, and `CRYPTO_PBKDF: argon2i`.

Control flow: Longhorn CSI reads these values during encrypted volume operations and passes them to the node crypto stack.

State and persistence: persists key configuration and passphrase in Kubernetes Secret storage.

Dependencies/integration points: depends on cryptsetup support for the selected cipher and PBKDF on all target nodes.

Risks/test signals: heterogeneous node crypto versions can make argon2i or cipher handling inconsistent. Test signals are encrypted PVC provisioning, node-stage logs, and cross-node attach tests.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn/examples/crypto/secret-crypto-customized.yaml -->
