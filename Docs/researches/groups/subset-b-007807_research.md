# subset-b-007807 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/ubik/remote.c -->
# sources/distributed-fs/openafs/src/ubik/remote.c

`remote.c` implements the server-side DISK RPC handlers that let a Ubik sync site drive write transactions on peer database replicas. It owns the single remote write transaction pointer `ubik_currentTrans` and exposes handlers for begin, commit, abort, lock, write, vector write, truncate, version query, full-file transfer, interface-address update, probing, and version-label advancement.

Important APIs are the `SDISK_*` entry points generated from `ubik_int.xg`: `SDISK_Begin`, `SDISK_Commit`, `SDISK_ReleaseLocks`, `SDISK_Abort`, `SDISK_Lock`, `SDISK_WriteV`, `SDISK_Write`, `SDISK_Truncate`, `SDISK_GetVersion`, `SDISK_GetFile`, `SDISK_SendFile`, `SDISK_UpdateInterfaceAddr`, and `SDISK_SetVersion`. All mutating RPCs call `ubik_CheckAuth`, hold `DBHOLD(ubik_dbase)`, verify a current transaction and write type, and call `urecovery_CheckTid` to abort stale local state when the sync site's transaction id no longer matches.

The core control flow mirrors the sync-site transaction lifecycle. `SDISK_Begin` checks quorum freshness via `urecovery_AllBetter`, creates a local write transaction with `udisk_begin`, and stamps it with the supplied tid. `SDISK_Write` and `SDISK_WriteV` apply remote data into the local transaction log through `udisk_write`; `SDISK_Truncate` queues truncation through `udisk_truncate`; `SDISK_Lock` obtains a propagated write lock with `ulock_getLock`. `SDISK_Commit` takes the application cache write lock before committing via `udisk_commit`, then updates the vote module's db version. Abort and release-lock handlers cleanly end `ubik_currentTrans` unless a lock wait is still active.

Persistence-sensitive paths are `SDISK_GetFile` and `SDISK_SendFile`. `GetFile` streams a local database file length and content over Rx, then returns the file label. `SendFile` receives a complete database image from the sync site into a temporary `*.TMP` file after first invalidating the live label to version 0; it renames the temp file into place, opens/invalidates local disk buffers, writes the new version label, and restores readable state on failure by relabeling with the prior epoch. This file-transfer path is intentionally conservative so a valid label appears only after file data is durable enough for the physical layer.

Dependencies and integration points include Rx calls and peers, `ubik_CheckAuth`, `udisk_*`, `ulock_*`, `urecovery_*`, `uvote_*`, `ubeacon_*`, physical database callbacks in `ubik_dbase`, and network-address state under `UBIK_ADDR_LOCK`. `SDISK_UpdateInterfaceAddr` reconciles multihomed peer addresses against `ubik_servers`, rejects inconsistent CellServDB mappings, and marks a restarted peer non-current so recovery will resend the database before future writes.

Risks cluster around concurrency and trust boundaries: the global `ubik_currentTrans` assumes only one remote write transaction; all callers must preserve lock ordering. File transfer constructs database paths with fixed buffers and depends on trusted authenticated sync sites; address update rejects cross-server address overlap but depends on correct primary-address mapping. Test signals are mostly integration-oriented: exercise remote transaction begin/write/commit/abort, stale tid aborts, `DISK_WriteV` buffer bounds, `SendFile` failure cleanup, multihomed address updates, and sync-site mismatch rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/ubik/remote.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/ubik/ubik.c -->
# sources/distributed-fs/openafs/src/ubik/ubik.c

`ubik.c` is the public server-side transaction engine and initialization hub for Ubik. It wires together the lower-level vote, beacon, disk, lock, recovery, and remote modules; creates Rx VOTE and DISK services; exposes public transaction operations; and propagates write operations to a quorum.

The file defines global server state such as `ubik_quorum`, `ubik_dbase`, `ubik_servers`, `ubik_host`, `urecovery_state`, `ubik_callPortal`, `version_globals`, and server security callback pointers. Initialization flows through `ubik_ServerInitCommon`, wrapped by `ubik_ServerInitByInfo` and `ubik_ServerInit`. That routine allocates `struct ubik_dbase`, initializes pthread/LWP locks, installs physical I/O callbacks (`uphys_*`), calls `rx_Init`, initializes disk/lock/vote/recovery/beacon modules, creates Rx security classes, registers VOTE and DISK services, starts Rx server processing early, publishes interface addresses, and starts beacon and recovery worker threads.

Write replication is organized through `ContactQuorum_iterate` plus small wrappers for `DISK_Begin`, `DISK_Lock`, `DISK_Truncate`, `DISK_WriteV`, `DISK_SetVersion`, `DISK_Commit`, `DISK_Abort`, and `DISK_ReleaseLocks`. The iterator skips down or non-current replicas, handles pthread connection refs while dropping the DB lock during I/O, marks failed servers down, clears `currentDB`, and notifies recovery. `ContactQuorum_rcode` treats local success plus enough remote successes as quorum.

Transaction control starts in `BeginTrans`, which enforces read-any semantics, requires `ubik_SyncWriterCacheProc` for read-any-write cache safety, waits for single-writer exclusivity via `DBWRITING`, verifies sync-site status for writes, creates a disk transaction, stamps a tid from `version_globals.ubik_epochTime` and the database counters, and starts write transactions on a quorum. `ubik_AbortTrans` aborts local and remote writes and invalidates application cache state. `ubik_EndTrans` flushes buffered writes, commits locally, updates application cache, commits remotely, waits for potentially partitioned down servers to age out for `BIGTIME`, and finally releases remote locks.

