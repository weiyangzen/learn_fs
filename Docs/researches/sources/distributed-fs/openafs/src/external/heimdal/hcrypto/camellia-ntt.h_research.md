## sources/distributed-fs/openafs/src/external/heimdal/hcrypto/camellia-ntt.h

Purpose: public header for the bundled NTT Camellia core.

Important APIs/types/macros: defines `CAMELLIA_BLOCK_SIZE`, `CAMELLIA_TABLE_BYTE_LEN`, `CAMELLIA_TABLE_WORD_LEN`, aliases `u32` to `uint32_t` and `u8` to `unsigned char`, defines `KEY_TABLE_TYPE` as a 68-word array, and declares `Camellia_Ekeygen`, `Camellia_EncryptBlock`, and `Camellia_DecryptBlock`.

Control flow: none; callers generate a key table then pass it to block encrypt/decrypt.

State and persistence: `KEY_TABLE_TYPE` is caller-owned persistent expanded key material.

Dependencies: requires `uint32_t` to be available from included context. Provides C++ linkage guards.

Integration points: included by `camellia-ntt.c` and `camellia.c`; acts as the low-level implementation contract below the hcrypto OpenSSL-like wrapper.

Risks: the header does not include a fixed-width integer header. API returns `void`, so invalid key lengths are not reported through the type system. Names can conflict with `camellia.h` because both define block/table macros with the same values.

Test signals: compile/link coverage for C and C++ callers, key table size assertions, and known-answer tests through the low-level API.
