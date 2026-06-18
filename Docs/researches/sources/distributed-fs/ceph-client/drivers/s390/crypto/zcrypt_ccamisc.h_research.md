# sources/distributed-fs/ceph-client/drivers/s390/crypto/zcrypt_ccamisc.h

## Purpose
`zcrypt_ccamisc.h` is the public local interface for CCA helper logic. It defines CCA token type/version constants, packed views of CCA AES DATA, AES CIPHER, and ECC private key tokens, CCA AES CIPHER export-control bits, the `cca_info` facility-state structure, and prototypes for the helper functions implemented in `zcrypt_ccamisc.c`.

## Important APIs, Types, And Functions
Important types are `struct keytoken_header`, `struct secaeskeytoken`, `struct cipherkeytoken`, `struct eccprivkeytoken`, and `struct cca_info`. Important constants include `TOKTYPE_NON_CCA`, `TOKTYPE_CCA_INTERNAL`, `TOKTYPE_CCA_INTERNAL_PKA`, `TOKVER_CCA_AES`, `TOKVER_CCA_VLSC`, `MAXCCAVLSCTOKENSIZE`, and the `KMF1_XPRT_*` bit definitions. Function prototypes expose token validation, CCA key generation/import, secure-to-protected conversion, crypto-facility query, APQN selection, and module init/exit routines.

## Control Flow
The header has no executable control flow, but it defines the contract used by pkey and zcrypt call sites. Callers validate token buffers with the check helpers before extracting fields, then use the generate/import/unwrap/query APIs with card/domain selectors and optional `ZCRYPT_XFLAG_*` flags. `cca_findcard2()` communicates APQN matches by updating an input/output count and filling a caller-provided `u32` array.

## State And Persistence
The header declares `struct cca_info`, which is a transient in-memory snapshot of hardware type, master-key states, master-key verification patterns, and adapter serial number. It does not define persistent storage.

## Dependencies And Integration Points
It includes `asm/zcrypt.h`, `asm/pkey.h`, and `zcrypt_api.h`, making it a bridge between architecture zcrypt ioctls, pkey key types, and the zcrypt internal queue/device model. Packed token layouts are ABI-sensitive because they are cast over opaque firmware-generated key blobs.

## Risks And Test Signals
Risks are accidental layout drift, token-version confusion, and callers using these structs on undersized buffers. Test signals include compile-time structure consumers, token validation against known CCA samples, key-size mapping checks for AES 128/192/256, and APQN discovery tests that inspect the `cca_info` fields populated by `cca_get_info()`.
