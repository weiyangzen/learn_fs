# Research Group: subset-b-007800

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/rxkad/fcrypt.c -->
# sources/distributed-fs/openafs/src/rxkad/fcrypt.c

Purpose: Implements the rxkad private "fcrypt" block cipher used for rxkad packet sealing and challenge-response encryption. It supplies key scheduling plus ECB and CBC operations over 8-byte blocks, using static S-boxes from `sboxes.h`.

Important APIs: `fc_keysched` compresses the 8-byte `ktc_encryptionKey` by dropping DES parity bits and rotating the resulting 56-bit state into a 16-round `fc_KeySchedule`. `fc_ecb_encrypt` encrypts or decrypts one 8-byte block using a Feistel-like pair of 32-bit halves, S-box substitution, and 5-bit rotation. `fc_cbc_encrypt` chains ECB blocks with an 8-byte IV and updates the caller-provided IV so scatter/gather callers can continue CBC across segments.

Control flow and state: The file is stateless except for optional `TCRYPT` global `ROUNDS`; normal builds use 16 rounds. `fc_ecb_encrypt` switches on encrypt/decrypt, walks the schedule forward for encryption and backward for decryption, and stores output in network byte order. `fc_cbc_encrypt` pads only the final encryption block with zeroes and never pads on decrypt; it mutates the IV argument after every block.

Dependencies and integration: Used by `rxkad_client.c`, `rxkad_common.c`, `rxkad_server.c`, packet crypto in `crypt_conn.c`, and test programs. It depends on OpenAFS endian wrappers, `rxkad.h`, `rxkad_stats.h`, and `sboxes.h`.

Risks: This is legacy cryptography, not modern DES/AES. The CBC IV mutation is intentional but easy to misuse if callers reuse IV storage unexpectedly. The code assumes 8-byte aligned logical blocks and copies fixed 8-byte chunks even for the final padded encrypt block.

Test signals: `tcrypt.c` and `test/fc_test.c` directly exercise ECB/CBC round trips, known vectors, and avalanche behavior; stress tests indirectly exercise packet sealing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/rxkad/fcrypt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/rxkad/fcrypt.h -->
# sources/distributed-fs/openafs/src/rxkad/fcrypt.h

Purpose: Defines the small public type contract for the rxkad fcrypt primitive.

Important APIs/types: `ENCRYPTIONBLOCKSIZE` is fixed at 8 bytes. `fc_InitializationVector` is two 32-bit words. `MAXROUNDS` is 16 and `fc_KeySchedule` is an array of 16 32-bit words. `FCRYPT_ENCRYPT` and `FCRYPT_DECRYPT` encode operation direction.

Control flow and state: Header-only definitions; no runtime state. It deliberately undefines prior `ENCRYPTIONBLOCKSIZE` and `MAXROUNDS` macros to keep the rxkad cipher ABI stable.

Dependencies and integration: Included by `rxkad_prototypes.h`, `private_data.h`, `fcrypt.c`, packet crypto, and tests. The types assume `afs_int32` is already visible through OpenAFS headers.

Risks: The 8-byte block and 16-round schedule are hard ABI assumptions across connection-private structures and packet layout. Any change breaks encrypted challenge packets and packet sealing.

Test signals: Build coverage comes from every rxkad object; direct functional signals come from `fc_test` and `tcrypt`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/rxkad/fcrypt.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/rxkad/lifetimes.h -->
# sources/distributed-fs/openafs/src/rxkad/lifetimes.h

Purpose: Provides the Kerberos-style compact lifetime table used by rxkad ticket creation and decoding.

Important APIs/types: Defines `TKTLIFENUMFIXED`, `TKTLIFEMINFIXED`, `TKTLIFEMAXFIXED`, `TKTLIFENOEXPIRE`, `MAXTKTLIFETIME`, and the 64-entry `tkt_lifetimes` table mapping lifetime byte values `0x80` through `0xBF` to seconds.

Control flow and state: Header data only. `ticket.c` uses the table in `life_to_time` and `time_to_life`; values below `0x80` mean five-minute units, `0xFF` means no expiration, and the fixed range reaches 30 days.

