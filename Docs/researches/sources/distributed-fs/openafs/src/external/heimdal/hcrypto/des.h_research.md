## sources/distributed-fs/openafs/src/external/heimdal/hcrypto/des.h

Purpose: public DES compatibility header for hcrypto.

Important APIs/types/macros: symbol-renames DES APIs to `hc_` names, defines `DES_CBLOCK_LEN`, `DES_KEY_SZ`, `DES_ENCRYPT`, and `DES_DECRYPT`, declares `DES_cblock` and `DES_key_schedule`, and exposes parity/key-schedule, random/deprecated, block/mode, checksum, password, string-to-key, and `_DES_ipfp_test()` functions. Defines `HC_DEPRECATED` for GCC/MSVC or empty fallback.

Control flow: none in the header.

State and persistence: caller-owned `DES_key_schedule`, `DES_cblock`, IVs, and CFB offset pointers are part of the API contract. Deprecated random APIs imply external RNG state in implementations elsewhere or compatibility stubs.

Dependencies: requires `uint32_t` from including context and provides C++ linkage guards.

Integration points: included by `des.c`, hcrypto EVP provider, and legacy Kerberos/OpenSSL-compatible callers. Symbol renaming prevents collisions with system/OpenSSL DES.

Risks: exposes many deprecated or weak cryptographic interfaces. Some declared random/password functions are deprecated or may be implemented outside this file. Header does not include fixed-width integer definitions itself.

Test signals: compile/link all exported symbols expected in a full hcrypto build, deprecation attribute behavior, and C++ inclusion.
