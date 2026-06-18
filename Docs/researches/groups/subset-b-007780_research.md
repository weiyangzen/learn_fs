# subset-b-007780 Research

Grouped research for the listed OpenAFS `src/kauth` files. Each section preserves its original source path and is delimited for deterministic splitting into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/kauth/crypt.c -->
# sources/distributed-fs/openafs/src/kauth/crypt.c

## Purpose
Provides a local DES-based Unix `crypt(3)` implementation for platforms that need it, specifically noted as used by the Andrew string-to-key path on Windows while Unix platforms use their system `crypt`. It implements classic and extended DES password hashing using generated permutation tables, DES key scheduling, salt handling, and base-64-style result encoding.

## Important APIs, Types, And Functions
The public entry point is `crypt(const char *key, const char *setting)`, returning a pointer to static `cryptresult`. Internal helpers include `des_setkey`, `des_cipher`, `init_des`, `init_perm`, optional `permute`, and debug-only `prtab`. `C_block` is the core packed 64-bit block representation. Static tables include DES IP, expansion, PC1/PC2, rotations, S-boxes, P32, CIFP, `itoa64`, `a64toi`, generated permutation tables, `SPE`, the key schedule `KS`, and `constdatablock`.

## Control Flow
`crypt` converts up to eight password bytes into a DES key block, initializes the DES tables lazily through `des_setkey`, handles extended settings beginning with `_` by folding additional password chunks through repeated encryption, parses iteration count and salt from the setting, encrypts a constant block with `des_cipher`, and encodes the resulting 64 bits into 11 printable characters after the copied salt prefix. `des_setkey` builds 16 key-schedule blocks using PC1/PC2 rotation permutations. `des_cipher` performs initial bit splitting/permutation, repeatedly runs the DES round function with salt-dependent swaps, then applies the final compression/permutation.

## State And Persistence
All state is process-local static memory: generated lookup tables, the key schedule, the readiness flag, and a single static result buffer. There is no disk persistence or locking. The returned pointer is overwritten by later calls and is not thread-safe.

## Dependencies And Integration Points
The file depends on `afsconfig.h`, `afs/param.h`, `roken.h`, and Windows headers. It is part of the kauth compatibility surface used by string-to-key code on Windows and must match expected Unix DES `crypt` behavior for legacy password/key derivation compatibility.

## Risks And Test Signals
The major risk is deliberate legacy cryptography: DES, small salts, static output buffers, and non-thread-safe global state. Portability risks come from byte-order/alignment-sensitive `C_block` use and `long` sizing. Test signals include known `crypt` test vectors, extended setting behavior, Windows Andrew string-to-key interoperability, repeated-call overwrite behavior, and builds across 32-bit and 64-bit Windows targets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/kauth/crypt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/kauth/crypt.h -->
# sources/distributed-fs/openafs/src/kauth/crypt.h

## Purpose
Declares the local `crypt` compatibility function used by the kauth Windows string-to-key path.

## Important APIs, Types, And Functions
The header only defines the include guard `__CRYPT_H_ENV__` and declares `char *crypt(char *, char *)`.

## Control Flow
There is no runtime control flow. Including code calls `crypt` in `crypt.c` to produce legacy DES password-hash material.

## State And Persistence
The header stores no state. The declaration exposes a function whose implementation returns static process-local state.

## Dependencies And Integration Points
It is an integration shim for callers that need a `crypt` declaration on platforms without a suitable system header. It must stay ABI-compatible with the implementation in `crypt.c`.

## Risks And Test Signals
The prototype uses non-const `char *` parameters while `crypt.c` defines `const char *`; strict-prototype builds are the main signal for drift. Functional coverage comes from callers that include the header and link against the local implementation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/kauth/crypt.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/kauth/decode_ticket.c -->
# sources/distributed-fs/openafs/src/kauth/decode_ticket.c

## Purpose
Implements a small diagnostic utility that decodes and prints an AFS/Kerberos-4-style ticket using a supplied server key. It is intended for inspecting ticket contents rather than participating in normal authentication flow.

## Important APIs, Types, And Functions
The only function is `main`. It uses `ka_ReadBytes` to parse octal byte strings, DES parity/weak-key checks, `tkt_DecodeTicket`, `tkt_CheckTimes`, `ka_PrintUserID`, `ka_PrintBytes`, and `ka_timestr`. Key data types are `ktc_principal`, `ktc_encryptionKey`, `Date`, and the fixed `MAXKTCTICKETLEN` ticket buffer.

## Control Flow
The utility initializes RXK and KA error tables, requires exactly two arguments (`key` and `ticket`), parses the key as eight bytes, rejects bad DES server keys, parses the ticket bytes, decodes the ticket into client identity, session key, host, start, and end times, validates ticket time status on decode failure, rejects bad session keys, and prints the client principal, optional cell, session key, and validity interval.

## State And Persistence
All state is stack-local except the static `whoami` program-name pointer. The utility does not write files, tokens, or databases.

## Dependencies And Integration Points
It depends on the kauth utility format for byte-string input, hcrypto DES key validation, rxkad ticket decoding, and OpenAFS error tables. It is a debugging companion for the ticket formats generated by `kaprocs.c` and client code in the broader kauth library.

## Risks And Test Signals
Risks include exposing decrypted session keys on stdout, accepting secret material on the command line, and the assignment-precedence bug-shaped line `if (code = tkt_CheckTimes(...) <= 0)`, which stores a boolean rather than the checker return code. Test signals include successful decode of a known ticket/key pair, rejection of weak or malformed keys, malformed ticket handling, and correct display of expired/not-yet-valid ticket times.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/kauth/decode_ticket.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/kauth/ka-forwarder.c -->
# sources/distributed-fs/openafs/src/kauth/ka-forwarder.c

## Purpose
Implements a UDP forwarding daemon for KA requests on AFS database servers. It listens on a local KA port and forwards client requests to one or more fakeka/MIT Kerberos servers, then forwards replies back to the original client.

## Important APIs, Types, And Functions
Important functions are `perrorexit`, `setup_servers`, `setup_socket`, `packet_is_reply`, and `main`. Global state includes `prog`, `num_servers`, `cur_server`, and the dynamically allocated `servers` array. `BUFFER_SIZE` is 2048.

