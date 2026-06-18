# sources/distributed-fs/openafs/src/kauth/kauth_internal.h

## Purpose
Collects private kauth prototypes and small conversion helpers shared across server, client, and utility modules.

## Important APIs, Types, And Functions
Declares admin command entry, database initialization/lookup/threading/cache helpers, logging initialization, `InitAuthServ`, Kerberos ticket-file and UDP initialization, and `name_instance_legal`. Inline helpers reinterpret between generated `EncryptionKey`, hcrypto `DES_cblock`, and `ktc_encryptionKey`. The `check_ka_skew` macro compares two time values with explicit 64-bit casts.

## Control Flow
No standalone control flow exists. The inline casts are used before DES calls, and `check_ka_skew` is used in RPC request validation to avoid unsigned/signed time promotion bugs.

## State And Persistence
The header stores no state. It exposes functions that mutate the Ubik database, token files, logging, and UDP service state.

## Dependencies And Integration Points
It includes hcrypto DES and is included by `kas.c`, `kaserver.c`, `kaprocs.c`, and other kauth internals. It is the glue between generated rxgen key types, ktc key types, and DES library APIs.

## Risks And Test Signals
Risks include type-punning assumptions in inline casts, prototype drift, and macro side effects if time expressions are not simple. Test signals include strict-aliasing builds, DES key validation paths, skew rejection near 32-bit boundaries, and server/client module compile coverage.
