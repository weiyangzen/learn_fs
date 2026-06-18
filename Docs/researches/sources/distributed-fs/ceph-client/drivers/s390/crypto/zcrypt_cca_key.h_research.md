# sources/distributed-fs/ceph-client/drivers/s390/crypto/zcrypt_cca_key.h

Purpose: defines CCA RSA key token structures and inline builders that translate userspace RSA key parameters into type-6 AP message key blocks for modular exponentiation and CRT operations.

Important APIs and types: `struct t6_keyblock_hdr`, `struct cca_token_hdr`, `struct cca_public_sec`, and `struct cca_pvt_ext_crt_sec` model packed CCA key-token sections. Constants identify extended token headers, private CRT sections, clear private format, and usage flags. `zcrypt_type6_mex_key_en()` builds a public-section key block from exponent and modulus pointers in `ica_rsa_modexpo`. `zcrypt_type6_crt_key()` builds a private CRT token from p, q, dp, dq, u, padding, synthetic public section, and exponent 65537.

Control flow: both builders first enforce a defensive `inputdatalength <= 512` check, clear the output area, populate static header/section fields, copy key parts from userspace, compute token/section lengths, and return the number of bytes written or a negative errno.

State and persistence: no state persists. Static header templates are immutable. Generated key blocks live in caller-provided AP message buffers.

Dependencies and integration: depends on s390 zcrypt userspace ABI structures `ica_rsa_modexpo` and `ica_rsa_modexpo_crt`, `copy_from_user()`, and message type 6 request builders that include this header.

Risks: packed binary layout and length arithmetic are hardware ABI-sensitive. The inline functions trust the caller to provide a sufficiently large destination buffer; the 512-byte plausibility checks guard against known dispatch limits but do not size the destination. All user copies must be checked to avoid partially built messages.

Test signals: build MEX keys for 1K/2K/4K RSA sizes, CRT keys with odd/even input lengths, invalid lengths above 512, fault-injected `copy_from_user()`, expected section lengths/padding, and hardware/message-type parser acceptance.
