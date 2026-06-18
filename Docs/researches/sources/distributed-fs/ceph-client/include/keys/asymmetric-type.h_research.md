# sources/distributed-fs/ceph-client/include/keys/asymmetric-type.h

Source read summary: 95 lines, 3050 bytes.

Purpose: `sources/distributed-fs/ceph-client/include/keys/asymmetric-type.h` declares the common asymmetric key type payload layout, key ID helpers, and optional certificate-list loader entry point.

Important APIs, types, and functions: Important exported functions or hooks: `asymmetric_key_id_same`, `asymmetric_key_id_partial`, `x509_load_certificate_list`. Important types: `asymmetric_payload_bits`, `asymmetric_key_id`, `asymmetric_key_ids`. Important constants/macros: none.

Control flow: Callers compare full or partial IDs with `asymmetric_key_id_same()` and `asymmetric_key_id_partial()`, while keyring/certificate code stores ID arrays in `struct asymmetric_key_ids` for lookup and trust decisions.

State and persistence behavior: Key IDs and payload bits persist as part of instantiated key payloads until the key is revoked or garbage-collected. Certificate-list loading affects trusted keyrings during initialization.

Dependencies and integration points: It includes `linux/key-type.h`, `linux/verification.h`. Integration is with the owning kernel subsystem implementation and any external ABI named by the structures or constants.

Risks and edge cases: Partial ID matching can be ambiguous; payload index constants must match subtype parser allocation. Certificate loading failures can reduce trust roots without obvious runtime symptoms.

Test signals: Exercise key lookup by exact and partial ID, boot-time certificate loading, blacklist interaction, and malformed ID payload handling.
