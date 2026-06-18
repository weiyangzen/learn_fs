# Research: subset-b-007689

Grouped MooseFS master research report. Each file section preserves the source path in its title and is wrapped for deterministic reconciliation into source-tree-aligned per-file documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/moosefs/mfsmaster/matocsserv.c -->
## sources/distributed-fs/moosefs/mfsmaster/matocsserv.c

Purpose: implements the master-to-chunkserver service. It accepts chunkserver TCP connections, performs registration and optional AUTH_CODE challenge/response, tracks server capacity/load/labels, exposes server-selection helpers for the chunk manager, sends chunk operation commands, receives operation status and chunk inventory updates, and integrates the socket service into the main poll/keepalive/reload/destruct loops.

Important APIs and types: the central private type is `matocsserventry`, which owns socket state, packet queues, server identity, space counters, label data, current replication/delete counters, cumulative reason counters, registration state, timeout state, and the `csdb` connection pointer. `out_packetstruct` and `in_packetstruct` are variable-size queued packet nodes. The operation DB uses `opsrv` in `ophash` to deduplicate and count deletes; the replication DB uses `repdst`/`repsrc` in `rephash` to count source reads and destination writes. Public functions include server discovery and scheduling helpers (`matocsserv_getservers_wrandom`, `matocsserv_getservers_lessrepl`, `matocsserv_get_server_groups`, `matocsserv_recalculate_storagemode_scounts`), status accessors (`matocsserv_get_csdata`, `matocsserv_getservdata`, `matocsserv_gettotalspace`, `matocsserv_receiving_chunks_state`), and command senders for create/delete/replicate/set-version/duplicate/truncate/local-split/chunkop.

Control flow: `matocsserv_init` reads config, opens the listen socket, initializes replication state, and registers callbacks with `main`. `matocsserv_desc` contributes the listen socket and active chunkserver sockets to the master poll set. `matocsserv_serve` accepts new sockets, initializes `matocsserventry`, reads available data, parses queued packets for up to about 10 ms per iteration, writes queued output, emits NOP keepalives, enforces read timeouts, and runs the disconnection cleanup loop. `matocsserv_gotpacket` dispatches protocol messages such as `CSTOMA_REGISTER`, `CSTOMA_SPACE`, `CSTOMA_CURRENT_LOAD`, chunk status, chunk damage/loss/new reports, labels, and operation completion statuses. `matocsserv_register` is a multi-stage protocol: begin registers identity/space/version and allocates a csid via `csdb`/`chunks`; chunks packets stream inventory; end marks the server registered; disconnect requests graceful shutdown.

State and persistence behavior: this file keeps only live runtime state; durable chunk topology is updated through `chunk_server_has_chunk`, `chunk_lost`, `chunk_damaged`, `chunk_got_*_status`, and `chunk_server_disconnected`, and server identity persistence flows through `csdb`. In-memory counters gate scheduling and are reset or rotated periodically. Metadata save children call `matocsserv_close_lsock` so inherited listen sockets do not leak across fork. No `bio` metadata section is written here directly.

Dependencies and integration points: depends heavily on `MFSCommunication` protocol IDs, `datapack` encoding, `sockets`, `cfg`, `main`, `chunks`, `csdb`, `storageclass`, `labelparser`, `multilan`, `md5`, `random`, and `mfslog`. The chunk manager calls exported senders and server-selection helpers to create, replicate, rebalance, and delete chunks. `matoclserv`/status paths use space and server data accessors. `metadata.c` calls close/no-pending helpers during save/shutdown.

Risks: protocol length mistakes intentionally kill connections, so compatibility changes must update every size check. Many counters are manually balanced in begin/end/disconnect paths; missing an end path can permanently throttle replication/deletion scheduling. The `COMBINE_CHUNKID_AND_ECID` encoding reserves the high byte of chunk id for EC id, so callers must not pass unmasked full-width ids. Weighted round-robin uses static buffers and process-global state, so it assumes single-threaded master execution. Registration rejects loopback chunkservers and too-old EC-incompatible versions; test mixed-version clusters carefully.

Test signals: exercise chunkserver registration phases with and without AUTH_CODE, bad packet sizes, timeout forcing, server label updates, space updates, lost/new/damaged chunk reports, and every chunk operation status. Integration tests should verify counter decrements after success, failure, and disconnect; scheduling output under overloaded/maintenance/no-space states; multi-LAN remapping in `matocsserv_get_csdata`; and metadata-save fork behavior closing listen sockets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/moosefs/mfsmaster/matocsserv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/moosefs/mfsmaster/matocsserv.h -->
## sources/distributed-fs/moosefs/mfsmaster/matocsserv.h

