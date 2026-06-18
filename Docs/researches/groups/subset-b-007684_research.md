# subset-b-007684 research

This grouped report covers MooseFS master chunk metadata APIs, chunkserver database state, client-visible chunkserver IP mapping, session data-cache coherency hints, and export authorization parsing. Each file section is wrapped with reconciliation markers for deterministic splitting into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/moosefs/mfsmaster/chunks.h -->
# sources/distributed-fs/moosefs/mfsmaster/chunks.h

Purpose: declares the MooseFS master chunk metadata and placement interface. This header is the central contract between filesystem namespace operations, chunkserver connection handling, storage-class policy code, metadata load/store, and the background chunk job engine implemented in `chunks.c`.

Important APIs/types/functions: `MAXCSCOUNT` bounds chunkserver-related arrays at 10000. The `CHUNK_OP_*` constants and `CHUNK_STATS_CNT` define operation statistics slots for delete, replicate, create, change, and split attempts/outcomes. `chunkfloop` classifies file-loop checks such as missing chunks, wrong versions, partial EC state, under-goal placement, and OK. Metadata/changelog replay APIs include `chunk_mr_multi_modify()`, `chunk_mr_multi_truncate()`, `chunk_mr_unlock()`, `chunk_mr_increase_version()`, `chunk_mr_set_version()`, `chunk_mr_nextchunkid()`, `chunk_mr_chunkadd()`, `chunk_mr_chunkdel()`, and `chunk_mr_flagsclr()`. Runtime APIs cover read/write chunk selection, repair, file-to-chunk reference updates, chunkserver status notifications, label-set validation, persistence, cleanup, and memory accounting.

Control flow: namespace code asks chunk APIs to create, modify, truncate, repair, unlock, or delete chunk references. Client read/write paths fetch versions and chunkserver location arrays through `chunk_get_version_and_csdata()` or `chunk_get_version_and_copies()`. Chunkserver registration paths call `chunk_server_connected()`, `chunk_server_has_chunk()`, `chunk_damaged()`, `chunk_lost()`, `chunk_server_register_end()`, and `chunk_server_disconnected()` to reconcile server reports into master metadata. Completion packets from chunkservers flow through the `chunk_got_*_status()` callbacks, which feed the chunk operation/job state machine.

State/persistence: this header exposes only declarations, but its API makes clear that chunk state is durable master metadata: `chunk_load()` and `chunk_store()` serialize the CHNK metadata section, `chunk_newfs()` initializes an empty filesystem, and `chunk_is_afterload_needed()` signals version-dependent post-load work. Runtime state includes chunk locks, busy operations, job queues, missing-log membership, storage-class counters, archive/trash flags, server placement, and repair/replication progress.

Dependencies/integration: depends on `bio.h` for metadata I/O and `storageclass.h` for `storagemode`. It is consumed by `metadata.c`, `filesystem.c`, `matoclserv.c`, `matocsserv.c`, `storageclass.c`, `chunkdelay.c`, and related master modules. It integrates with `csdb` indirectly through server availability and with multilan/client IP behavior through chunkserver location APIs that accept `clientip`.

Risks/test signals: this is a high-blast-radius API surface. Risks include version mismatches between metadata replay and live operations, incorrect chunkserver location serialization sizes, EC part accounting errors, lock/unlock imbalance, job completion callbacks arriving after disconnects, and storage-class label fulfillment drifting from real server labels. Useful signals are metadata round-trip tests across versions, changelog replay equivalence for modify/truncate/delete/unlock, chunkserver register/disconnect scenarios, read/write chunk selection for copy and EC chunks, damaged/lost report handling, and storage-class counter consistency checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/moosefs/mfsmaster/chunks.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/moosefs/mfsmaster/csdb.c -->
# sources/distributed-fs/moosefs/mfsmaster/csdb.c

Purpose: implements the master-side chunkserver database. It tracks known chunkservers by IP/port and optional 16-bit server id, connection liveness, maintenance state, heavy-load grace windows, display ordering, metadata persistence, and changelog replay operations.

