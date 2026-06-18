# sources/distributed-fs/ceph-client/drivers/crypto/cavium/nitrox/nitrox_algs.c

Purpose: provides the aggregate crypto algorithm registration entry points for the NITROX driver.

Important APIs and control flow: `nitrox_crypto_register()` first calls `nitrox_register_skciphers()`, then `nitrox_register_aeads()`, unregistering skciphers if AEAD registration fails. `nitrox_crypto_unregister()` unregisters AEADs before skciphers.

State and persistence: no independent state; it coordinates global algorithm registration state held by the Linux crypto API.

Dependencies and integration points: depends on `nitrox_common.h`, `nitrox_skcipher.c`, and `nitrox_aead.c`. Main driver code calls these once devices are available and removes them during teardown.

Risks and test signals: risks include global registration while no usable device exists if caller ordering is wrong, and unregister ordering assumptions if partial registration changes. Test signals include algorithm list entries appearing once, AEAD registration failure rolling back skciphers, and clean removal with active transform references rejected or drained by higher layers.