Data operations are local-first but quorum-aware. `ubik_Read`, `ubik_Seek`, and `ubik_Tell` operate on transaction seek state after `urecovery_AllBetter` checks. `ubik_Write` writes locally through `udisk_write` and batches remote writes in transaction iovec buffers for `ubik_Flush`; large writes recurse in `IOVEC_MAXBUF` chunks. `ubik_Truncate` flushes first, truncates locally, then propagates. `ubik_SetLock` obtains read locks locally, while write locks require a fresh quorum and remote `DISK_Lock` propagation.

State and persistence behavior are guarded by `DBHOLD`, `UBIK_VERSION_LOCK`, and `cache_lock`. The application cache protocol uses `ubik_CheckCache` to upgrade from read to shared/write cache locks, call a caller-supplied refresh function, and stamp `cachedVersion`. Write commits call `WritebackApplicationCache` immediately after local commit and before remote commit returns, minimizing stale reads for read-any-write users.

Risks are high-impact distributed-systems risks: lock ordering must stay exact, local commit before remote quorum commit creates a narrow ambiguous-failure window handled by quorum rules, iovec buffering requires careful flush-on-lock/truncate/end discipline, and down-server timeout waits can delay commits. Test signals include multi-server write commit/abort, quorum loss at each propagation step, read-any cache invalidation, concurrent writers blocking on `DBWRITING`, and remote failures marking recovery state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/ubik/ubik.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/ubik/ubik.p.h -->
# sources/distributed-fs/openafs/src/ubik/ubik.p.h

`ubik.p.h` is the main private/public Ubik interface header. It defines the transaction API, database and client handles, service ids, quorum constants, internal state structures, lock macros, module globals, and prototypes used across Ubik implementation files and generated Rx code.

Public-facing types include `struct ubik_client`, `struct ubik_hdr`, `struct ubik_trans`, `struct ubik_trunc`, `struct ubik_stat`, `struct ubik_dbase`, and `ubik_updatecache_func`. Public constants include transaction modes `UBIK_READTRANS` and `UBIK_WRITETRANS`, lock modes `LOCKREAD`, `LOCKWRITE`, `LOCKWAIT`, client flags `UPUBIKONLY` and `UBIK_CALL_NEW`, service ids `VOTE_SERVICE_ID`, `DISK_SERVICE_ID`, `USER_SERVICE_ID`, `MAXSERVERS`, `UBIK_MAGIC`, and `UBIK_MILESTONE`.

The central state model is `struct ubik_dbase`: path prefix, active transactions, version, version lock, transaction counters, disk-operation callbacks, reader counts, `cachedVersion`, and `cache_lock`. `struct ubik_trans` binds a transaction to its database, lock state, queued truncates, tid, seek position, flags, type, and write batching iovec buffers. `struct ubik_client` stores randomized Rx connections, per-server failure bits, sync-site hint, and a pthread mutex where available.

Under `UBIK_INTERNALS`, the header defines disk/log constants, transaction flags (`TRDONE`, `TRABORT`, `TRREADANY`, `TRCACHELOCKED`, `TRREADWRITE`), timer constants (`MAXSKEW`, `POLLTIME`, `RPCTIMEOUT`, `BIGTIME`, `SMALLTIME`, `VOTE_RPCTIMEOUT`), `struct ubik_server`, recovery state bits, and global structures for beacon, vote, address, and version locks. The lock-order comment is a critical integration contract: application cache, database, beacon, vote, version, then address lock.

Dependencies are broad: Rx-generated `ubik_int.h`, pthread or LWP, AFS locks, cell configuration, security classes, and physical disk/recovery/beacon/vote modules. The header is also where server/client security callback APIs and generic client initialization (`ugen_ClientInit*`) are declared.

Risks are mostly ABI and concurrency risks. This header exposes private internals to many compilation units, so flag or struct layout changes can silently affect lock/recovery semantics. `vcmp` subtracts version fields and assumes safe signed deltas. Test signals are compile- and integration-heavy: build all Ubik consumers, run client/server initialization, validate cache callback contracts, and stress lock ordering with pthread builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/ubik/ubik.p.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/ubik/ubikclient.c -->
# sources/distributed-fs/openafs/src/ubik/ubikclient.c

`ubikclient.c` implements Ubik client-side connection management, retry selection, sync-site discovery hints, and legacy variadic call wrappers. It is the layer that applications use to call generated Ubik RPC stubs while tolerating server failures and sync-site movement.

Important APIs are `ubik_ParseClientList`, `afs_random`, `ubik_ClientInit`, `ubik_ClientDestroy`, `ubik_RefreshConn`, `ubik_CallIter`, `ubik_Call_New`, legacy `ubik_Call`, and `ubik_CallRock`. `ubik_ParseClientList` parses `-servers` command-line entries into network-order addresses. `ubik_ClientInit` optionally reinitializes an existing client, destroys old connections, initializes the mutex, randomizes connection ordering using `afs_randomMod15`, and stores the connection list. `ubik_ClientDestroy` releases/destroys all Rx connections and frees the client.