Purpose: declares the public contract for the master-to-chunkserver service and exposes reason enums shared with chunk scheduling, logging, and operation accounting. It intentionally hides `matocsserventry`; callers pass opaque `void *` server handles obtained from chunkserver database/chunk structures.

Important APIs and types: `REPL_*` reasons classify copy, erasure-coded replication, local split, join, and recover operations; `OP_*` reasons classify generic/delete-invalid/delete-not-used/delete-overgoal operations. `REPL_REASONS_STRINGS` and `OP_REASONS_STRINGS` keep human-readable order coupled to the enums. Exported APIs cover label matching, server counts, replication-capable server lists, weighted random creation server selection, replication-limit grouping, global space access, per-server data access, per-server counters, command senders, chunk status broadcast, validity/disconnection notification, shutdown/drain helpers, and initialization.

Control flow and integration: `chunks.c` is the primary consumer. It asks this module for candidate servers, opaque server properties, and rate counters, then invokes senders to enqueue protocol commands. `metadata.c` uses `matocsserv_close_lsock`, `matocsserv_no_more_pending_jobs`, and shutdown-related functions. `storageclass` integration enters through `storagemode` recounting and label expression matching.

State and persistence behavior: the header itself owns no state, but its APIs expose runtime scheduling state and bridge chunkserver state into durable metadata subsystems. Reason enum order is effectively part of diagnostic output and counter interpretation.

Dependencies: includes `chunks.h` for `MAXCSCOUNT` and `storageclass.h` for `storagemode`; also uses fixed-width integer types and `SCLASS_EXPR_MAX_SIZE` via the storage class header.

Risks: because server handles are opaque `void *`, type safety depends on callers only passing live `matocsserventry` pointers. Enum/string list drift would corrupt diagnostics and reason counters. Adding a new command sender requires updating both this header and the protocol dispatch/status handling in the implementation.

Test signals: compile coverage from `chunks.c` and metadata shutdown paths is necessary. Behavioral tests should validate that each exported sender queues a protocol command and that each reason enum maps to the intended log label.
<!-- END_FILE_RESEARCH: sources/distributed-fs/moosefs/mfsmaster/matocsserv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/moosefs/mfsmaster/matomlserv.c -->
## sources/distributed-fs/moosefs/mfsmaster/matomlserv.c

Purpose: implements the master control service for metaloggers and supervisors. Metaloggers receive live and historical changelog records so they can mirror metadata state. Supervisors can request master state and trigger metadata storage. The same socket framework also serves metadata/session/changelog file download requests.

Important APIs and types: `matomlserventry` owns socket queues, timeout/version/client type, metalogger `logstate`, next historical log version, peer IP string, and open file descriptors for downloads. `clienttype` distinguishes unknown, metalogger, and supervisor clients; `logstate` distinguishes no log stream, delayed catch-up, and live sync. Public APIs include metalogger list sizing/data, `matomlserv_get_min_version`, changelog broadcast functions, shutdown/drain helpers, port accessors, listen-socket close, and init.

Control flow: `matomlserv_init` reads config, opens the `MATOML` listen socket, and registers poll, keepalive, reload, destruct, and timeout-broadcast callbacks. `matomlserv_serve` accepts clients, reads packets, dispatches via `matomlserv_gotpacket`, sends queued output, emits NOPs for registered metaloggers, enforces timeouts, and incrementally drains old changelogs for delayed metaloggers. Registration supports simple metalogger protocol, advanced metalogger protocol with requested minimum version and old-change replay, and supervisor protocol that replies with `MATOAN_STATE`. Downloads start by selecting `metadata.mfs.back`, changelog files, or `sessions.mfs`; requests return offset, length, data, and CRC.

State and persistence behavior: this file does not mutate metadata except through supervisor `ANTOMA_STORE_METADATA`, which calls `meta_do_store_metadata`. It reads persisted metadata/changelog/session files for download. Live changelog persistence is owned by `changelog.c`; this module broadcasts log strings and rotates to connected metaloggers, and `matomlserv_get_min_version` tells changelog retention how far delayed clients still need history.

Dependencies and integration points: uses `MFSCommunication` protocol IDs, `datapack`, `changelog`, `metadata`, `crc`, `cfg`, `main`, `sockets`, and `mfslog`. `changelog.c` calls `matomlserv_broadcast_logstring` and `matomlserv_broadcast_logrotate`. `metadata.c` closes the listen socket in saver children. Supervisor CLI code reaches this service through the `mastersupervisor` client library.

Risks: old-change catch-up is bounded by `OLD_CHANGES_GROUP_COUNT`; delayed clients must continue draining only when output queues empty, so write backpressure can keep old changelogs retained. `matomlserv_desc` sets `events` to `POLLIN` even when output exists, relying on later write attempts when output is queued; this is a subtle poll behavior worth regression testing. File download paths are relative to the master's data directory and kill the connection on bad offsets/lengths/read failures. There is no AUTH_CODE handling in this file.