Important APIs/types/functions: `struct csdbentry` stores `ip`, `port`, `csid`, sorted `number`, `heavyloadts`, current `load`, maintenance timeout/state, disconnection timestamp, live `eptr`, and hash-chain linkage. `csdbhash[256]` indexes by IP/port while `csdbtab[65536]` indexes by `csid`. `csdb_new_connection()` attaches a live matocs connection to an existing or new entry, can migrate IP/port by trusted `csid`, and emits changelog records. `csdb_get_csid()` lazily allocates ids. `csdb_lost_connection()`, `csdb_remove_server()`, `csdb_remove_unused()`, `csdb_maintenance()`, and `csdb_temporary_maintenance_mode()` mutate availability. `csdb_mr_op()` replays durable CSDB operations. `csdb_store()` and `csdb_load()` serialize metadata. `csdb_servlist_data()` builds client/operator server-list records.

Control flow: initialization loads config values and registers periodic self-check and unused-server cleanup callbacks. When a chunkserver connects, the master first tries exact `csid` plus IP/port, then IP/port, then `csid` relocation, then allocates a fresh record. Disconnections leave records in memory and increment disconnected counters. Operator actions from `matoclserv` call remove, back-to-work, or maintenance toggles; successful durable mutations log `CSDBOP(...)` records. Metadata replay runs through `csdb_mr_op()`, applying the same add/delete/id/maintenance/IP-port changes while incrementing metadata version. Periodic `csdb_self_check()` expires maintenance windows and repairs aggregate counters if they drift.

State/persistence: persistent metadata stores each server as IP, port, `csid`, maintenance mode, and maintenance timeout in the CSDB chunk; older metadata versions load shorter records. Runtime-only fields include live connection pointer, server load, heavy-load timestamp, sorted display number, and disconnection timestamp. Config-driven state includes `CS_HEAVY_LOAD_GRACE_PERIOD`, `CS_HEAVY_LOAD_THRESHOLD`, `CS_HEAVY_LOAD_RATIO_THRESHOLD`, `CS_MAINTENANCE_MODE_TIMEOUT`, `CS_TEMP_MAINTENANCE_MODE_TIMEOUT`, and `CS_DAYS_TO_REMOVE_UNUSED`. `loadsum`, `servers`, `disconnected_servers`, and `disconnected_servers_in_maintenance` are aggregate process state.

Dependencies/integration: depends on MooseFS protocol constants from `MFSCommunication.h`, metadata I/O through `bio`/`datapack`, changelog and `meta_version_inc()`, config reload hooks, main time callbacks, logging/assert helpers, `matocsserv_getservdata()` for live server metrics, `multilan_map()` for client-facing server IPs, `sockets.h` formatting helpers, and `metadata.c` for load/store orchestration. `matoclserv.c` exposes maintenance/removal/server-list controls to clients/operators.

Risks/test signals: the header declares `csdb_accept_server()` but this implementation does not define it, so callers/build coverage should verify whether the declaration is stale. `csdb_newid()` can return 65536 cast to `uint16_t` if all ids are exhausted; practical limits may avoid this but tests should cover id exhaustion. Counter drift is corrected periodically, implying mutation paths are subtle. `csdb_mr_op(CSDB_OP_ADD)` writes `csdbtab[arg]` even when `arg` is zero, matching allocation logic but worth regression coverage. Tests should cover reconnect by id, IP/port migration, duplicate load entries with and without ignore mode, maintenance timeout expiry, disconnected-maintenance counters, heavy-load detection and grace clearing, client server-list record sizes for both modes, metadata round trips for versions 0x10 through current, and unused-server cleanup changelog replay.
<!-- END_FILE_RESEARCH: sources/distributed-fs/moosefs/mfsmaster/csdb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/moosefs/mfsmaster/csdb.h -->
# sources/distributed-fs/moosefs/mfsmaster/csdb.h

Purpose: public interface for the MooseFS master chunkserver database. It exposes connection lifecycle, server status queries, operator mutations, metadata persistence, initialization, and master-replay operations to the rest of the master.