Control flow in calls is two-pass retry. `CallIter` is the primitive iterator: choose the current connection, refresh it if Rx reports an error, skip recently failed servers when `UPUBIKONLY` is set, invoke the RPC function, mark negative errors as network failure, and advance the position. `ubik_Call_New` loops first over known-up servers and then all servers, returning on success or non-retryable global errors. Legacy `ubik_Call` additionally remembers RPC procedure pointers that returned `UNOTSYNC`, then biases later calls toward the remembered `syncSite` host. `ubik_CallRock` provides the same retry behavior for a type-safe callback carrying `struct ubik_callrock_info`.

State is entirely client-side and transient: connection array, `CFLastFailed` bits, initialization generation, sync-site host hint, and a small static cache of procedure addresses that need a sync site. There is no persistent storage. In pthread builds, pseudo-random state is thread-specific and client state is mutex-protected.

Dependencies include Rx connection APIs, rxgen constants, pthread globals, host lookup, and `ubik.h`. Risks include legacy function-pointer casts through `int *`, variadic long-argument RPC wrappers, weak non-cryptographic randomization, and behavior differences between pthread cached connections and non-pthread destruction. Test signals include reinitialization during an in-flight call, Rx connection errors causing refresh, first-pass skip/second-pass retry behavior, sync-site hint reuse, and `UBIK_CALL_NEW` compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/ubik/ubikclient.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/ubik/ubikcmd.c -->
# sources/distributed-fs/openafs/src/ubik/ubikcmd.c

`ubikcmd.c` provides command-line parsing helpers for Ubik server applications. Its single API, `ubik_ParseServerList`, discovers the local host address, parses `-servers`, filters the local host out of the peer list, recognizes `-dubik`, and returns a null-terminated server list.

The function resolves the current hostname with `gethostname`/`gethostbyname`, stores that address in `*ahost`, then walks argv. While inside the `-servers` list, it resolves hostnames, appends non-local addresses until `MAXSERVERS`, and stops on the next option. It separately records whether `-servers` was present and sets global `ubik_debugFlag` when `-dubik` is seen.

There is no persistence; output is in-memory network-order addresses consumed by `ubik_ServerInit`. Dependencies are libc host lookup, Rx/XDR includes, AFS locks, `ubik.h`, and the global debug flag.

Risks are mostly operational: fixed 64-byte local hostname buffer, old `gethostbyname` IPv4 behavior, no duplicate peer suppression besides the local address, and strict dependence on a `-servers` argument. Test signals are parser-level: missing `-servers` returns `UNOENT`, unknown host returns `UBADHOST`, overlong server list returns `UNHOSTS`, local host is excluded, and `-dubik` toggles debug output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/ubik/ubikcmd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/ubik/udebug.c -->
# sources/distributed-fs/openafs/src/ubik/udebug.c

`udebug.c` is the standalone Ubik diagnostic client. It contacts a server's VOTE service, fetches global and per-peer debug structures, and prints election, recovery, lock, transaction, version, and peer status in human-readable form.

Important functions are `PortNumber`, `PortName`, `CommandProc`, and `main`. `PortName` maps service names like `vlserver`, `ptserver`, `kaserver`, and `buserver` to default ports if service lookup fails. `CommandProc` resolves the target host and port, initializes Rx with null security, calls `VOTE_XDebug` with fallback to `VOTE_Debug` and old pre-3.5 `VOTE_DebugOld`, then optionally iterates `VOTE_XSDebug`/`VOTE_SDebug`/old equivalents for peer details.

Control flow is probe-and-print. After fetching `struct ubik_debug`, it compares remote and local clocks, warns when skew exceeds `MAXSKEW`, prints last yes vote and sync-site lease information, displays local and sync-site db versions, lock counts, active transaction tid, recovery flags, and for `-long` or sync sites prints each peer's addresses, clone flag, remote db version, last vote/beacon timing, and current/up/beaconSince state.

There is no persistent state. Dependencies are Rx client APIs, command parser `cmd`, host utilities, Ubik generated VOTE stubs, and structures from `ubik_int.h`. The tool intentionally uses null security because debug RPCs are informational.

Risks are diagnostic accuracy and compatibility: old server fallback uses struct casts, printed times depend on local clock comparison, and single-server sync-site state is fudged locally because voting is skipped for one server. Test signals include probing modern and old servers, named and numeric ports, localhost default, clone reporting, skew warning, and `-long` peer iteration termination.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/ubik/udebug.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/ubik/uinit.c -->
# sources/distributed-fs/openafs/src/ubik/uinit.c

`uinit.c` implements generic Ubik client initialization from AFS cell configuration and security settings. It hides config-directory lookup, cell host discovery, Rx security object creation, and `ubik_ClientInit` connection assembly behind several convenience APIs.

Important APIs are `ugen_ClientInitCell`, `ugen_ClientInitServer`, `ugen_ClientInitFlags`, and legacy `ugen_ClientInit`; internal helpers are `internal_client_init` and `internal_client_init_dir`. `internal_client_init_dir` opens a config directory, selects a cell name, retrieves `afsconf_cell` host information for a service id, and delegates. `internal_client_init` calls `rx_Init`, sets dead time, chooses a client security object via `afsconf_PickClientSecObj`, optionally reports fallback to null authentication, invokes a caller security callback, builds Rx connections either to one explicit server or every cell server, and initializes a `struct ubik_client`.

State is transient: a static `serverconns[MAXSERVERS]` array is reused during initialization and the resulting ownership is handed to Ubik client structures. Security flags combine local-auth, no-auth, fallback-null, and always-encrypt options. There is no file persistence beyond reading CellServDB/config data through afsconf.