Test signals: cover simple and advanced metalogger registration, delayed-to-sync transitions, changelog retention minimum version, supervisor registration state payloads across version modes, store request authorization by client type, metadata/changelog/session downloads with CRC, forced timeout broadcast, reload listen socket replacement, and malformed packet size handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/moosefs/mfsmaster/matomlserv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/moosefs/mfsmaster/matomlserv.h -->
## sources/distributed-fs/moosefs/mfsmaster/matomlserv.h

Purpose: declares the externally visible master-to-metalogger/supervisor service functions. It hides all connection internals and exposes only list, changelog, lifecycle, port, and initialization hooks needed by adjacent master modules.

Important APIs: `matomlserv_mloglist_size` and `matomlserv_mloglist_data` serialize connected metalogger versions/IPs for status clients. `matomlserv_get_min_version` feeds changelog retention. `matomlserv_broadcast_logstring` and `matomlserv_broadcast_logrotate` push live metadata changes and log rotation markers. Lifecycle APIs include `matomlserv_no_more_pending_jobs`, `matomlserv_disconnect_all`, `matomlserv_close_lsock`, and `matomlserv_init`; port helpers return the current control port.

Control flow and integration: `changelog.c` broadcasts through this header, `matoclserv`/status code can list metaloggers, and `metadata.c` uses close/drain helpers during forked store and shutdown. `main` calls the registered callbacks set up by `matomlserv_init`, not declared here directly.

State and persistence behavior: the header owns no state but provides access to runtime connection state and changelog retention requirements. Persistence is indirect: broadcasts mirror changelog content, and supervisor calls can trigger metadata storage in the implementation.

Dependencies: only fixed-width integer types are exposed; protocol structures remain private.

Risks: callers depend on `matomlserv_get_min_version` to avoid deleting changelog history still needed by delayed metaloggers. Misusing broadcast calls before initialization or after disconnect-all would silently drop mirror updates.

Test signals: compile and integration tests should verify changelog broadcasts reach registered metaloggers, delayed metaloggers influence minimum version, and shutdown drains pending output before process exit.
<!-- END_FILE_RESEARCH: sources/distributed-fs/moosefs/mfsmaster/matomlserv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/moosefs/mfsmaster/merger.c -->
## sources/distributed-fs/moosefs/mfsmaster/merger.c

Purpose: merges multiple textual changelog files by ascending change id and applies them through `restore_file`. It is used during automatic metadata restoration to replay changelog fragments after loading the best available metadata snapshot.

Important APIs and types: `hentry` stores a changelog file handle, shared filename pointer, line buffer, parsed line pointer, and next change id. The global heap orders entries by `nextid`. `merger_start` opens all input files, initializes heap entries, records maximum allowed id hole and progress bounds. `merger_loop` repeatedly applies the lowest-id change and advances or removes that file. Helper functions implement heap up/down, entry reading, entry deletion, and entry creation.

Control flow: each file's first valid line is read by `merger_nextentry`; invalid or empty files are dropped. The heap root is applied with `restore_file(filename, id, ptr, verblevel)`. After each successful restore, the same file advances one line; if it reaches EOF or invalid data, it is removed and the heap is rebalanced. Progress is printed periodically for ids divisible by 2497 when first/last bounds are known.

State and persistence behavior: no durable state is written directly here; persistence mutation occurs through `restore_file`, which replays metadata changelog operations into in-memory structures. The module owns file handles and buffers during a restore run and frees them on completion or error.

Dependencies and integration points: depends on `restore.h` for changelog application, `sharedpointer` for filename ownership, `mfslog` for warnings, and `clocks` for progress ETA. `metadata.c` calls it from `meta_loadall` after selecting metadata and changelog files.

Risks: `maxidhole` rejects non-monotonic or unexpectedly distant ids per file as garbage, which protects restore but may discard a damaged tail. `merger_delete_entry` operates on `heap[heapsize]` after callers decrement/swap; that convention must be preserved. Progress ETA divides by `(heap[0].nextid - firstlv)` only after current id is above the first version; the code handles below-first separately.

Test signals: test merging two or more interleaved changelogs, duplicate/out-of-order ids, large id holes, unreadable files, restore errors, and progress-bounds behavior. Use fake `restore_file` in unit tests to assert exact application order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/moosefs/mfsmaster/merger.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/moosefs/mfsmaster/merger.h -->
## sources/distributed-fs/moosefs/mfsmaster/merger.h

Purpose: exposes the small changelog-merging API used by metadata restore.