Dependencies and integration: Included by `ticket.c`, `ticket5.c`, and `crc.c`. It ties ticket wire encoding to constants in `rxkad.p.h` such as `MAXKTCTICKETLIFETIME` and `NEVERDATE`.

Risks: The static table is protocol data; changing it changes ticket lifetime interpretation. The no-expire value remains a security-sensitive compatibility feature.

Test signals: Ticket tests and stress-generated tickets exercise `time_to_life`; server authentication paths exercise `life_to_time` and `tkt_CheckTimes`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/rxkad/lifetimes.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/rxkad/private_data.h -->
# sources/distributed-fs/openafs/src/rxkad/private_data.h

Purpose: Defines rxkad private security-object and per-connection structures shared by client, server, and common packet code.

Important APIs/types: `connStats` tracks byte/packet counters. `rxkad_endpoint` binds challenge responses and packet checksums to epoch, CID, and security index and must remain 8-byte multiple sized. `rxkad_cprivate` stores client level, kvno, ticket, key schedule, and IV. `rxkad_cconn` stores client per-connection checksum IV and stats. `rxkad_sprivate` stores server key callbacks, user validation callback, enctype key callback, and flags. `rxkad_sconn` stores server authentication state, expiration, challenge id, key material, packet checksum state, stats, and optional saved principal. Challenge and response wire structs define old and v2 protocol formats.

Control flow and state: These structures are allocated in `rxkad_NewClientSecurityObject`, `rxkad_NewServerSecurityObject`, and `rxkad_NewConnection`; they are freed by `rxkad_DestroyConnection` and `rxkad_Close`. Server connections transition from unauthenticated to authenticated after `rxkad_CheckResponse`.

Dependencies and integration: Consumed by `rxkad_client.c`, `rxkad_common.c`, `rxkad_server.c`, and packet crypto. It depends on `rxkad.h`, `fcrypt.h`, and Rx constants such as `RX_MAXCALLS`.

Risks: The client and server private structs intentionally share `type` and `level` offsets. Wire structs require network byte order in selected fields. `PDATA_SIZE(ticketLen)` is sensitive to validation order.

Test signals: Stress call-number and hijack tests specifically validate `rxkad_v2ChallengeResponse`, `preSeq`, `cksumSeen`, and endpoint binding behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/rxkad/private_data.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/rxkad/rxkad.p.h -->
# sources/distributed-fs/openafs/src/rxkad/rxkad.p.h

Purpose: Main rxkad public-private protocol header for ticket sizes, principal structures, security levels, ticket type numbers, and stats indexing macros.

Important APIs/types: Defines `MAXKTCTICKETLIFETIME`, ticket length bounds, principal name bounds, clock skew, `ktc_encryptionKey`, `ktc_principal`, `rxkad_type`, `rxkad_level`, `rxkad_clear`, `rxkad_auth`, `rxkad_crypt`, ticket type values for Kerberos v5 and v5 encrypted-part-only tickets, and `rxkad_get_key_enctype_func`.

Control flow and state: No runtime flow. Constants drive validation in ticket decode, security negotiation in client/server challenge processing, packet security header sizes, and stats index mapping.

Dependencies and integration: Includes `<rx/rxkad_prototypes.h>` after defining core types. This header is the canonical include behind installed `rx/rxkad.h` style users.

Risks: Size constants are wire and ABI limits. `MAXKTCTICKETLEN` is large enough for v5 tickets, so all stack buffers using it are security-relevant. Stats macros sanitize invalid type/level inputs to index 0, which avoids bounds errors but can hide bad callers.

Test signals: Stress command parsing exercises level names and ticket creation; v4/v5 ticket routines enforce the bounds defined here.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/rxkad/rxkad.p.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/rxkad/rxkad_client.c -->
# sources/distributed-fs/openafs/src/rxkad/rxkad_client.c

Purpose: Implements client-side rxkad security object creation and challenge responses.

Important APIs: `rxkad_NewClientSecurityObject` allocates an Rx security class, schedules the session key, stores the IV from the session key, records kvno/ticket length, and copies the server ticket. `rxkad_GetResponse` parses old or v2 server challenges and writes the matching response plus ticket into an Rx packet.