Dependencies include Rx, `afsconf`, AFS auth/key configuration, dirpath constants, `ubik_ClientInit`, and service ids. Risks include the static connection array, maxserver checks, possible null-security fallback when tokens are unavailable, and confusing interaction between `serviceid` strings and numeric `usrvid` service ids. Test signals include explicit-server initialization, configured-cell initialization, noauth/localauth paths, too many configured servers, failed config open/cell lookup, and security callback invocation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/ubik/uinit.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/ubik/utst_client.c -->
# sources/distributed-fs/openafs/src/ubik/utst_client.c

`utst_client.c` is a simple sample/test client for the Ubik test service generated from `utst_int.xg`. It demonstrates parsing a server list, creating null-security Rx connections to USER service id on port 3000, initializing a Ubik client, and invoking sample RPCs through generated client wrappers.

The main commands are `-inc`, `-try`, `-qget`, `-get`, `-trunc`, `-minc`, and `-mget`. Single-shot commands call `ubik_SAMPLE_Inc`, `ubik_SAMPLE_Test`, `ubik_SAMPLE_QGet`, `ubik_SAMPLE_Get`, or `ubik_SAMPLE_Trun`. Looping modes repeatedly interleave get and increment calls with one-second sleeps to expose failover and race behavior.

There is no local persistence. State is the `struct ubik_client`, Rx connection array, and returned integer sample value. Dependencies are `ubik_ParseClientList`, Rx null security, generated sample stubs, and platform sleep/select differences.

Risks are limited because it is a test utility: infinite loops in `-minc`/`-mget`, null authentication, hard-coded port 3000, and sparse argument validation. Test signals are manual integration tests against `utst_server`: read/write/truncate behavior, quick read-any get, repeated sync-site discovery, and behavior while servers are restarted or partitioned.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/ubik/utst_client.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/ubik/utst_server.c -->
# sources/distributed-fs/openafs/src/ubik/utst_server.c

`utst_server.c` is the matching sample Ubik server. It creates a replicated test database under the system temp directory, exports sample RPC handlers, and demonstrates basic read/write transactions, locking, abort, truncate, and read-any behavior.

Important RPC handlers are `SSAMPLE_Inc`, `SSAMPLE_Get`, `SSAMPLE_QGet`, `SSAMPLE_Trun`, and `SSAMPLE_Test`. `SSAMPLE_Inc` starts a write transaction, obtains a whole-database write lock by convention at position 1, optionally sleeps, reads an integer with `UEOF` treated as zero, increments it, seeks to offset 0, writes it, and commits. `SSAMPLE_Get` starts a read transaction and read lock; `SSAMPLE_QGet` uses `ubik_BeginTransReadAny`; `SSAMPLE_Trun` truncates the database to zero; `SSAMPLE_Test` starts and locks a write transaction, reads, then deliberately aborts.

The `main` path parses `-sleep`, uses `ubik_ParseServerList`, initializes Ubik with `/tmp/testdb` equivalent and port 3000, registers a null-security SAMPLE service, sets min/max Rx procs, and starts the Rx server. Persistence is the Ubik database files with prefix `testdb`; the logical payload is a single 32-bit integer.

Dependencies are the Ubik public API, generated `utst_int.h`/SAMPLE service, Rx null server security, and temp-directory utilities. Risks are appropriate for a sample: hard-coded port and database naming, null security, no cleanup, no endian conversion for stored integer, and coarse locking convention. Test signals are direct: increment/get cycles, abort not changing state, truncate resetting to `UEOF`/zero, sleep-induced lock contention, and multi-server quorum behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/ubik/utst_server.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/ubik/vote.c -->
# sources/distributed-fs/openafs/src/ubik/vote.c

`vote.c` implements Ubik's vote/election state machine and debug RPCs. It enforces the lease-style invariant that a site cannot vote yes for two different sync-site candidates within `BIGTIME`, tracks the current sync-site claim, excludes clone servers from candidacy, and exposes current state to `udebug`.

Important APIs are `uvote_ShouldIRun`, `uvote_GetSyncSite`, `SVOTE_Beacon`, `SVOTE_Debug`, `SVOTE_XDebug`, `SVOTE_SDebug`, `SVOTE_XSDebug`, old debug variants, `uvote_Init`, `uvote_set_dbVersion`, `uvote_eq_dbVersion`, and `uvote_HaveSyncAndVersion`. `vote_globals` stores last yes vote time/host/state, current sync host/time, lowest host seen, and the sync site's db version/tid.

Election control flow begins with beacons. `SVOTE_Beacon` maps the caller to a primary Ubik address, rejects unknown hosts, recognizes clones, updates the lowest eligible host, refreshes or expires current sync-host knowledge, applies heuristics to avoid election loops, and grants a yes vote only when the prior yes lease is expired or the same host is renewing. On a yes vote it records the candidate's version and tid, then calls `urecovery_CheckTid` under the database lock so stale write transactions are aborted when a new tid arrives.

`uvote_ShouldIRun` tells the beacon module whether this server should seek votes: clones never run, valid other sync sites suppress candidacy, and lower-address valid candidates defer this host. `uvote_GetSyncSite` returns the last yes host only while its sync-site claim is still within `SMALLTIME`. Debug functions package vote, beacon, disk, lock, recovery, active write, tid, epoch, interface, and peer states into generated RPC structs, with old-struct compatibility.