Important APIs/types/functions: connection APIs are `csdb_new_connection()`, `csdb_get_csid()`, `csdb_temporary_maintenance_mode()`, `csdb_lost_connection()`, and the declared `csdb_accept_server()`. Status and list APIs are `csdb_server_load()`, `csdb_server_is_overloaded()`, `csdb_server_is_being_maintained()`, `csdb_servlist_data()`, `csdb_have_all_servers()`, `csdb_stop_chunk_jobs()`, `csdb_servers_count()`, `csdb_get_server_counters()`, `csdb_sort_servers()`, and `csdb_getnumber()`. Mutators include `csdb_remove_server()`, `csdb_back_to_work()`, and `csdb_maintenance()`. Persistence and replay APIs are `csdb_store()`, `csdb_load()`, `csdb_mr_op()`, plus `csdb_mr_csadd` and `csdb_mr_csdel` macros.

Control flow: `matocsserv` creates and updates opaque csdb entry pointers for live chunkserver connections; `matoclserv` asks for server-list data and applies administrative operations; `metadata.c` calls load/store during master startup and checkpointing; replay code uses `csdb_mr_op()` or the add/delete macros to apply changelog entries. Callers treat `void *` handles as opaque and pass them back for id, load, maintenance, and sort-number queries.

State/persistence: the header hides all internal tables. Its persistence contract is explicit through `bio`-based load/store and the replay op API. `csdb_store(NULL)` is used as a metadata format-version query in the implementation pattern, returning the current format code rather than writing data.

Dependencies/integration: includes `bio.h` and fixed-width integer types. It depends semantically on MooseFS status/error constants for return values, even though those constants come from other headers in callers. The macro op numbers must stay synchronized with `csdb.c`'s internal `CSDB_OP_ADD` and `CSDB_OP_DEL` values.

Risks/test signals: `csdb_accept_server()` appears in the header but not in the inspected implementation file, which can indicate a stale API declaration or an implementation hidden by build configuration elsewhere; build/link tests should catch it. Since most APIs accept opaque pointers, misuse after `csdb_cleanup()` or after server removal is possible unless higher layers own lifetime strictly. Tests should compile all consumers, verify replay macro values against actual changelog parsing, and exercise null-pointer-tolerant counter APIs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/moosefs/mfsmaster/csdb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/moosefs/mfsmaster/csipmap.c -->
# sources/distributed-fs/moosefs/mfsmaster/csipmap.c

Purpose: implements configurable chunkserver IP remapping for clients on selected networks. It lets the master return an alternate chunkserver address to a client when the client's IP falls into a configured class/range and a server IP has a mapping in that section.

Important APIs/types/functions: `struct ipclass` stores client `fromip`/`toip` ranges and a section number. `struct ipmap` stores source chunkserver IP, mapped destination IP, section, and hash linkage. `csipmap_map()` finds the first matching client class, then looks up the server IP in the active per-section hash table. `csipmap_parseline()` parses class/range/map lines. `csipmap_loadmap()` loads a complete map file into staging lists, validates ordering and section limits, and atomically swaps active maps only after a clean parse. `csipmap_cleanup()`, `csipmap_use_loaded_map()`, `csipmap_term()`, and `csipmap_init()` manage memory. A `#ifdef TEST` block provides standalone parsing, dumping, and CLI diagnostics.

Control flow: config lines are processed as whitespace-insensitive entries with comments. Class/range lines start or extend a section; once mapping lines have been seen, a later class/range advances `current_section`. Mapping lines require a preceding class or range, otherwise `BAD_SECTION_ORDER` aborts loading. Repeated source IP mappings in the same section overwrite the staged destination. On file open failure, the existing active map remains unchanged. On parse error, the staged map is freed and the active map remains unchanged. On successful EOF, a class/range section with no mappings is rejected; otherwise the active map is freed and replaced with the staged map.

State/persistence: active runtime state is `ipclass_head` plus `ipmap_hashtab[1024]`; staged state during reload is `load_head` plus `load_hashtab[1024]`. The file itself is external configuration, not MooseFS metadata, and is not persisted by this module. `MAX_SECTIONS` limits the file to 10 sections. `current_section` and `lstate` are transient parser state.

