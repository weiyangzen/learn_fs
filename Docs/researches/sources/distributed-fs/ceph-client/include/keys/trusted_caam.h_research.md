# sources/distributed-fs/ceph-client/include/keys/trusted_caam.h

Source read summary: 12 lines, 243 bytes.

Purpose: `sources/distributed-fs/ceph-client/include/keys/trusted_caam.h` declares the CAAM trusted-key backend operations object.

Important APIs, types, and functions: Important exported functions or hooks: none. Important types: none. Important constants/macros: none.

Control flow: The common trusted key type can select `trusted_key_caam_ops` when CAAM-backed sealing is enabled and available.

State and persistence behavior: No local state exists; sealed blobs and decrypted key bytes are owned by the common trusted-key payload.

Dependencies and integration points: It is self-contained at include level. Integration is with the owning kernel subsystem implementation and any external ABI named by the structures or constants.

Risks and edge cases: Backend registration must match CAAM hardware availability and must fail closed when secure key operations are unavailable.

Test signals: Build CAAM trusted-key configurations and run create/load tests on CAAM-capable hardware or emulation.