## Control Flow
`main` parses `-p port`, normalizes `optind`, builds the target server list, binds a UDP socket, opens syslog, and enters an infinite receive/forward loop. Incoming packets from configured servers are treated as replies: the first eight payload bytes are interpreted as saved client address and port, and the rest is sent to that client. Other packets are treated as client requests: the forwarder prepends the client address and port, round-robins to the next server, logs the forwarding event, and sends the augmented packet.

## State And Persistence
State is entirely in memory: configured server addresses, the current round-robin index, and one stack packet buffer per loop iteration. There is no durable state except syslog entries.

## Dependencies And Integration Points
The daemon uses BSD sockets, name/service resolution, syslog, and KA port conventions. It bridges legacy AFS KA clients to a fakeka service and assumes that fakeka understands the prepended 8-byte return address header.

## Risks And Test Signals
There is no authentication of reply sources beyond address/port matching the configured server list, no packet length guard before subtracting 8 on replies, and no IPv6 support. `setup_servers` mutates argv strings when splitting `host/port`. Useful tests cover numeric and DNS host parsing, service-name port parsing, round-robin request forwarding, reply forwarding with embedded client address, short reply packets, socket bind failure, and syslog output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/kauth/ka-forwarder.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/kauth/ka_util.c -->
# sources/distributed-fs/openafs/src/kauth/ka_util.c

## Purpose
Provides a legacy utility to dump an AFS authentication database to text or reconstruct a database from text. It directly reads or writes the Ubik database file instead of using Ubik transactions, so its own comment requires a quiescent database for valid output.

## Important APIs, Types, And Functions
The main functions are old-style `main` and `display_entry`; `es_Report` is a stub to satisfy shared database references. Globals include `kah`, `uv`, `dbase_fd`, `dfp`, `dynamic_statistics`, KA/Ubik placeholder globals, and option flags. It uses `struct ubik_hdr`, `struct ubik_version`, `struct kaheader`, and `struct kaentry`.

## Control Flow
`main` parses options, opens the database path, reads the Ubik header and KA header, initializes KA errors, then either writes a fresh KA header and appends parsed text entries (`-w`) or iterates fixed-size `kaentry` slots and prints each entry with escaped key bytes. At the end it rereads the Ubik header and warns if the Ubik version changed during execution.

## State And Persistence
This tool can directly modify the database file when `-w` is supplied. It writes a new KA header and raw entries but does not rebuild all higher-level structures such as hash chains in the same way the server path does. Output mode writes an ASCII dump to a file or stdout.

## Dependencies And Integration Points
It depends on internal Ubik disk header layout and kauth database record layout from `kaserver.h`. It also calls kauth parsing utilities such as `ka_ParseLoginName`. It is outside the normal server/client transaction path.

## Risks And Test Signals
The principal risks are corruption from direct disk writes, stale output if the database is live, endianness mistakes, incomplete reconstruction of indexes, old K&R-style declarations, and suspicious key printing code that casts a byte value as a pointer in `fprintf`. Test signals include dump/restore on a disposable database, Ubik version-change detection, correct handling of empty/free entries, and comparison against server-side list/get-entry results.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/kauth/ka_util.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/kauth/kaaux.c -->
# sources/distributed-fs/openafs/src/kauth/kaaux.c

## Purpose
Implements XDR serializers for kauth counted byte-string structures used by RPC interfaces: `ka_CBS` and `ka_BBS`.

## Important APIs, Types, And Functions
The exported functions are `xdr_ka_CBS` and `xdr_ka_BBS`. They operate on `XDR`, `struct ka_CBS`, and `struct ka_BBS`; both enforce `MAXBS` of 2048 bytes to avoid excessive allocation.

## Control Flow
For `XDR_FREE`, each function frees `SeqBody`. For encode, `ka_CBS` emits `SeqLen` then opaque bytes, while `ka_BBS` emits `MaxSeqLen`, `SeqLen`, and opaque bytes. For decode, each function reads lengths, rejects negative or over-limit values, validates supplied preallocated buffers when `SeqBody` is non-NULL, allocates a new buffer otherwise, updates the length fields, and decodes opaque data.

## State And Persistence
The functions only allocate or free memory referenced by the caller-provided structures. There is no global or durable state.

## Dependencies And Integration Points
They depend on Rx XDR helpers and `afs/kauth.h` generated structures. They are called by rxgen-generated KA RPC marshalling paths for authentication, password-change, ticket, and answer byte buffers.

## Risks And Test Signals
Important risks are allocation failure not being explicitly checked after `malloc`, callers expecting `SeqBody` to be null after `XDR_FREE`, and exact max-size compatibility with generated RPC expectations. Test signals include encode/decode round trips, oversized and negative length rejection, preallocated-buffer decode rejection when too small, `XDR_FREE` cleanup, and zero-length body handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/kauth/kaaux.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/kauth/kaauxdb.c -->
# sources/distributed-fs/openafs/src/kauth/kaauxdb.c

## Purpose
Maintains the auxiliary authentication database file `auxdb`, which stores failed-authentication counters and last-failure timestamps outside the main Ubik KA database.

## Important APIs, Types, And Functions
Functions are `kaux_opendb`, `kaux_closedb`, `kaux_read`, `kaux_write`, `kaux_inc`, and `kaux_islocked`. Static state is the process-wide file descriptor `fd`. The record key is derived from a main-database `kaentry` offset and the fixed `ENTRYSIZE`/`kaheader` layout.

## Control Flow
`kaux_opendb` builds `<path>/auxdb` by appending `auxdb` to the provided path and opens it read/write with mode 0600. `kaux_read` and `kaux_write` translate a main-database entry offset into an auxiliary file offset and read or write `{nfailures,lasttime}`. `kaux_inc` expires old failures based on locktime and increments the counter. `kaux_islocked` scales allowed attempts across Ubik servers, gives the sync site the remainder, and returns 0 for unlocked, -1 for indefinite/fully locked, or an unlock timestamp.

## State And Persistence
Persistent state lives in the sidecar `auxdb` file. It is not replicated by Ubik and is maintained independently on each server. Runtime state is only the open descriptor.

## Dependencies And Integration Points
It depends on Ubik beacon state (`ubeacon_Debug`, `ubeacon_AmSyncSite`) and kauth database layout from `kaserver.h`. `kaprocs.c` calls it for failed-login lockout checks, increments, unlock, lock-status, and cleanup when deleting users.

