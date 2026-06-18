# sources/distributed-fs/ceph-client/include/keys/trusted_dcp.h

Source read summary: 12 lines, 194 bytes.

Purpose: `sources/distributed-fs/ceph-client/include/keys/trusted_dcp.h` declares the DCP trusted-key backend operations object.

Important APIs, types, and functions: Important exported functions or hooks: none. Important types: none. Important constants/macros: none.

Control flow: The common trusted key type can dispatch trusted key seal/unseal operations through `trusted_key_dcp_ops` on supported DCP hardware.

State and persistence behavior: No local state exists; backend hardware and common trusted-key payloads hold the durable wrapped-key state.

Dependencies and integration points: It is self-contained at include level. Integration is with the owning kernel subsystem implementation and any external ABI named by the structures or constants.

Risks and edge cases: Incorrect backend selection or missing DCP support can make trusted keys fail at runtime.

Test signals: Build DCP trusted-key configurations and test add/load/revoke flows with DCP-backed keys.