State is in-memory and time-based; no direct disk persistence occurs here, but db version/tid values influence recovery and remote version-label acceptance. Dependencies include `ubik_servers`, `ubik_host`, `amIClone`, `beacon_globals`, `udisk_Debug`, `ulock_Debug`, `ubeacon_Debug`, and Rx caller identity. Risks include subtle time-skew assumptions, primary-address mapping correctness, election-loop prevention, and old debug casts. Test signals include clone behavior, unknown-host beacon rejection, lower-host deferral, BIGTIME vote lockout, sync-site expiry, db version comparisons, and debug RPC compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/ubik/vote.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/update/Makefile.in -->
# sources/distributed-fs/openafs/src/update/Makefile.in

This makefile builds the OpenAFS update service tools `upserver` and `upclient` and their rxgen-generated protocol support. It defines dependencies on auth, rx, rxkad, cmd, util, and opr libraries, and exposes `all`, `generated`, install, dest, and clean targets.

Generated artifacts come from `update.xg`: `update.cs.c`, `update.ss.c`, `update.xdr.c`, and `update.h`. `upclient` links `client.o`, client stubs, `utils.o`, and the common libraries; `upserver` links `server.o`, `utils.o`, server stubs, and the same library set. Object dependencies ensure `update.h`, `global.h`, and `AFS_component_version_number.c` are available.

Integration points are the top-level OpenAFS make configuration, pthread config, rxgen, libtool static linker rules, and server installation directories. Persistence behavior is build/install only: binaries land under server libexec or legacy destination paths.

Risks are mostly build-system drift: generated file dependencies must match rxgen outputs, clean must remove generated protocol files, and library ordering matters for static links. Test signals are `make generated`, full `make upclient upserver`, install/dest staging, and clean/regenerate idempotence.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/update/Makefile.in -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/update/client.c -->
# sources/distributed-fs/openafs/src/update/client.c

`client.c` implements `upclient`, a polling file synchronizer that copies exported files from an `upserver` to local directories. It fetches directory manifests, compares local files by mtime and size, downloads changed files to `.NEW` staging files, removes local files absent from the server manifest, and renames staged files into place.

Important functions are `main`, `GetServer`, `IsCompatible`, `FetchFile`, `update_ReceiveFile`, `NotOnHost`, `RenameNewFiles`, `GetFileFromUpServer`, and `PathsAreEquivalent`. `main` parses host, `-time`, `-crypt`, `-clear`, and `-verbose`, normalizes requested directories, initializes Rx and server-local authentication, then loops forever over directories. For each directory, it constructs a local path, ensures it exists, fetches remote directory info via `UPDATE_FetchInfo`, scans manifest lines containing quoted path, mtime, length, mode, uid, gid, and atime, and fetches incompatible files via `UPDATE_FetchFile`.

Transfer control flow uses `FetchFile` for both manifest and file data. It starts the relevant rxgen streaming call, opens/truncates the local output, and delegates to `update_ReceiveFile`, which reads a network-order length followed by data chunks sized from filesystem block size. `GetFileFromUpServer` writes to `<local>.NEW`, then applies mode, uid/gid on Unix, and access/modify times before later atomic-ish rename by `RenameNewFiles`.

State and persistence are filesystem-based. Temporary manifest files are created under `gettmpdir()` as `upclient.<pid>`, staged downloads use `.NEW`, and extra local non-directory/non-`.NEW` files are unlinked if not in `okhostfiles`. Lists are maintained with `struct filestr` from `global.h` and `utils.c`.

Dependencies include Rx, rxkad, afsconf local auth, path normalization/localization helpers, `update.h` generated stubs, and the update server's manifest format. Risks include trusting server-supplied metadata, fixed `MAXFNSIZE` buffers with `strcpy`/`strcat` in several paths, deletion of local files not in the server manifest, manifest parsing fragility, and retry loops that sleep indefinitely. Test signals include changed/unchanged file comparison, `.NEW` cleanup on failed fetch, deletion filtering, path equivalence on Unix/Windows, crypt/clear auth modes, reconnect after repeated failures, and metadata restoration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/update/client.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/update/global.h -->
# sources/distributed-fs/openafs/src/update/global.h

`global.h` contains shared constants and the linked-list type used by `upclient`, `upserver`, and update utilities. It defines `TIMEOUT` as the default resync interval, `MAXFNSIZE` as the maximum filename buffer size, `MAXENTRIES` as the maximum exported directory entries accepted by `upserver`, and `UPDATEERR`.

The only type is `struct filestr`, a singly linked list of dynamically allocated names. `utils.c` manages this list with `AddToList` and `ZapList`; `client.c` uses it for requested directories, modified files, and server-manifest files.

There is no direct persistence or control flow here. Dependencies are minimal, with a Windows include for NT builds. Risks are fixed-size constants driving buffer assumptions throughout update code and a generic list type without ownership annotations. Test signals are compile coverage and list lifecycle checks through the client synchronization loop.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/update/global.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/update/server.c -->
# sources/distributed-fs/openafs/src/update/server.c

`server.c` implements `upserver`, the authenticated Rx file-export service consumed by `upclient`. It exposes configured directories, enforces superuser and security-level authorization, streams file contents, and generates directory manifest files.

Important functions are `main`, `AuthOkay`, `PathInDirectory`, `UPDATE_FetchFile`, `UPDATE_FetchInfo`, `update_SendFile`, `update_SendDirInfo`, `AddObject`, `Quit`, and `update_rxstat_userok`. `main` parses exported directories interleaved with security-level options (`-crypt`, `-clear`, `-auth`) and `-rxbind`, localizes each export path through `AddObject`, opens server config, optionally binds Rx to a configured address, builds server security objects, creates the UPDATE service, and starts the Rx server.