## Risks And Test Signals
Risks include non-replicated lockout counters, no explicit file locking, host-endian on-disk integers, path concatenation assumptions, no reset of `fd` after close, and offset coupling to fixed `kaentry` positions. Test signals include failed-login accumulation, lock expiry, sync-site remainder behavior, delete/unlock counter reset, no-limit attempts behavior, and operation when `auxdb` is missing or truncated.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/kauth/kaauxdb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/kauth/kadatabase.c -->
# sources/distributed-fs/openafs/src/kauth/kadatabase.c

## Purpose
Implements low-level KA database storage management over Ubik transactions. It initializes and validates the database header, allocates and frees fixed-size records, maintains name hash chains, iterates entries, manages special-server old-key records, and maintains an in-memory server-key cache.

## Important APIs, Types, And Functions
Important functions include `NameHash`, `kawrite`, `karead`, `init_kadatabase`, `CheckInit`, `AllocBlock`, `FreeBlock`, `FindBlock`, `ThreadBlock`, `UnthreadBlock`, `NextBlock`, `ka_NewKey`, `ka_DelKey`, `ka_debugKeyCache`, `ka_Encache`, `ka_LookupKvno`, `ka_LookupKey`, `ka_FillKeyCache`, `update_admin_count`, and `name_instance_legal`. Internal state includes `keycache_lock`, `keyCache`, `keyCacheVersion`, `maxCachedKeys`, `maxKeyLifetime`, and `dbfixup`.

## Control Flow
`CheckInit` delegates to `ubik_CheckCache`, whose callback reads the KA header, verifies both initial and terminal version fields, caches `cheader`, and optionally rebuilds an empty database. Allocation either pops `cheader.freePtr` or extends `eofPtr`; freeing writes a `KAFFREE` block and threads it onto the free list. Name lookup hashes name+instance and walks `cheader.nameHash`. Thread/unthread modify either the header hash bucket or a prior entry's `next` field. Old-key management scans the global `kvnoPtr` chain, supersedes current keys, drops expired or colliding kvnos, creates old-key blocks as needed, and increments `specialKeysVersion` to invalidate key caches.

## State And Persistence
Persistent state is the Ubik database: `kaheader`, fixed 200-byte `kaentry`/`kaOldKeys` records, free-list, EOF pointer, name hash table, admin count, stats, and old-key chain. Runtime state is a growable key cache guarded by `keycache_lock`. Fields on disk are mostly network byte order.

## Dependencies And Integration Points
This file is used by `kaprocs.c` and `kaserver.c` for every account and key operation. It depends on Ubik transaction APIs, Rx locks, kauth generated definitions, server layout from `kaserver.h`, and utility functions for debugging.

## Risks And Test Signals
Risks include fixed on-disk layout coupling, mixed byte-order handling, cache invalidation correctness, `realloc` fatal exit on allocation failure, a likely misleading expired-key log after zeroing fields, and lookup behavior that treats NULL instance as wildcard. Test signals include database creation, create/delete/list/get-entry round trips, hash-chain integrity, free-list reuse, old-key rollover and lookup by kvno, cache invalidation after special key changes, and corruption handling through `CheckInit`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/kauth/kadatabase.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/kauth/kadatabase.h -->
# sources/distributed-fs/openafs/src/kauth/kadatabase.h

## Purpose
Declares the internal KA database API implemented by `kadatabase.c`.

## Important APIs, Types, And Functions
The header declares Ubik seek/read/write wrappers, `update_admin_count`, key lookup functions, block allocation/free, name lookup, hash threading/unthreading, entry iteration, and `ka_DelKey`. It forward-relies on `struct ubik_trans`, `struct kaentry`, and `struct ktc_encryptionKey` being visible to including files.

## Control Flow
Callers begin a Ubik transaction elsewhere, use these functions to mutate or inspect the KA database, and then commit or abort the transaction. The header itself has no control flow.

## State And Persistence
No state is stored in the header. Its declarations expose functions that operate on the persistent Ubik KA database and the in-memory key cache.

## Dependencies And Integration Points
It is included by server and RPC implementation files such as `kaprocs.c` and `kaserver.c`. It must remain consistent with `kauth_internal.h`, `kaserver.h`, and `kadatabase.c`.

## Risks And Test Signals
Risks are declaration drift and duplicated declarations for `ka_LookupKvno`. Build coverage of server code and RPC account-management tests are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/kauth/kadatabase.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/kauth/kalocalcell.c -->
# sources/distributed-fs/openafs/src/kauth/kalocalcell.c

## Purpose
Provides kauth cell/realm helper routines isolated from other kauth modules so consumers can use afsconf without awkward linker dependencies.

## Important APIs, Types, And Functions
Exports `ka_CellConfig`, `ka_LocalCell`, `ka_ExpandCell`, and `ka_CellToRealm`. Static state consists of an `afsconf_dir *conf` and cached `cell_name`.

## Control Flow
`ka_CellConfig` closes any prior config directory, opens the supplied directory, and caches the local cell. `ka_LocalCell` lazily opens the client etc directory and fetches the local cell if not already configured. `ka_ExpandCell` resolves an empty cell to the local cell or lowercases and looks up a named cell in CellServDB, returning the canonical cell and whether it is local. `ka_CellToRealm` expands the cell and uppercases the result as the Kerberos realm.

## State And Persistence
Runtime state is the cached config handle and local cell name protected by the global pthread lock macros. The code reads CellServDB-style configuration but does not write it.

## Dependencies And Integration Points
It depends on afsconf, global pthread locking, Rx/XDR includes required by kauth headers, and string case helpers. It is used by clients, token functions, `klog`, `kpasswd`, and server initialization.

## Risks And Test Signals
Risks include global mutable config state shared by all callers, `strcpy` into caller buffers whose sizes are assumed by convention, and error paths that leave `conf` as NULL. Test signals include local-cell discovery, alternate config directory selection, canonical cell expansion, unknown-cell failure, realm uppercase conversion, and concurrent callers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/kauth/kalocalcell.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/kauth/kalog.c -->
# sources/distributed-fs/openafs/src/kauth/kalog.c

## Purpose
Logs kaserver activity either to a DBM/GDBM-backed last-use database when `AUTH_DBM_LOG` is enabled or to the normal Vice text log otherwise.

## Important APIs, Types, And Functions
With DBM logging enabled, exports `kalog_Init` and `kalog_log` and uses global `kalog_db`. In all builds, `ka_log` formats text log events. It consumes operation constants from `kalog.h` and external `verbose_track`.

