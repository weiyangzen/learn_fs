<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/bdev/crypto.rs -->
# sources/control-plane/mayastor/io-engine/src/bdev/crypto.rs

Purpose: Manages SPDK crypto vbdev creation/destruction and tracks crypto key usage across vbdevs.

Important APIs/types: global `KEY_CRYPTO_VBDEV_MAP` maps key names to crypto vbdev users under `RwLock`. `EncryptionKey` carries cipher, key name, key material, lengths, and optional second key. `Cipher` maps API cipher values and displays SPDK strings. `enable_dpdk_cryptodev_accel_module()` enables DPDK cryptodev and assigns encrypt/decrypt opcodes. `create_crypto_key()` creates or reuses SPDK accel crypto keys. `create_crypto_vbdev_on_base_bdev()` creates a key/user mapping, builds crypto opts, and calls `create_crypto_disk`. `destroy_crypto_vbdev()` deletes the disk, resolves/removes its key mapping, and destroys the key when last user is removed.

Control flow: key-user state is updated before crypto disk creation; destroy tolerates missing bdev but cleans key mapping when possible.

State and dependencies: mutates SPDK accel key registry, crypto vbdev registry, and process-global key map. Depends on raw libspdk crypto APIs and io-engine RPC cipher types.

Risks and test signals: if disk creation fails after `add_key_user`, map cleanup is not performed in this function. Key material is intentionally omitted from `Debug`. Test multiple vbdevs sharing a key, last-user key destruction, and creation failure cleanup behavior.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/bdev/crypto.rs -->
