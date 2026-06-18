# sources/distributed-fs/ceph-client/drivers/crypto/caam/caamhash_desc.h

## Purpose
`caamhash_desc.h` declares descriptor size constants and shared descriptor constructor APIs for CAAM hash operations. It is the small interface layer used by both job-ring and QI2 hash implementations.

## Important APIs, Types, And Functions
The descriptor length constants (`DESC_AHASH_BASE`, `DESC_AHASH_UPDATE_LEN`, `DESC_AHASH_UPDATE_FIRST_LEN`, `DESC_AHASH_FINAL_LEN`, `DESC_AHASH_DIGEST_LEN`) describe expected command-space needs in CAAM command-size units. `is_xcbc_aes()` identifies AES-XCBC algorithm selectors. The external constructors are `cnstr_shdsc_ahash()` and `cnstr_shdsc_sk_hash()`.

## Control Flow
The only local executable logic is `is_xcbc_aes()`, which masks an algorithm type against `OP_ALG_ALGSEL_MASK | OP_ALG_AAI_MASK` and compares it to AES plus XCBC-MAC. The rest of the header establishes compile-time contracts for implementation files.

## State And Persistence Behavior
There is no mutable state. The constants influence static descriptor buffer sizing in callers, and the helper provides a pure classification of an algorithm word.

## Dependencies And Integration Points
The header assumes CAAM descriptor and operation macros are already available through included CAAM compatibility/descriptor headers in the including source. It is included by `caamhash.c`, `caamhash_desc.c`, and `caamalg_qi2.c`.

## Risks
If descriptor length constants fall behind constructor changes, callers may under-allocate descriptor buffers. If `is_xcbc_aes()` masks the wrong bits, XCBC paths may use CMAC-style key/context handling or vice versa.

## Test Signals
Build coverage detects missing declarations and many sizing mismatches. Runtime validation comes from successful XCBC/CMAC/HMAC/hash selftests and absence of CAAM descriptor length/status errors.
