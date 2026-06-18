# Research: subset-b-007781

This grouped report covers the requested OpenAFS kauth, kopenafs, libacl, and libadmin utility files. Each section preserves the source path in its title and is wrapped for deterministic reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/kauth/krb_tf.c -->
## sources/distributed-fs/openafs/src/kauth/krb_tf.c

Purpose: `krb_tf.c` exports `krb_write_ticket_file`, a compatibility bridge that takes the caller's existing AFS ticket-granting token and writes a Kerberos v4-style ticket cache file. It exists so AFS authentication can interoperate with tools that expect the historical `/tmp/tkt<uid>` or `KRBTKFILE` ticket-file format.

Important APIs and control flow: the function validates the realm length, constructs a `krbtgt.<realm>` server principal, lowercases the cell realm for the token lookup, and calls `ktc_GetToken` to fetch the token plus client principal from the kernel/interim token cache. It chooses the output path from `KRBTKFILE` or `gettmpdir()/tkt<uid>`, opens it with mode `0700`, and writes the client name/instance header followed by service, instance, uppercase realm, session key, Kerberos lifetime byte expanded into an `int`, kvno, ticket length, raw ticket bytes, and issue date.

State and persistence: this is explicitly persistent local state: it truncates or creates a ticket cache file containing reusable authentication material. It does not fsync or atomically replace the file, so interrupted writes can leave a partial cache. It closes the descriptor on both success and write failure.

Dependencies and integration points: depends on `ktc_GetToken`, `time_to_life`, `lcstring`, `ucstring`, OpenAFS `ktc_principal`/`ktc_token`, and platform temp-directory helpers. The format is documented in the file comment as Kerberos-derived but with null-terminated strings and host-order scalar fields.

Risks: the code treats `fd <= 0` as open failure, so a valid descriptor 0 would be reported as an error. Ticket cache data is written in host byte order, which matches the historical local-file contract but is not portable across architectures. The cache contains secret material; permissions are restrictive, but path selection via `KRBTKFILE` can target arbitrary locations selected by the environment.

Test signals: no direct test is in this file. `manyklog.c` and `kauth/test/multiklog.c` expose `-tmp` flows that call this function after authentication, giving integration coverage when those tools are built and run against a live cell.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/kauth/krb_tf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/kauth/krb_udp.c -->
## sources/distributed-fs/openafs/src/kauth/krb_udp.c

Purpose: `krb_udp.c` implements the kaserver's UDP-facing Kerberos v4 compatibility service. It listens on Kerberos v4 and Kerberos v5 UDP service ports, accepts authentication and application ticket requests, translates them into KA database reads, and emits Kerberos v4 protocol replies so Kerberos clients can obtain AFS tickets.

Important APIs and functions: `init_krb_udp` opens and binds UDP sockets, starts the `SocketListener` LWP, and starts `FiveMinuteCheckLWP` to reopen logs periodically. `process_udp_request` validates `KRB_PROT_VERSION`, extracts byte order from the message type low bit, and dispatches to `process_udp_auth` for `AUTH_MSG_KDC_REQUEST` or `process_udp_appl` for `AUTH_MSG_APPL_REQUEST`. `UDP_Authenticate` handles initial ticket issuance from a name/password-derived key. `UDP_GetTicket` validates an existing TGT and authenticator, then issues a service ticket. Helper routines include `create_cipher`, `create_reply`, `check_auth`, and `err_packet`.

Control flow: listener select-loops over `sock_kerb` and `sock_kerb5`, receives into a fixed `struct packet`, initializes default principal pointers, and processes in-place. Authentication requests parse client principal, realm, timestamp, lifetime, and requested server principal; realm must be empty or match `lrealm`. The server validates user/service entries through ubik read transactions, checks user expiration, TGS flags, password expiration fields, clock skew, max lifetime, and server key lookup, then creates a DES session key, calls `tkt_MakeTicket`, encrypts the reply cipher with the user's key, and sends a KDC reply. Application requests parse kvno, auth realm, ticket, authenticator, and requested service, decode the TGT with the TGS key, verify time and cross-realm policy (`krb4_cross`), decrypt and validate the authenticator, find caller/server entries, enforce `KAFNOTGS` and `KAFNOSEAL`, and returns a new ticket encrypted under the authenticator session key.

State and persistence: runtime state is the two static sockets, global debug flag, global principal buffers used for logging/audit context, and the five-minute log reopen loop. Persistent state is read-only from the KA ubik database. No database mutation happens here.

Dependencies and integration points: includes LWP/IOMGR, Rx, rxkad, ubik, DES, KA database internals, ticket utilities, audit, kalog, and `prot.h` packet constants. It integrates with the kaserver process through `InitAuthServ`, `FindBlock`, `ka_LookupKey`, `ka_LookupKvno`, `KALOG`, and `osi_audit`.

Risks: packet parsing uses pointer arithmetic and macros such as `getstr`/`getint`; several reads assume enough bytes remain before `strlen`, so malformed packets can stress bounds before the final length check. The implementation relies on DES/PCBC and Kerberos v4 semantics, which are legacy cryptography. Error replies include formatted internal error codes. `create_cipher` encrypts in-place and rounds length after encryption, so buffer sizing depends on careful caller limits.

Test signals: the file has a `#if MAIN` standalone harness with stubs for selected dependencies. Broader behavior is indirectly exercised by `test_kaserver`, `test_badtix.c`, `test_getticket.c`, and `test_rxkad_free.c`, which require live kaserver/ubik/cache-manager services.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/kauth/krb_udp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/kauth/manyklog.c -->
## sources/distributed-fs/openafs/src/kauth/manyklog.c

Purpose: `manyklog.c` is a klog-like stress utility intended to authenticate multiple names in one invocation. It borrows the normal klog command-line shape and adds a `-names` list for repeated `ka_UserAuthenticateGeneral` calls.

Important APIs and control flow: `main` builds a `cmd` syntax with switches for principal, password, tmp ticket file, cell, explicit servers, pipe input, silent mode, lifetime, setpag, and multiple names. `CommandProc` scrubs command-line arguments, initializes KA state with `ka_Init`, resolves the local cell and realm, parses explicit cell/server options, gets the password from the argument, stdin, or `ka_UserReadPassword`, optionally configures ubik server addresses with `ka_ExplicitCell`, and loops over `-names`, calling `ka_UserAuthenticateGeneral` with `KA_USERAUTH_DOSETPAG2` if requested.

State and persistence: stores password in a stack buffer and clears password argument strings. Authentication writes tokens through lower-level KA/KTC helpers. `-tmp` is parsed into `writeTicketFile`, but this source does not actually call `krb_write_ticket_file` after authentication, unlike `multiklog.c`.