Control flow and state: Client objects carry immutable ticket/session-key data. On challenge, the client rejects requested levels above its configured level. For v2 challenges it builds endpoint data, call number vector, incremented challenge id, negotiated level, kvno, and ticket length; computes a response checksum; encrypts the v2 encrypted substructure with fcrypt CBC; then appends the ticket. For old challenges it encrypts only the old 8-byte response with fcrypt ECB.

Dependencies and integration: Hooks into `rx_securityOps` with common close/new-connection/packet functions and client `op_GetResponse`. Uses Rx packet APIs, `private_data.h`, `stats.h`, and fcrypt.

Risks: `PDATA_SIZE(ticketLen)` is computed before the explicit max-length check, so callers must provide sane nonnegative lengths. V2 response correctness depends on endpoint and call-number vector serialization in network order.

Test signals: Stress client creates rxkad client objects from generated or real tokens, while hijack tests validate v2 response binding and checksum behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/rxkad/rxkad_client.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/rxkad/rxkad_common.c -->
# sources/distributed-fs/openafs/src/rxkad/rxkad_common.c

Purpose: Shared rxkad implementation for initialization, stats aggregation, endpoint derivation, packet prepare/check, object lifetime, connection lifetime, and level conversion.

Important APIs: `rxkad_Init` initializes pthread-only stats and random mutex state. `rxkad_SetupEndpoint` serializes epoch, masked CID, and security index. `rxkad_DeriveXORInfo` encrypts endpoint data to derive per-connection checksum material. `rxkad_CksumChallengeResponse` hashes v2 challenge responses with the endpoint checksum field zeroed. `rxkad_SetLevel` sets Rx security header/trailer sizes. `rxkad_NewConnection`, `rxkad_DestroyConnection`, `rxkad_PreparePacket`, `rxkad_CheckPacket`, `rxkad_GetStats`, `rxkad_StringToLevel`, and `rxkad_LevelToString` implement the shared security-class operations.

Control flow and state: Client connections derive `preSeq` immediately from the session key and endpoint. Server connections allocate empty state and become usable after authentication. `rxkad_PreparePacket` always sets a packet checksum, seals sequence/call-number/length into the first word for auth/crypt levels, rounds packet length, and encrypts either the first block or the whole packet. `rxkad_CheckPacket` verifies optional checksum, decrypts, validates the sealed sequence/call-number value, and restores the real data size.

Dependencies and integration: Central glue between Rx calls/packets, fcrypt, private structures, stats macros, and packet crypto functions from `crypt_conn.c`.

Risks: Packet data layout is tightly coupled to Rx header/trailer sizes. Expiration checks happen per packet. Checksum adoption uses `cksumSeen`, so compatibility with old clients is stateful.

Test signals: Stress call tests and hijack tests directly exercise sealed call-number checks, checksum downgrade prevention, and connection expiration/authentication behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/rxkad/rxkad_common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/rxkad/rxkad_convert.h -->
# sources/distributed-fs/openafs/src/rxkad/rxkad_convert.h

Purpose: Provides inline pointer conversion helpers between rxkad `ktc_encryptionKey`, raw char buffers, and hcrypto `DES_cblock` types.

Important APIs: `ktc_to_cblock`, `ktc_to_charptr`, `ktc_to_cblockptr`, `charptr_to_cblock`, and `charptr_to_cblockptr` are all cast-only helpers.

Control flow and state: Header-only, no state. It intentionally centralizes casts needed by DES/hcrypto APIs.

Dependencies and integration: Used by ticket creation/decode and stress tests when calling DES key scheduling, random-key generation, PCBC/CBC encryption, and random generator setup.

Risks: The helpers assume identical 8-byte storage layout and correct alignment. They provide no validation and should not be used with arbitrary buffers shorter than 8 bytes.

Test signals: `ticket.c`, `ticket5.c`, and `stress_c.c` compile-time and runtime paths exercise the conversions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/rxkad/rxkad_convert.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/rxkad/rxkad_prototypes.h -->
# sources/distributed-fs/openafs/src/rxkad/rxkad_prototypes.h

