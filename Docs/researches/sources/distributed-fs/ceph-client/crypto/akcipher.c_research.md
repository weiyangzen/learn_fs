# sources/distributed-fs/ceph-client/crypto/akcipher.c

Purpose: provides the generic public-key cipher (`akcipher`) front end: allocation, spawn grabbing, registration, instance registration, proc/netlink reporting, transform lifecycle, default unsupported operations, and synchronous encrypt/decrypt wrappers.

Important APIs, types, and functions: exports `crypto_grab_akcipher()`, `crypto_alloc_akcipher()`, `crypto_register_akcipher()`, `crypto_unregister_akcipher()`, `akcipher_register_instance()`, `crypto_akcipher_sync_encrypt()`, and `crypto_akcipher_sync_decrypt()`. Internal helper state is `struct crypto_akcipher_sync_data`.

Control flow and behavior: registration fills missing encrypt/decrypt/private-key callbacks with `-ENOSYS` defaults, stamps the crypto type, and registers the base algorithm. Sync helpers allocate one buffer large enough for request, algorithm request context, and max(input, output), copy input into it, set a single SG for in-place operation, wait for completion, copy output back, and wipe/free the request buffer.

State and persistence: transform-private state belongs to individual algorithms such as RSA. The sync helper uses temporary heap state only. Registered algorithms persist in the global crypto registry until unregistered.

Dependencies and integration points: depends on `crypto/internal/akcipher.h`, scatterlists, crypto wait helpers, generic algorithm/template registration, and cryptouser reporting. Public-key implementations and padding templates register through this layer.

Risks and correctness concerns: synchronous buffer length computation must avoid overflow and must wipe sensitive material. `crypto_akcipher_sync_encrypt()` returns only operation status while decrypt returns output length on success, so callers must honor the API distinction. Default `-ENOSYS` callbacks avoid NULL calls but can hide missing implementation coverage until runtime.

Test signals: RSA encrypt/decrypt/signature padding through akcipher, sync wrapper success and insufficient-output behavior, async completion wait handling, invalid keys returning `-ENOSYS` or algorithm errors, registration with missing callbacks, and netlink/proc reporting.
