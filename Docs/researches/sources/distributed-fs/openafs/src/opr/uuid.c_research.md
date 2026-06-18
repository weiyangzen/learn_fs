# sources/distributed-fs/openafs/src/opr/uuid.c

Purpose: UUID creation, comparison, hashing, string conversion, parsing, and packed/unpacked conversion.

Important APIs/types/functions: exports `opr_uuid_create`, `opr_uuid_isNil`, `opr_uuid_equal`, `opr_uuid_hash`, userland `opr_uuid_toString`, `opr_uuid_freeString`, `opr_uuid_fromString`, plus `opr_uuid_pack` and `opr_uuid_unpack`.

Control flow: creation uses Windows `UuidCreate`, platform `uuid_generate`, or random bytes from hcrypto with version/variant bits set. Equality and nil checks use `memcmp`. String conversion formats canonical hex groups; parsing accepts canonical format and an older AFS grouping. Pack/unpack converts structured fields with network byte order for multi-byte components.

State and persistence: no global mutable state except constant nil UUID. UUID values are caller-owned. No persistence.

Dependencies/integration: depends on hcrypto random, optional libuuid, Windows RPC, Jenkins hash, and network byte-order helpers. Exposed by `uuid.h`.

Risks and test signals: fallback random path must have reliable `RAND_bytes`; return value is ignored. `sscanf` parsing with `%02x` accepts variable-width hex in C semantics, so strict validation may be weaker than expected. Tests should cover nil, equality, roundtrip string parse, old AFS parse format, and pack/unpack byte order.
