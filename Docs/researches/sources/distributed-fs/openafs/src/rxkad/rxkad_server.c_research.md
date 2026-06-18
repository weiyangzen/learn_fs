# sources/distributed-fs/openafs/src/rxkad/rxkad_server.c

Purpose: Implements server-side rxkad security objects, challenge creation, response validation, server principal retrieval, and configuration.

Important APIs: `rxkad_NewServerSecurityObject` and `rxkad_NewKrb5ServerSecurityObject` allocate server classes with key callbacks. `rxkad_CreateChallenge` seeds a per-connection challenge id and level. `rxkad_GetChallenge` emits old or v2 challenge packets. `rxkad_CheckResponse` decodes tickets, validates challenge responses, installs session keys, sets packet level, and marks a connection authenticated. `rxkad_GetServerInfo` returns saved client identity. `rxkad_SetConfiguration` manages object flags.

Control flow and state: A static fcrypt schedule and seed implement challenge-id generation protected by a pthread mutex. Challenge style depends on packet checksum use. Response validation reads ticket kvno/length, optionally invokes `rxkad_AlternateTicketDecoder`, otherwise handles Kerberos v5 ticket types or v4 tickets. It validates ticket time, schedules the session key, decrypts old/v2 response data, checks endpoint/call-number binding for v2, validates challenge id and level, derives per-connection checksum material, and stores identity unless `user_ok` handles authorization.

Dependencies and integration: Integrates Rx server security ops, ticket.c/ticket5.c, fcrypt, private structures, stats, and configuration flags such as dot-check disabling.

Risks: Challenge randomness is legacy time-seeded fcrypt. Authentication relies on callback correctness and DES-derived session keys. V2 endpoint and call-number checks are critical replay defenses.

Test signals: `stress_s.c` runs a server using this path; `stress_c.c` hijack/call tests validate replay and challenge-redirection defenses.