## Control Flow
`kalog_Init` opens a rotating server log and the DBM database. `kalog_log` builds a key from client principal, optional realm, optional service principal, and operation suffix, stores `kalog_elt {last_use,host}` with `DBM_REPLACE`, and logs through `ViceLog`. `ka_log` builds the same logical key using bounded `strl*` calls and sends it to `ViceLog`.

## State And Persistence
DBM mode persists one record per operation key in the configured KA log database, recording only the last host/time. Text mode persists through the server log file. The DBM handle is process-global.

## Dependencies And Integration Points
It is called from `kaprocs.c` after create, delete, authenticate, password-change, set-fields, unlock, and ticket operations. It depends on OpenAFS log rotation helpers and optional DBM/GDBM APIs.

## Risks And Test Signals
Risks include unbounded `strcpy`/`strcat` use in DBM mode despite fixed 512-byte `keybuf`, lack of DBM locking, and loss of event history because records are replaced. Test signals include all operation suffixes, DBM open failure fallback behavior, text log formatting, long principal/service names, and host address rendering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/kauth/kalog.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/kauth/kalog.h -->
# sources/distributed-fs/openafs/src/kauth/kalog.h

## Purpose
Defines the KA activity-log record type, operation identifiers, optional DBM compatibility mappings, and the `KALOG` macro used by server procedures.

## Important APIs, Types, And Functions
Defines `kalog_elt {time_t last_use; afs_int32 host;}`, `KALOG_DB_MODE`, operation constants such as `LOG_GETTICKET`, `LOG_CHPASSWD`, `LOG_AUTHENTICATE`, and `LOG_TGTREQUEST`, DBM/GDBM macro aliases, and prototypes for `kalog_Init`, `kalog_log`, and `ka_log`.

## Control Flow
There is no runtime logic. Compile-time `AUTH_DBM_LOG` selects whether `KALOG` expands to DBM logging or text logging.

## State And Persistence
The header defines the durable DBM value layout and the mode used when creating the log database, but stores no runtime state by itself.

## Dependencies And Integration Points
It is shared by `kaserver.c`, `kaprocs.c`, `kalog.c`, and `kdb.c`. DBM mode depends on either GDBM on Linux or NDBM elsewhere.

## Risks And Test Signals
Risks include ABI drift in `kalog_elt`, operation-code mismatch with logging callers, and platform DBM macro differences. Test signals are successful DBM-enabled and DBM-disabled builds plus `kdb` compatibility with records generated by `kalog.c`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/kauth/kalog.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/kauth/kaopcodes.h -->
# sources/distributed-fs/openafs/src/kauth/kaopcodes.h

## Purpose
Preserves obsolete numeric KA opcode definitions and optional opcode names for legacy code or debugging references.

## Important APIs, Types, And Functions
Defines opcodes 501 through 510 for SetPassword, Authenticate, GetTicket, SetFields, CreateUser, DeleteUser, GetEntry, ListEntry, ChangePassword, and GetStats, plus `LOWEST_OPCODE`, `HIGHEST_OPCODE`, and `NUMBER_OPCODES`. When `OPCODE_NAMES` is defined, it declares a static `opcode_names` array.

## Control Flow
The header has no runtime control flow. Its comments note that opcodes are now defined by `kauth.rg`.

## State And Persistence
There is no state or persistence.

## Dependencies And Integration Points
It can be included by older tooling that still wants the historic opcode map. The active Rx/RPC dispatch path is generated from `kauth.rg`.

## Risks And Test Signals
The main risk is stale duplication if generated RPC numbers change. Build and debug-output checks are enough; runtime RPC tests should rely on generated interfaces rather than this file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/kauth/kaopcodes.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/kauth/kaport.h -->
# sources/distributed-fs/openafs/src/kauth/kaport.h

## Purpose
Defines portable packing helpers for four one-byte KA password-control fields stored or transported as a single 32-bit value.

## Important APIs, Types, And Functions
The macros are `unpack_long(src, dst)` and `pack_long(src)`. They map bytes 0..3 to big-endian positions in an `afs_uint32`.

## Control Flow
There is no function control flow. Macro expansion performs direct byte extraction or composition.

## State And Persistence
The header stores no state. It defines the encoding used by `kaprocs.c` for `misc_auth_bytes` in set-fields/get-entry paths.

## Dependencies And Integration Points
It assumes `afs_int32`/`afs_uint32` are available and that 32-bit words are four bytes. It integrates with `kaentry.misc_auth_bytes` fields for expiration, reuse, attempts, and locktime.

## Risks And Test Signals
Risks are macro side effects if arguments have expressions with side effects and implicit assumptions about field order. Tests should cover round-trip packing/unpacking and compatibility with `kamSetFields` and `kamGetEntry`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/kauth/kaport.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/kauth/kaprocs.c -->
# sources/distributed-fs/openafs/src/kauth/kaprocs.c

## Purpose
Implements the kaserver Rx RPC procedure logic for authentication, ticket granting, maintenance/account administration, statistics, debug, lockout, and password changes. It is the central policy layer above `kadatabase.c`.

## Important APIs, Types, And Functions
Key public functions include `init_kaprocs`, `InitAuthServ`, `AwaitInitialization`, `save_principal`, `kamCreateUser`, `ChangePassWord`, `kamSetPassword`, `kamSetFields`, `kamDeleteUser`, `kamGetEntry`, `kamListEntry`, `kamGetStats`, `kamGetPassword`, `kamGetRandomKey`, `kamDebug`, `SKAM_Unlock`, and `SKAM_LockStatus`, plus many `SKA*` audit wrappers. Internal helpers include `get_time`, `initialize_database`, `check_auth`, `special_name`, `create_user`, `impose_reuse_limits`, `set_password`, `GetEndTime`, `PrepareTicketAnswer`, `Authenticate`, and `GetTicket`.

## Control Flow
Initialization discovers the local realm, applies no-auth/fast-key/fixup flags, initializes the database layer, opens a read transaction to verify builtin keys, seeds DES randomness, opens `auxdb`, and marks `kaprocsInited`. Each RPC starts with `COUNT_REQ`, obtains a Ubik transaction through `InitAuthServ`, performs rxkad or no-auth authorization with `check_auth`, does database lookup/mutation, commits with `ubik_EndTrans`, or aborts and increments abort counters. Authentication decrypts client requests with the user's key, checks lockout, labels, skew, password expiration, and creates TGT/admin tickets. Ticket granting decodes a TGS ticket, validates requested times and cross-realm policy, creates a service ticket, and encrypts the answer with the TGS session key. Maintenance calls create/delete principals, set keys/fields, return entries/stats/debug data, unlock users, and report lock status.