Important APIs: `merger_start(files, filenames, maxhole, minlv, maxlv)` initializes a heap over changelog files, filters unusable files, and records allowed id gaps and progress boundaries. `merger_loop(verblevel)` applies all changes in sorted order through the restore subsystem and returns restore status.

Control flow and integration: callers initialize once, then run the loop. In this tree, `metadata.c` is the main caller during automatic restore after choosing a metadata snapshot and gathering changelog files.

State and persistence behavior: implementation state is process-global between start and loop. It writes no metadata itself; it drives replay into in-memory metadata through `restore_file`.

Dependencies: only fixed-width integer types are exposed.

Risks: the API is not reentrant because heap state is global. Callers must keep filename strings valid through `merger_start`; the implementation duplicates accepted filenames through `sharedpointer` internally.

Test signals: compile users, then verify restore order and error propagation with controlled changelog inputs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/moosefs/mfsmaster/merger.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/moosefs/mfsmaster/metadata.c -->
## sources/distributed-fs/moosefs/mfsmaster/metadata.c

Purpose: is the master metadata lifecycle hub. It initializes all metadata-owning subsystems, loads metadata from disk, restores from backups/changelogs, stores metadata snapshots foreground or background, tracks metadata version/id/checksum/status, manages periodic saves and changelog rotation, and performs cleanup on shutdown.

Important APIs and types: global state includes `metaversion`, `metaid`, restore flags, last store time/status/version/checksum, save configuration, background saver pid/mode, and a linked list of `chlog_keep` records that temporarily retain changelog versions while metadata is being sent or saved. Core APIs include `meta_store`, `meta_load`, `meta_loadall`, `meta_storeall`, `meta_restore`, `meta_init`, `meta_term`, `meta_version_inc`, `meta_version`, `meta_get_id`, `meta_set_id`, `meta_mr_setmetaid`, `meta_info`, and flag setters for ignore/autorestore/empty-start/verbosity.

Control flow: `meta_init` initializes dictionaries, storage classes, patterns, filesystem, chunks, xattrs, ACLs, locks, csdb, sessions, and open files; then loads metadata unless empty-start is requested; registers reload/info/timer/may-exit/destruct callbacks; renumerates edges; and ensures a meta id exists. `meta_store` writes a signature-level metadata body with header version/id and ordered sections: sessions, storage classes, patterns, nodes, edges, free list, quota, xattrs, ACLs, open files, flock locks, POSIX locks, csdb, chunks, and EOF. `meta_load` reads old or sectioned formats, verifies section versions against local store functions, calls subsystem load functions, handles unknown/short sections according to `ignoreflag`, and finishes with filesystem consistency checks.

State and persistence behavior: persistent files include `metadata.mfs`, `metadata.mfs.back`, rotated backups, `metadata.mfs.back.tmp`, `metadata.crc`, changelog files, and emergency metadata locations. `meta_storeall` optionally forks a saver, locks the temp file, closes listen sockets in the child, writes metadata plus CRC, rotates backups, renames temp to back, unlinks old current metadata, and records store status. Foreground shutdown rotates changelog, stores, renames `metadata.mfs.back` to `metadata.mfs`, then cleans in-memory subsystems. `meta_loadall` validates current/back/metalogger/emergency metadata, optionally selects the best snapshot, applies changelogs through `merger`, handles backup freshness/id conflicts, and removes stale temp files.

Dependencies and integration points: integrates almost every master metadata subsystem: `sessions`, `dictionary`, `xattr`, `posixacl`, `flocklocks`, `posixlocks`, `openfiles`, `csdb`, `storageclass`, `patterns`, `chunks`, `filesystem`, `changelog`, `merger`, `matoclserv`, `matocsserv`, and `matomlserv`. It is registered with `main` for periodic saves, reload, shutdown, exit gating, and info dumps. `matomlserv` supervisors call `meta_do_store_metadata`; replication replay calls `meta_mr_setmetaid`; many subsystems call `meta_version_inc`.

Risks: section ordering is part of the metadata contract; comments note dependencies such as storage classes/patterns before nodes and locks after open files. Background save uses `fork`, temp files, locks, and emergency fallbacks, so process and filesystem error paths must be handled carefully. `meta_mr_setmetaid` appears to call `fs_set_root_times(metaid>>32)` while `metaid` is still zero in the zero-id branch, which is worth reviewing against intended replay semantics. `meta_reload` computes `MetaSaveOffset = MetaSaveOffset % 60*24`, which by C precedence is `(MetaSaveOffset % 60) * 24`, likely not modulo 1440. Restore with `ignoreflag` can drop unknown/corrupt sections and continue, trading data loss for availability.