Dependencies and integration points: depends on `cmd`, cellconfig, ubik client-list parsing, KA user-auth APIs, Rx shutdown, and Unix user lookup. It also supplies a stub `osi_audit` for linking outside the full audit environment.

Risks: this file appears historically stale or not built by the shown test Makefile. It contains apparent compile issues in the checked source, including `p if (code || !(lcell = ka_LocalCell()))` and use of `itp` without a visible declaration. It should be treated as legacy or broken until a target build proves otherwise. Password handling uses `strncpy` without guaranteed final NUL in several buffers.

Test signals: no build target in `kauth/test/Makefile.in` references `manyklog.c`. Similar maintained behavior is covered by `test/multiklog.c`, which is explicitly the only known-working C test target in that Makefile.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/kauth/manyklog.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/kauth/prot.h -->
## sources/distributed-fs/openafs/src/kauth/prot.h

Purpose: `prot.h` defines Kerberos v4 protocol constants, packet field macros, default ports, maximum packet/text lengths, message type values, and public Kerberos error codes used by kauth UDP compatibility code.

Important types and macros: it defines `KRB_PORT` 750, `KRB5_PORT` 88, `KRB_PROT_VERSION` 4, `MAX_PKT_LEN`/`MAX_TXT_LEN` 1000, and packet access macros such as `pkt_version`, `pkt_msg_type`, `pkt_a_name`, `pkt_a_inst`, `pkt_a_realm`, `pkt_time_ws`, `pkt_x_date`, `pkt_err_code`, and `pkt_err_text`. Message constants leave the low bit for byte order. Error constants range from `KERB_ERR_OK` to `KERB_ERR_NULL_KEY`, with `KERB_ERR_MAXIMUM` set to 10.

Control flow and integration: this header has no runtime control flow, but it is central to `krb_udp.c` and `user_nt.c` packet construction/parsing. The macros encode wire layout assumptions directly as pointer offsets based on null-terminated strings.

State and persistence: none.

Dependencies: no external includes beyond its guard, but callers must provide packet-like objects with a `dat` member for the macros.

Risks: macros do not perform bounds checking and use repeated `strlen` on packet contents. Any caller must validate packet length before using them on untrusted network data. Operator precedence in message constants relies on C precedence of shift vs bitwise operations; current usage is consistent but not self-documenting.

Test signals: packet layout is indirectly exercised by UDP authentication tests and by the Windows client-side implementation in `user_nt.c`, which uses these constants/macros to parse replies.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/kauth/prot.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/kauth/rebuild.c -->
## sources/distributed-fs/openafs/src/kauth/rebuild.c

Purpose: `rebuild.c` implements `kadb_check`, an offline KA database checker and optional rebuild-script generator. It reads a ubik database file, validates its ubik and KA headers, walks database entries and link chains, reports structural problems, and can emit `kas` commands to recreate normal user entries.

Important APIs and functions: `readUbikHeader` reads and validates the ubik header. `CheckHeader` converts and validates the KA header. `PrintHeader` and `PrintEntry` provide diagnostic output. `ntohEntry` converts a `kaentry` to host order, though the main loop notably reads entries without calling it before inspecting flags in the shown source. `NameHash` recomputes the KA name hash. `readDB` seeks past the ubik header and reads database-relative offsets. `RebuildEntry` writes `create`, `setfields`, and `setkey` commands. `WorkerBee` drives command parsing and validation. `badEntry` explains inconsistent state bitsets.

Control flow: after opening and sizing the database, the program verifies ubik/header properties, computes how many `kaentry` slots exist, classifies each slot as normal/free/oldkey/past-EOF/unrecognized, checks key parity and weak DES keys for normal entries, optionally prints entries or emits rebuild commands, then independently follows name hash chains, free chain, and old-key chain. A final pass compares classification bits with chain-membership bits to detect missing, duplicate, circular, or misallocated entries.

State and persistence: it reads the database file read-only. If `-rebuild` is supplied, it writes a command script to the chosen output path. Global state includes `fd`, `out`, `whoami`, and listing/verbosity flags.

Dependencies and integration points: depends on ubik on-disk header layout, `kadatabase`/`kauth` structures, DES key checks, KA string/byte conversion helpers, `cmd`, and com_err. The rebuild script assumes `kas` command semantics such as `create`, `setfields`, and `setkey`.

Risks: on-disk endianness handling is delicate; header conversion is explicit but entry conversion is not consistently applied in the visible main scan. Output rebuilds entries with `-initial_password foo` and then sets keys, so script protection is important. Several allocation/read failures exit directly. Hash-chain walking trusts offsets enough to index into `entrys`, so corrupt files can cause out-of-range behavior if offsets are not sane.

Test signals: no direct automated test in this subset. Its signals are operational: run against known-good and intentionally corrupted KA ubik databases, with `-uheader`, `-kheader`, `-entries`, `-verbose`, and `-rebuild` outputs compared.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/kauth/rebuild.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/kauth/test/Makefile.in -->
## sources/distributed-fs/openafs/src/kauth/test/Makefile.in

Purpose: this makefile builds kauth test utilities and defines the historical `runtest` integration sequence.

Important targets: `all test tests` build only `multiklog`, and the comment says the only tests known to work are `multiklog` and Tcl scripts. Additional explicit targets build `test_date`, `test_badtix`, `decode_ticket`, `test_interim_ktc`, `test_rxkad_free`, `test_getticket`, and `background`. `runtest` builds selected helpers, runs `test_interim_ktc`, `test_kaserver`, and two `test_rxkad_free` modes.

Dependencies and integration points: links against LWP, DES, rxkad, auth, cmd, ubik, prot, sys, rx, com_err, kauth, and afsutil. Test configuration variables require real usernames, passwords, Vice IDs, optional remote-cell credentials, and running KA/PT/cache-manager services.

State and persistence: test scripts create files/processes under `/tmp`, start background kaserver instances, and manipulate local token state and test directories.

Risks: defaults such as `TESTERNAME=xxx` and `TESTERPASSWORD=xxx` make `runtest` unsuitable without explicit local configuration. Several test programs are not part of default `all`, and the file itself warns that most C tests may not be known-good.

Test signals: the file is the primary signal map for kauth tests: `multiklog` is the default build smoke test; `runtest` is the broader integration lane for token cache, kaserver, ticket, and rxkad cleanup behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/kauth/test/Makefile.in -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/kauth/test/background.c -->
## sources/distributed-fs/openafs/src/kauth/test/background.c