Purpose: Declares the rxkad API surface across packet crypto, fcrypt, client/server security classes, common connection operations, ticket routines, CRC helpers, and Kerberos v5 support.

Important APIs: Prototypes include `rxkad_EncryptPacket`, `rxkad_DecryptPacket`, `fc_*`, `rxkad_NewClientSecurityObject`, `rxkad_GetResponse`, shared connection/packet/stats operations, `rxkad_NewServerSecurityObject`, `rxkad_NewKrb5ServerSecurityObject`, challenge processing, `rxkad_GetServerInfo`, `rxkad_SetConfiguration`, v4 ticket routines, v5 ticket routines, and `tkt_DeriveDesKey`.

Control flow and state: No runtime behavior, but this header establishes cross-file coupling and installed declarations.

Dependencies and integration: Included from `rxkad.p.h` after core typedefs are defined. It pulls in `fcrypt.h` and `rx/rx.h`.

Risks: Some legacy prototypes expose mutable char pointers and broad callback signatures. ABI compatibility constrains cleanup. The declared `rxkad_AllocCID` and `rxkad_ResetState` are historical declarations not implemented in this file group.

Test signals: All rxkad builds depend on prototype consistency; stress clients and servers exercise the public constructors and server-info APIs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/rxkad/rxkad_prototypes.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/rxkad/rxkad_server.c -->
# sources/distributed-fs/openafs/src/rxkad/rxkad_server.c

Purpose: Implements server-side rxkad security objects, challenge creation, response validation, server principal retrieval, and configuration.

Important APIs: `rxkad_NewServerSecurityObject` and `rxkad_NewKrb5ServerSecurityObject` allocate server classes with key callbacks. `rxkad_CreateChallenge` seeds a per-connection challenge id and level. `rxkad_GetChallenge` emits old or v2 challenge packets. `rxkad_CheckResponse` decodes tickets, validates challenge responses, installs session keys, sets packet level, and marks a connection authenticated. `rxkad_GetServerInfo` returns saved client identity. `rxkad_SetConfiguration` manages object flags.

Control flow and state: A static fcrypt schedule and seed implement challenge-id generation protected by a pthread mutex. Challenge style depends on packet checksum use. Response validation reads ticket kvno/length, optionally invokes `rxkad_AlternateTicketDecoder`, otherwise handles Kerberos v5 ticket types or v4 tickets. It validates ticket time, schedules the session key, decrypts old/v2 response data, checks endpoint/call-number binding for v2, validates challenge id and level, derives per-connection checksum material, and stores identity unless `user_ok` handles authorization.

Dependencies and integration: Integrates Rx server security ops, ticket.c/ticket5.c, fcrypt, private structures, stats, and configuration flags such as dot-check disabling.

Risks: Challenge randomness is legacy time-seeded fcrypt. Authentication relies on callback correctness and DES-derived session keys. V2 endpoint and call-number checks are critical replay defenses.

Test signals: `stress_s.c` runs a server using this path; `stress_c.c` hijack/call tests validate replay and challenge-redirection defenses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/rxkad/rxkad_server.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/rxkad/sboxes.h -->
# sources/distributed-fs/openafs/src/rxkad/sboxes.h

Purpose: Supplies four 256-byte substitution tables for the fcrypt block cipher.

Important APIs/data: `sbox0`, `sbox1`, `sbox2`, and `sbox3` are `static const unsigned char` arrays indexed by bytes of the fcrypt round input. They are arranged so `fc_ecb_encrypt` can combine substitution and byte permutation.

Control flow and state: No flow or mutable state. Inclusion creates private static table copies in translation units that include it; this group uses it in `fcrypt.c`.

Dependencies and integration: Direct dependency of `fcrypt.c`; indirectly affects every rxkad encrypted packet, packet checksum, and challenge response.

Risks: Table edits silently change the cipher and break interoperability. The static-header pattern can duplicate data if included elsewhere.

Test signals: Known-vector and round-trip behavior in `fc_test`/`tcrypt` would catch accidental table changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/rxkad/sboxes.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/rxkad/stats.h -->
# sources/distributed-fs/openafs/src/rxkad/stats.h