Authorization combines AFS superuser status with export-directory matching. `AuthOkay` first requires `afsconf_SuperUser`, derives rxkad level for authenticated connections, checks whether the requested local path is inside any configured export root via `PathInDirectory`, and rejects access when a matched subtree requires a stronger security level than the connection provides. Later matching entries can be more restrictive, so all entries are scanned.

Persistence behavior is read-only export except for a temporary manifest. `UPDATE_FetchFile` localizes the requested path, validates authorization, opens the file, and calls `update_SendFile`, which sends network-order length and file bytes in block-size chunks. `UPDATE_FetchInfo` verifies the requested path is a directory and calls `update_SendDirInfo`; that function scans direct children, writes non-directory entries and metadata to `gettmpdir()/upserver.tmp`, streams that temp file, then unlinks it.

Dependencies include Rx/rxkad, afsconf server security, authcon, path localization/normalization, generated `update.h`, and OpenAFS dirpath/network binding helpers. Risks include fixed global temp manifest name shared across calls, fixed-size path buffers with concatenation, direct-child-only manifest behavior, race windows between stat/open/read, and strict reliance on SuperUser configuration. Test signals include auth matrix by security level, path traversal/localization rejection, concurrent manifest requests, exported subtree restriction precedence, `-rxbind` host selection, and streaming error handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/update/server.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/update/update_internal.h -->
# sources/distributed-fs/openafs/src/update/update_internal.h

`update_internal.h` is the small private header shared within the update directory. It declares list helpers from `utils.c` and the server-side generated RPC entry points `UPDATE_FetchFile` and `UPDATE_FetchInfo`.

The file has no runtime control flow or persistence. Its integration role is to keep `client.c`, `server.c`, and `utils.c` prototypes consistent without exposing them as a broader installed API.

Dependencies are `struct filestr` from `global.h` and `struct rx_call` from Rx headers included by consumers. Risks are limited to prototype drift if generated RPC signatures or utility ownership semantics change. Test signals are build coverage for both upclient and upserver.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/update/update_internal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/update/utils.c -->
# sources/distributed-fs/openafs/src/update/utils.c

`utils.c` implements the update package's simple `struct filestr` linked-list helpers. `AddToList` allocates a node, pushes it at the head of a caller-owned list, and stores a `strdup` of the supplied name. `ZapList` walks the list, frees each name and node, and resets the head to `NULL`.

There is no persistence beyond heap ownership. Dependencies are `global.h`, libc allocation, and platform includes for NT builds. The functions are used heavily by `upclient` to manage configured directories, modified files, and host manifest entries.

Risks are small but real: allocation failures are not checked, `AddToList` always returns 0, and callers rely on LIFO order being acceptable. Test signals are memory-leak/error-injection checks and repeated `ZapList` calls in the synchronization loop.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/update/utils.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/usd/Makefile.in -->
# sources/distributed-fs/openafs/src/usd/Makefile.in

This makefile builds the USD user-space device library as both libtool shared/static output and a legacy `libusd.a`, and installs `usd.h`. Objects are `usd_file.lo` and `AFS_component_version_number.lo`; dependencies include `liboafs_opr`.

Targets include `liboafs_usd.la`, `libusd.a`, top-level library/header copies, install, dest, and clean. It includes top-level config, pthread config, and libtool rules. The makefile only builds the POSIX implementation in this path; Windows builds use the platform makefile and `usd_nt.c`.

Persistence is build artifact installation into library and include directories. Risks are build-system consistency between libtool and legacy static outputs, symbol list alignment through `liboafs_usd.la.sym`, and ensuring `usd.h` is copied to the top include tree. Test signals are full library build, install/dest staging, and downstream link of the USD test.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/usd/Makefile.in -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/usd/test/Makefile.in -->
# sources/distributed-fs/openafs/src/usd/test/Makefile.in

This makefile builds the `usd_test` executable against the top-level `libusd.a`. It includes OpenAFS config and LWP make settings, sets include paths for the destination include tree and parent directory, and defines `test`/`tests` as aliases depending on the binary.

The main build rule links `usd_test.o` with `LIBUSD` and platform libraries. `clean` removes objects, executable, core files, and component version output.

Risks are mostly dependency freshness: `usd_test` depends on installed/copied `afs/usd.h` and `libusd.a`, so partial builds can fail if the parent library was not built first. Test signals are successful compile/link and manual execution against a tape-capable device.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/usd/test/Makefile.in -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/usd/test/usd_test.c -->
# sources/distributed-fs/openafs/src/usd/test/usd_test.c

`usd_test.c` is a destructive/manual integration test for the USD tape-device abstraction. It opens a supplied tape device read/write with a write lock, prepares and rewinds it, writes blocks and file marks, reads back content, exercises forward/backward file spacing, shuts down the tape, and closes the USD handle.

Important helpers are `err_exit`, `bufeql`, `Rewind`, `WriteEOF`, `ForwardSpace`, `BackSpace`, `PrepTape`, `ShutdownTape`, and `PrintTapePos`. The main flow writes ten 1024-byte blocks, writes one EOF mark, rewinds and reads ten blocks, writes five data/filemark pairs, tests `FSF` by reading expected marker bytes, tests `BSF` plus `FSF`, then shuts down and closes.

State and persistence are on the target tape device. The test intentionally changes media contents and assumes tape semantics. It uses `USD_IOCTL_TAPEOPERATION`, `USD_READ`, `USD_WRITE`, `USD_SEEK`, and `USD_CLOSE`; Windows position reporting calls `GetTapePosition` directly via `hTape->handle`, while Unix uses `USD_SEEK(SEEK_CUR)`.