Dependencies/integration: uses `mfs_log` in normal builds and a fprintf shim in `TEST` builds. It is called by `multilan.c`, which loads `MULTILAN_IPMAP_FILENAME` and consults `csipmap_map()` before its class-based multilan logic. `csdb_servlist_data()` and `matocsserv_getservers` paths ultimately use multilan mapping to present client-specific chunkserver addresses.

Risks/test signals: parser behavior is intentionally strict and aborts the whole reload on the first bad line, but open failures preserve old state; tests should assert both behaviors. The `ipclass_head` search is linear and first-match by reverse insertion order because new classes are prepended, so overlapping ranges can produce non-obvious precedence. The bit-mask parser does `0xFFFFFFFF << (32 - octet)` and needs coverage for `/0` to ensure compiler/platform behavior is acceptable. `malloc()` results are not checked in this file. Tests should cover repeated mappings, section rollover, too many sections, empty files, class without mappings, missing files before and after an active map, CIDR and explicit masks, ranges with bad order, comments/whitespace, and standalone `TEST` mode map queries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/moosefs/mfsmaster/csipmap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/moosefs/mfsmaster/csipmap.h -->
# sources/distributed-fs/moosefs/mfsmaster/csipmap.h

Purpose: declares the small public API for chunkserver IP mapping. This is the low-level mapping layer used by the master multilan subsystem to convert a server IP into a client-specific reachable IP.

Important APIs/types/functions: `csipmap_map(servip, clientip)` returns a mapped destination IP or zero when no map applies. `csipmap_loadmap(fname)` reloads the external mapping file. `csipmap_term()` frees active mapping state. `csipmap_init()` initializes empty state.

Control flow: callers initialize once, load or reload a named mapping file when configuration is read, call `csipmap_map()` during server address serialization, and call `csipmap_term()` on shutdown. A zero return is not an error; it means the caller should keep the original address or fall through to another mapping strategy.

State/persistence: all state is internal to `csipmap.c` and in-memory. The mapping file is external configuration and is not written through this API.

Dependencies/integration: only includes fixed-width integer types. The main integration point is `multilan.c`, which wraps this API and exposes `multilan_map()` to chunkserver-list and chunk-location serialization code.

Risks/test signals: because zero is a valid sentinel rather than a status code, callers must not treat `0.0.0.0` as a usable mapped address. Tests should cover init/load/map/term sequencing, no-map fallback behavior, and reload preserving prior maps after errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/moosefs/mfsmaster/csipmap.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/moosefs/mfsmaster/datacachemgr.c -->
# sources/distributed-fs/moosefs/mfsmaster/datacachemgr.c

Purpose: implements an in-memory master hint table for whether a client session may keep cached file data when opening an inode. It tracks recent `(inode, sessionid)` pairs and invalidates other sessions' cache-ok state when one session modifies the inode.

Important APIs/types/functions: `datacache_entry` stores `inode`, a one-bit `cacheok`, a 31-bit `sessionid`, inode-hash links, and LRU links. `DCM_TAB_LENG` fixes capacity at 500000 entries; `DCM_INODEHASH_LENG` uses half that for hash buckets; `DCM_NIL` is the link sentinel. `dcm_open()` returns whether the pair is known cache-safe and inserts/replaces an LRU entry when missing. `dcm_access()` marks an existing pair as cache-safe after a read/access path. `dcm_modify()` removes entries for the same inode but other sessions and marks the modifying session cache-safe if present. `dcm_init()` builds the free/LRU list. Commented `dcm_test()` and `dcm_getelcount()` provide internal consistency diagnostics when enabled.

Control flow: a client open asks `dcm_open(inode, sessionid)`. If the pair exists, it is moved to the LRU tail and its `cacheok` bit is returned. If missing, the LRU head is recycled, removed from any old inode hash chain, reinitialized for the new pair with `cacheok=0`, and inserted into the new inode hash. Read/access paths call `dcm_access()` to set `cacheok=1` for a known pair. Write/modify paths call `dcm_modify()`, which scans the inode bucket, removes all entries for other sessions by moving them to the LRU head and marking them empty, and sets the same-session entry cache-ok.