## State And Persistence
Persistent state is the Ubik KA database and the auxiliary failed-login `auxdb`. Runtime state includes `cheader`, cached last principals, auto-change-password timers and counters, `noAuthenticationRequired`, initialization flags, and dynamic statistics. Builtin AuthServer and TGS keys can be automatically rotated through `get_time` using weak time-derived randomness.

## Dependencies And Integration Points
It depends on Rx, rxkad, Ubik, DES/hcrypto, afsconf, audit, KA generated RPC types, `kaserver.h`, `kadatabase.h`, `kalog.h`, `kaport.h`, and `kauth_internal.h`. It is invoked by rxgen service dispatch from `kaserver.c` and logs through audit and KALOG.

## Risks And Test Signals
High-risk areas include legacy DES/krb4 security, no-auth mode, command-line/server key logging in debug paths, password lockout sidecar consistency, fixed-size packet assembly, subtle endian conversions, key-cache invalidation, and old-interface compatibility. Test signals should cover server initialization, empty database rebuild, admin authorization, create/delete/list/get-entry, self and admin password changes, password reuse/min-hours/expiration, failed-login lockout/unlock/status, TGT/admin/service ticket issuance, cross-realm enable/disable, stats/debug RPCs, and Ubik quorum failure behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/kauth/kaprocs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/kauth/kaprocs.h -->
# sources/distributed-fs/openafs/src/kauth/kaprocs.h

## Purpose
Declares the internal callable RPC implementation functions from `kaprocs.c`.

## Important APIs, Types, And Functions
The header declares initialization/transaction helpers and maintenance operations including `kamCreateUser`, `ChangePassWord`, `kamSetPassword`, `kamSetFields`, `kamDeleteUser`, `kamGetEntry`, `kamListEntry`, `kamGetStats`, `kamGetPassword`, `kamGetRandomKey`, and `kamDebug`.

## Control Flow
Callers invoke these functions directly from SKA audit wrappers or service glue. The header itself has no logic.

## State And Persistence
No state is defined here. Declared functions operate on Ubik KA database state, auxiliary lockout state, and process statistics.

## Dependencies And Integration Points
It requires KA generated types such as `EncryptionKey`, `ka_CBS`, `ka_BBS`, `kaentryinfo`, `kaident`, `kasstats`, and `kadstats`, plus `struct rx_call` and `struct ubik_trans`. It is included by `kaprocs.c` and `kaserver.c`.

## Risks And Test Signals
Risks are prototype drift against audit wrappers or rxgen-generated signatures. Full kaserver build and RPC smoke tests are the primary signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/kauth/kaprocs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/kauth/kas.c -->
# sources/distributed-fs/openafs/src/kauth/kas.c

## Purpose
Implements the `kas` administrative command entry point. It initializes kauth client state and dispatches into the interactive/admin command implementation.

## Important APIs, Types, And Functions
The only function is `main`. It initializes multiple OpenAFS error tables, optional Windows socket support, calls `ka_Init`, and dispatches to `ka_AdminInteractive`.

## Control Flow
After platform setup and error-table initialization, `main` skips `ka_Init` for help/version/apropos-style invocations. It then rewrites the argument vector when no subcommand, cell/server/noauth/admin/password options, or a principal-looking first argument indicate the implicit `interactive` command. Otherwise it passes the original argv to `ka_AdminInteractive`, finalizes Rx, and exits based on the returned code.

## State And Persistence
The file stores no durable state. It initializes client-side kauth/Rx state and may cause downstream admin commands to mutate the KA database.

## Dependencies And Integration Points
It depends on command parsing and admin implementation in `admin_tools.c`, client initialization from the kauth library, Rx finalization, and platform-specific Windows socket setup.

## Risks And Test Signals
Risks are argument rewriting edge cases, failure to initialize cell info before real commands, and inherited security risk from password arguments passed to downstream admin tooling. Test signals include help/version without cell config, implicit interactive behavior, explicit subcommand dispatch, principal/cell option handling, Windows winsock failure handling, and clean `rx_Finalize`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/kauth/kas.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/kauth/kaserver.c -->
# sources/distributed-fs/openafs/src/kauth/kaserver.c

## Purpose
Bootstraps and runs the deprecated OpenAFS KA authentication server. It parses command-line configuration, opens cell/server configuration, initializes Ubik and Rx services, starts the KA RPC services, initializes procedure/database state, and optionally enables the old UDP interface.

## Important APIs, Types, And Functions
Important functions are `KA_rxstat_userok`, `KA_IsLocalRealmMatch`, `es_Report`, `initialize_dstats`, `convert_cell_to_ubik`, `kvno_admin_key`, and `main`. Global server state includes `dynamic_statistics`, `KA_dbase`, `myHost`, `verbose_track`, `krb4_cross`, `rxBind`, `SHostAddrs`, `KA_conf`, `MinHours`, and `npwSums`.

## Control Flow
`main` initializes audit and server paths, parses options for database/local paths, noauth, fast keys, dbfixup, cellservdb, security level, crossrealm, rxbind, minhours, and rxstats. It opens KA cell config, logging, emits a deprecation warning, derives or parses the Ubik server list, configures audit user checks, sets Ubik client/server security procs, binds Rx, starts Ubik, creates authentication, ticket-granting, maintenance, and rxstats services, initializes dynamic stats, allows rxstat management by superusers, starts Rx server processing, initializes `kaprocs`, starts legacy UDP access if possible, and donates the main LWP to `rx_ServerProc`.

## State And Persistence
Persistent state includes the Ubik KA database at `dbpath`, local auxiliary files at `lclpath`, server logs, and optional audit logs. Runtime global state configures security, cell config, statistics, server address binding, and rxkad key lookup.

## Dependencies And Integration Points
It integrates afsconf cell/security config, Ubik replication, Rx/rxkad services, audit, server logging, `kadatabase.c`, `kaprocs.c`, `kalog.c`, and `krb_udp.c`. The maintenance service uses rxkad with `kvno_admin_key`, which consults the in-memory key cache only.

