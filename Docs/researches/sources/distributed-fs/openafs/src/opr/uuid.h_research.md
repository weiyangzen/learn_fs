# sources/distributed-fs/openafs/src/opr/uuid.h

Purpose: public UUID data structures and API declarations.

Important APIs/types/functions: `struct opr_uuid` stores 16 raw bytes; `struct opr_uuid_unpacked` exposes time fields, clock sequence, and node bytes. Defines `opr_uuid_t` and XDR compatibility alias `opr_uuid`. Declares create, nil/equality/hash, userland string functions, and pack/unpack.

Control flow: no runtime logic in the header.

State and persistence: caller-owned UUID values only.

Dependencies/integration: requires OpenAFS integer typedefs. Installed as `opr/uuid.h`.

Risks and test signals: packed layout is exactly 16 bytes and should not change. Compile coverage and UUID roundtrip tests validate users.
