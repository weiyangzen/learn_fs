# sources/distributed-fs/openafs/src/external/heimdal/hcrypto/hmac.h

Purpose: declares the hcrypto HMAC API and `HMAC_CTX` layout.

Important APIs/types/functions: renames HMAC symbols to `hc_*`, defines `HMAC_MAX_MD_CBLOCK`, declares opaque typedef `HMAC_CTX` while exposing `struct hc_HMAC_CTX`, and prototypes context lifecycle, size, init/update/final, and one-shot `HMAC`.

Control flow: consumers allocate `HMAC_CTX`, call init/init_ex/update/final/cleanup, or use one-shot `HMAC`. The actual data flow is in `hmac.c`.

State and persistence: defines persistent per-HMAC fields: digest pointer, engine pointer, nested EVP context, key/digest buffer length, opad, ipad, and digest buffer.

Dependencies and integration points: includes `hcrypto/evp.h`; therefore digest descriptors and engine types are shared with the EVP layer. It is used by PBKDF2 and validation code.

Risks and test signals: layout exposure makes ABI compatibility important. Compile-time signature checks plus HMAC known-answer tests are the primary signals.