## Risks And Test Signals
Risks include running a deprecated DES-based auth server, `-noAuth`, clear Ubik security level, old UDP service exposure, address-selection/bind mistakes, command-line parsing by prefix, and reliance on single-thread KA service max procs. Test signals include startup with CellServDB and explicit servers, rxbind/netinfo behavior, Ubik quorum formation, service registration IDs, noauth and crossrealm flags, audit/log file creation, rxstats authorization, and clean failure on missing paths or config.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/kauth/kaserver.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/kauth/kaserver.h -->
# sources/distributed-fs/openafs/src/kauth/kaserver.h

## Purpose
Defines the on-disk KA database layout, key/entry structures, statistics macros, offset helpers, and shared kaserver globals/prototypes.

## Important APIs, Types, And Functions
Defines `KADBVERSION`, `HASHSIZE`, `NULLO`, `struct kaheader`, `ENTRYSIZE`, `KA_NPWSUMS`, `struct kaentry`, `struct kaOldKey`, `struct kaOldKeys`, `NOLDKEYS`, password-control byte indexes, `COUNT_REQ`, `COUNT_ABO`, `DOFFSET`, and `IOFFSET`. It declares globals such as `cheader`, `dynamic_statistics`, `myHost`, and `krb4_cross`, plus auxiliary DB and `es_Report` functions.

## Control Flow
No runtime flow lives in the header. The macros are expanded inside request handlers and database helpers to update statistics and compute disk offsets.

## State And Persistence
This file is the authoritative description of KA persistent database records. Fields are documented as network byte order; record size is fixed at 200 bytes, and the header embeds the name hash table and version sentinels.

## Dependencies And Integration Points
It is included by `kadatabase.c`, `kaprocs.c`, `kaserver.c`, `ka_util.c`, and `kaauxdb.c`. It must remain compatible with Ubik storage, generated kauth types, and old database files.

## Risks And Test Signals
Risks include ABI/layout drift, `ENTRYSIZE` padding assumptions, endian mistakes, and changing `HASHSIZE` or fields without migration. Test signals include `sizeof(struct kaentry) == sizeof(struct kaOldKeys)`, database version checks, dump/restore compatibility, old-key rollover, and cross-version server startup against test databases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/kauth/kaserver.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/kauth/katoken.c -->
# sources/distributed-fs/openafs/src/kauth/katoken.c

## Purpose
Provides client-side token-cache helpers that obtain kauth tickets from the AuthServer and store them in the kernel token cache.

## Important APIs, Types, And Functions
Exports `ka_GetAuthToken`, `ka_GetServerToken`, `ka_GetAdminToken`, and `ka_VerifyUserToken`. It uses `ktc_token`, `ktc_principal`, `ubik_client`, KA service IDs, cell/realm helpers, `ka_Authenticate`, `ka_GetToken`, and `ktc_SetToken`/`ktc_GetToken`.

## Control Flow
`ka_GetAuthToken` expands a cell, connects unauthenticated to the authentication service, authenticates with the supplied key to get a TGS token, and stores it under the `krbtgt` server principal. `ka_GetServerToken` first checks for a cached service token, obtains or imports the correct TGS token, supports inter-cell token acquisition through the local cell when needed, contacts the target cell's ticket-granting service, gets a service token, and stores it, optionally with `AFS_SETTOK_SETPAG`. `ka_GetAdminToken` similarly obtains or caches an admin-service token. `ka_VerifyUserToken` authenticates without storing a token.

## State And Persistence
State changes are writes to the kernel token cache through ktc APIs. Function-local connections are destroyed after use. The global pthread lock serializes these flows.

## Dependencies And Integration Points
It bridges high-level tools such as `klog`/`kpasswd` to low-level client RPC helpers in `authclient.c` and token-cache APIs in `afs/auth.h`. It depends on kauth cell config and Ubik client connections.

## Risks And Test Signals
Risks include holding the global mutex across network calls, token-cache principal naming subtleties for local versus foreign cells, inter-cell fallback behavior, and cleanup leaks on early returns after connection creation. Test signals include fresh and cached auth/admin/service tokens, `-setpag` token placement, foreign-cell token acquisition, unavailable server errors, and token verification without cache writes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/kauth/katoken.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/kauth/kauth_internal.h -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/kauth/kauth_internal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/kauth/kautils.c -->
# sources/distributed-fs/openafs/src/kauth/kautils.c

## Purpose
Implements miscellaneous kauth formatting, byte conversion, key checksum, zero-key, and time-string utilities.

## Important APIs, Types, And Functions
Exports `ka_PrintUserID`, `ka_PrintBytes`, `ka_ConvertBytes`, `ka_ReadBytes`, `umin`, `ka_KeyCheckSum`, `ka_KeyIsZero`, and `ka_timestr`. It uses hcrypto DES, rxkad conversion helpers, and kauth error constants.

## Control Flow
User/principal and byte printing escape nonportable characters with octal sequences. `ka_ConvertBytes` writes printable or octal-escaped bytes to a caller buffer and returns the number of unconverted bytes. `ka_ReadBytes` reverses the representation into binary. `ka_KeyCheckSum` DES-encrypts a zero block under the key and returns the first four bytes as a host-order checksum. `ka_timestr` formats `NEVERDATE`, zero/invalid dates, or localized time strings.

## State And Persistence
All state is caller-provided or stack-local. No persistent state is modified.

## Dependencies And Integration Points
These helpers are used by diagnostic tools, admin utilities, `kaprocs.c`, password reuse checks, and ticket decoding. They define the human-readable byte format expected by `decode_ticket.c` and old utilities.

## Risks And Test Signals
Risks include permissive `ka_ReadBytes` parsing that assumes three octal digits after backslash, caller buffer-size assumptions in output routines, localized time output variation, and DES dependency for key checksums. Test signals include byte conversion round trips, truncated output return counts, principal escaping/parsing compatibility, checksum stability, zero-key checks, and `NEVERDATE` formatting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/kauth/kautils.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/kauth/kautils.p.h -->
# sources/distributed-fs/openafs/src/kauth/kautils.p.h

## Purpose
Defines the public kauth client utility API, service identifiers, protocol labels, authentication macros, and wire-format request/answer structures.

