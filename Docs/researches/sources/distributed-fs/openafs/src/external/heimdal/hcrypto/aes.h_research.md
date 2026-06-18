## sources/distributed-fs/openafs/src/external/heimdal/hcrypto/aes.h

Purpose: public AES compatibility header for Heimdal hcrypto.

Important APIs/types/macros: symbol-renames OpenSSL-like names to `hc_` symbols. Defines `AES_BLOCK_SIZE`, `AES_MAXNR`, `AES_ENCRYPT`, `AES_DECRYPT`, and `AES_KEY` with `(AES_MAXNR + 1) * 4` 32-bit round-key words plus `rounds`. Declares key setup, block encrypt/decrypt, CBC, and CFB8 APIs.

Control flow: none in the header; mode behavior is implemented in `aes.c`.

State and persistence: `AES_KEY` is caller-allocated persistent key schedule state. IV mutation is implied by non-const IV pointers in mode APIs.

Dependencies: requires `uint32_t` to be available before or through surrounding hcrypto/Kerberos headers. Adds C++ `extern "C"` guards.

Integration points: included by hcrypto EVP provider and any code needing AES primitives without linking OpenSSL symbols.

Risks: macro `#define AES_set_decrypt_key hc_AES_decrypt_key` appears to rename to `hc_AES_decrypt_key`, while the naming pattern and implementation function are `AES_set_decrypt_key`; consumers must rely on build symbol-renaming consistency. Header does not include a fixed-width integer header itself. OpenSSL compatibility is partial and limited to listed APIs.

Test signals: compile/link tests for each renamed symbol, struct size assumptions, and C++ inclusion.
