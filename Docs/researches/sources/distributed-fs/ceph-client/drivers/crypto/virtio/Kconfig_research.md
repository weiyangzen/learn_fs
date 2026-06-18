
# sources/distributed-fs/ceph-client/drivers/crypto/virtio/Kconfig

Purpose: build-time configuration for the virtio crypto driver.

Important APIs, types, and functions: `config CRYPTO_DEV_VIRTIO` defines a tristate option named "VirtIO crypto driver". It depends on `VIRTIO` and selects crypto subsystems needed by this implementation: AEAD, AKCIPHER2, SKCIPHER, CRYPTO_ENGINE, RSA, and MPILIB.

Control flow: Kconfig selection controls whether the module is built in, built as `virtio_crypto`, or omitted. No runtime logic is present.

State and persistence: no runtime state is stored in this file. It affects kernel configuration state and module availability.

Dependencies and integration points: integrates with the kernel crypto menu and virtio stack. The selected RSA/MPILIB symbols match `virtio_crypto_akcipher_algs.c`, while skcipher and engine symbols support AES-CBC request queuing.

Risks and test signals: dependency drift is the key risk. If algorithm files gain AEAD/hash implementations, Kconfig selections must remain aligned. Test signals are successful allmodconfig/build coverage, module load with `CONFIG_CRYPTO_DEV_VIRTIO=m`, and absence of unresolved crypto symbols.
