# sources/distributed-fs/openafs/src/rxkad/private_data.h

Purpose: Defines rxkad private security-object and per-connection structures shared by client, server, and common packet code.

Important APIs/types: `connStats` tracks byte/packet counters. `rxkad_endpoint` binds challenge responses and packet checksums to epoch, CID, and security index and must remain 8-byte multiple sized. `rxkad_cprivate` stores client level, kvno, ticket, key schedule, and IV. `rxkad_cconn` stores client per-connection checksum IV and stats. `rxkad_sprivate` stores server key callbacks, user validation callback, enctype key callback, and flags. `rxkad_sconn` stores server authentication state, expiration, challenge id, key material, packet checksum state, stats, and optional saved principal. Challenge and response wire structs define old and v2 protocol formats.

Control flow and state: These structures are allocated in `rxkad_NewClientSecurityObject`, `rxkad_NewServerSecurityObject`, and `rxkad_NewConnection`; they are freed by `rxkad_DestroyConnection` and `rxkad_Close`. Server connections transition from unauthenticated to authenticated after `rxkad_CheckResponse`.

Dependencies and integration: Consumed by `rxkad_client.c`, `rxkad_common.c`, `rxkad_server.c`, and packet crypto. It depends on `rxkad.h`, `fcrypt.h`, and Rx constants such as `RX_MAXCALLS`.

Risks: The client and server private structs intentionally share `type` and `level` offsets. Wire structs require network byte order in selected fields. `PDATA_SIZE(ticketLen)` is sensitive to validation order.

Test signals: Stress call-number and hijack tests specifically validate `rxkad_v2ChallengeResponse`, `preSeq`, `cksumSeen`, and endpoint binding behavior.