## Important APIs, Types, And Functions
The header declares token acquisition, server connection, authentication, ticket retrieval, password change, string-to-key, password reading, login-name parsing, initialization, cell/realm helpers, byte/time utilities, user-authentication wrappers, debug key cache access, and ticket-file helpers. It defines `Date`, `KA_TIMESTR_LEN`, user-auth flag bits, password-control bits, KA service IDs, builtin principal names, labels such as `gTGS`, `gADM`, `CPWl`, and `gtkt`, and structs for TGT, ticket, change-password, and get-ticket messages.

## Control Flow
There is no implementation flow. The macro wrappers build versioned calls to `ka_UserAuthenticateGeneral`, and the structs define the payloads encrypted and decrypted by client and server code.

## State And Persistence
No state is stored here. The declared APIs manipulate token caches, Ubik connections, passwords, and ticket files elsewhere.

## Dependencies And Integration Points
It includes authentication, Rx/XDR, Ubik, cellconfig, and afsutil headers. It is the central public header for `klog`, `kpasswd`, admin tools, token helpers, and server request code.

## Risks And Test Signals
Risks include ABI drift in wire structures, label or service-ID mismatch with `kaprocs.c` and generated RPC code, macro compatibility, and `Date` remaining 32-bit. Test signals include client/server authentication interoperability, old and new ticket-answer formats, password-change request/answer layout, public library symbol builds, and cross-platform struct packing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/kauth/kautils.p.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/kauth/kdb.c -->
# sources/distributed-fs/openafs/src/kauth/kdb.c

## Purpose
Implements `kdb`, a diagnostic dumper for the KA DBM activity-log database when `AUTH_DBM_LOG` is enabled. In non-DBM builds it reports that the tool is unsupported.

## Important APIs, Types, And Functions
DBM builds define `cmdproc` and `main`, use global `dbmfile`, and read `kalog_elt` records from a DBM/GDBM file. Non-DBM builds define a simple `main(void)`.

## Control Flow
`main` builds a command syntax with optional `-dbmfile`, `-key`, `-long`, and `-numeric`. `cmdproc` opens the DBM file, either enumerates all keys or fetches specified keys, optionally reads values and prints last host/time information, closes the database, and returns success. Non-DBM mode prints `kdb not supported` and exits 1.

## State And Persistence
The tool reads but does not modify the KA activity-log DBM file. It keeps only local iteration state.

## Dependencies And Integration Points
It depends on `kalog.h` for DBM compatibility macros and `kalog_elt` layout, plus OpenAFS command and host utility helpers. It is a companion to `kalog.c` DBM mode.

## Risks And Test Signals
Risks include DBM backend portability, corrupted record handling, key enumeration semantics differing between NDBM and GDBM, and host formatting differences. Test signals include dumping all keys, fetching individual keys, long and numeric output, missing key behavior, corrupted value-size detection, and non-DBM build behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/kauth/kdb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/kauth/kkids.c -->
# sources/distributed-fs/openafs/src/kauth/kkids.c

## Purpose
Manages the optional `kpwvalid` child process used by `kpasswd` to enforce local password-quality policy. It tries to find `kpwvalid` next to the running `kpasswd` binary and only uses it if the path is considered secure.

## Important APIs, Types, And Functions
Exports `init_child`, `password_bad`, `give_to_child`, and `terminate_child`. Internal helpers include `simplify_name`, `find_me`, `InAFS`, `ParseAcl`, `safestrtok`, `is_secure`, and `kpwvalid_is`. Static state includes `using_child`, `childin`, and `childout`.

## Control Flow
`init_child` resolves the executable path, checks that the parent directory is in AFS and that ACLs on each AFS path component grant write/admin power only to `system:administrators`, verifies a sibling `kpwvalid`, creates two pipes, forks, connects child stdin/stdout to the pipes, and execs `kpwvalid`. `give_to_child` sends the old password. `password_bad` sends a proposed password and reads an integer result. `terminate_child` kills the child on Unix; Windows disables the child process path.

## State And Persistence
State is a live child process and two stdio pipes. It reads filesystem metadata and AFS ACLs but does not persist data.

## Dependencies And Integration Points
It is used only by `kpasswd.c`. It depends on pioctl operations (`VIOC_FILE_CELL_NAME`, `VIOCGETAL`), AFS ACL rights constants, Unix process APIs, and `kpwvalid` protocol of writing an integer result to stdout.

## Risks And Test Signals
Risks include path-resolution races, symlink handling, fixed-size path buffers, incomplete ACL memory cleanup, pipe deadlocks if the child misbehaves, killing by pid without wait/close cleanup, and platform divergence on Windows. Test signals include secure and insecure directory detection, absence of `kpwvalid`, old-password handoff, rejection/acceptance protocol, child exec failure, and password-change fallback when no child is used.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/kauth/kkids.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/kauth/kkids.h -->
# sources/distributed-fs/openafs/src/kauth/kkids.h

## Purpose
Declares the `kpasswd` password-validator child-process interface implemented by `kkids.c`.

## Important APIs, Types, And Functions
The exported functions are `init_child`, `password_bad`, `give_to_child`, and `terminate_child`.

## Control Flow
The intended flow is: initialize the child with the program name, send the old password, check candidate new passwords with `password_bad`, and terminate the child before exit.

## State And Persistence
The header stores no state. The implementation maintains process and pipe state.

## Dependencies And Integration Points
It is included by `kpasswd.c` and provides the only public interface to optional `kpwvalid` policy checks.

## Risks And Test Signals
Risks are prototype drift and missing cleanup in callers. Build coverage of `kpasswd` and runtime validation with and without `kpwvalid` are the test signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/kauth/kkids.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/kauth/klog.c -->
# sources/distributed-fs/openafs/src/kauth/klog.c

## Purpose
Implements the `klog` command-line client that obtains AFS authentication tokens from kaserver and optionally writes a Kerberos-style ticket file.

## Important APIs, Types, And Functions
Important functions are `main`, `getpipepass`, and `CommandProc`. The command syntax supports principal, password, cell, explicit servers, pipe input, silent mode, ticket lifetime, `-setpag`, and `-tmp`. `KLOGEXIT` maps KA errors into process exit codes and finalizes Rx.

## Control Flow
`main` registers command arguments and dispatches. `CommandProc` zeroes command-line arguments, initializes cell state, parses explicit cell/server/principal inputs, derives the local username when needed, scrubs password arguments, parses lifetime, reads a password interactively or from stdin, expands cell to realm, optionally applies explicit server addresses, calls `ka_UserAuthenticateGeneral` to obtain/cache tokens, clears the password buffer, optionally writes a ticket file, and returns.