Purpose: `background.c` is a minimal helper for starting a command in the background and printing the child PID for later cleanup by scripts such as `test_kaserver`.

Important APIs and control flow: `main` requires at least one command argument, forks, prints the child PID and exits in the parent, and calls `execve(argv[1], argv + 1, 0)` in the child. On exec failure, it prints `perror`.

State and persistence: no durable state itself, but it intentionally leaves the child process running. Environment passed to the child is null because `execve` is called with a null environment pointer.

Dependencies and integration points: used by the csh `test_kaserver` script to launch `kaserver` and write its PID to `/tmp/pid`.

Risks: no argument validation beyond `argc == 1`; no environment propagation may change child behavior; parent writes just the PID without newline. It uses K&R style and implicit-int-era patterns.

Test signals: its success is observable by scripts reading the printed PID and being able to kill the launched process.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/kauth/test/background.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/kauth/test/multiklog.c -->
## sources/distributed-fs/openafs/src/kauth/test/multiklog.c

Purpose: `multiklog.c` is a klog-derived stress test that repeats AFS authentication a configurable number of times. It is meant to expose repeated-login failures, leaks, and token/ticket behavior rather than serve as a user tool.

Important APIs and control flow: `main` defines a `cmd` syntax with principal, password, tmp ticket file, cell, explicit servers, stdin password, silent mode, lifetime, and `-repeat`. `CommandProc` scrubs command-line arguments, initializes KA, resolves cell/realm, parses server lists, resolves principal from arguments or Unix uid, reads password, converts lifetime strings, applies explicit ubik server lists, and loops `reps` times calling `ka_UserAuthenticateGeneral(KA_USERAUTH_VERSION, ...)`. It records the last non-zero error, zeroes the password buffer, and optionally calls `krb_write_ticket_file` when `-tmp` is set.

State and persistence: repeated authentication updates local token cache state through lower-level auth APIs. Optional `-tmp` writes a Kerberos ticket file. It scrubs command-line password storage and stack password buffer before exit.

Dependencies and integration points: depends on command parser, Unix password database, ubik server parsing, cellconfig, KA authentication APIs, `krb_tf.c` for ticket file writing, and a stub `osi_audit`.

Risks: still uses older C idioms and `strncpy` patterns that may not always terminate. Exit code is the raw KA code in some paths. Repeated authentication can alter the caller's token state unless isolated in a PAG/test environment.

Test signals: default kauth test build target creates `multiklog`, and its primary signal is successful repeated authentication with `-repeat` under real cell credentials.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/kauth/test/multiklog.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/kauth/test/test_badtix.c -->
## sources/distributed-fs/openafs/src/kauth/test/test_badtix.c

Purpose: `test_badtix.c` is a broad KA ticket and old-key regression test. It validates string-to-key vectors, live authentication, service ticket behavior, bad-key rejection, forged/altered ticket handling, auto password-change/old-key rollover, and optional execution under a new PAG.

Important APIs and functions: `print_entry` displays `kaentryinfo`; `TestOldKeys` exercises admin/TGS token validity across password/key changes and auto-CPW timing; `main` initializes error tables, validates `lcstring`/`ucstring` and `strcasecmp`, tests `ka_StringToKey` against hard-coded DES-key vectors, initializes rx/ka/ubik, fetches the `guest` key through loopback `KAM_GetPassword` or falls back to string-to-key, obtains TGS/admin tokens, checks jittered ticket times, tests `KAM_SetPassword` validation, constructs an AuthServer ticket with `tkt_MakeTicket`, damages a ticket byte, and expects rxkad rejection.

Control flow: the program first runs local deterministic conversion tests, then moves into live kaserver integration. `TestOldKeys` creates an alternate `krbtgt` principal, runs a timed vector of password changes, debug calls, token captures, and field updates, then later verifies all saved admin and TGS tokens still work with expected kvno behavior before deleting the alternate user.

State and persistence: mutates the KA database substantially: creates/deletes users, changes service passwords, changes fields/lifetimes, and may exec a supplied script after `setpag`. It also interacts with local token/PAG state and uses loopback kaserver connections.

Dependencies and integration points: requires running authentication and maintenance services, ubik, rxkad, DES, LWP/IOMGR timing, `kauth` RPCs, and configured test principals. It assumes a local host kaserver via explicit server list.

Risks: destructive against test KA state; not safe for production cells. Timing-sensitive old-key tests depend on auto-CPW intervals and sleeps. Hard-coded principal names and passwords require controlled test fixtures. The code uses legacy DES and old C patterns.

Test signals: success prints `All clear!`; intended failures include bad-key rejection and damaged-ticket rejection. The `test_kaserver` script invokes this with a temporary kaserver and a follow-on script to test bad ticket handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/kauth/test/test_badtix.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/kauth/test/test_date.c -->
## sources/distributed-fs/openafs/src/kauth/test/test_date.c

Purpose: `test_date.c` is a small CLI harness for date parsing and formatting helpers in `kautils`.

Important APIs and control flow: `main` expects a date string argument, calls `ktime_DateToInt32(argv[1], &time)`, and on success formats it with `ka_timestr` into a fixed buffer and prints the result. Usage text mentions `[-n] [-u]`, but the implementation only accepts a single date argument.

State and persistence: none.

Dependencies and integration points: includes `kautils.h` and exercises the KA time conversion API.

Risks: if invoked with no argument, it dereferences `argv[1]` despite only checking `argc > 2`. The usage string is inconsistent with implementation. It uses legacy implicit-int style `main`.

Test signals: useful as a manual smoke test for KA date parsing, but not wired into the default make target.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/kauth/test/test_date.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/kauth/test/test_getticket.c -->
## sources/distributed-fs/openafs/src/kauth/test/test_getticket.c

Purpose: despite its filename, this source identifies itself as `test_rxkad_free` and focuses on ticket lifetime/error behavior for AFS service ticket acquisition. It mutates KA entry flags, expirations, and lifetimes, authenticates through user-level APIs, and verifies resulting AFS token lifetimes and expected failure codes.

Important APIs and functions: `Crash` restores the original AFS token before exiting; `PrintRxkadStats` reports rxkad object/connection counters; `SetFields` wraps `KAM_SetFields` for flags, expiration, and lifetime changes; `CheckLife` compares token end times either exactly or through Kerberos v4 lifetime quantization; `GetTokenLife` calls `ka_UserAuthenticateLife` and validates the installed AFS token; `Main` obtains an admin token and ubik maintenance connection, applies a series of field changes, and tests success/failure outcomes.

