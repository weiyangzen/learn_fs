# sources/distributed-fs/openafs/src/rxkad/rxkad_client.c

Purpose: Implements client-side rxkad security object creation and challenge responses.

Important APIs: `rxkad_NewClientSecurityObject` allocates an Rx security class, schedules the session key, stores the IV from the session key, records kvno/ticket length, and copies the server ticket. `rxkad_GetResponse` parses old or v2 server challenges and writes the matching response plus ticket into an Rx packet.

Control flow and state: Client objects carry immutable ticket/session-key data. On challenge, the client rejects requested levels above its configured level. For v2 challenges it builds endpoint data, call number vector, incremented challenge id, negotiated level, kvno, and ticket length; computes a response checksum; encrypts the v2 encrypted substructure with fcrypt CBC; then appends the ticket. For old challenges it encrypts only the old 8-byte response with fcrypt ECB.

Dependencies and integration: Hooks into `rx_securityOps` with common close/new-connection/packet functions and client `op_GetResponse`. Uses Rx packet APIs, `private_data.h`, `stats.h`, and fcrypt.

Risks: `PDATA_SIZE(ticketLen)` is computed before the explicit max-length check, so callers must provide sane nonnegative lengths. V2 response correctness depends on endpoint and call-number vector serialization in network order.

Test signals: Stress client creates rxkad client objects from generated or real tokens, while hijack tests validate v2 response binding and checksum behavior.