Test signals: test new metadata creation, current metadata load, backup freshness/id mismatch rejections, autorestore best-file selection, changelog replay ordering, unsupported section versions, unknown sections with and without ignore, background and foreground saves, emergency save fallback, CRC processing, periodic save scheduling with offsets, shutdown retry behavior, and metadata id generation/replay.
<!-- END_FILE_RESEARCH: sources/distributed-fs/moosefs/mfsmaster/metadata.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/moosefs/mfsmaster/metadata.h -->
## sources/distributed-fs/moosefs/mfsmaster/metadata.h

Purpose: declares the master metadata lifecycle API consumed by filesystems, changelog replay, supervisors, status handlers, and process startup/shutdown.

Important APIs: version and id management (`meta_version_inc`, `meta_version`, `meta_get_id`, `meta_set_id`, `meta_mr_setmetaid`), lifecycle (`meta_init`, `meta_cleanup`, `meta_restore`), runtime flags (`meta_setignoreflag`, `meta_allowautorestore`, `meta_emptystart`, `meta_incverboselevel`), explicit storage (`meta_do_store_metadata`), store/download status (`meta_download_status`, `meta_info`), and changelog retention floor (`meta_chlog_keep_version`).

Control flow and integration: startup code calls flag setters before `meta_init`; normal metadata mutations call `meta_version_inc`; replication replay calls the `mr` API; supervisors trigger explicit store; status code calls `meta_info`; changelog retention consults `meta_chlog_keep_version`.

State and persistence behavior: the header exposes controls for the persistent metadata file set managed in `metadata.c` but stores nothing itself. Return codes follow MooseFS status/error conventions for replay APIs.

Dependencies: includes `stdio.h` and fixed-width integers. It intentionally hides the metadata section list and subsystem load/store functions.

Risks: `meta_version_inc` increments global metadata version and should only be used on changes that are or will be changelogged/replayed. `meta_setignoreflag` and autorestore are powerful recovery switches that can allow metadata loss if used casually.

Test signals: compile coverage across startup, restore tools, changelog replay, and supervisor paths. Regression tests should assert metadata version/id updates and status reporting around save, download, and replay operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/moosefs/mfsmaster/metadata.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/moosefs/mfsmaster/mfsmetarestore -->
## sources/distributed-fs/moosefs/mfsmaster/mfsmetarestore

Purpose: shell compatibility stub for the removed `mfsmetarestore` command.

Important behavior: the script has a `/bin/sh` shebang and prints one message: `mfsmetarestore has been removed in version 1.7, use mfsmaster -a instead`.

Control flow: there is no option parsing or branching; every invocation emits the message and exits with the shell's status for `echo`, normally zero.

State and persistence behavior: no state is read or written. It does not invoke `mfsmaster -a`; it only informs the user.

Dependencies and integration points: depends only on POSIX shell and `echo`. Packaging or install rules may still ship it to preserve user-facing command compatibility.

Risks: returning success may confuse automation that expects a restore attempt. If scripts parse stderr, note the message is written to stdout.

Test signals: execute the script and assert exact message text and expected zero exit status, or deliberately change exit behavior if product policy requires failure for removed commands.
<!-- END_FILE_RESEARCH: sources/distributed-fs/moosefs/mfsmaster/mfsmetarestore -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/moosefs/mfsmaster/mfssupervisor.c -->
## sources/distributed-fs/moosefs/mfsmaster/mfssupervisor.c

Purpose: command-line supervisor client for the MooseFS master control port. It connects to master servers, optionally requests forced metadata storage, and supports verbose/debug output.

Important APIs and types: no custom types. `usage` prints command help and exits. `main` parses `-h`, `-v`, `-x`, `-s`, `-H`, `-P`, and `-B`, initializes string error handling, fills defaults from `DEFAULT_MASTERNAME` and `DEFAULT_MASTER_CONTROL_PORT`, then calls `msupervisor_simple(masterhost, masterport, bindhost, debug, store)`.

Control flow: options allocate replacement strings with `strdup` and free old values if repeated. Help/version exit early via a shared cleanup label. After defaulting missing host/port/bind values, the result of `msupervisor_simple` becomes the process exit code.

State and persistence behavior: no persistent state is stored locally. With `-s`, the remote master may perform metadata storage through the supervisor protocol handled by `matomlserv.c`.

Dependencies and integration points: depends on `mastersupervisor.h` for client protocol, `strerr` initialization, `idstr` for version/default constants, libc `getopt`, and heap allocation. It integrates operationally with the `MATOML` master control service.

Risks: all host/port/bind inputs are trusted strings passed to the supervisor library; validation belongs there. `usage` exits with status 1 even for `-h`, but `main` calls it directly for `-h`, so the later `res=0` path is unreachable in that case.

Test signals: CLI tests should cover help/version, repeated options, default values, bind address handling, `-s` store flag propagation, and connection failures from `msupervisor_simple`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/moosefs/mfsmaster/mfssupervisor.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/moosefs/mfsmaster/missinglog.c -->
## sources/distributed-fs/moosefs/mfsmaster/missinglog.c