State/persistence: all state is static process memory: a 500000-entry table, a 250000-bucket inode hash, and LRU head/tail indexes. There is no disk persistence, metadata integration, reload hook, or dynamic sizing. Empty entries have `inode=0`, but still participate in the LRU list so they can be recycled.

Dependencies/integration: includes only standard integer/stdio headers in this file and exposes its API through `datacachemgr.h`. `matoclserv.c` calls `dcm_modify()` around write/truncate-changing operations and `dcm_access()` after read chunk access; session ids come from the sessions subsystem.

Risks/test signals: `sessionid` is a 31-bit bitfield, so ids above `0x7fffffff` would be truncated. `inode=0` is reserved as empty; callers should not pass zero as a real inode. The code assumes `dcm_init()` has built a non-empty LRU list before any operation. LRU splice operations duplicate logic and are sensitive to head/tail edge cases. Tests should exercise first open/access/open cache hits, cross-session modify invalidation, same-session modify preserving cache-ok, LRU replacement of non-empty entries, hash-chain removal with head/middle/tail nodes, capacity pressure, and the commented consistency checker if re-enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/moosefs/mfsmaster/datacachemgr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/moosefs/mfsmaster/datacachemgr.h -->
# sources/distributed-fs/moosefs/mfsmaster/datacachemgr.h

Purpose: declares the master data-cache hint manager API. It gives client-service code a small interface to decide when session-local cached file data can be reused and when inode modifications should invalidate other sessions' cached data.

Important APIs/types/functions: `dcm_open(inode, sessionid)` returns an integer cache-ok decision and ensures the pair is represented in the LRU table. `dcm_access(inode, sessionid)` marks the pair as safe after access. `dcm_modify(inode, sessionid)` invalidates other sessions for the inode and records the modifying session. `dcm_init()` initializes static manager state.

Control flow: call order is normally initialize, open check, access mark after successful read-like use, and modify notification before or during write-like operations. The API is intentionally fire-and-forget for `access` and `modify`; only `open` returns a decision.

State/persistence: the header exposes no state and no persistence hooks. The implementation is purely in-memory, so all cache hints reset on master restart.

Dependencies/integration: only depends on fixed-width integer types. It integrates with `matoclserv.c` and the session subsystem through the `sessionid` values passed by callers.

Risks/test signals: consumers must call `dcm_modify()` on every operation that can make another client's cached file data stale; missing a call is a coherency risk. Tests should verify that all write/truncate/chunk-changing paths in client service code notify this API and that startup calls `dcm_init()` before first use.
<!-- END_FILE_RESEARCH: sources/distributed-fs/moosefs/mfsmaster/datacachemgr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/moosefs/mfsmaster/exports.c -->
# sources/distributed-fs/moosefs/mfsmaster/exports.c

Purpose: implements MooseFS master export authorization. It parses `mfsexports.cfg`, stores export records, authenticates client sessions by IP/version/path/password, computes an export checksum for session invalidation/visibility, and serializes export records for management clients.

Important APIs/types/functions: `struct exports` stores path, IP range, minimum client version, password digest, flags (`alldirs`, `needpassword`, `meta`, `rootredefined`), session flags, umask, storage-class groups, trash-retention bounds, uid/gid mappings, disabled command bits, and list linkage. `exports_entry_checksum()` combines packed record fields, CRC32, and murmur3. `exports_info_size()` and `exports_info_data()` emit protocol-version-dependent export descriptions. `exports_check()` performs matching and password verification. Parser helpers cover token splitting, network ranges, storage-class groups, deprecated goals, umask, versions, uid/gid names, disabled commands, and option lists. `exports_loadexports()`, `exports_reload()`, `exports_term()`, and `exports_init()` manage file lifecycle.

Control flow: initialization resolves `EXPORTS_FILENAME`, including fallback from the newer `ETC_PATH/mfs/mfsexports.cfg` to the older `ETC_PATH/mfsexports.cfg`, then loads records. Loading reads each trimmed line into a reusable `exports` allocation. `DEFAULTS` lines update a copied default record; normal lines parse IP/network, path or meta `.`, options, uid/gid mapping side effects, and path normalization without leading/trailing slashes. A fully read file replaces the active list and recomputes `exports_csum`; file-open or read errors preserve existing exports when possible. Session authorization normalizes the requested path, scans every record, checks IP/version/meta/path/alldirs, optionally verifies MD5 challenge response, and chooses among all matches by preferring read-write, unrestricted root, admin, password-protected, and more-specific path records.

