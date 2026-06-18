# sources/distributed-fs/ceph-client/crypto/aes.c

Purpose: registers the generic AES block cipher backed by `crypto_lib_aes`, plus optional AES-based shash MAC algorithms for CMAC, XCBC-MAC, and CBC-MAC depending on enabled Kconfig symbols.

Important APIs, types, and functions: core cipher callbacks are `crypto_aes_setkey()`, `crypto_aes_encrypt()`, and `crypto_aes_decrypt()`. Optional MAC callbacks include CMAC/XCBC setkey/init/update/final/digest helpers and CBC-MAC setkey/init/update/final/digest helpers. Module init/exit register `alg` and `mac_algs`.

Control flow and behavior: module init registers the `aes` cipher first, then registers any compiled shash MACs; failure unregisters the cipher. AES transform context stores `struct aes_key`. CMAC and XCBC share most runtime callbacks but use different key preparation. CBC-MAC uses encryption-only key material and reinitializes for one-shot digest.

State and persistence: per-transform contexts hold AES key schedules or MAC keys. Per-request shash descriptors hold MAC running state. Registered algorithm aliases persist until module exit; no filesystem state exists.

Dependencies and integration points: depends on `crypto/aes.h`, `crypto/aes-cbc-macs.h`, `crypto/internal/hash.h`, and generic algorithm/shash registration. Kconfig selects AES libraries and optional hash/MAC support. Other templates such as CBC, XTS, CCM, and Adiantum may spawn `aes`.

Risks and correctness concerns: the file assumes key/context alignment fits `CRYPTO_MINALIGN`. Optional MAC registration must track Kconfig; AES cipher registration failure cleanup must be exact. XCBC only permits 128-bit keys. CBC-MAC is not a standalone authenticated mode and should be used only by protocols/templates expecting it.

Test signals: AES ECB known-answer tests, setkey rejection for invalid sizes, CMAC/XCBC/CBC-MAC vectors when enabled, module alias autoloading for `aes`, `aes-lib`, `cmac(aes)`, `xcbc(aes)`, and `cbcmac(aes)`, plus registration rollback failure injection.