Purpose: keeps a bounded, deduplicated, two-window log of missing chunk references for reporting. It records `(chunkid, inode, index, type)` tuples, swaps the active set into a previous set, and serializes the previous set to status clients.

Important APIs and types: `mlogentry` stores one tuple. Static globals hold active and previous open-addressed hash tables, table sizes, element counts, capacity, and a `blocked` flag. `missing_log_insert` deduplicates and inserts into the active hash. `missing_log_swap` rotates active to previous and clears a new active table. `missing_log_getdata` either returns serialized size after pruning entries no longer missing, or writes tuples to a buffer. `missing_log_reload` reads `MISSING_LOG_CAPACITY`; `missing_log_init` initializes and registers reload.

Control flow: insertion returns early when blocked, full, or chunk id zero. The hash and displacement mix inode/index/chunk id and use odd displacement for probing. Reload reallocates the active table when capacity changes and blocks one cycle after a live resize to avoid mixing old/new windows. Size calculation also calls `chunk_remove_from_missing_log` to drop entries already resolved.

State and persistence behavior: state is memory-only and intentionally lossy/bounded. It is not serialized in metadata. Reload can clear active data when capacity changes.

Dependencies and integration points: depends on `cfg`, `main` reload registration, `datapack` serialization, `chunks` for pruning, and `mfslog`. Status/reporting code can call `missing_log_getdata`; chunk/filesystem paths insert missing references.

Risks: the table has no dynamic growth beyond configured capacity; once full, new events are dropped. `mloghashprev` is initially NULL/size zero, so consumers should tolerate empty previous windows until the first swap. The open addressing code assumes `mloghashsize` is a power of two and nonzero after reload.

Test signals: test deduplication, capacity bounds/clamping, resize blocking, swap behavior, size vs data modes, optional `type` byte mode, and pruning via a fake `chunk_remove_from_missing_log`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/moosefs/mfsmaster/missinglog.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/moosefs/mfsmaster/missinglog.h -->
## sources/distributed-fs/moosefs/mfsmaster/missinglog.h

Purpose: declares the missing chunk log API for insertion, window rotation, serialization, and initialization.

Important APIs: `missing_log_insert` records a missing chunk reference; `missing_log_swap` rotates active entries into the reportable previous window; `missing_log_getdata` returns size or writes packed records depending on whether the buffer is NULL; `missing_log_init` initializes tables and reload handling.

Control flow and integration: chunk/filesystem code inserts events, a periodic task is expected to swap windows, and status code reads the previous window for client responses.

State and persistence behavior: implementation state is volatile and bounded by `MISSING_LOG_CAPACITY`; the header exposes no persistence controls.

Dependencies: only fixed-width integer types.

Risks: callers must pass nonzero chunk ids and correctly size buffers using the NULL-buffer size query before serialization. Mode controls record width, so client/server protocol must agree.

Test signals: compile coverage and serialization-size agreement tests for mode 0 and mode 1.
<!-- END_FILE_RESEARCH: sources/distributed-fs/moosefs/mfsmaster/missinglog.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/moosefs/mfsmaster/multilan.c -->
## sources/distributed-fs/moosefs/mfsmaster/multilan.c

Purpose: maps chunkserver addresses to client-appropriate LAN addresses in multi-homed deployments. It supports explicit source/client mappings through `csipmap` and class-based address rewriting through `MULTILAN_BITS`/`MULTILAN_CLASSES`.

Important APIs and types: global config state includes `MultiLanMask`, number of classes, and `MultiLanClassTab`. `multilan_map(servip, clientip)` first tries `csipmap_map`, then rewrites the network bits of `servip` to match `clientip` if both belong to configured classes. `multilan_match(servip, iptab, iptablen)` chooses a matching alternate IP from a server IP table. `multilan_parse_netlist` parses class lists. `multilan_reload` loads config and the optional IP map file. `multilan_init` initializes `csipmap` and registers reload/destruct.

Control flow: reload enables class rewriting only if both `MULTILAN_BITS` and `MULTILAN_CLASSES` are defined and valid. Parse errors log warnings and preserve/clear state according to the branch. If class config is absent, class mapping is disabled. The explicit IP map file is loaded on every reload from `MULTILAN_IPMAP_FILENAME` or default path.

State and persistence behavior: all state is in memory and derived from config files. No metadata is written. `multilan_term` frees class state and terminates `csipmap`.

Dependencies and integration points: depends on `cfg`, `main`, `mfslog`, `massert`, `csipmap`, and `MFSCommunication` defaults. `matocsserv_get_csdata` calls `multilan_map` before returning chunkserver addresses to clients.