Risks include destructive media writes, uninitialized buffer contents in the first write/read comparison except for later marker bytes, recursion concerns avoided in `ShutdownTape`, and platform/device dependence. Test signals are explicit console pass/fail messages, transferred byte counts, data equality, tape operation return codes, and optional position debug output via `USDTEST_DEBUG`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/usd/test/usd_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/usd/usd.h -->
# sources/distributed-fs/openafs/src/usd/usd.h

`usd.h` defines the public user-space device abstraction used by OpenAFS components that need to treat regular files and devices uniformly across Unix and Windows. It exposes an opaque-ish `usd_handle_t` containing operation function pointers plus private handle fields.

Important APIs are `usd_Open`, `usd_StandardInput`, `usd_StandardOutput`, and macros `USD_READ`, `USD_WRITE`, `USD_SEEK`, `USD_IOCTL`, and `USD_CLOSE`. Open flags include read-only/read-write, synchronous I/O, read/write lock, and create. Ioctls include type, full name, device id, size get/set, tape operation, block size, and seekability. Tape operations include write EOF, rewind, forward/backward space file, prepare, and shutdown.

State is held in `struct usd_handle`: callbacks, platform handle, full path, open flags, and private data. The header documents errno-style integer returns and output parameters for transferred byte counts and offsets. It also documents the Windows constraint that device locks must be tied to open handles.

Dependencies are AFS integer types and platform implementations in `usd_file.c`/`usd_nt.c`. Risks include callers treating private fields as stable, the macro API lacking null checks, and cross-platform semantic gaps for devices, locks, and seekability. Test signals are compile coverage and exercising all ioctl cases through `usd_test` and regular-file unit tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/usd/usd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/usd/usd_file.c -->
# sources/distributed-fs/openafs/src/usd/usd_file.c

`usd_file.c` is the POSIX implementation of the USD abstraction. It wraps file descriptors in `usd_handle_t`, implements read/write/seek/ioctl/close callbacks, supports large-file seeking when available, maps common tape operations to platform ioctls, and optionally obtains advisory whole-file locks at open time.

Important functions are `usd_FileRead`, `usd_FileWrite`, `usd_FileSeek`, `usd_FileIoctl`, `usd_FileClose`, `usd_FileOpen`, `usd_Open`, `usd_StandardInput`, and `usd_StandardOutput`. `usd_FileIoctl` handles type/device/size/fullname/setsize/tape/blocksize/seekable requests using `fstat`, `ftruncate`, `ioctl(MTIOCTOP)` or AIX `STIOCTOP`, and platform block-size fallbacks. `usd_FileOpen` maps USD flags to `open`/`open64` flags, allocates a handle, installs callbacks, duplicates the path, and applies read or write locks via `fcntl`.

Persistence behavior is direct filesystem/device I/O. Writes go immediately to the fd; `USD_OPEN_SYNC` maps to `O_SYNC` when available. Close calls `fsync` only for writable block devices before closing and freeing the handle. Size changes call `ftruncate`/`ftruncate64`. Standard input/output wrappers allocate dummy handles that do not close the underlying fd.

Dependencies include POSIX I/O, `mtio`/AIX tape headers, OpenAFS assertions, and offset type feature macros. Risks include partial read/write semantics being surfaced only through `xferdP`, advisory locks not guaranteeing device exclusivity everywhere, removed hard-disk attachment checks, platform tape ioctl differences, and standard handles using static string names freed only by dummy close. Test signals include regular-file open/read/write/seek/truncate, lock conflict tests, block/char/fifo seekability, tape ioctl mapping, large offsets, and block-device close fsync behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/usd/usd_file.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/usd/usd_nt.c -->
# sources/distributed-fs/openafs/src/usd/usd_nt.c

`usd_nt.c` is the WinNT implementation of the USD abstraction. It wraps Win32 `HANDLE`s, maps Unix-style errno returns through `nterr_nt2unix`, handles regular files, disk devices, and tape drives, and implements tape operations with Win32 tape APIs.

Important functions are `usd_DeviceRead`, `usd_DeviceWrite`, `usd_DeviceSeek`, `usd_DeviceIoctl`, `usd_DeviceClose`, `usd_DeviceOpen`, `usd_Open`, `usd_StandardInput`, and `usd_StandardOutput`. Open maps USD flags to `CreateFile` access/share/create/attribute flags; read/write call `ReadFile` and `WriteFile`; seek maps whence to `SetFilePointerEx` and optionally bounds disk-device offsets using cached geometry-derived size in `privateData`.

`usd_DeviceIoctl` detects object type using `GetFileInformationByHandle`, `IOCTL_DISK_GET_DRIVE_GEOMETRY`, and `GetTapeStatus`; supports size get/set, full name, block size, seekability, and tape commands. Tape operations map to `WriteTapemark`, `SetTapePosition`, `PrepareTape`, `GetTapeStatus`, and `GetTapeParameters`, with retries for transient media/bus errors during prepare/rewind flows.

Persistence is through Win32 file/device handles. `USD_OPEN_SYNC` maps to `FILE_FLAG_WRITE_THROUGH`; locks are approximated through sharing modes because Windows locks devices by handle. `USD_IOCTL_SETSIZE` seeks then calls `SetEndOfFile`. Close frees `fullPathName` and the USD handle after `CloseHandle`.

