# sources/distributed-fs/ceph-client/include/keys/asymmetric-subtype.h

Source read summary: 61 lines, 1696 bytes.

Purpose: `sources/distributed-fs/ceph-client/include/keys/asymmetric-subtype.h` defines the asymmetric-key subtype interface, public-key query/operation parameter structs, signature payload layout, and callbacks used by RSA/ECDSA or certificate-backed key implementations.

Important APIs, types, and functions: Important exported functions or hooks: none. Important types: `kernel_pkey_query`, `kernel_pkey_params`, `public_key_signature`, `asymmetric_key_subtype`. Important constants/macros: none.

Control flow: The asymmetric key type delegates describe, destroy, query, encrypt/decrypt, sign/verify, and ID lookup behavior through `struct asymmetric_key_subtype` after a parser installs subtype-specific payloads.

State and persistence behavior: Key payloads persist under key retention rules and may be RCU-protected. Signature and public-key parameter structs are transient operation inputs owned by callers.

Dependencies and integration points: It includes `linux/seq_file.h`, `keys/asymmetric-type.h`. Integration is with the owning kernel subsystem implementation and any external ABI named by the structures or constants.

Risks and edge cases: Mismatched subtype callbacks or algorithm/hash identifiers can produce false verification results or leaks. Buffer lengths and digest sizes must be validated before crypto operations.

Test signals: Run asymmetric key selftests, signature verification with supported and unsupported algorithms, key destruction under RCU, and parser/subtype handoff failure cases.