State/persistence: active state is a singly linked `exports_records` list, a 64-bit `exports_csum`, and heap-owned `ExportsFileName`. Export configuration is external text, not MooseFS metadata; reload replaces in-memory state only after a successful parse/read. Passwords are stored as MD5 digests in memory. `exports_checksum()` lets session code detect export changes when creating or changing sessions.

Dependencies/integration: depends on `MFSCommunication.h` for session flags, export group counts, status codes, and disabled-operation bits; `md5` for password challenge/digest handling; `datapack`, `crc`, and `hashfn` for serialization/checksum; `cfg` and `main` for config/destructor lifecycle; `mfslog`/`massert`; libc passwd/group lookup; and `timeparser` for retention options. `matoclserv.c` calls `exports_check()` for FUSE and metadata session setup, `exports_info_*()` for admin export listings, and passes `exports_checksum()` into session creation/change.

Risks/test signals: matching is not first-match-wins, so overlapping rules can grant more privilege than an operator expects according to the hard-coded preference order. `exports_parseuidgid()` resolves numeric uid without explicit gid through the local passwd database, making config validity host-dependent. Plain `password=` stores MD5 of the provided string; `md5pass=` accepts raw digests; both rely on MD5 challenge response rather than stronger authentication. `exports_parseumask()` does not reject trailing characters after four octal chars. Default records are shallow-copied; defaults normally have no owned path, but this is worth guarding if extended. Tests should cover overlapping export precedence, password missing/bad/good outcomes, meta export behavior, `DEFAULTS` inheritance, maproot/mapall uid/gid by name and number, host-dependent lookup failures, deprecated goal/trash options, disable command parsing, minversion filtering, path normalization, fallback filename selection, failed reload preserving active exports, checksum changes, and protocol-version export-info sizes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/moosefs/mfsmaster/exports.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/moosefs/mfsmaster/exports.h -->
# sources/distributed-fs/moosefs/mfsmaster/exports.h

Purpose: public interface for MooseFS export authorization and export-info serialization. It is used by client-session handling and administrative listing paths in the master.

Important APIs/types/functions: `exports_info_size(versmode)` computes the byte size needed for serialized export records; `exports_info_data(versmode, buff)` writes those records. `exports_check()` authorizes a client IP, protocol version, path or meta request, optional password challenge/response, and returns session flags, umask, uid/gid mappings, storage-class groups, trash-retention bounds, and disabled operation bits. `exports_reload()` reloads configuration. `exports_checksum()` returns the current aggregate checksum. `exports_init()` initializes and validates that at least one export exists.

Control flow: startup calls `exports_init()`. Client session setup calls `exports_check()` with a real path for filesystem sessions or `NULL` path for metadata sessions; password-protected exports require the caller to supply the challenge and response buffers. Administrative clients first call `exports_info_size()` to allocate a packet and then `exports_info_data()` to fill it. Reload is coordinated elsewhere, with this header exposing the reload hook.

State/persistence: the header exposes only in-memory operations. The implementation reads an external config file and keeps active records in process memory. `exports_checksum()` is the state-change signal passed to session management.

Dependencies/integration: includes fixed-width integer types and semantically depends on MooseFS protocol status codes, session flags, export groups, and disabled-operation masks. Main consumers are `matoclserv.c` and the sessions subsystem.

Risks/test signals: callers must provide valid output pointers to `exports_check()`; the implementation writes all result fields on success. Callers must also respect `MFS_ERROR_NOPASSWORD` and `MFS_ERROR_BADPASSWORD` distinctly so password negotiation works. Tests should cover allocation using `exports_info_size()` followed by `exports_info_data()`, meta versus filesystem checks, checksum propagation into session changes, and reload-triggered session invalidation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/moosefs/mfsmaster/exports.h -->