Risks include privateData storing a 32-bit kilobyte upper bound in a pointer, coarse disk size estimation from whole-disk geometry, `USD_IOCTL_GETDEV` unreachable code after an immediate `EINVAL`, standard input/output helpers allocating handles but not assigning `*usdP`, and platform-specific tape behavior. Test signals include regular file and device open modes, share-lock conflicts, disk seek bounds, tape prepare/rewind transient retries, end-of-media write behavior, and standard stream wrapper correctness.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/usd/usd_nt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/uss/Makefile.in -->
# sources/distributed-fs/openafs/src/uss/Makefile.in

This makefile builds the `uss` user/account provisioning tool and its lex/yacc parser. It compiles core modules for procedures, common utilities, volume creation, ACLs, ptserver, kauth, fs interactions, plus generated `lex.yy.o` and `y.tab.o`, and links against kauth, volser, cmd, and opr libraries.

Generated parser flow is explicit: `lex.yy.c` is produced from `lex.l`, then transformed by `yy-lsed`; `y.tab.c` and `y.tab.h` are produced from `grammar.y` and also transformed by `yy-lsed`. Special CFLAGS are used for generated lexer code to suppress unused/old-style/implicit-fallthrough warnings. Install places `uss` under `sbindir`; dest places it under legacy `/etc`.

Dependencies reflect the parser and module coupling: `uss.c` depends on common/procs/kauth/fs headers; procedure modules depend on ACL, volume, common, and fs headers. Persistence is build/install artifact generation only.

Risks include generated-file sed post-processing, yacc/lex tool differences, generated header ordering (`lex.yy.o` depends on `y.tab.c`), and broad static link dependencies. Test signals are clean parser regeneration, full `uss` link, install/dest staging, and parser smoke tests with sample bulk/template files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/uss/Makefile.in -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/uss/grammar.y -->
# sources/distributed-fs/openafs/src/uss/grammar.y

`grammar.y` defines the yacc grammar for `uss` bulk/template commands. It maps parsed command lines into provisioning actions such as directory creation, file copy, echo, command execution, link creation, volume creation, directory-pool group declaration, and authentication field updates.

Tokens include command tokens (`DIR_TKN`, `FILE_TKN`, `ECHO_TKN`, `EXEC_TKN`, `LINK_TKN`, `SYMLINK_TKN`, `VOL_TKN`, `GROUP_TKN`, `AUTH_TKN`, `VOL1_TKN`), `STRING_TKN`, and `EOL_TKN`. The `entry` rule calls implementation functions directly: `uss_procs_BuildDir`, `uss_procs_CpFile`, `uss_procs_EchoToFile`, `uss_procs_Exec`, `uss_procs_SetLink`, `uss_vol_CreateVol`, `uss_procs_AddToDirPool`, and `uss_kauth_SetFields`. Return values are assigned to global `uss_perr`.

The `accesslist` rule recursively consumes pairs of strings and builds a space-separated ACL string in a fixed 1000-byte semantic value buffer, defaulting to a single space when absent. Error handling prints line-relative context through `uss_procs_PrintErr`, and `yyerror` writes a short parse error to stderr.

There is no direct persistence here, but parser actions immediately call routines that modify filesystem, AFS volumes, ACLs, and authentication state. Dependencies include lexer token values from `y.tab.h`, global `line`, `uss_perr`, and the uss procedure/volume/kauth modules.

Risks include immediate side effects during parsing, fixed-size semantic buffers, recursive ACL string concatenation truncation/error behavior, and a grammar that only validates command shape while deeper validation lives in action functions. Test signals include parsing each command type, optional and multi-entry ACLs, syntax error line reporting, long token/ACL rejection, and `VOL`/`VOL1` compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/uss/grammar.y -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/uss/lex.l -->
# sources/distributed-fs/openafs/src/uss/lex.l

`lex.l` is the lexer for `uss` bulk/template files. It recognizes line-leading single-letter commands, comments, whitespace, quoted strings, unquoted strings, end-of-line tokens, invalid commands, and performs variable substitution before returning `STRING_TKN`.

Important patterns are comments `#[^\n]*`, command starts `D/F/L/S/E/X/V/G/A/Y` followed by whitespace, unquoted strings beginning with `[.A-Z0-9a-z/$]`, quoted strings without embedded newlines, and invalid line-leading command characters. The global `line` counter increments on blank lines and newline tokens. `yywrap` returns 1 for single-input completion.

The key function is `Replace`. It strips opening quotes, scans for `$` variables, expands positional `$1`..`$9`, rejects `$0`, checks against `uss_VarMax`, expands named variables like `$USER`, `$UID`, `$SERVER`, `$PART`, `$MTPT`, `$NAME`, `$AUTO`, and `$PWEXPIRES`, and warns while copying through unknown variables. `$AUTO` calls `uss_procs_PickADir`, then uses global `uss_Auto`.

State and side effects are parser globals and substitution globals from `uss_common.h`/`uss_procs.h`. The lexer itself does not persist data, but substitutions drive later provisioning side effects. Dependencies include yacc-generated `y.tab.h`, uss common globals, and `uss_procs_PrintErr`.

Risks include unchecked `strcpy` into yacc semantic buffers during substitution, quoted-string pattern accepting newline as a terminator, unknown variable handling advancing one character at a time, command recognition only at line start, and direct `exit` on invalid positional variables. Test signals include all command tokens, comments/blank lines, quoted and unquoted strings, every supported variable, `$AUTO` selection, unknown variable warnings, invalid commands, and line-number accuracy.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/uss/lex.l -->