Risks: address parsing is permissive about shortened classes but rejects garbage bits outside the common mask. Class-based rewrite can create unreachable addresses if LANs are not symmetric. `multilan_match` returns the original address when more than one candidate matches, treating ambiguity as an error case.

Test signals: test explicit map precedence, no-client-ip fallback, absent config, invalid bit counts/classes, class rewrite when both networks are known, no rewrite when either side is unknown, ambiguous `multilan_match`, and reload/destruct memory behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/moosefs/mfsmaster/multilan.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/moosefs/mfsmaster/multilan.h -->
## sources/distributed-fs/moosefs/mfsmaster/multilan.h

Purpose: declares the multi-LAN address mapping interface used by master services when returning chunkserver endpoints.

Important APIs: `multilan_map` maps one server IP for a given client IP; `multilan_match` selects an alternate server IP from a table; `multilan_init` loads config, initializes the explicit map subsystem, and registers reload/destruct hooks.

Control flow and integration: `matocsserv` uses `multilan_map` in its client-facing server data path. Initialization should happen during master startup before clients request chunk locations.

State and persistence behavior: state is runtime config derived from `MULTILAN_*` settings and IP map files; no durable metadata is exposed.

Dependencies: only fixed-width integer types are public.

Risks: consumers must pass IPs in the internal integer byte order expected by the parser and socket helpers. Calling before successful init degrades to unmapped behavior only if globals are zeroed.

Test signals: unit tests for mapping and match selection, plus integration tests for client-visible chunkserver addresses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/moosefs/mfsmaster/multilan.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/moosefs/mfsmaster/openfiles.c -->
## sources/distributed-fs/moosefs/mfsmaster/openfiles.c

Purpose: tracks which sessions have which inodes open. It supports live client open/release synchronization, metadata serialization of open files, restoration/replay operations, lsof-style reporting, and lock cleanup when a file is closed.

Important APIs and types: `ofrelation` links one `(sessionid, inode)` into both session and inode hash chains using next pointers and pointer-to-previous links. Static hash tables index by session and inode. Public APIs include `of_openfile`, `of_sync`, `of_session_removed`, `of_isfileopen`, `of_isfileopened_by_session`, `of_noofopenedfiles`, `of_lsof`, `of_sessions_info_for_inode`, `of_mr_acquire`, `of_mr_release`, `of_store`, `of_load`, `of_cleanup`, and `of_init`.

Control flow: `of_openfile` inserts a relation if absent and writes an `ACQUIRE` changelog. `of_sync` sorts the provided inode list, removes currently tracked opens not present in the list with `RELEASE` changelogs, and adds missing opens with `ACQUIRE` changelogs. Deleting a node calls `flock_file_closed` and `posix_lock_file_closed` before unlinking from both hashes. Metadata replay APIs mutate state without changelogging and increment metadata version. Load reads fixed 8-byte records until a zero/zero terminator, only restoring entries whose sessions still exist.

State and persistence behavior: open file relations are persisted in the `OPEN` metadata section version `0x10`. Live user operations are changelogged, and replay operations increment metadata version. Cleanup frees all relation nodes and clears hash heads.

Dependencies and integration points: depends on `metadata`, `flocklocks`, `posixlocks`, `sessions`, `changelog`, `main`, `datapack`, `bio`, and MooseFS status codes. `metadata.c` stores/loads the section and orders locks after open files because lock cleanup depends on open state.

Risks: `of_sync` mutates and sorts the caller-provided inode array. The static bitmask cache grows but only frees on process exit. Duplicate prevention depends on checking before insert for live paths; replay/load paths assume input consistency. Lock cleanup is coupled to every delete path through `of_delnode`.

Test signals: test acquire/release changelog emission, sync add/remove/no-op behavior, session removal lock cleanup, metadata store/load with missing sessions, lsof sizes/data for all vs one session, replay mismatch errors, and duplicate open prevention.
<!-- END_FILE_RESEARCH: sources/distributed-fs/moosefs/mfsmaster/openfiles.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/moosefs/mfsmaster/openfiles.h -->
## sources/distributed-fs/moosefs/mfsmaster/openfiles.h

Purpose: declares the open-file relation subsystem used by sessions, metadata, lock managers, status handlers, and changelog replay.

Important APIs: live operations (`of_openfile`, `of_sync`, `of_session_removed`), queries (`of_checknode`, `of_isfileopen`, `of_isfileopened_by_session`, `of_noofopenedfiles`, `of_lsof`, `of_sessions_info_for_inode`), replay operations (`of_mr_acquire`, `of_mr_release`), and metadata lifecycle (`of_store`, `of_load`, `of_cleanup`, `of_init`).