Purpose: Defines rxkad statistics structures and increment/aggregation macros for threaded and non-threaded builds.

Important APIs/types: `struct rxkad_stats` or `rxkad_stats_t` tracks connections, destruction paths, expiry, challenge/response counts, packet prepare/check counts, encrypted/decrypted bytes, fcrypt/DES operations, object counts, and spares. Pthread builds maintain `rxkad_global_stats`, `rxkad_stats_key`, and macros that lazily create per-thread stat records. Non-pthread builds mutate global `rxkad_stats` directly.

Control flow and state: Pthread stats are inserted into a global doubly linked list and aggregated by `rxkad_stats_agg` in `rxkad_common.c`. Macros allocate thread-local records on first use.

Dependencies and integration: Included by rxkad client/server/common and fcrypt code; uses pthreads and `opr_Verify` in threaded builds.

Risks: Comments explicitly accept nearly accurate aggregation. Thread-local allocations are not freed by a destructor in this header. OpenBSD-specific macros disable add/sub operations due to known issues.

Test signals: Stress tests with `-printstats` and packet operations drive counters; build matrix coverage is important because macro behavior differs by pthread/kernel platform.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/rxkad/stats.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/rxkad/tcrypt.c -->
# sources/distributed-fs/openafs/src/rxkad/tcrypt.c

Purpose: Standalone diagnostic and timing program for the fcrypt primitive.

Important APIs/functions: `print_msg` prints 8-byte-aligned buffers and a simple checksum. `compare` counts changed bits between two 64-bit blocks. `main` supports timing ECB encryption, timing key scheduling, CBC round-trip testing, and avalanche testing across data/key bit flips.

Control flow and state: In normal mode it iterates even round counts, optionally changing global `ROUNDS` under `TCRYPT`, encrypts a fixed block under key `abcdefgh`, flips every data and effective key bit, and reports average/minimum bit differences. CBC mode constructs a 40-byte message, encrypts/decrypts it, and compares output.

Dependencies and integration: Includes `fcrypt.h` and defines a local `ktc_encryptionKey` for standalone compilation. It also includes component version metadata.

Risks: Old K&R-style function definitions and some suspicious CBC IV local usage reflect its diagnostic nature. It is not a production test harness and mostly reports rather than asserts.

Test signals: Useful manual signal for cipher reversibility, avalanche quality, and rough performance.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/rxkad/tcrypt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/rxkad/test/Makefile.in -->
# sources/distributed-fs/openafs/src/rxkad/test/Makefile.in

Purpose: Automake-style makefile template for rxkad stress and fcrypt tests.

Important targets: `all`, `test`, and `system` build `stress`, `th_stress`, and `fc_test`. RXGEN rules generate `stress.ss.c`, `stress.cs.c`, `stress.xdr.c`, and `stress.h` from `stress.rg`. Error-table rules generate `stress_errs.c/h`. Separate LWP and pthread link lines build legacy and threaded stress binaries.

Control flow and state: Build orchestration only. `clean` removes generated RPC stubs, error files, binaries, and objects. `fc_test.o` adds rxkad include paths.

Dependencies and integration: Links auth, rx, lwp, cmd, rxkad, hcrypto, com_err, util, opr, rfc3961, roken, pthread, and generated RPC/error sources.

Risks: Generated source dependencies must be correct or stale stubs can mask interface changes. Library order is significant for legacy static linking.

Test signals: Successful `stress`, `th_stress`, and `fc_test` builds provide compile/link coverage for rxkad core, test RPCs, and hcrypto integration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/rxkad/test/Makefile.in -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/rxkad/test/fc_test.c -->
# sources/distributed-fs/openafs/src/rxkad/test/fc_test.c

Purpose: Automated regression test for fcrypt block and CBC operations.

Important flow: Defines static input, expected encrypted output, and key bytes. `main` schedules the key, verifies ECB encryption against expected bytes, verifies ECB decryption back to cleartext, verifies CBC encryption against expected two-block output with an all-zero IV, and verifies CBC decryption back to cleartext.

Dependencies and integration: Uses TAP-style helpers from `tests/tap/basic.h`, OpenAFS config headers, `rx/rxkad.h`, `fcrypt.h`, and `rxkad_prototypes.h`.