Control flow: after parsing admin credentials/cell/server options, it saves the current AFS token, obtains a maintenance token, normalizes flags/lifetimes/expirations for `afs`, `krbtgt`, and the test user, and checks default/user/server/TGS lifetime limiting. It then restores the original token before negative tests for expired users, expired `afs`, `KAFNOSEAL`, `KAFNOTGS`, and old TGS reuse. With `-patient`, it waits about five minutes to test aging of an old TGS ticket.

State and persistence: mutates KA database entries for service and user principals and local token cache state. It tries to restore saved tokens and fields, but failures can leave altered test state.

Dependencies and integration points: requires a live KA maintenance service, cache-manager token store, ubik, rxkad stats, command parser, and admin credentials.

Risks: unsafe outside a controlled test cell because it changes flags and expirations on service principals such as `afs` and `krbtgt`. The source has minor defects such as `fprintf("Can't get admin token\n")` without a stream in one branch. Timing and Kerberos lifetime rounding make assertions sensitive to wall-clock behavior.

Test signals: prints expected lifetime checks and `All Okay` on success. It is buildable through the makefile as `test_getticket`, but not in default `all`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/kauth/test/test_getticket.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/kauth/test/test_interim_ktc.c -->
## sources/distributed-fs/openafs/src/kauth/test/test_interim_ktc.c

Purpose: `test_interim_ktc.c` validates token cache behavior across interim and kernel KTC implementations, including special client-name parsing, auth2-style pioctl compatibility, token forgetting, remote-cell tokens, and real AFS access checks.

Important APIs and functions: printing helpers display principals and tokens. `CheckUnixUID` and `CheckAFSId` verify how `ktc_SetToken`/`ktc_GetToken` preserve or translate client identities based on names like `AFS ID <n>`. `CheckAuth2` manually constructs old Auth2 pioctl buffers with kvno 999 and verifies KTC interpretation. `ListCellsCmd` scans cache-manager cell configuration via `VIOCGETCELL`. ACL helpers copied from `fs` parse and rewrite directory ACL strings. `TryAuthenticating` calls `ka_UserAuthenticate` and validates token times and Vice IDs. `CheckAFSTickets` creates a test directory/file, adjusts ACLs, switches PAGs, authenticates test users, forgets tokens, and verifies access changes.

Control flow: `main` parses tester/local/remote-cell arguments, initializes error tables and cell config, optionally prints an existing token, finds an unused cell token slot, runs pathological `ktc_SetToken` cases, tests AFS ID and Unix UID identity encoding, tests Auth2 token compatibility, frees the unused cell, and then runs filesystem-backed AFS ticket checks in a new PAG.

State and persistence: heavily mutates local token cache/PAG state, creates and removes `./tester_dir/touch`, and changes ACLs on the test directory. It may authenticate to a remote cell if credentials are provided.

Dependencies and integration points: depends on cache-manager pioctls, KA user authentication, KTC APIs, protection server name/CPS lookup, AFS filesystem access, ACL rights constants, and configured test users/Vice IDs.

Risks: requires a writable AFS working directory and valid test accounts. It manipulates ACLs and token state, so failed cleanup can leave local artifacts. Several helper functions use unsafe string concatenation/formatting patterns and old implicit-int declarations.

Test signals: intended success prints `All OK`; the makefile documents prerequisites in detail and includes this in `runtest` with local and optional remote tester settings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/kauth/test/test_interim_ktc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/kauth/test/test_kaserver -->
## sources/distributed-fs/openafs/src/kauth/test/test_kaserver

Purpose: `test_kaserver` is a csh integration script that starts a temporary kaserver, seeds a test database, exercises authentication and password/key operations, and tears the server down.

Important control flow: it prepares `/tmp/db`, launches `kaserver` with `-noauth` through `background`, aliases `kasu` to run `kas` against the local host, creates/admin-enables users and the `afs` service, sets the AuthServer.Admin password, stops the noauth server, restarts with `-fastkeys`, generates a temporary script that runs `tokens` and `klog`, calls `test_badtix`, then performs additional create/password/delete/setkey/setfields/list operations before killing the server.

State and persistence: creates and deletes files in `/tmp/db`, `/tmp/pid`, and `/tmp/foo`; starts/stops background kaserver processes; writes a temporary KA database. It depends on `$user` from the shell environment.

Dependencies and integration points: requires csh, built `background`, `kaserver`, `kas`, `klog`, `kpasswd`, `test_badtix`, `/usr/vice/etc` cellservdb, and historically `/usr/andy/bin/tokens`.

Risks: hard-coded `/tmp` paths and external tool paths make this fragile. It kills PIDs from `/tmp/pid`, so stale files are dangerous. It assumes local hostname service setup and a mutable temp database. Not portable to systems without csh or those historical paths.

Test signals: success is the script completing under `-e`; failures abort. It is included by `runtest` after `test_interim_ktc`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/kauth/test/test_kaserver -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/kauth/test/test_rxkad_free.c -->
## sources/distributed-fs/openafs/src/kauth/test/test_rxkad_free.c

Purpose: `test_rxkad_free.c` stress-tests rxkad object/connection cleanup while repeatedly obtaining admin tokens and making KA RPCs, or while repeatedly calling the higher-level user authentication path.

Important APIs and control flow: `Main` parses iteration count, verbose output, host-usage reporting, rate limiting, reap waiting, do-auth mode, admin credentials, cell, and explicit servers. In normal mode it derives the admin key with `ka_StringToKey`, loops obtaining an admin token via `ka_GetAdminToken`, opens a maintenance ubik connection with `ka_AuthServerConn`, optionally prints connection/security-object details, calls `KAM_GetEntry`, records server usage from ubik RPC connections, and destroys the ubik client. In `-doauth` mode it calls `ka_UserAuthenticateLife` instead. It monitors `sbrk(0)` memory usage over time, finalizes Rx, prints rxkad stats, optionally waits for connection reap, and asserts object/destroy counters match.

State and persistence: writes local token state when `-doauth` is used. Otherwise it creates and destroys rxkad/ubik client objects in memory. It does not persist files.

Dependencies and integration points: requires live KA services, valid admin credentials, rx/rxkad stats globals, ubik, command parser, and optional server list parsing.

Risks: memory-leak detection uses `sbrk`, which is allocator/platform-sensitive. Counter names in the final check include `rxkad_stats_clientObjects`, which may depend on macro/global definitions outside this file. Host-usage reporting is incompatible with `-doauth`. Rate and reap timing affect results.