## State And Persistence
State changes include kernel token-cache updates through kauth user-auth helpers, optional ticket-file creation under `/tmp`, and process-local password buffers that are scrubbed. Command-line password arguments are overwritten.

## Dependencies And Integration Points
It depends on the OpenAFS command package, kauth client utilities, cell config, token APIs, and `krb_write_ticket_file`. It is the primary user-facing consumer of `katoken.c` and user-authentication code.

## Risks And Test Signals
Risks include password exposure before argv scrubbing, non-null instance warnings but continued operation, lifetime parsing edge cases, exit-code mapping assumptions, and legacy DES/kaserver security. Test signals include username and `name@cell` parsing, explicit server lists, pipe and interactive password input, silent mode, lifetime bounds, setpag behavior, failed-auth reason output, password buffer clearing, and ticket-file writing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/kauth/klog.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/kauth/knfs.c -->
# sources/distributed-fs/openafs/src/kauth/knfs.c

## Purpose
Implements `knfs`, a utility for copying, displaying, or removing AFS tokens for an NFS translator client identified by host and UID, and optionally setting that client's `@sys` value.

## Important APIs, Types, And Functions
Important helpers are `SetSysname`, `GetTokens`, `NFSUnlog`, `NFSCopyToken`, `cmdproc`, and `main`. It defines a local `ClearToken` layout matching cache-manager expectations and builds raw `ViceIoctl` buffers with NFS exporter pioctl headers.

## Control Flow
`main` registers `-host`, `-id`, `-sysname`, `-unlog`, and `-tokens`. `cmdproc` resolves the host, parses or derives UID, then either displays remote tokens, unlogs the remote identity, or copies local AFS service tokens into the NFS translator and optionally sets sysname. Token copy enumerates local `afs` service tokens, retrieves each token, constructs encrypted-ticket and clear-token payloads plus cell name, and sends `_VICEIOCTL(99)` pioctls. Token display sends get-token pioctls and formats expiration and identity information.

## State And Persistence
State changes occur in the cache manager/NFS translator token table and sysname state through pioctl calls. The process itself keeps only stack buffers.

## Dependencies And Integration Points
It depends on ktc token APIs, pioctl, Vice ioctl conventions, host utilities, command parsing, and hard-coded pioctl sub-opcode numbers for set token, get token, unlog, and sysname.

## Risks And Test Signals
Risks include raw fixed-size buffer assembly, hard-coded pioctl indexes, bounds sensitivity around ticket and cell-name copy, legacy clear-token layout, host/UID authorization failures, and IPv4-only address handling. Test signals include copy/display/unlog flows, multiple cell tokens, expired-token display, UID wildcard/default behavior, sysname set, translator passwd-sync error messages, oversized ticket rejection, and pioctl error mapping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/kauth/knfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/kauth/kpasswd.c -->
# sources/distributed-fs/openafs/src/kauth/kpasswd.c

## Purpose
Implements the `kpasswd` command for changing a user's KA password. It authenticates to the maintenance service with the old password, optionally validates the new password through `kpwvalid`, and submits a password-change RPC.

## Important APIs, Types, And Functions
Important functions are `main`, `getpipepass`, `read_pass`, optional `timedout`, and `CommandProc`. It uses `kkids` helpers, `ka_StringToKey`, `DES_string_to_key`, `ka_GetAdminToken`, `ka_AuthServerConn`, and `ka_ChangePassword`.

## Control Flow
`main` initializes the optional validator child and command syntax. `CommandProc` scrubs argv, initializes cell and Rx state, parses cell/server/principal/password/newpassword options, derives the local username if needed, reads old and new passwords from stdin or terminal, sends the old password to the validator, loops until the validator accepts an interactive new password, optionally truncates to eight characters, derives both AFS and MIT DES keys, gets a short-lived admin token with fallback between string-to-key styles and first-eight-character compatibility, connects to the maintenance service, calls `ka_ChangePassword`, scrubs keys/passwords, destroys the Ubik client, finalizes Rx, terminates the child, and exits.

## State And Persistence
Persistent state changes only if the server accepts the password change in the KA database. Runtime state includes password/key buffers, a possible child validator process, a Ubik client connection, and token material. Password buffers are explicitly zeroed in many paths.

## Dependencies And Integration Points
It depends on command parsing, hcrypto DES/UI helpers, kauth client APIs, `kkids.c`, ktc tokens, Ubik client connections, and platform-specific username discovery on Windows.

## Risks And Test Signals
Risks include password exposure before argv scrubbing, numerous direct `exit` paths, legacy DES string-to-key ambiguity, fallback behavior that may surprise users, validator child reliability, optional password truncation, and partial cleanup on early failures. Test signals include interactive and pipe password changes, explicit cell/server paths, wrong old password, AFS and MIT string-to-key fallback, validator accept/reject, mismatch handling, no-change paths, connection cleanup, and server-side reuse/min-hours rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/kauth/kpasswd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/kauth/kpwvalid.c -->
# sources/distributed-fs/openafs/src/kauth/kpwvalid.c

## Purpose
Provides the default external password-quality checker used by `kpasswd` through the `kkids` child-process protocol.

## Important APIs, Types, And Functions
The only function is `main`. It includes component version metadata and uses two fixed 512-byte buffers for the old password and candidate passwords.

## Control Flow
The program reads the first stdin line as the old password, then loops over candidate new-password lines. For each candidate it accepts passwords whose line length is greater than eight characters, writes `0` to stdout, and returns status 0. Otherwise it writes an explanatory error to stderr, writes `1` to stdout, and returns status 1 if input ends after a rejection.

## State And Persistence
It stores only the old and candidate password lines in local buffers. It writes no files and persists no policy state.

## Dependencies And Integration Points
It is execed by `kkids.c` and communicates by newline-delimited stdin/stdout. `kpasswd.c` sends the old password first and expects integer decisions for subsequent candidates.

## Risks And Test Signals
Risks include the simplistic policy, newline-counting semantics where a visible eight-character password plus newline passes, unused old-password comparison, fixed-size input truncation by `fgets`, and protocol fragility if stderr/stdout are mixed by wrappers. Test signals include short, eight-character, longer, EOF, and truncated-line cases under the `kkids` pipe protocol.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/kauth/kpwvalid.c -->