Control flow and integration: session/client code records opens; session teardown removes all opens; lock subsystems are notified indirectly on close; metadata stores and restores the `OPEN` section; changelog replay uses `of_mr_*`.

State and persistence behavior: implementation persists open relations through `bio` and updates metadata version during replay mutations.

Dependencies: exposes `bio` in the store/load API and fixed-width integer types.

Risks: callers of `of_sync` should treat the inode array as scratch because it is sorted in place. Buffer sizing for `of_lsof` and `of_sessions_info_for_inode` must use the size-return mode before writing.

Test signals: API-level tests for open tracking, buffer sizes, metadata round trips, and replay mismatch return codes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/moosefs/mfsmaster/openfiles.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/moosefs/mfsmaster/patterns.c -->
## sources/distributed-fs/moosefs/mfsmaster/patterns.c

Purpose: manages automatic file creation patterns that match names and user/group selectors to apply storage class, trash retention, and extended attribute masks. It stores patterns in metadata, exposes admin add/delete/list operations, and provides the runtime matcher used by filesystem creation paths.

Important APIs and types: `pattern` stores compiled `glob`, validity/modified flags, glob name, effective uid/gid filters, priority, operation mask, storage class id, trash retention, and set/clear eattr masks. `patterntab` is a fixed 1024-entry array sorted by validity, descending priority, storage class id, and name; `validpatterns` marks active prefix length. Key functions are `patterns_find_matching`, `patterns_add`, `patterns_delete`, `patterns_mr_add`, `patterns_mr_delete`, `patterns_sclass_delete`, `patterns_list`, `patterns_store`, `patterns_load`, `patterns_cleanup`, and `patterns_init`.

Control flow: add validates nonempty glob and eattr mask consistency, resolves storage class name if requested, rejects duplicates, fills the first free slot, recompiles modified glob entries, sorts, and either changelogs `PATADD` or increments metadata version for replay. Delete marks matching entries invalid, recompiles/sorts, and changelogs or increments metadata version. Matching scans the sorted active prefix and returns the first pattern whose uid/gid filter and glob match. Loading clears existing patterns, reads records until a sentinel, supports old version `0x10` without `clreattr`, and optionally skips excess entries under `ignoreflag`.

State and persistence behavior: patterns are persisted in metadata section `PATT`, version `0x11`. Runtime compiled glob objects are rebuilt after load/add/delete and freed on invalidation. Admin operations are changelogged; replay operations update metadata version.

Dependencies and integration points: depends on `globengine`, `storageclass`, `metadata`, `changelog`, `main`, `bio`, `datapack`, `mfslog`, and MooseFS status/error constants. `metadata.c` loads storage classes before patterns, and filesystem creation code can query `patterns_find_matching`.

Risks: fixed capacity returns `MFS_ERROR_PATLIMITREACHED`. Sorting means table index is not stable across changes. Glob compilation happens for every modified valid pattern during `patterns_have_changed`; invalid patterns free their glob. `patterns_sclass_delete` silently removes patterns referencing a deleted storage class, which can change create behavior.

Test signals: test duplicate detection, capacity limit, eattr validation, storage class lookup, priority ordering, uid/gid filtering, glob matching, changelog vs replay paths, section version load compatibility, too-many-pattern handling with and without ignore, list buffer sizing, and storage-class deletion side effects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/moosefs/mfsmaster/patterns.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/moosefs/mfsmaster/patterns.h -->
## sources/distributed-fs/moosefs/mfsmaster/patterns.h

Purpose: declares the creation-pattern subsystem interface for matching, administration, replay, metadata persistence, and cleanup.

Important APIs: `patterns_find_matching` returns the operation mask and selected storage/trash/eattr outputs for a filename and credential set. `patterns_add`/`patterns_delete` are live admin operations with changelog side effects. `patterns_mr_add`/`patterns_mr_delete` are metadata-replay variants. `patterns_sclass_delete` removes patterns tied to a storage class. `patterns_list` serializes active patterns. `patterns_store`, `patterns_load`, `patterns_cleanup`, and `patterns_init` handle metadata lifecycle.

Control flow and integration: filesystem creation paths query matching; admin/status paths add/delete/list; metadata save/load uses the `bio` functions; changelog replay uses `mr` variants; storage class deletion calls `patterns_sclass_delete`.

State and persistence behavior: implementation persists the fixed pattern table in the `PATT` metadata section and compiles glob objects at runtime.

Dependencies: exposes `bio` and fixed-width integer types. Error/status codes are returned as MooseFS `MFS_*` values from the implementation.

Risks: callers must provide a 256-byte name buffer and valid gid array/count. Buffer sizing for `patterns_list` should use the NULL-buffer query mode.

Test signals: matching, list serialization, metadata round trip, and live vs replay add/delete behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/moosefs/mfsmaster/patterns.h -->
