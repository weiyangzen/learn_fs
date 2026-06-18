# sources/distributed-fs/ceph-client/include/keys/big_key-type.h

Source read summary: 24 lines, 816 bytes.

Purpose: `sources/distributed-fs/ceph-client/include/keys/big_key-type.h` declares the `big_key` key-type operations for preparsing, updating, revoking, destroying, describing, and reading large user key payloads.

Important APIs, types, and functions: Important exported functions or hooks: `big_key_preparse`, `big_key_free_preparse`, `big_key_revoke`, `big_key_destroy`, `big_key_describe`, `big_key_read`, `big_key_update`. Important types: none. Important constants/macros: none.

Control flow: The key subsystem calls these hooks through the key type when userspace adds, updates, reads, or revokes a big key; implementation code may store payloads in memory or encrypted temporary storage depending on size.

State and persistence behavior: Payload state persists in the key object until revoke/destroy, with preparse state used only during instantiation/update.

Dependencies and integration points: It includes `linux/key-type.h`. Integration is with the owning kernel subsystem implementation and any external ABI named by the structures or constants.

Risks and edge cases: Large payload size, update/revoke races, quota accounting, and secure cleanup of temporary/encrypted storage are the important edge cases.

Test signals: Run keyutils add/read/update/revoke tests across small and large payload thresholds, quota limits, and revoke while readers hold references.