Test signals: the makefile runs this twice in `runtest`, once normal and once with `-doauth`, both with `-waitforreap`. Success prints stats and exits 0; failures include unmatched rxkad destruction counts or increasing high-water memory.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/kauth/test/test_rxkad_free.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/kauth/user.c -->
## sources/distributed-fs/openafs/src/kauth/user.c

Purpose: `user.c` is the Unix/non-Windows high-level user authentication interface for kauth. It converts passwords into keys, obtains TGT and AFS service tickets, optionally creates/uses PAGs, installs tokens, and exposes password-reading and password-verification wrappers.

Important APIs: `GetTickets` calls `ka_GetAuthToken`, clears the derived key, then calls `ka_GetAFSTicket`. `ka_GetAFSTicket` obtains an `afs` server token via `ka_GetServerToken`; on old pioctl interfaces it resolves the user's PTS Vice ID and installs a token with client name `AFS ID <id>`. `ka_UserAuthenticateGeneral` validates the interface version, initializes KA, derives the key with `ka_StringToKey`, handles alarm preservation on Unix, optionally verifies only with `ka_VerifyUserToken`, optionally calls `setpag`/`ktc_newpag`, applies default max lifetime, and retries with MIT DES `DES_string_to_key` if the Andrew string-to-key path yields `KABADREQUEST`. `ka_UserAuthenticate`, `ka_UserReadPassword`, and `ka_VerifyUserPassword` are compatibility wrappers.

State and persistence: updates process PAG and token cache state through `setpag`, `ktc_newpag`, and `ktc_SetToken` via lower helpers. It clears password-derived keys after use and restores Unix alarms/Rx state if it interrupted a pre-existing alarm.

Dependencies and integration points: depends on hcrypto DES/UI, Rx/rxkad, cellconfig, ptserver client APIs, KTC, KA token helpers, pioctl behavior, and error tables. The old-pioctl PTS path integrates authentication with filesystem identity by converting names to Vice IDs.

Risks: legacy DES fallback broadens compatibility but preserves weak cryptographic modes. Root with null instance is rejected as local-only. Some reason strings are generic or derived from error tables. PTS lookup failures in old-pioctl mode are logged but can return 0 in some error branches, intentionally tolerating inability to translate.

Test signals: exercised by `multiklog`, `test_interim_ktc.c`, `test_getticket.c`, and `test_rxkad_free.c` via `ka_UserAuthenticate*`, `ka_GetServerToken`, and token installation behaviors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/kauth/user.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/kauth/user_nt.c -->
## sources/distributed-fs/openafs/src/kauth/user_nt.c

Purpose: `user_nt.c` is the Windows implementation of high-level kauth authentication. Instead of relying on the Unix KA helper stack, it discovers cell servers, performs a Kerberos v4 UDP ticket request directly, validates/decrypts the reply with either Andrew or MIT string-to-key, and installs the returned AFS token through Windows KTC/RPC paths.

Important APIs and functions: `ka_UserAuthenticateGeneral` delegates to `ka_UserAuthenticateGeneral2`, which resolves cell servers through registry, CellServDB, or DNS; uppercases the realm; derives two candidate keys; sets the Kerberos UDP port from services; calls `krb_get_in_tkt_ext`; maps errors to user-readable reasons; and fills `ktc_principal`/`ktc_token` before `ktc_SetToken`. `ka_AddHostProc`, `krb_add_host`, and `krb_set_port` maintain the server list. `krb_get_in_tkt_ext` constructs the `AUTH_MSG_KDC_REQUEST`, sends it with `send_to_kdc`, validates version/type/byte order, maps kaserver error replies, decrypts and verifies the cipher with `check_response`, extracts session key/ticket/kvno/expiration, checks KDC clock skew, and returns token material. `send_to_kdc`/`send_recv` handle UDP retry/select logic. `pkt_cipher`/`pkt_clen` parse reply cipher offsets. `Andrew_StringToKey` and `StringToKey` implement historical key algorithms.

State and persistence: process-global state includes the linked list of Kerberos hosts, host count, UDP port, swap-bytes flag, debug flag, and static reason buffers. Successful authentication persists an AFS token in the Windows cache-manager/RPC token store. Host list entries are allocated and not freed in this file.

Dependencies and integration points: tightly integrated with Windows headers/RPC, cache-manager cell search (`cm_SearchCellRegistry`, `cm_SearchCellFile`, `cm_SearchCellByDNS`), Kerberos v4 packet constants, DES, crypt, rxkad token definitions, and KTC token installation. It interoperates with `krb_udp.c` server replies.

Risks: uses legacy Kerberos v4 and DES/crypt algorithms. Packet parsing relies on unbounded string macros from Kerberos headers and fixed-size buffers. `krb_nhosts * CLIENT_KRB_TIMEOUT` can be zero if no hosts are recorded, though earlier discovery should add hosts. The server list is global and can accumulate across calls. Error strings use static buffers, so concurrent calls are unsafe.

Test signals: not covered by Unix `kauth/test/Makefile.in`. Best signals are Windows authentication integration tests against kaserver/CellServDB/DNS discovery and cross-checks with server-side `krb_udp.c` behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/kauth/user_nt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/kopenafs/Makefile.in -->
## sources/distributed-fs/openafs/src/kopenafs/Makefile.in

Purpose: this makefile builds and installs `libkopenafs`, a small standalone OpenAFS syscall/pioctl compatibility library and header.

Important targets: `all` builds shared/static `libkopenafs` and installs `kopenafs.h` into the top include directory. `LT_objs` include `glue`, `pioctl`, `setpag`, `kopenafs`, and version object. Foreign source build rules compile code from `../sys`. `syscall.lo` handles platform-specific syscall assembly for SGI, AIX, HP-UX, or creates an empty object fallback. Test targets build `test-unlog` and `test-setpag` statically against `libkopenafs.a`.

State and persistence: build artifacts are libraries, libtool metadata, installed headers, test binaries, and generated version/syscall objects.

Dependencies and integration points: depends on config, libtool, pthread make fragments, sys syscall sources, `libkopenafs.la.sym`, and install variables. It exposes a library intended for Heimdal/KTH `libkafs` compatibility.

Risks: the comment notes foreign implicit rules do not work because sources live elsewhere. Platform-specific syscall assembly paths are fragile and rely on `SYS_NAME`. Shared-library installation removes `.la` files after libtool install.

Test signals: successful build of `libkopenafs.a`/shared library and optional `test-setpag`/`test-unlog` binaries; runtime tests require a native AFS client.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/kopenafs/Makefile.in -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/kopenafs/kopenafs.c -->
## sources/distributed-fs/openafs/src/kopenafs/kopenafs.c

