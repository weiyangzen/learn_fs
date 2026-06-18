# sources/distributed-fs/ceph-client/include/keys/rxrpc-type.h

Source read summary: 113 lines, 3014 bytes.

Purpose: `sources/distributed-fs/ceph-client/include/keys/rxrpc-type.h` defines RxRPC/AFS key token layouts for rxkad and rxgk security classes, Kerberos-derived tickets, token limits, and legacy v1 payload data.

Important APIs, types, and functions: Important exported functions or hooks: none. Important types: `rxkad_key`, `rxgk_key`, `rxrpc_key_token`, `rxrpc_key_data_v1`. Important constants/macros: `AFSTOKEN_LENGTH_MAX`, `AFSTOKEN_STRING_MAX`, `AFSTOKEN_DATA_MAX`, `AFSTOKEN_CELL_MAX`, `AFSTOKEN_MAX`, `AFSTOKEN_BDATALN_MAX`, `AFSTOKEN_RK_TIX_MAX`, `AFSTOKEN_GK_KEY_MAX`, `AFSTOKEN_GK_TOKEN_MAX`.

Control flow: AFS/RxRPC authentication code parses key payloads into `struct rxrpc_key_token` entries and uses the embedded keys, tickets, expiry, kvno, and cell/principal names when securing calls.

State and persistence behavior: Tokens persist in key payloads until expiry, revoke, or key destruction. Sensitive ticket and session-key bytes must be protected and cleared.

Dependencies and integration points: It includes `linux/key.h`, `crypto/krb5.h`. Integration is with the owning kernel subsystem implementation and any external ABI named by the structures or constants.

Risks and edge cases: Length limits are security boundaries; malformed token counts, oversized tickets, or unsupported security indexes can lead to failed authentication or memory bugs.

Test signals: Test rxkad/rxgk token parsing, expiry handling, malformed length rejection, and AFS/RxRPC authenticated call setup.
