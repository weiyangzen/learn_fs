# sources/distributed-fs/openafs/src/libadmin/kas/afs_kasAdmin.h

## Purpose
This public header defines the KAS admin API, including principal identities, encryption keys, principal metadata, KAS server statistics/debug structures, and function declarations for KAS database administration.

## Important APIs, Types, and Functions
- Constants define name/key lengths, principal flag externs, operation-name lengths, and key-cache debug capacity.
- `kas_identity_t`, `kas_encryptionKey_t`, and enums for admin/TGS/encryption/change-password/password-reuse settings model principal identity and policy.
- `kas_principalEntry_t` exposes principal flags, expiration/modification data, key version/key/checksum, password expiration, failed-login count, and lock time.
- `kas_serverStats_t`, `kas_serverProcStats_t`, `key_keyCacheItem_t`, and `kas_serverDebugInfo_t` expose KAS server telemetry and debug data.
- Function declarations cover server open/close, principal CRUD and iteration, key/password changes, lock status/unlock, field updates, stats/debug/random-key retrieval, string-to-key, and checksum.

## Control Flow and State
The header defines the caller contract for opaque server handles and iterator handles. Principal enumeration follows the standard begin/next/done pattern. Many field-set parameters are pointers so callers can update only selected attributes.

## Persistence and Side Effects
Declared functions can mutate KAS principals, keys, policy fields, and lock state. Stats/debug/key utility calls are mostly read-only but still perform RPC or cryptographic operations in the implementation.

## Dependencies and Integration Points
The header includes AFS base/admin types and `time.h`; Windows builds account for winsock include ordering. It is installed by `kas/Makefile.in` and consumed by admin clients, tests, and any application managing legacy OpenAFS KAS data.

## Risks
KAS is a legacy authentication service, and the API exposes raw fixed-size C buffers and key material. The many `extern const int` flag declarations require matching definitions elsewhere. Callers must observe fixed sizes and pointer-optional update semantics exactly.

## Test Signals
Compile-time ABI checks should verify structure sizes and header inclusion on Unix/Windows. API tests should validate selective field updates, iterator usage, and safe handling of maximum-length principal/instance/debug strings.
