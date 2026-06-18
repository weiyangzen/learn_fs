# sources/distributed-fs/lustre-release/include/linux/lnet/lnet_crypto.h

Purpose: kernel internal crypto helper declarations for LNet/libcfs hashing.

Important APIs/functions: `cfs_crypto_hash_init()` creates an async hash request for an algorithm and optional key. `cfs_crypto_hash_update_page()` and `cfs_crypto_hash_update()` feed page or linear data. `cfs_crypto_hash_final()` completes the digest. `cfs_crypto_register()`/`cfs_crypto_unregister()` manage algorithm registration/lifecycle, and `cfs_crypto_hash_speed()` reports measured speed.

Control flow: callers select an algorithm from the UAPI enum, initialize a request, perform one or more updates, finalize into a hash buffer, and release/cleanup through implementation-specific behavior.

State and persistence: no persistent state in the header. Implementations maintain crypto API registrations and speed tables.

Dependencies/integration: includes `<asm/page.h>` and `uapi/linux/lnet/lnet-crypto.h`, integrating kernel crypto operations with the shared algorithm descriptors.

Risks and test signals: risks include unsupported algorithms, key length mismatch, page offset/length errors, async crypto failure, and digest buffer sizing. Test signals are each enum algorithm, page and linear updates, digest-size reporting, registration/unregistration, and speed table population.
