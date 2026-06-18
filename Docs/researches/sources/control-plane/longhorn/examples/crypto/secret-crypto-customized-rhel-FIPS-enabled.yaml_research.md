<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn/examples/crypto/secret-crypto-customized-rhel-FIPS-enabled.yaml -->
# sources/control-plane/longhorn/examples/crypto/secret-crypto-customized-rhel-FIPS-enabled.yaml

Purpose: FIPS/RHEL-oriented crypto Secret example for encrypted Longhorn volumes.

Important APIs/types/functions: Secret `longhorn-crypto` includes passphrase/provider plus cipher `aes-cbc-essiv:sha256`, hash `sha256`, key size `256`, and PBKDF `pbkdf2`; optional PBKDF iteration and memory settings are documented.

Control flow: CSI encryption operations consume these keys to configure cryptsetup in a FIPS-compatible way, avoiding non-FIPS KDFs.

State and persistence: stores encryption parameters and passphrase in Kubernetes Secret storage.

Dependencies/integration points: depends on Longhorn encrypted volume support, node cryptsetup behavior on RHEL/FIPS systems, and StorageClass secret references.

Risks/test signals: wrong cipher/KDF choices can fail attach or violate FIPS expectations; example passphrase is not production-safe. Test signals are successful encrypted volume creation on FIPS nodes, cryptsetup compatibility, and attach after node reboot.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn/examples/crypto/secret-crypto-customized-rhel-FIPS-enabled.yaml -->
