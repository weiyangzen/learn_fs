# sources/distributed-fs/ceph-client/drivers/s390/crypto/pkey_pckmo.c

Purpose: implements the pkey handler backed by the s390 CPACF PCKMO instruction. It supports protected-key tokens and clear-key tokens for AES, AES-XTS, HMAC, and ECC protected-key types where the architecture exposes the needed PCKMO subfunction.

Important APIs and functions: `is_pckmo_key()` accepts non-CCA clear-key and protected-key token versions. `pckmo_clr2protkey()` maps pkey key types to CPACF PCKMO function codes, checks key and output sizes, queries/caches the PCKMO function mask, calls `cpacf_pckmo()`, and returns protected material plus WKVP. `pckmo_verify_protkey()` creates a dummy AES-128 protected key and compares WKVPs to reject keys wrapped under a different wrapping key. `pckmo_key2protkey()` copies existing protected tokens or converts clear tokens, respecting `PKEY_XFLAG_NOCLEARKEY`. `pckmo_gen_protkey()` creates random protected-key material by generating a dummy protected token and replacing the key bytes with random bytes while preserving a valid WKVP. Wrapper callbacks populate `pckmo_handler`.

Control flow: pkey core dispatches into the handler. Conversion validates the token header, token version, key type, embedded length, and output buffer before touching CPACF. Generation validates subtype `PKEY_TYPE_PROTKEY`, supported key type, randomizes clear input, calls PCKMO, then randomizes the protected key portion.

State and persistence: the only retained state is the static `cpacf_mask_t pckmo_functions`, lazily filled by `cpacf_query()`. No key material persists beyond caller buffers and local stack arrays, which are zeroed where temporary protected-key verification material is used.

Dependencies and integration: depends on `asm/cpacf.h`, Linux random APIs, AES WKVP size constants, token formats from zcrypt CCA misc, and pkey handler registration gated by `S390_CPU_FEATURE_MSA`.

Risks: PCKMO function-code mapping must remain exact for all key types. The protected-key verification method trusts WKVP comparison, so tests must catch wrapping-key mismatch handling. Generated protected keys intentionally replace the key bytes after PCKMO, so accidental replacement of the WKVP would make outputs unusable.

Test signals: cover all supported AES, XTS, HMAC, and ECC key types; unsupported subtype/type rejection; short clear key and short output buffer errors; unavailable CPACF subfunction; protected-token WKVP mismatch; `NOCLEARKEY`; and module init on CPUs without PCKMO.