State and persistence: No persistent state. Test-local IV arrays are reset for encrypt/decrypt checks.

Risks: The test has narrow vectors but is valuable because fcrypt interoperability depends on exact byte order and S-box behavior.

Test signals: Emits four planned TAP checks covering ECB encrypt, ECB decrypt, CBC encrypt, and CBC decrypt.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/rxkad/test/fc_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/rxkad/test/stress.c -->
# sources/distributed-fs/openafs/src/rxkad/test/stress.c

Purpose: Command-line driver for the rxkad stress test, starting server and/or client roles and translating options into shared parameter structs.

Important APIs/functions: `StringToAuth` parses authentication names into rxkad levels or unauthenticated mode. `CommandProc` handles all command options, starts server worker via pthread or LWP, configures client load/call/hijack/repeat/timing/token options, initializes Rx, and starts the client. `main` builds the command syntax.

Control flow and state: Defaults to combined local server and client if neither role is specified. Server parameters include thread count, minimum auth, trace, and keyfile. Client parameters include target server, call counts, transfer sizes, auth level, repeat behavior, max skew, token use, cell, and stop-server behavior.

Dependencies and integration: Uses OpenAFS command parser, Rx, rxkad, LWP/pthread abstractions, stress RPC generated headers, and globals such as `rxi_2dchoice`.

Risks: Many options mutate global Rx behavior. Some compatibility options are retained but ignored. Combined server/client mode depends on thread/LWP scheduling.

Test signals: This is the entrypoint for load, call-number replay, checksum hijack, timing, and server shutdown test modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/rxkad/test/stress.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/rxkad/test/stress_c.c -->
# sources/distributed-fs/openafs/src/rxkad/test/stress_c.c

Purpose: Client-side implementation for rxkad stress tests, including load generation, generated-ticket setup, real-token setup, call-number replay tests, and packet hijack tests.

Important APIs/functions: `GetToken` retrieves existing AFS tokens; `GetTicket` creates a test v4-style ticket. `Copious`, `DoClient`, `RunLoadTest`, and `RepeatLoadTest` perform fast, slow, and large streaming RPCs over multiple worker threads/LWPs. `RunCallTest` manipulates call-number vectors to verify replay detection and v2 challenge call-number synchronization. `RunHijackTest` installs Rx packet hooks to zero or mutate packet checksums and redirect challenges between connections. `rxkst_StartClient` wires security objects, runs requested tests, prints stats, finalizes Rx, and exits.

Control flow and state: Worker structs track concurrent call exit codes. Multi-channel tests track per-channel call numbers. Hijack tests use global incoming/outgoing operation structs and Rx hooks `rx_justReceived` and `rx_almostSent` to observe or alter packets.

Dependencies and integration: Uses rxkad client constructors, ticket creation, DES random-key helpers, generated stress RPC stubs, Rx internal packet/call-number APIs, and auth token APIs.

Risks: Tests intentionally create broken client behavior and manipulate Rx internals. Hooks must be cleared after hijack tests. Generated tickets use a static test service key unless `-usetokens` is selected.

Test signals: Strong coverage for replay prevention, checksum downgrade detection, checksum tamper detection, challenge-oracle prevention, concurrent channel behavior, streaming integrity, and load timing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/rxkad/test/stress_c.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/rxkad/test/stress_internal.h -->
# sources/distributed-fs/openafs/src/rxkad/test/stress_internal.h

Purpose: Shared private definitions for rxkad stress client/server sources.

Important APIs/types: Declares `serviceKey`, `serviceKeyVersion`, test principal constants, `serverParms`, `clientParms`, `rxkst_StartServer`, and compatibility `opaque` typedefs. It also defines a local `assert` macro and compatibility aliases for older Rx symbols.

Control flow and state: Header only. Parameter structs carry command-line configuration from `stress.c` into server/client implementations.

Dependencies and integration: Included by `stress.c`, `stress_c.c`, and `stress_s.c`; depends on generated `stress.h` and rxkad public types.

Risks: The local `assert` aborts the process and is always active. Constants hard-code test identities and cell names.

