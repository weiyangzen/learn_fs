
# sources/distributed-fs/ceph-client/drivers/crypto/virtio/Makefile

Purpose: composes the virtio crypto module objects.

Important APIs, types, and functions: `obj-$(CONFIG_CRYPTO_DEV_VIRTIO) += virtio_crypto.o` declares the module, and `virtio_crypto-objs` links skcipher algorithms, akcipher algorithms, device manager, and core virtio driver objects.

Control flow: no runtime flow; object ordering ensures all implementation units are linked into `virtio_crypto.o`.

State and persistence: no runtime state. Build state is driven by `CONFIG_CRYPTO_DEV_VIRTIO`.

Dependencies and integration points: integrates with Kbuild and the Kconfig option in the same directory. All listed objects share `virtio_crypto_common.h`.

Risks and test signals: missing an object would surface as unresolved symbols for registration or request paths. Test signals are module build, `modinfo virtio_crypto`, and load/unload with both skcipher and akcipher code linked.