Purpose: `kopenafs.c` implements the public `kopenafs` wrapper API: detect AFS availability, create PAGs, issue pioctls, unlog tokens, and detect whether the process is in a PAG without dragging in the full Rx/auth stack.

Important APIs: `k_hasafs` installs a temporary `SIGSYS` handler, issues a deliberately invalid `VIOCSETTOK` pioctl through `lpioctl`, and considers AFS present if the syscall exists and returns `EINVAL`; it restores `errno` and the signal handler. `k_setpag` calls `lsetpag` retrying on `EINTR`. `k_pioctl` forwards to `lpioctl`. `k_unlog` sends `VIOCUNLOG`. `k_haspag` tries `VIOC_GETPAG` and falls back to `os_haspag`.

Control flow and OS behavior: `os_haspag` is platform-specific. AIX 5.2 uses `getpagvalue("afs")`; AIX 5.1 reports false; other systems inspect group lists for one-group PAG markers or classic two-group PAG encodings and reconstruct the PAG value to check for the `A` marker.

State and persistence: static `syscall_okay` is updated by the SIGSYS handler. `k_setpag` changes process credentials/PAG membership. `k_unlog` clears tokens in the current PAG.

Dependencies and integration points: depends on `afs/afssyscalls.h`, `afs/vioc.h` through `kopenafs.h`, OS signal/group APIs, and sys-layer `lpioctl`/`lsetpag`.

Risks: `k_hasafs` uses a process-wide signal handler and static flag, making concurrent calls signal-sensitive. `os_haspag` allocates based on `getgroups(0,NULL)` and does not handle a negative return before allocation size calculation. Group-list PAG detection is heuristic and OS-layout dependent.

Test signals: `test-setpag.c` exercises `k_hasafs`, `k_haspag`, and `k_setpag`; `test-unlog.c` exercises `k_hasafs` and `k_unlog`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/kopenafs/kopenafs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/kopenafs/kopenafs.h -->
## sources/distributed-fs/openafs/src/kopenafs/kopenafs.h

Purpose: `kopenafs.h` declares the minimal standalone AFS client syscall API compatible with Heimdal/KTH libkafs expectations.

Important APIs: it exposes `k_hasafs`, `k_setpag`, `k_haspag`, `k_unlog`, and `k_pioctl`, and includes `afs/vioc.h` for `VIOC*` constants and `struct ViceIoctl`.

State and persistence: no state in the header; declared functions can change process PAG/token state or issue cache-manager pioctls.

Dependencies and integration points: consumers link against `libkopenafs` and call `k_hasafs` before other functions. The header explicitly states the calls only work with native AFS clients, not the NFS translator.

Risks: the API is intentionally thin and reports only integer syscall-style status, so callers must inspect `errno` for detail.

Test signals: used by `test-setpag.c` and `test-unlog.c`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/kopenafs/kopenafs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/kopenafs/test-setpag.c -->
## sources/distributed-fs/openafs/src/kopenafs/test-setpag.c

Purpose: `test-setpag.c` is a runtime smoke test for `libkopenafs` PAG creation.

Important control flow: if `k_hasafs` returns true, it prints current PAG status via `k_haspag`, calls `k_setpag`, prints status and `errno`, checks that `k_haspag` is now true, and optionally `execvp`s a command supplied on the command line. If AFS is unavailable, it prints that AFS is apparently not running.

State and persistence: changes the current process PAG and optionally executes another program inside that PAG.

Dependencies and integration points: includes public `kopenafs.h` and standard `errno`, `stdio`, `unistd`.

Risks: prints `errno` after `k_setpag` regardless of whether the call succeeded, so stale errno can be misleading. If `execvp` fails, the program does not explicitly report `perror`.

Test signals: expected success is status 0 and `k_haspag` true after `k_setpag`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/kopenafs/test-setpag.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/kopenafs/test-unlog.c -->
## sources/distributed-fs/openafs/src/kopenafs/test-unlog.c

Purpose: `test-unlog.c` is a runtime smoke test for clearing tokens via `libkopenafs`.

Important control flow: it checks `k_hasafs`, calls `k_unlog` if available, and prints status plus `errno`; otherwise it reports that AFS is not running.

State and persistence: clears tokens in the current PAG/session through `VIOCUNLOG`.

Dependencies and integration points: includes `kopenafs.h` and standard error/stdio headers. It is built by the kopenafs makefile test target.

Risks: like `test-setpag`, it prints `errno` even on success where it may be stale. `main` does not return an explicit status in the source.

Test signals: expected success is `k_unlog` status 0 on a machine with a native AFS client.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/kopenafs/test-unlog.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/libacl/Makefile.in -->
## sources/distributed-fs/openafs/src/libacl/Makefile.in

Purpose: this makefile builds the OpenAFS ACL library and installs public ACL/right headers.

Important targets: `all` builds `liboafs_acl.la`, installs static `libacl.a`, and runs `depinstall` for `afs/acl.h`, `afs/prs_fs.h`, and component version generation. `LT_objs` are `aclprocs.lo`, `netprocs.lo`, and version object. The shared library depends on ptserver protection RPC support. `test` descends into `test`.

State and persistence: produces static/shared libraries, installed headers, generated version source, and cleaned object/library files.

Dependencies and integration points: includes config, LWP, and lwptool make fragments; links with ptserver protection library for name/ID translation in ACL conversion.

Risks: install target puts `libacl.a` under `libdir/afs`; consumers must match that library layout. The `clean` target removes `acltest` even though the test binary is produced in a subdirectory target.

Test signals: building `libacl.a`/`liboafs_acl.la` and running `make test` in `libacl/test`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/libacl/Makefile.in -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/libacl/acl.h -->
## sources/distributed-fs/openafs/src/libacl/acl.h

Purpose: `acl.h` defines the internal and external ACL contracts used by AFS file-server/VICE code and declares ACL allocation, conversion, rights-checking, initialization, and byte-order APIs.

Important types and APIs: `acl_accessEntry` stores a protection ID and rights mask. `acl_accessList` stores size, version, total, positive count, negative count, and an entries array; negative entries are stored backwards from the end. `ACL_MAXENTRIES` is 20. External ACLs are strings beginning with positive and negative counts, followed by name/right lines. Declared APIs include `acl_NewACL`, `acl_FreeACL`, `acl_NewExternalACL`, `acl_FreeExternalACL`, `acl_Externalize`, `acl_Internalize`, `_pr` variants with custom translation functions, `acl_Initialize`, `acl_CheckRights`, `acl_IsAMember`, `acl_HtonACL`, and `acl_NtohACL`.