Test signals: Compile-time glue for every stress mode; incorrect struct fields would break command dispatch or auth setup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/rxkad/test/stress_internal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/rxkad/test/stress_s.c -->
# sources/distributed-fs/openafs/src/rxkad/test/stress_s.c

Purpose: Server-side implementation for the rxkad stress RPC service.

Important APIs/functions: `GetKey` returns a static service key or reads an AFS keyfile and selects a kvno. `rxkst_StartServer` creates rxnull and rxkad server security classes and starts the Rx service. `CheckAuth` verifies security class, minimum auth level, and consistent authenticated client identity. RPC handlers implement `Kill`, `Fast`, `Slow`, and `Copious`.

Control flow and state: Server startup installs `minAuth`, configures service min/max procs, and donates the startup thread to `rx_StartServer`. `CheckAuth` caches the first rxkad client identity and requires later calls to match. `Copious` reads a requested byte stream, checks sum, writes a generated stream, and returns output sum. A small free list reuses 10KB buffers.

Dependencies and integration: Uses rxnull/rxkad server constructors, generated stress RPC executor, AFS keyfile structures, Rx call APIs, and stress error codes.

Risks: `Kill` intentionally finalizes and exits the process. Static identity cache and buffer free list are process-global. Keyfile parsing reads the whole legacy key structure and assumes expected layout.

Test signals: Provides server behavior used by load, auth, call replay, hijack, and stop-server client tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/rxkad/test/stress_s.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/rxkad/test/stress_test_mp -->
# sources/distributed-fs/openafs/src/rxkad/test/stress_test_mp

Purpose: Shell helper for running repeated multi-process/threaded stress tests against rxkad.

Important flow: Defines loops and command aliases around `stm`/stress invocation, runs server and client combinations, and includes crypt-auth test invocations in the background.

State and persistence: Shell-only orchestration; process state is external to the script. It relies on the stress binary and environment rather than storing artifacts.

Dependencies and integration: Integrates with `stress`/`th_stress` test programs built by `Makefile.in`.

Risks: Background processes and timing make failures environment-sensitive. It is a manual/system stress helper rather than a deterministic unit test.

Test signals: Useful for repeated auth/crypt stress runs and multi-process behavior not covered by single TAP tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/rxkad/test/stress_test_mp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/rxkad/ticket.c -->
# sources/distributed-fs/openafs/src/rxkad/ticket.c

Purpose: Implements legacy Kerberos v4/Athena-style rxkad ticket assembly, encryption, decryption, lifetime conversion, and time validation.

Important APIs/functions: `tkt_DecodeTicket` DES-PCBC decrypts a ticket and parses client/server fields. `tkt_MakeTicket` assembles and DES-PCBC encrypts a ticket. `tkt_CheckTimes` validates start/end/now with skew and max lifetime. `ktohl` handles ticket-endian flags. `life_to_time` and `time_to_life` convert compact lifetime bytes.

Control flow and state: Decode validates ticket length and 8-byte alignment, schedules DES key, decrypts using the key as IV, parses strings and session key, computes end time, and checks time validity. Encode validates strings, writes fields in network order, computes a lifetime byte, rounds to 8 bytes, and encrypts in place.

Dependencies and integration: Uses hcrypto DES, Rx error codes, `lifetimes.h`, `rxkad.h`, and key conversion helpers. Server response validation calls it for non-v5 tickets; stress client uses it to generate test tickets.

Risks: DES PCBC and v4 ticket formats are legacy. String parsing uses bounded protocol maxima but relies on decrypted NUL-terminated fields. `NEVERDATE` tickets are accepted subject to server policy.

Test signals: Stress-generated tickets exercise encode/decode; server auth paths exercise decode and time validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/rxkad/ticket.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/rxkad/ticket5.c -->
# sources/distributed-fs/openafs/src/rxkad/ticket5.c

Purpose: Implements Kerberos v5 ticket decoding/creation support for rxkad while deriving an rxkad-compatible 8-byte DES session key.

