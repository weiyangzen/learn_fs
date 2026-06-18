## sources/distributed-fs/openafs/src/external/heimdal/hcrypto/camellia.h

Purpose: public OpenSSL-like Camellia hcrypto header.

Important APIs/types/macros: symbol-renames `CAMELLIA_*` names to `hc_` symbols, defines block/table sizes and `CAMELLIA_ENCRYPT`/`CAMELLIA_DECRYPT`, declares `CAMELLIA_KEY` with `bits` and a 68-word table, and declares key setup, block encrypt/decrypt, and CBC mode functions.

Control flow: none in the header.

State and persistence: `CAMELLIA_KEY` is persistent caller-owned key schedule state. CBC IV mutation is exposed by non-const IV pointer.

Dependencies: requires `uint32_t` to be defined by the including context. Unlike some neighboring headers, it does not wrap declarations in C++ guards.

Integration points: included by Camellia wrapper implementation and hcrypto EVP provider. It intentionally mirrors OpenSSL naming while renaming symbols to avoid external collisions.

Risks: no explicit include for fixed-width types and no C++ guards may affect standalone consumers. OpenSSL compatibility is partial. Macro names overlap with `camellia-ntt.h`.

Test signals: compile/link tests for renamed symbols and struct sizing, plus C++ inclusion if this header is expected to be usable there.