State and persistence: the structure layout is used for secondary storage in VICE, so it is a persistence contract as well as a memory contract.

Dependencies and integration points: includes `afs/ptint.h` for protection server ID/name list types. `acl_CheckRights` is only declared when rxgen ptint types are available.

Risks: fixed `ACL_MAXENTRIES` and compact on-disk format mean callers must validate counts and sizes. Negative-entry reverse storage is non-obvious and must be preserved by serializers.

Test signals: exercised by `aclprocs.c`, `netprocs.c`, and interactive `test/acltest.c`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/libacl/acl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/libacl/aclprocs.c -->
## sources/distributed-fs/openafs/src/libacl/aclprocs.c

Purpose: `aclprocs.c` implements allocation, external/internal string conversion, protection-server name/ID translation, rights evaluation, membership tests, and a small freelist allocator for ACL objects.

Important APIs and functions: `acl_NewACL` and `acl_NewExternalACL` allocate internal and external ACL buffers, reusing `freeList` entries when possible. `acl_FreeACL` and `acl_FreeExternalACL` return buffers to the freelist. `acl_Externalize_pr` converts IDs to names via a caller-supplied function and emits external string format. `acl_Internalize_pr` parses external strings, translates names to IDs, stores positive entries at the front and negative entries at the back, and sorts them with `CmpPlus`/`CmpMinus`. `acl_CheckRights` intersects a caller's CPS group list with positive and negative ACL entries, grants all rights to `SYSADMINID`, and returns positive rights masked by negative rights. `acl_Initialize` checks the package version and initializes a pthread mutex when enabled. `acl_IsAMember` scans a CPS list.

Control flow: internalization starts with count parsing and limit checks, allocates an ACL, reads positive entries in order, reads negative entries into the reversed storage region, calls the name-to-ID translator once with all names, rejects `ANONYMOUSID`, then sorts positive ascending and negative descending. Rights checking walks sorted ACL and CPS arrays in merge style, accumulating matches.

State and persistence: process-global `freeList` caches allocations, protected by `acl_list_mutex` in pthread builds. Internal ACLs are storage-compatible with file-server ACL persistence and may later be converted to network order.

Dependencies and integration points: depends on ptserver client APIs `pr_IdToName` and `pr_NameToId`, rx/xdr types, OpenAFS `opr_Verify`, and constants like `ANONYMOUSID` and `SYSADMINID`.

Risks: allocation failures sometimes abort rather than returning errors. `acl_FreeExternalACL` assumes non-null input. External parsing uses `%63s` and expects tab-delimited rights. The freelist never releases memory back to the system. `acl_CheckRights` assumes sorted group CPS input for merge behavior.

Test signals: `test/acltest.c` exercises allocation, externalization/internalization, rights conversion, and protection-server-backed rights checks interactively.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/libacl/aclprocs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/libacl/netprocs.c -->
## sources/distributed-fs/openafs/src/libacl/netprocs.c

Purpose: `netprocs.c` converts internal ACL structures between host and network byte order with validation.

Important APIs: `acl_HtonACL` validates host-order header fields with `CheckAccessList`, converts active positive and negative entries, then converts header fields with `htonl`. `acl_NtohACL` converts header fields first with `ntohl`, validates them, then converts active entries with `ntohl`.

Control flow and validation: `CheckAccessList` rejects negative/too-large totals, mismatched positive+negative totals, and ACL sizes smaller than the minimum required for the declared active entries. The code intentionally allows `size` to exceed the minimum.

State and persistence: operates in-place on ACL structures, so callers must know whether the object is currently host or network order. The conversion supports on-disk/network persistence of ACLs.

Dependencies and integration points: depends on `acl.h`, rx/xdr byte-order environment, and ptclient includes for shared ACL type context.

Risks: in-place conversion means a failed or repeated conversion can corrupt caller expectations. Only active positive and negative entries are converted; unused slots are ignored. Callers must not call `acl_HtonACL` on already-network-order data because validation expects host-order counts.

Test signals: should be covered by round-trip tests that allocate ACLs with positive and negative entries, hton/ntoh them, and compare fields; no direct test in `acltest.c` is obvious from the source.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/libacl/netprocs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/libacl/prs_fs.h -->
## sources/distributed-fs/openafs/src/libacl/prs_fs.h

Purpose: `prs_fs.h` defines AFS directory/file ACL rights bit masks used by filesystem ACL tools, tests, and server-side ACL checks.

Important constants: base rights are `PRSFS_READ`, `PRSFS_WRITE`, `PRSFS_INSERT`, `PRSFS_LOOKUP`, `PRSFS_DELETE`, `PRSFS_LOCK`, and `PRSFS_ADMINISTER`. User-reserved high bits `PRSFS_USR0` through `PRSFS_USR7` occupy `0x01000000` through `0x80000000`.

State and persistence: rights masks are part of ACL persisted and transmitted state.

Dependencies and integration points: used by ACL tests and filesystem command code to translate symbolic rights like read/write/all into masks.

Risks: high user bits overlap the sign bit for `PRSFS_USR7` when interpreted as signed `int`; callers should treat rights as masks, not signed numeric values.

Test signals: `libacl/test/acltest.c` uses these constants in its `Convert` and `PRights` helpers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/libacl/prs_fs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/libacl/test/Makefile.in -->
## sources/distributed-fs/openafs/src/libacl/test/Makefile.in

Purpose: this makefile builds the interactive ACL test utility.

Important targets: `all` builds `acltest`; `acltest` links `acltest.o` with `-lacl`, `-lprot`, `-lubik`, `-lrx`, `-llwp`, `-lauth`, `-lrxkad`, `-lsys`, and platform libs. `clean` removes objects, archives, binary, and core files.

State and persistence: build artifacts only.

Dependencies and integration points: relies on top-level config/LWP make fragments and library search paths pointing at `TOP_LIBDIR`, destination AFS libs, and the parent directory.

Risks: no `install` or `dest` behavior. The test requires a protection server at runtime, so a successful build is not a full behavior signal.

Test signals: successful link of `acltest`; manual interactive use verifies ACL conversion and rights checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/libacl/test/Makefile.in -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/libacl/test/acltest.c -->
## sources/distributed-fs/openafs/src/libacl/test/acltest.c

Purpose: `acltest.c` is an interactive command shell for manually testing ACL externalization/internalization and rights evaluation against the protection server.