Important APIs/functions: `tkt_DecodeTicket5` decodes full v5 tickets or encrypted-part-only tickets, obtains service keys by kvno/enctype, decrypts enc-parts, converts v5 principals into rxkad v4-style name/instance/cell, validates flags/times, and derives the rxkad session key. `tkt_MakeTicket5` creates encrypted-part-only tickets. `tkt_DeriveDesKey` maps DES keys directly or derives DES keys from other enctypes. Internal helpers verify DES CRC/MD4/MD5 checksums, decrypt DES enc-parts, compress 3DES parity bits, and run SP800-108-style HMAC-MD5 derivation.

Control flow and state: The file includes renamed Heimdal DER and generated ASN.1 code directly. Decode chooses native DES decrypt for DES enctypes or hcrypto krb5 decrypt for other valid enctypes via `get_key_enctype`. Principal conversion applies service mapping and optional dot rejection. All decoded ASN.1 structures and crypto contexts are cleaned before return.

Dependencies and integration: Depends on hcrypto MD4/MD5/DES/HMAC, krb5 crypto APIs, `v5gen-rewrite.h`, `v5gen.h`, `der.h`, bundled `v5der.c`, generated `v5gen.c`, and rfc3961 constants. Called by `rxkad_server.c`.

Risks: Large stack buffers are bounded by `MAXKRB5TICKETLEN`. Dot-check disabling is configurable and security-sensitive. Non-DES keys are intentionally collapsed to DES-strength rxkad keys for protocol compatibility.

Test signals: Server-side v5 ticket acceptance is covered when stress or integration tests use v5 tokens; direct unit coverage is not visible in this subset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/rxkad/ticket5.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/rxkad/v5der.c -->
# sources/distributed-fs/openafs/src/rxkad/v5der.c

Purpose: Bundled Heimdal DER helper implementation used by rxkad Kerberos v5 ASN.1 generated code.

Important APIs/functions: Provides `_der_timegm`, `_der_gmtime`, DER getters for integers, lengths, booleans, strings, octet strings including BER constructed form, OIDs, tags, times, and bit strings; DER putters for the same families; free functions; DER length calculators; and deep copy helpers.

Control flow and state: Decode helpers validate lengths, allocate output buffers, return ASN.1 error codes, and free partial state on some failures. Encoding writes backward from the end of caller-provided buffers, matching Heimdal generated encoder expectations. Time helpers bound far-future calculations to avoid denial-of-service loops.

Dependencies and integration: Included directly by `ticket5.c` after `v5gen-rewrite.h`, so symbols are renamed to `_rxkad_v5_*`. It depends on ASN.1 error codes, Heimdal types from `der.h`/`v5gen.h`, and libc allocation/time functions.

Risks: Memory ownership is caller-sensitive. Some helpers accept BER indefinite/constructed forms even in a DER support file for compatibility. Because it is included into `ticket5.c`, local warnings and symbol rewriting matter for build hygiene.

Test signals: Any Kerberos v5 ticket decode/encode path exercises this file extensively through generated ASN.1 functions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/rxkad/v5der.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/rxkad/v5gen-rewrite.h -->
# sources/distributed-fs/openafs/src/rxkad/v5gen-rewrite.h

Purpose: Renames bundled Heimdal generated ASN.1 and DER symbols into an rxkad-private namespace.

Important APIs/data: Defines macros mapping `encode_*`, `decode_*`, `free_*`, `length_*`, `copy_*`, DER helper functions, and ticket-flag conversion helpers to `_rxkad_v5_*` names.

Control flow and state: Header-only preprocessor rewrite layer. It must be included before `v5gen.h`, `v5der.c`, and `v5gen.c` are compiled into `ticket5.c`.

Dependencies and integration: Generated from rxkad's v5 import workflow and documented by `README.v5`. It prevents symbol collisions with system Heimdal/MIT libraries or other OpenAFS components.

Risks: Missing a macro can export an unprefixed helper and collide at link time. Incorrect macro mapping can break generated-code calls in subtle ways. The file is mechanically generated and should stay synchronized with imported ASN.1/DER code.

Test signals: Link tests and v5 ticket encode/decode tests would catch most missing rewrites; `nm` checks described in the v5 README are useful for symbol hygiene.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/rxkad/v5gen-rewrite.h -->
