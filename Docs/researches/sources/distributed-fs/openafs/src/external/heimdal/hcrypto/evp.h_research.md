# sources/distributed-fs/openafs/src/external/heimdal/hcrypto/evp.h

Purpose: defines the public hcrypto EVP compatibility API and the in-memory descriptor/context layouts used by `evp.c` and provider implementations.

Important APIs/types/functions: typedefs cover `EVP_MD_CTX`, `EVP_PKEY`, `EVP_MD`, `EVP_CIPHER`, and `EVP_CIPHER_CTX`. `struct hc_CIPHER` defines metadata, mode/flag bits, init/do_cipher/cleanup/ctrl callbacks, context size, and app data. `struct hc_CIPHER_CTX` stores selected cipher, engine, direction, IVs, buffers, app data, key length, flags, provider data, and block mask. `struct hc_evp_md` defines digest sizes and init/update/final/cleanup callbacks. The header declares all digest, cipher, KDF, random-key, ctrl, and registration APIs implemented in `evp.c`.

Control flow: callers allocate or stack-initialize contexts using the declared APIs, never by directly calling provider callbacks. Provider files populate descriptor structs whose callbacks are invoked by the generic EVP code.

State and persistence: the header itself has no state, but it fixes ABI-sensitive state layout for contexts and descriptors. `EVP_MAX_IV_LENGTH`, `EVP_MAX_BLOCK_LENGTH`, and `EVP_MAX_MD_SIZE` bound internal buffers and caller expectations.

Dependencies and integration points: includes `hcrypto/engine.h`, exposes C++ linkage guards, and renames public symbols to `hc_*`. It must stay consistent with `evp.c`, `evp-hcrypto.c`, HMAC/PBKDF2 callers, and external code compiled against Heimdal hcrypto.

Risks and test signals: risks are ABI drift, mode flag misuse, and buffer constant mismatches with provider block sizes. Compile coverage across all provider files and runtime EVP validation are the useful signals.