Important APIs and control flow: it initializes the protection client with `pr_Initialize`, keeps up to 20 internal ACL pointers and 20 external ACL strings, and loops reading short commands. `ex` externalizes an internal ACL. `in` internalizes an external ACL. `sa` adds a positive external ACL entry with rights converted by `Convert`. `la` lists external ACL entries using `PRights`. `cr` translates a name to ID, obtains CPS groups with `pr_GetCPS`, and calls `acl_CheckRights`. `q` exits.

State and persistence: stores ACLs in process memory only. It uses a hard-coded `/usr/afs/etc` protection configuration path and talks to a live protection server.

Dependencies and integration points: depends on `acl.h`, `prs_fs.h`, ptclient/protection server APIs, rx/xdr cleanup, and symbolic rights mapping (`read`, `write`, `mail`, `all`, `none`, or individual `rlidwka` letters).

Risks: purely interactive and not scripted. Several code paths use unchecked `scanf` and fixed buffers. The `la` negative-rights branch appears to call `scanf(ptr, ...)` where `sscanf` was likely intended. `sa` performs manual string surgery that may be fragile for multi-digit ACL counts.

Test signals: useful for manual smoke testing, especially `sa`, `in`, `ex`, `la`, and `cr` command sequences against known protection users/groups.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/libacl/test/acltest.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/libadmin/Makefile.in -->
## sources/distributed-fs/openafs/src/libadmin/Makefile.in

Purpose: this makefile installs the top-level AFS admin public header.

Important targets: `all` ensures `${TOP_INCDIR}/afs/afs_Admin.h` is installed from `afs_Admin.h`. `install` and `dest` install the same header into package include directories. `clean` has no commands.

State and persistence: only installed header artifacts.

Dependencies and integration points: includes top-level config and pthread make fragments, indicating admin libraries are pthread-aware even though this makefile only handles the public header.

Risks: no library build happens here; subdirectories such as `adminutil` own utility library construction. Consumers expecting `make` in this directory to build all admin components must rely on higher-level orchestration.

Test signals: successful header installation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/libadmin/Makefile.in -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/libadmin/adminutil/Makefile.in -->
## sources/distributed-fs/openafs/src/libadmin/adminutil/Makefile.in

Purpose: this makefile builds `libafsadminutil.a`, generates and installs admin error-table headers/sources, installs `afs_utilAdmin.h`, and installs the aggregate `afs_AdminErrors.h`.

Important targets and data: `INCLS` lists subsystem admin error headers generated from `.et` files. `ERROROBJS` imports existing subsystem error tables from rxkad, bozo, kauth, auth, cmd, ptserver, ubik, vlserver, volser, and AFS unified errors. `ADMINOBJS` are generated admin error tables plus `afs_utilAdmin.o`. `LIBOBJS` combines both. Rules use `COMPILE_ET_H` and `COMPILE_ET_C` for each admin `.et` table. `libafsadminutil.a` archives all objects and ranlibs the result.

State and persistence: generates many `afs_Admin*Errors.c/.h` files, builds a static library, and installs headers and library into AFS include/lib trees.

Dependencies and integration points: ties together error spaces across many OpenAFS subsystems so admin APIs can report unified status. `afs_utilAdmin.o` depends on all generated and aggregate error headers.

Risks: generated files are removed by `clean`, so build ordering must ensure headers exist before dependent objects. The `install` rule creates `${libdir}` but installs into `${libdir}/afs/libafsadminutil.a`; it assumes the `afs` subdirectory exists or is created elsewhere. Broad cross-subsystem dependencies mean stale generated headers can produce confusing error-code mismatches.

Test signals: successful generation of all error tables and archive creation. Runtime signals are admin-library callers receiving correct mapped error strings/codes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/libadmin/adminutil/Makefile.in -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/libadmin/adminutil/afs_AdminErrors.h -->
## sources/distributed-fs/openafs/src/libadmin/adminutil/afs_AdminErrors.h

Purpose: `afs_AdminErrors.h` is an aggregate public header that includes all generated admin error-table headers.

Important contents: after `afs/param.h`, it includes BOS, client, common, KAS, misc, PTS, util, VOS, and config admin error headers.

State and persistence: no runtime state; it is installed as part of the admin utility API surface.

Dependencies and integration points: depends on generated headers from `adminutil/Makefile.in` and gives admin API consumers a single include for admin error constants.

Risks: build/install order matters because the included generated headers must exist in the include tree. This header does not include lower-level subsystem error tables, only admin-layer generated ones.

Test signals: successful compile of a consumer including `afs/afs_AdminErrors.h` after `adminutil` generation/install.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/libadmin/adminutil/afs_AdminErrors.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/libadmin/adminutil/afs_AdminInternal.h -->
## sources/distributed-fs/openafs/src/libadmin/adminutil/afs_AdminInternal.h

Purpose: `afs_AdminInternal.h` defines private admin-library handle and iterator structures used by the OpenAFS admin APIs to manage tokens, cell connections, server-list cache state, and background RPC iteration.

Important types and APIs: `afs_token_handle_t` includes magic sentinels, validity flags, kernel/source flags, AFS and KAS token flags, security index, cell name, AFS/KAS tokens, arrays of rx security classes, client principal, and end magic. `afs_cell_handle_t` holds magic/valid/null flags, token handle, working cell, ubik clients for KAS/PTS/VOS, validity flags, VOS version flag, and cached server list with TTL. `afs_admin_iterator_t` contains magic/valid flags, mutex/condition variables, background worker thread, cache counters and queue indexes, termination/done flags, last status, RPC-specific data, and callback function pointers. It declares `IteratorInit`, `IteratorNext`, and `IteratorDone`.

Control flow and concurrency model: iterator comments require holding the iterator mutex while manipulating fields, except while making RPCs. The cache size is fixed at `CACHED_ITEMS` 5 and background workers coordinate producers/consumers through `add_item` and `remove_item` conditions.

State and persistence: all structures are in-memory runtime state. Magic constants `BEGIN_MAGIC` and `END_MAGIC` support handle validation and corruption detection.

Dependencies and integration points: includes cellconfig, auth/KTC token types, ubik clients, pthreads, and admin status types from public admin headers. It is the internal contract shared across admin util/client/KAS/PTS/VOS implementations.

Risks: structure fields expose raw pthread and ubik state, so lifecycle ordering is critical. Token handles own arrays of rx security class pointers that must be destroyed exactly once. Iterator callbacks must obey locking rules to avoid deadlocks or cache corruption.

Test signals: no direct tests in this subset. Signals come from admin API iterator tests and leak/race testing around `IteratorInit`/`IteratorNext`/`IteratorDone` under concurrent RPC workloads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/libadmin/adminutil/afs_AdminInternal.h -->
