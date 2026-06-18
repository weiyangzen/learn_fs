# sources/distributed-fs/ceph-client/security/ipe/digest.c

Purpose: Parses, compares, frees, and audits digest values used in IPE policy properties.

Important APIs/types/functions: Implements `ipe_digest_parse()`, `ipe_digest_eval()`, `ipe_digest_free()`, and `ipe_digest_audit()`. Data shape is `struct digest_info` from `digest.h`.

Control flow: Parser expects `<alg_name>:<hex>`, duplicates the algorithm string, allocates digest bytes sized from hex length, decodes with `hex2bin()`, and returns ERR_PTR on parse or allocation failure. Evaluation requires equal digest length, identical algorithm string, and byte-for-byte digest equality. Audit emits algorithm as untrusted string plus hex digest.

State and persistence: Digest objects are heap allocations owned by parsed policies or LSM blobs. No global state.

Dependencies and integration: Used by IPE parser, dm-verity/fs-verity evaluators, audit formatting, and block-device integrity storage.

Risks and test signals: Odd hex lengths are rounded up before `hex2bin()`, so parser behavior should be validated carefully. Risks also include algorithm-string case sensitivity and no crypto algorithm availability check. Tests should cover missing colon, invalid hex, odd length, empty algorithm/digest, equal/different algorithms, and freeing ERR/NULL values.
