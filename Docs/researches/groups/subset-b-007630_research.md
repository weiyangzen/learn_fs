# subset-b-007630 Research

Grouped source research for LizardFS master service endpoints, metadata restore/dump helpers, task-manager-backed filesystem operations, quota/topology/personality state, and metadump/metalogger/metarestore build glue. Each source file has its own marker-delimited section for deterministic reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/master/matocsserv.cc -->
# sources/distributed-fs/lizardfs/src/master/matocsserv.cc

## Purpose

`matocsserv.cc` implements the master-to-chunkserver service. It owns the listening socket for `MATOCS_LISTEN_HOST`/`MATOCS_LISTEN_PORT`, accepts chunkserver connections only while this metadata server is master, tracks connected chunkservers, ingests their registration/space/chunk-status packets, and emits chunk operation packets requested by the chunk subsystem. The file was read as a complete 1851-line implementation.

## Important APIs, Types, and Functions

The central private type is `matocsserventry`, which stores socket state, poll position, timers, protocol input/output queues, advertised chunkserver address/version/label/space counters/load factor, operation counters, and the associated `csdbentry`. Publicly exported functions include placement/state queries (`matocsserv_getservers_sorted`, `matocsserv_getservers_for_new_chunk`, `matocsserv_getservers_lessrepl`, `matocsserv_getspace`, `matocsserv_getlocation`, counter getters), chunk operation senders (`matocsserv_send_createchunk`, `matocsserv_send_deletechunk`, `matocsserv_send_replicatechunk`, `matocsserv_send_liz_replicatechunk`, `matocsserv_send_setchunkversion`, `matocsserv_send_duplicatechunk`, `matocsserv_send_truncatechunk`, `matocsserv_send_duptruncchunk`), registration/status handlers, and event-loop hooks (`matocsserv_init`, `matocsserv_reload`, `matocsserv_desc`, `matocsserv_serve`, `matocsserv_term`). The local replication database uses `repsrc`, `repdst`, `rephash`, and free lists to count in-flight read/write replication pressure per chunkserver.

## Control Flow

Initialization reads config, opens a nonblocking listening socket, initializes replication tracking, and registers reload/destruct/poll callbacks. Poll descriptor creation adds the listener and every connected chunkserver, adding `POLLOUT` when output packets are queued. Service flow accepts new sockets only if `metadataserver::isMaster()`; each accepted entry starts with wildcard label, zeroed space, default timeout, and an unresolved `csdb` pointer. Reads accumulate `InputPacket` data until a full packet arrives, dispatch through `matocsserv_gotpacket`, and reset the parser. Writes drain queued `OutputPacket`s. Idle connections receive NOPs and stale reads time out. Killed entries are removed after notifying replication tracking, chunk state (`chunk_server_disconnected`), and chunkserver DB.

Incoming packet dispatch covers legacy MooseFS and LizardFS packet variants. Registration has old single-packet forms, versioned 1-4 forms, legacy version-5 phased packets, and LizardFS typed packets for host/chunks/space/label. Chunk reports update chunk metadata through `chunk_server_has_chunk`, `chunk_damaged`, and `chunk_lost`. Operation status packets are deserialized according to peer version and packet version, then forwarded to `chunk_got_*_status` callbacks.

## State and Persistence Behavior

The service keeps only runtime state: linked-list connection records, per-connection output queues, in-flight replication hash entries, and socket/config globals. Durable metadata changes happen indirectly in the chunk subsystem when chunkserver inventories and operation statuses update chunk placement. Space, label, and load state influence future placement but are refreshed from chunkserver packets and lost on process restart. The `csdb` integration preserves cross-connection chunkserver identity while the master is running.

## Dependencies and Integration Points

Key dependencies are event loop registration, socket helpers, `InputPacket`/`OutputPacket`, protocol namespaces `matocs` and `cstoma`, LizardFS version gates, `slice_traits`/`Goal` for standard/XOR/EC chunk parts, `master/chunks.h`, `chunkserver_db`, `filesystem` goal definitions, `GetServersForNewChunk`, media labels, and metadata-server personality. It is a high-impact integration point for chunk creation, deletion, replication, truncation, duplicate/duptrunc operations, EC compatibility, label-aware placement, avoiding same-IP placement, and chunkserver UI/status exports.

## Risks and Edge Cases

Protocol compatibility branches are dense and version-sensitive; wrong packet version handling can corrupt chunk type interpretation, especially around XOR/EC parts. Several malformed packets kill the connection, so boundary-size tests matter. Replication counters rely on begin/end/disconnect symmetry; missed status or duplicate operations can skew placement pressure. Placement depends on space values, load factor penalty, labels, history, and random shuffling, which makes deterministic regression testing harder. The service rejects localhost-advertised chunkservers and duplicate `csdb` connections. Output queues are unbounded per connection aside from operation flow control. Some state is manually allocated/free-listed, so disconnect cleanup and error paths are memory-risk areas.

## Test Signals

Useful signals include packet round-trip and malformed packet tests for legacy, XOR, and EC variants; integration tests where chunkservers register in phased and LizardFS packet modes; placement tests for labels, same-IP avoidance, load factor, full servers, and minimum version gates; replication counter tests for success, failure, duplicate, and disconnect paths; event-loop smoke tests for timeout/NOP/reload behavior; and cluster tests that verify chunk metadata reacts correctly to create/delete/replicate/truncate statuses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/master/matocsserv.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/master/matocsserv.h -->
# sources/distributed-fs/lizardfs/src/master/matocsserv.h

## Purpose

`matocsserv.h` is the public master-facing interface for the chunkserver service implemented in `matocsserv.cc`. It forward-declares opaque connection and chunkserver DB types and exposes functions used by chunk placement, chunk operation scheduling, status reporting, and module initialization. The source was read as a complete 127-line header.

## Important APIs, Types, and Functions

The header defines `matocsserventry`, `csdbentry`, `Chunkservers`, `ServerWithUsage`, and `IpCounter`. APIs cover label/usage/version/location accessors, sorted/filtered server selection, new-chunk placement for a goal, total/available space aggregation, replication/deletion counters, operation senders for create/delete/replicate/set-version/duplicate/truncate/duptrunc, initialization, and conversion to `ChunkserverListEntry`.

## Control Flow

The header has no executable control flow. It defines the call surface used by other master modules to ask the chunkserver service for placement candidates and to enqueue protocol messages to active chunkservers.

## State and Persistence Behavior

It owns no state directly. Exposed pointer types refer to connection records maintained by `matocsserv.cc`; callers must treat them as live runtime handles, not durable identities.

## Dependencies and Integration Points

It includes chunk part types, goal/media-label definitions, server selection helpers, `ChunkserverListEntry`, and compact map/vector utilities. It is integrated with the chunks module, admin/status paths, and placement algorithms that need chunkserver handles.

## Risks and Edge Cases

Opaque `matocsserventry*` handles can become invalid after disconnect cleanup, so users must not persist them beyond the chunkserver service lifecycle. The API exposes multiple version-sensitive operation senders; callers must pass compatible `ChunkPartType` values and source vectors.

## Test Signals

Compile/link coverage for all users, placement unit tests that mock connected servers, and integration tests that enqueue every declared chunk operation through live or simulated chunkserver entries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/master/matocsserv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/master/matomlserv.cc -->
# sources/distributed-fs/lizardfs/src/master/matomlserv.cc

## Purpose

`matomlserv.cc` implements the master-to-metalogger and master-to-shadow-master service. It broadcasts changelog records and log rotations, serves metadata/session/changelog file downloads, keeps a bounded in-memory cache of recent changes for catch-up, and coordinates shadow metadata-save requests after changelog apply failures. The file was read as a complete 1055-line implementation.

## Important APIs, Types, and Functions

Private connection state lives in `matomlserventry`, which stores a socket, parser mode, header/data buffers, output packet linked list, timeout, address/version/port, shadow flag, and open file descriptors for metadata/changelog downloads. `ShadowQueue` tracks shadows awaiting metadata dump result packets. `old_changes_block` and `old_changes_entry` store recent changelog packets. Public exports include `matomlserv_mloglist_size`, `matomlserv_mloglist_data`, `matomlserv_shadows`, `matomlserv_shadows_count`, `matomlserv_broadcast_logstring`, `matomlserv_broadcast_logrotate`, `matomlserv_broadcast_metadata_saved`, `matomlserv_canexit`, and `matomlserv_init`.

## Control Flow

Initialization reads config, binds the MATOML listener, caps `MATOML_LOG_PRESERVE_SECONDS`, registers exit/reload/destruct/poll hooks, and schedules a periodic warning about missing metaloggers after master promotion. Accepted connections are admitted only on a master. Reads are a two-state header/data parser over an 8-byte packet header and a bounded data allocation. Dispatch handles metalogger registration, LizardFS shadow registration, metadata download start/data/end, shadow changelog-apply errors, and shadow client-port advertisement. Writes drain a manually allocated packet queue.

Changelog broadcast first stores the log string in the recent-change cache, then sends `MATOML_METACHANGES_LOG` to every registered peer. Shadow registration compares shadow metadata version with the master version and either replies with a version from which cached changes can replay or forces the shadow to download metadata. Download flow opens metadata/session/current changelog/rotated changelog files and replies with sizes, data chunks, and CRCs. Exit flow sends end-session packets, stops accepting, and waits until all connections are gone.

## State and Persistence Behavior

The persistent data served by this module is external: `metadata.mfs`, sessions, and changelog files. Internally it maintains runtime sockets, output queues, file descriptors, shadow request sets, recent changelog blocks, and rate-limiting timestamps. `matomlserv_store_logstring` prunes old cached blocks by configured seconds and can discard all cached changes when preservation is disabled. Metadata-save requests call `fs_storeall(MetadataDumper::kBackgroundDump)` and optionally trigger checksum recalculation for bad metadata checksum reports.

## Dependencies and Integration Points

The module depends on `common/cfg`, `event_loop`, sockets, CRC, metadata filenames, filesystem store/checksum APIs, metadata-server personality, and `protocol/matoml`/`protocol/mltoma`. It integrates with master changelog emission, shadow promotion/catch-up, metalogger status APIs, graceful shutdown, and metadata dump completion notification from `MetadataDumper`.

## Risks and Edge Cases

Recent-change replay is only as good as the in-memory retention window; shadows behind `old_changes_head->minversion` require a full metadata download. Manual allocation of packet queues and download buffers creates cleanup-sensitive paths. Download requests are ignored during exit to avoid racing shutdown. `METADATA_SAVE_REQUEST_MIN_PERIOD` rate-limits shadow-triggered dumps, so delayed shadows must handle explicit delay status. File-size reads use `lseek` and `pread`; changing files during download requires protocol-level tolerance. Legacy shadow registration is rejected, and low timeouts are raised.

## Test Signals

Tests should cover registration version/length validation, shadow catch-up with and without cached changes, metadata download size/data/CRC paths for each filenum, changelog broadcast and rotation packets, rate-limited changelog apply error handling, exit draining, listener reload, and malformed packet disconnect behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/master/matomlserv.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/master/matomlserv.h -->
# sources/distributed-fs/lizardfs/src/master/matomlserv.h

## Purpose

`matomlserv.h` declares the public interface for the master-to-metalogger/shadow service. It exposes status, shadow listing, changelog broadcast, metadata-save result broadcast, initialization, and graceful-exit queries. The source was read as a complete 50-line header.

## Important APIs, Types, and Functions

Functions include `matomlserv_mloglist_size`, `matomlserv_mloglist_data`, `matomlserv_shadows`, `matomlserv_broadcast_logstring`, `matomlserv_broadcast_logrotate`, `matomlserv_broadcast_metadata_saved`, `matomlserv_init`, `matomlserv_canexit`, and `matomlserv_shadows_count`.

## Control Flow

There is no executable flow in the header. It defines entry points used by filesystem/changelog code to push changes and by event-loop startup/shutdown paths to run the service.

## State and Persistence Behavior

No state is owned here. The implementation owns runtime connections, shadow queues, and cached changelog blocks; persistent metadata/changelog files are accessed indirectly.

## Dependencies and Integration Points

The only project-specific type exposed is `MetadataserverListEntry`, making this header part of status/reporting surfaces as well as the metadata replication pipeline.

## Risks and Edge Cases

Callers of `matomlserv_broadcast_logstring` pass raw buffers and sizes; ownership remains with the caller, but the implementation copies into its cache and output queues. `matomlserv_canexit` reflects connection-drain state and must be polled during shutdown.

## Test Signals

Compile coverage from master filesystem/changelog/status code, integration tests that observe changelog packets at metaloggers/shadows, and shutdown tests that wait on `matomlserv_canexit`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/master/matomlserv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/master/matotsserv.cc -->
# sources/distributed-fs/lizardfs/src/master/matotsserv.cc

## Purpose

`matotsserv.cc` implements the master-to-tapeserver service used for tape/archive copy tracking. It accepts tapeserver connections on `MATOTS_LISTEN_HOST`/`MATOTS_LISTEN_PORT`, registers named tapeservers, receives lists of tape-stored files, queues file keys for tapeserver transfer, and exposes connected tapeserver info. The source was read as a complete 535-line implementation.

## Important APIs, Types, and Functions

Private `matotsserventry` stores mode, socket, poll position, timers, protocol queues, server name/label/id/address/version, and whether initial files were registered. Static globals track the listening socket, connected tapeservers, and a queue of `TapeKey`s to send. Public functions are `matotsserv_init`, `matotsserv_can_enqueue_node`, `matotsserv_enqueue_node`, `matotsserv_get_tapeserver_info`, and `matotsserv_get_tapeservers`.

## Control Flow

Initialization binds the listener, registers event-loop hooks, and schedules periodic file flushing when master. Poll handling accepts only on master, reads `InputPacket`s, dispatches register/has-files/end-of-files messages, writes output packets, sends NOP keepalives, and kills timed-out connections. Periodic flow sends queued `TapeKey`s to the first connected tapeserver via `matots::putFiles::build` and clears the queue.

## State and Persistence Behavior

The module stores runtime connection state and an in-memory queue of file keys waiting to be sent. Persistent file-copy state is updated indirectly through `fs_add_tape_copy` when tapeservers report files, and by callers that enqueue tape copies after filesystem operations. Tapeserver IDs are hashes of server names and kept in a static set to reject duplicate active registrations.

## Dependencies and Integration Points

It depends on event-loop callbacks, socket wrappers, `InputPacket`/`OutputPacket`, `protocol/matots` and `protocol/tstoma`, media labels, network addresses, filesystem tape-copy APIs, and personality promotion hooks. `SetGoalTask` calls `matotsserv_can_enqueue_node` and `fsnodes_enqueue_tape_copies` when file goals change.

## Risks and Edge Cases

Server IDs are `std::hash<std::string>()` values, which are not a cryptographic identity and may vary by implementation or collide. `matotsserv_enqueue_node` asserts that a registered tapeserver exists after callers check availability; misuse can abort. The file queue is cleared after sending to the first tapeserver, so distribution/failover semantics are minimal. Registered server labels remain wildcard in this implementation. Malformed packets disconnect the tapeserver.

## Test Signals

Signals include register success/failure and duplicate-name rejection tests, has-files integration with filesystem tape-copy state, queue flush tests for `putFiles`, timeout/NOP/reload behavior, and status API checks for registered versus unregistered connections.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/master/matotsserv.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/master/matotsserv.h -->
# sources/distributed-fs/lizardfs/src/master/matotsserv.h

## Purpose

`matotsserv.h` declares the public interface for LizardFS master tapeserver integration. It exposes service initialization, file enqueue capability, file enqueueing, and tapeserver status lookup/listing. The file was read as a complete 45-line header.

## Important APIs, Types, and Functions

It defines `TapeserverId` as `uint32_t` and declares `matotsserv_init`, `matotsserv_can_enqueue_node`, `matotsserv_enqueue_node`, `matotsserv_get_tapeserver_info`, and `matotsserv_get_tapeservers`. Public parameter/return types include `TapeKey` and `TapeserverListEntry`.

## Control Flow

No executable flow exists in the header; callers use it to decide whether tape copy work can be queued and to retrieve connected tapeserver metadata.

## State and Persistence Behavior

The header owns no state. Returned IDs refer to runtime tapeserver registrations and filesystem tape-copy associations maintained elsewhere.

## Dependencies and Integration Points

It includes ID pool, tape key/copy info, and network address definitions. It integrates filesystem operations that enqueue archival copies and admin/status handlers that display tapeserver state.

## Risks and Edge Cases

Callers must respect `matotsserv_can_enqueue_node` before enqueueing. `TapeserverId` identity is implementation-defined by the service and should not be assumed globally stable without checking the implementation.

## Test Signals

Compile coverage from filesystem goal/tape paths and integration tests that connect a tapeserver, enqueue a file, and retrieve its status.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/master/matotsserv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/master/metadata_dumper.cc -->
# sources/distributed-fs/lizardfs/src/master/metadata_dumper.cc

## Purpose

`metadata_dumper.cc` implements `MetadataDumper`, the helper that lets the master dump metadata either in the foreground, in a forked child, or by executing `mfsmetarestore` against a rotated changelog. It monitors child output over a pipe and records whether the dump succeeded. The file was read as a complete 258-line implementation.

## Important APIs, Types, and Functions

Important methods are the constructor, `dumpSucceeded`, `inProgress`, `useMetarestore`, `setMetarestorePath`, `setUseMetarestore`, `start`, `pollDesc`, `pollServe`, `dumpingFinished`, and the two `waitUntilFinished` overloads. `createPipe` is a local helper. `start` is the main state transition method and may return true in the child process after converting the dump to foreground mode.

## Control Flow

For foreground dumps, `start` returns false and leaves dumping to the caller. For background dumps it creates a pipe and forks. The child redirects stdout to the pipe; if metarestore is enabled and the previous dump succeeded, it execs `mfsmetarestore` with metadata input/output paths, checksum, previous-copy count, and rotated changelog. If exec is skipped or fails, the child changes the dump type to foreground so it stores metadata itself and reports `"OK"` through stdout. The parent assumes failure until it reads exactly `OK\n`. Poll integration adds the child pipe, reads status text, and closes the fd on EOF/error/hangup. Timed waits poll until completion or mark the dump finished after timeout.

## State and Persistence Behavior

State is per `MetadataDumper`: booleans for metarestore use and last success, the child pipe fd and poll index, whether output was empty, and metadata/tmp/metarestore paths. Persistent metadata files are written by filesystem store code or by the external `mfsmetarestore` process; this helper only orchestrates and observes the process.

## Dependencies and Integration Points

Dependencies include Unix `pipe`, `fork`, `dup2`, `execv`, `nice`, `access`, `poll`, metadata constants (`kChangelogFilename`, `gStoredPreviousBackMetaCopies`), logging, filesystem storage, and personality include context. It is called by filesystem metadata store paths and reports completion to other services such as metalogger/shadow notification.

## Risks and Edge Cases

The success protocol is fragile: any child stdout other than exactly `OK\n` marks failure. Fork/pipe/dup2/exec errors fall back to foreground master dumping. The parent does not waitpid here, so process lifecycle must be handled by broader process behavior or child termination. Missing rotated changelog disables metarestore for that attempt. Timeout handling closes the fd and marks the process finished even if the child may still exist.

## Test Signals

Unit/integration signals include fork/pipe failure injection, metarestore exec success/failure with mocked stdout, missing changelog fallback, poll EOF/error paths, timeout behavior, and verifying the next dump chooses master or metarestore based on `dumpingSucceeded_` and `useMetarestore_`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/master/metadata_dumper.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/master/metadata_dumper.h -->
# sources/distributed-fs/lizardfs/src/master/metadata_dumper.h

## Purpose

`metadata_dumper.h` declares the `MetadataDumper` class used by the master to orchestrate foreground/background metadata dumping and optional metarestore-assisted dumping. The source was read as a complete 88-line header.

## Important APIs, Types, and Functions

The class exposes `DumpType` (`kForegroundDump`, `kBackgroundDump`), construction with metadata/tmp filenames, status getters, setters for metarestore path/use, `start`, poll hooks `pollDesc`/`pollServe`, and blocking waits. Protected state includes dump success flags, child pipe fd, poll index, output-empty flag, metarestore path, and metadata paths.

## Control Flow

The header documents the class API but has no implementation flow. Callers invoke `start` before a metadata store and then use poll or wait helpers to observe the background process.

## State and Persistence Behavior

The class stores runtime process-monitoring state only. It names metadata files but does not define their format or write them directly in the header.

## Dependencies and Integration Points

It includes polling, logging, time utilities, and standard path/string/vector support. It integrates with the master event loop and filesystem metadata store logic.

## Risks and Edge Cases

Callers must respect the special child-return case from `start`: true means execution continues in the child and `dumpType` has been changed to foreground. Poll hooks support at most one fd per dumper instance.

## Test Signals

Compile coverage, API tests for state transitions, and integration tests that run background dump flows through event-loop polling or timeout waits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/master/metadata_dumper.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/master/mfsrestoremaster.in -->
# sources/distributed-fs/lizardfs/src/master/mfsrestoremaster.in

## Purpose

`mfsrestoremaster.in` is a Bash template script that promotes a metalogger host into a spare master by restoring metadata from metalogger backups, moving the master IP to a network interface, and starting `mfsmaster`. The source was read as a complete 158-line script.

## Important APIs, Types, and Functions

Shell helpers are `notice`, `panic`, `get_config_option`, `if_equal`, and `is_tcp_port_open`. The script consumes `<net-interface>` and optional `<etc-mfs-dir>`, reads `mfsmetalogger.cfg` and `mfsmaster.cfg`, uses `mfsmetarestore`, `ifconfig`, and `mfsmaster`, and relies on configured template paths `@ETC_PATH@` and `@DATA_PATH@`.

## Control Flow

After argument and root checks, it loads metalogger/master config paths, validates readable configs, resolves the intended master host from metalogger `MASTER_HOST` and master MATOML/MATOCS/MATOCL listen addresses, verifies no host or TCP service already owns the address, restores `metadata.mfs` from `metadata_ml.mfs.back` plus `changelog_ml.*`, assigns the IP address to the requested interface, and starts the master server with the selected config.

## State and Persistence Behavior

It writes the restored master metadata file in the master data path, changes host network interface state, and starts a daemon. It does not update configs itself. Failures call `panic` and abort before starting master, but side effects before a later failure, such as restored metadata or changed interface address, may remain.

## Dependencies and Integration Points

Dependencies include Bash with `set -e -u`, `awk`, Python socket module, `ping`, `mfsmetarestore`, `ifconfig`, and `mfsmaster`. It bridges metalogger backup data and master startup in failover operations.

## Risks and Edge Cases

The config parser is simple AWK matching and ignores include/quoting complexities. `ifconfig $net_interface $master_host` is unquoted for the interface. TCP reachability and ping checks are race-prone. If restoration succeeds but interface or daemon startup fails, cleanup is manual. The script assumes legacy network tooling and Python availability.

## Test Signals

Shellcheck-like static checks, dry-run tests with fixture configs, mocked command-path tests for restore/interface/start failure points, and integration drills on a test network where the target IP is free.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/master/mfsrestoremaster.in -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/master/personality.cc -->
# sources/distributed-fs/lizardfs/src/master/personality.cc

## Purpose

`personality.cc` implements metadata server personality state: master versus shadow, with special validation and promotion behavior for HA-cluster-managed installations. The file was read as a complete 188-line implementation.

## Important APIs, Types, and Functions

Exports in namespace `metadataserver` are `getPersonality`, `setPersonality`, `registerFunctionCalledOnPromotion`, `promoteToMaster`, `personality_reload`, `promoteAutoToMaster`, `personality_validate`, `personality_init`, and `isMaster`. Static state includes `gPersonality` and `gChangePersonalityReloadFunctions`. Helpers parse `PERSONALITY`, command-line extra arguments, and the `ha-cluster-managed` mode.

## Control Flow

Initialization registers reload handling outside `METARESTORE`, validates mutually exclusive initial-personality arguments, and derives master/shadow state from either HA-managed command-line arguments or non-HA config. Reload refuses switching between HA-managed and non-HA-managed modes; in non-HA mode it permits shadow-to-master promotion but rejects master-to-shadow. Promotion logs, calls registered promotion hooks, then sets personality to master. `promoteAutoToMaster` only promotes a HA-managed shadow.

## State and Persistence Behavior

Personality is in-process global state. The persistent source of desired personality is the configuration file plus process command-line arguments. Promotion callbacks let services reconfigure event-loop behavior after a transition, but no durable promotion marker is written here.

## Dependencies and Integration Points

The module integrates with config (`cfg_get`, `cfg_filename`), command-line argument inspection, reload events, logging, and services that register promotion callbacks such as metalogger and tapeserver services.

## Risks and Edge Cases

`setPersonality` itself does not enforce the documented forbidden master-to-shadow transition; policy is enforced by higher-level reload/init code. HA-managed mode requires exact coordination between config and command-line option. Promotion callback order is registration order and callbacks are raw function pointers. Reload errors are logged but intentionally do not abort the running instance.

## Test Signals

Tests should cover config strings case-insensitively, invalid personalities, HA/non-HA mismatch exceptions, mutually exclusive initial options, shadow-to-master callback execution, forbidden master-to-shadow reload logging, and `promoteAutoToMaster` behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/master/personality.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/master/personality.h -->
# sources/distributed-fs/lizardfs/src/master/personality.h

## Purpose

`personality.h` declares metadata server personality APIs and the `Personality` enum used to distinguish master and shadow behavior. The source was read as a complete 72-line header.

## Important APIs, Types, and Functions

It declares `enum class Personality { kMaster, kShadow }`, `getPersonality`, `setPersonality`, `personality_validate`, `personality_init`, `isMaster`, `registerFunctionCalledOnPromotion`, and `promoteAutoToMaster`.

## Control Flow

No executable flow is present. The header documents that promotion from shadow to master is allowed but master-to-shadow is forbidden at the intended API level.

## State and Persistence Behavior

The header owns no state. It exposes process-global personality state maintained by the implementation.

## Dependencies and Integration Points

It depends only on `common/platform.h` and is included by master services that conditionally accept connections or register promotion hooks.

## Risks and Edge Cases

Because `setPersonality` is public, misuse can bypass policy unless callers follow the documented contract. Services relying on `isMaster` must handle runtime promotion.

## Test Signals

Compile coverage and service integration tests that confirm shadow instances reject master-only client connections until promotion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/master/personality.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/master/quota_database.cc -->
# sources/distributed-fs/lizardfs/src/master/quota_database.cc

## Purpose

`quota_database.cc` implements `QuotaDatabase` operations that are not inline in the header: removing quotas, testing quota exceedance, enumerating entries, and computing a checksum. The source was read as a complete 123-line implementation.

## Important APIs, Types, and Functions

Methods implemented are `remove(owner_type, owner_id, rigor, resource)`, `remove(owner_type, owner_id)`, `exceeds`, `getEntries`, `getEntriesWithStats`, and `checksum`. They operate on `quota_data_`, a per-owner-type map from owner ID to a `Limits` array indexed by `QuotaRigor` and `QuotaResource`.

## Control Flow

Remove finds the owner map entry, clears a single resource or erases the whole owner, and erases empty all-zero limit arrays. `exceeds` returns false for missing entries, then checks each proposed resource delta against the selected soft/hard limit plus current used value. Enumeration walks user/group/inode owner types and soft/hard resources, optionally emitting used stats only for resources with a nonzero soft/hard limit. Checksum folds only nonzero soft/hard limits into a deterministic seed.

## State and Persistence Behavior

State is in-memory quota limits and usage counters. Usage (`QuotaRigor::kUsed`) participates in exceedance and stats enumeration but is intentionally excluded from `checksum`, so metadata checksums represent quota limits, not live usage.

## Dependencies and Integration Points

It depends on `protocol/quota.h`, hash helpers, and checksum combination helpers. Filesystem quota code updates usage and consults exceedance during operations such as snapshots and creation.

## Risks and Edge Cases

`update` in the header adds signed deltas into unsigned counters without local underflow checks. `exceeds` adds an `int64_t` delta to `uint64_t` usage, so negative deltas require caller discipline. Zero limits mean no limit. `getEntriesWithStats` omits used-only entries when no soft/hard limit exists for that resource.

## Test Signals

Quota unit tests cover set/get/remove, exceedance boundaries, corner cases, and checksum invariance to usage. Additional useful tests would include negative updates, all owner types, and stats enumeration ordering expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/master/quota_database.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/master/quota_database.h -->
# sources/distributed-fs/lizardfs/src/master/quota_database.h

## Purpose

`quota_database.h` declares and partly implements `QuotaDatabase`, an in-memory storage object for quota limits and usage by owner type, owner ID, rigor, and resource. The source was read as a complete 150-line header.

## Important APIs, Types, and Functions

Types include `Limits` (`array<array<uint64_t, 2>, 3>`) and `DataTable` (`unordered_map<uint32_t, Limits>`). Inline methods include `get`, `set`, `update`, `removeEmpty`, `hash`, and templated `forEach`; non-inline methods are declared for remove/exceeds/enumeration/checksum.

## Control Flow

Inline setters create owner entries on demand and write array slots directly. `removeEmpty` erases entries whose entire `Limits` value is zero. `forEach` iterates owner types user/group/inode, then entries, then soft/hard rigor and inode/size resources.

## State and Persistence Behavior

The database stores quota state in memory. Persistence is external through metadata serialization/changelog replay; this header defines the structure that those paths populate and inspect.

## Dependencies and Integration Points

It integrates with `protocol/quota.h` types, filesystem quota enforcement, restore `SETQUOTA` application, metadata checksum computation, and tests. `common/hashfn.h` supplies hash combination.

## Risks and Edge Cases

The array layout depends on enum integer values. Direct `update` has no validation for underflow/overflow. `forEach` intentionally excludes `kUsed` rigor, so code needing usage must use different iteration logic.

## Test Signals

Unit tests for enum-index mapping, set/update/removeEmpty behavior, checksum stability, and all owner/resource combinations are the main confidence signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/master/quota_database.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/master/quota_database_unittest.cc -->
# sources/distributed-fs/lizardfs/src/master/quota_database_unittest.cc

## Purpose

`quota_database_unittest.cc` provides GoogleTest coverage for `QuotaDatabase` set/get, remove, exceedance, boundary behavior, and checksum semantics. The source was read as a complete 159-line test file.

## Important APIs, Types, and Functions

The helper macro `EXPECT_ENTRY_EQ` checks used inode/size and soft/hard inode/size values for a quota entry. Tests are `SetGetQuota`, `RemoveQuota`, `IsExceeded`, `IsExceededCornerCase`, and `Checksum`.

## Control Flow

Each test creates a fresh `QuotaDatabase`, mutates quota limits/usage, and asserts direct entry layout or boolean/checksum results. The checksum test collects multiple distinct checksums after changing one field at a time, verifies they differ, then verifies rewriting the same limit and changing usage do not alter the checksum.

## State and Persistence Behavior

The tests operate purely in memory. They validate that usage is tracked for exceedance but excluded from metadata checksum.

## Dependencies and Integration Points

The file depends on GoogleTest and `master/quota_database.h`. It is created by the build system as part of quota/metarestore or master test suites depending on CMake collection.

## Risks and Edge Cases

Coverage is focused but does not directly test `getEntries`, `getEntriesWithStats`, negative `update` deltas, removal of all quota dimensions for user/group/inode, or overflow/underflow. It also assumes deterministic checksum behavior over unordered maps through order-independent checksum combination.

## Test Signals

Passing this suite is a strong signal for core quota semantics. Additional tests should target serialization ordering, stats enumeration, and delta edge cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/master/quota_database_unittest.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/master/recursive_remove_task.cc -->
# sources/distributed-fs/lizardfs/src/master/recursive_remove_task.cc

## Purpose

`recursive_remove_task.cc` implements `RemoveTask`, a `TaskManager::Task` that removes directory trees incrementally by enqueueing child-removal subtasks before unlinking non-empty directories. The source was read as a complete 84-line implementation.

## Important APIs, Types, and Functions

Methods are `isFinished`, `retrieveNodes`, `doUnlink`, and `execute`. The task stores subtask names, parent inode, `FsContext`, and a repeat counter to detect directories that are continuously repopulated.

## Control Flow

`execute` resolves the parent directory and current child, validates write and sticky permissions, then either enqueues a new `RemoveTask` for a non-empty child directory or unlinks the current child. Directory children are pushed to the front of the shared work queue so a depth-first removal sequence empties directories before the parent advances. After too many repeats on the same directory, it returns `ENOTEMPTY`.

## State and Persistence Behavior

Each successful unlink emits an `UNLINK` changelog entry, updates filesystem stats, and calls `fsnodes_unlink`, which mutates in-memory metadata and downstream persistence via changelog. Task progress is the current iterator and repeat counter.

## Dependencies and Integration Points

It depends on filesystem node lookup, access checks, sticky access, changelog emission, stats, `FsContext`, `HString`, and `TaskManager`. It is used by recursive remove operations that cannot complete in one event-loop tick.

## Risks and Edge Cases

If the parent disappears, permissions change, or child disappears, the task fails. Concurrent creation inside a deleting directory can hit the repeat counter. The code static-casts parent to directory after lookup/access, relying on callers to pass directory parents. Recursive work is generated from a snapshot of current entries.

## Test Signals

Tests should cover recursive non-empty directories, permission/sticky failures, missing parent/child, repeated repopulation causing `ENOTEMPTY`, changelog ordering, and cancellation through `TaskManager`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/master/recursive_remove_task.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/master/recursive_remove_task.h -->
# sources/distributed-fs/lizardfs/src/master/recursive_remove_task.h

## Purpose

`recursive_remove_task.h` declares `RemoveTask`, the task-manager-backed implementation of recursive deletion. The source was read as a complete 85-line header.

## Important APIs, Types, and Functions

`RemoveTask` derives from `TaskManager::Task`, defines `SubtaskContainer` as a vector of `HString`, has a constructor taking subtasks, parent inode, and `FsContext`, overrides `execute` and `isFinished`, and provides `generateDescription`. Private helpers are `retrieveNodes` and `doUnlink`; state includes `kMaxRepeatCounter`.

## Control Flow

The header describes the task model: one task handles one node/name at a time, adds children to the front of the queue for non-empty directories, and removes itself from the queue once its subtask iterator finishes.

## State and Persistence Behavior

State is per-task in memory. Persistent filesystem effects are performed by the implementation through changelog and node operations.

## Dependencies and Integration Points

It includes special inode definitions, filesystem node/operations, `HString`, `FsContext`, and `TaskManager`, making it part of asynchronous filesystem operation handling.

## Risks and Edge Cases

The constructor initializes `current_subtask_` from the moved vector; callers must pass a non-empty meaningful subtask list. The task retains a shared context, so context lifetime is shared with background processing.

## Test Signals

Compile coverage and filesystem operation tests that submit `RemoveTask` through `TaskManager` with recursive and permission-sensitive cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/master/recursive_remove_task.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/master/restore.cc -->
# sources/distributed-fs/lizardfs/src/master/restore.cc

## Purpose

`restore.cc` is the changelog replay interpreter for master/metarestore recovery. It parses textual changelog entries, dispatches them to filesystem apply functions, enforces monotonically contiguous metadata versions, and supports both strict and parse-error-tolerant restore modes. The file was read as a complete 1054-line implementation.

## Important APIs, Types, and Functions

Public functions are `restore_reset`, `restore`, and `restore_setverblevel`; `restore_line` is the central dispatcher. Parser macros `EAT`, `GETNAME`, `GETPATH`, `GETDATA`, `GETCHAR`, `GETU32`, and `GETU64` decode changelog syntax and percent-escaped data. Operation handlers include access, append, acquire, attr, checksum, create/session/free-inodes/incversion/link/length/move, lock operations, purge/release/repair, seteattr/setgoal/setpath/settrashtime/setxattr, ACL/richACL/quota, clone/symlink/undel/unlink/unlock/nextchunkid/trunc/write, and deprecated snapshot/emptytrash/emptyreserved forms.

## Control Flow

`restore` initializes expected versions from `fs_getversion`, ignores entries older than the current version, detects duplicate entries, rejects holes in changelog sequence, and otherwise calls `restore_line`. `restore_line` parses a `": timestamp|OP..."` suffix, switches by first operation character, matches operation names, and calls the handler. After a successful operation, `restore` checks that the filesystem metadata version advanced exactly one step. Parse errors can be ignored when `RestoreRigor::kIgnoreParseErrors` is selected; semantic operation errors stop processing.

## State and Persistence Behavior

Static restore state tracks `nextFsVersion`, `currentFsVersion`, `lastfn`, and verbosity. Several parsers use static growable buffers for paths, xattrs, and ACL strings. Filesystem state is mutated through `fs_*` functions with restore contexts and persistence is represented by the replayed changelog itself. Version sequencing is the main guard against missing or duplicated durable changes.

## Dependencies and Integration Points

Dependencies include LizardFS error codes, logging, protocol constants, filesystem core, snapshot, and operations APIs. This file is linked into `mfsmetarestore` and the master build paths that need changelog application, and CMake explicitly pulls it into the metarestore library with task/snapshot/setgoal/settrashtime support.

## Risks and Edge Cases

The parser is macro-heavy and manually advances raw C strings; malformed or truncated percent escapes can produce parse errors, and long names are capped at 255 bytes for `GETNAME`. Static buffers are not thread-safe. Some legacy/deprecated formats are still accepted. Correct restore depends on every `fs_*` apply path incrementing metadata version exactly once. Negative operation status and parse errors are treated differently by rigor mode. Changelog holes stop restore with inconsistency.

## Test Signals

Strong coverage requires golden changelog replay tests for every operation, version hole/duplicate/old-entry cases, parse-error rigor behavior, percent escaping and long data/path buffers, metadata-version mismatch injection, legacy format compatibility, and metarestore end-to-end tests from metadata plus changelogs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/master/restore.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/master/restore.h -->
# sources/distributed-fs/lizardfs/src/master/restore.h

## Purpose

`restore.h` declares the public changelog restore API. The source was read as a complete 29-line header.

## Important APIs, Types, and Functions

It defines `enum class RestoreRigor { kIgnoreParseErrors, kDontIgnoreAnyErrors }` and declares `restore_reset`, `restore`, and `restore_setverblevel`.

## Control Flow

The header has no executable flow. Callers reset restore state, pass changelog entries and versions to `restore`, and optionally set verbosity.

## State and Persistence Behavior

Restore state is implementation-global and reset by `restore_reset`. Persistent effects occur through filesystem apply functions in `restore.cc`.

## Dependencies and Integration Points

It depends on platform/inttypes and is included by metarestore/master code that replays changelogs.

## Risks and Edge Cases

Because restore state is global, multiple concurrent restore streams are not supported. Callers must pass entries in changelog order with correct version values.

## Test Signals

Compile coverage and end-to-end restore tests that call the public API with ordered, duplicate, missing, and malformed entries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/master/restore.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/master/setgoal_task.cc -->
# sources/distributed-fs/lizardfs/src/master/setgoal_task.cc

## Purpose

`setgoal_task.cc` implements `SetGoalTask`, a task-manager-backed recursive operation for changing file/directory storage goals. The source was read as a complete 95-line implementation.

## Important APIs, Types, and Functions

Methods are `execute`, `isFinished`, and `setGoal`. The task tracks a vector of inode IDs, current iterator, user ID, desired goal, set mode, and shared stats array.

## Control Flow

Each `execute` processes one inode, advances the iterator, resolves the node, calls `setGoal`, and, if recursive mode is enabled on a directory, pushes a new task containing its children to the front of the work queue. Non-recursive permission denial returns `EPERM`; otherwise stats are incremented and changed nodes emit a `SETGOAL` changelog entry.

## State and Persistence Behavior

Changing a file calls `fsnodes_changefilegoal`, may enqueue tape copies when tapeservers are available, updates ctime and checksum, and logs the changelog. Directories store the goal on the node. Stats accumulate in a shared array across subtasks.

## Dependencies and Integration Points

Dependencies include filesystem checksum/node/operations, `TaskManager`, protocol status constants, and `matotsserv` outside `METARESTORE`. It integrates storage goal changes with tape archival enqueueing.

## Risks and Edge Cases

The implementation assumes `stats_` is non-null whenever a result other than `kNoAction` is possible. Permission checks honor `EATTR_NOOWNER`, root UID, and owner UID. Only files/directories/trash/reserved nodes are actionable. Tape enqueueing happens for file goal changes and depends on tapeserver availability at execution time.

## Test Signals

Tests should cover changed/not-changed/not-permitted stats, recursive directory traversal, non-recursive permission failure, checksum/ctime/changelog updates, tape enqueueing, and metarestore build behavior without tapeserver integration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/master/setgoal_task.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/master/setgoal_task.h -->
# sources/distributed-fs/lizardfs/src/master/setgoal_task.h

## Purpose

`setgoal_task.h` declares `SetGoalTask`, the task abstraction for potentially recursive goal changes. The source was read as a complete 83-line header.

## Important APIs, Types, and Functions

The class derives from `TaskManager::Task`, defines result counters `kChanged`, `kNotChanged`, `kNotPermitted`, `kStatsSize`, and `kNoAction`, exposes `StatsArray`, constructors for batch and single-node style use, `execute`, `isFinished`, `generateDescription`, and `setGoal`.

## Control Flow

The header establishes one-inode-at-a-time task execution with optional generation of child tasks from the implementation.

## State and Persistence Behavior

State is held per task and shared stats pointer. Persistent metadata changes are performed by implementation methods.

## Dependencies and Integration Points

It depends on `TaskManager` and filesystem node definitions and is used by filesystem APIs implementing setgoal requests.

## Risks and Edge Cases

The batch constructor asserts a non-empty inode list. The alternate constructor leaves `inode_list_` empty and is suitable only for direct `setGoal`-style use unless initialized before `execute`.

## Test Signals

Compile coverage plus task-manager integration tests for recursive goal changes and direct `setGoal` behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/master/setgoal_task.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/master/settrashtime_task.cc -->
# sources/distributed-fs/lizardfs/src/master/settrashtime_task.cc

## Purpose

`settrashtime_task.cc` implements `SetTrashtimeTask`, a task-manager-backed operation for changing trash retention time over one or more inodes, optionally recursively. The source was read as a complete 115-line implementation.

## Important APIs, Types, and Functions

Methods are `execute`, `isFinished`, and `setTrashtime`. The task tracks inode list, current iterator, user ID, target trash time, set mode, and shared stats.

## Control Flow

Execution processes one inode, applies `setTrashtime`, queues child tasks for recursive directories, maps non-recursive permission denial to `EPERM`, updates stats, and emits a `SETTRASHTIME` changelog on change. `setTrashtime` supports set, increase, and decrease modes.

## State and Persistence Behavior

When changed, the node trash time and ctime are updated, checksum is recomputed, and trash nodes are reindexed in `gMetadata->trash` under their new `TrashPathKey`. Persistent replay is represented by the emitted changelog.

## Dependencies and Integration Points

Dependencies include filesystem checksum/operations, metadata trash map, node types, `TaskManager`, and protocol set-mode constants. It integrates with recursive metadata operations and trash subsystem indexing.

## Risks and Edge Cases

Stats pointer must be valid for actionable operations. Permission behavior mirrors setgoal. Reindexing trash entries uses `gMetadata->trash.at(old_trash_key)`, so missing old keys would throw or abort depending container behavior. Increase/decrease modes change only if the target moves in the requested direction.

## Test Signals

Tests should cover set/increase/decrease, trash-map rekeying, changed/not-changed/not-permitted stats, recursive traversal, permission failures, and changelog/checksum updates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/master/settrashtime_task.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/master/settrashtime_task.h -->
# sources/distributed-fs/lizardfs/src/master/settrashtime_task.h

## Purpose

`settrashtime_task.h` declares `SetTrashtimeTask`, the task abstraction for recursive trash-time changes. The source was read as a complete 82-line header.

## Important APIs, Types, and Functions

The class defines result counters and `StatsArray`, constructors for batched and direct usage, `execute`, `isFinished`, `generateDescription`, and `setTrashtime`. It stores inode iteration state, UID, trash time, set mode, and stats.

## Control Flow

The header defines the one-task-per-batch model; the implementation advances the current iterator and can enqueue child work.

## State and Persistence Behavior

Only in-memory task state is stored here. Metadata mutation and changelog persistence are in the implementation.

## Dependencies and Integration Points

It includes filesystem node and task manager types and is used by filesystem operations that change retention settings.

## Risks and Edge Cases

The batch constructor asserts non-empty input; the direct constructor leaves the inode vector empty and should not be used with `execute` without setup.

## Test Signals

Compile coverage and filesystem operation tests for set/increase/decrease trash-time changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/master/settrashtime_task.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/master/snapshot_task.cc -->
# sources/distributed-fs/lizardfs/src/master/snapshot_task.cc

## Purpose

`snapshot_task.cc` implements `SnapshotTask`, a task-manager-backed recursive snapshot/clone operation that copies filesystem nodes and queues child clones for directories. The source was read as a complete 254-line implementation.

## Important APIs, Types, and Functions

Important methods are `cloneNodeTest`, `cloneToExistingNode`, `cloneToNewNode`, `cloneToExistingFileNode`, `cloneChunkData`, two `cloneDirectoryData` overload declarations with the const overload implemented here, `cloneSymlinkData`, `emitChangelog`, `cloneNode`, and `execute`.

## Control Flow

`execute` clones the current source inode to the destination parent/name, advances the iterator, optionally ignores missing sources, and splices locally generated child tasks into the global work queue. `cloneNode` resolves source and destination parent, rejects trash/reserved sources, checks quota/type/overwrite constraints, clones over an existing node or creates a new node, updates checksums, emits or simulates changelog version advancement, and validates requested destination inode. Directories queue child snapshot tasks when `enqueue_work_` is true.

## State and Persistence Behavior

Snapshotting mutates in-memory metadata by creating/replacing nodes, copying mode/owners/timestamps/goal/trashtime/chunks/symlink paths/devices, updating parent stats and quota usage for file sizes, incrementing chunk file references, and emitting `CLONE` changelog records when enabled. Without changelog emission it increments `gMetadata->metaversion` directly.

## Dependencies and Integration Points

Dependencies include filesystem checksum, metadata, operations, quota checks/updates, chunk reference updates, `TaskManager`, `HString`, and node type definitions. Restore replay uses `fs_clone_node`, which links to this task via metarestore CMake.

## Risks and Edge Cases

Quota checks for file size use a delta of 1 before actual chunk copy, so deeper quota validation may be elsewhere. Existing file replacement unlinks and recreates the file if length/chunks differ. Chunk IDs missing from chunk metadata are logged as structure errors but cloning continues. The header declares a non-const `cloneDirectoryData` overload not implemented in this file, implying either inline/unused linkage expectations or dead declaration. Ignoring missing sources converts `ENOENT` to success.

## Test Signals

Tests should cover cloning each node type, overwrite rules, destination inode mismatch, recursive directory cloning, quota failures, missing source ignore behavior, chunk reference increments, stats/quota updates, and changelog versus metarestore metaversion behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/master/snapshot_task.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/master/snapshot_task.h -->
# sources/distributed-fs/lizardfs/src/master/snapshot_task.h

## Purpose

`snapshot_task.h` declares `SnapshotTask`, the task-manager-backed implementation of recursive snapshot creation. The source was read as a complete 124-line header.

## Important APIs, Types, and Functions

The class derives from `TaskManager::Task`, defines `SubtaskContainer` as `(inode, name)` pairs, has a constructor with source/destination/options, declares `cloneNode`, `execute`, `isFinished`, `generateDescription`, and protected clone helpers for node testing, existing/new nodes, file chunks, directories, symlinks, and changelog emission.

## Control Flow

The header documents that each clone task handles one inode and may enqueue new tasks for directory children. Constructor assertions enforce either a single subtask with an explicit destination inode or multiple subtasks with destination inode zero.

## State and Persistence Behavior

State includes original inode, destination parent/inode, overwrite and ignore-missing flags, changelog and enqueue-work flags, current subtask iterator, and a local task list. Persistent effects are performed by implementation through filesystem and changelog APIs.

## Dependencies and Integration Points

It depends on `TaskManager`, filesystem nodes, `HString`, and standard containers. It is used by snapshot filesystem operations and metarestore replay.

## Risks and Edge Cases

The class holds raw task pointers in intrusive lists and relies on `TaskManager` cleanup. Callers must choose flags carefully: `emit_changelog_` changes persistence behavior, and `enqueue_work_` determines whether directories are recursively cloned.

## Test Signals

Compile coverage and task-manager tests for recursive snapshots, explicit inode restore snapshots, overwrite handling, and cancellation/cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/master/snapshot_task.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/master/task_manager.cc -->
# sources/distributed-fs/lizardfs/src/master/task_manager.cc

## Purpose

`task_manager.cc` implements a small cooperative job manager for filesystem tasks that may need to be split across event-loop iterations. The file was read as a complete 128-line implementation.

## Important APIs, Types, and Functions

Implemented methods include `TaskManager::Job::finalize`, `finalizeTask`, `processTask`, `getInfo`, `TaskManager::submitTask` overloads, `processJobs`, `getCurrentJobsInfo`, and `cancelJob`.

## Control Flow

Submitting a task creates a `Job`, attaches a temporary callback to detect immediate completion, processes up to `initial_batch_size` tasks synchronously, and either returns the final status or enqueues the job with the caller callback and returns `WAITING`. `processJobs` rotates through the job list, executing one task per job until a task budget or `SignalLoopWatchdog` expiry. Finished tasks are erased; status errors finalize the entire job. Cancelling finalizes a matching job with `NOTDONE`.

## State and Persistence Behavior

The manager stores an in-memory list of jobs and a monotonically increasing job ID counter. It owns dynamically allocated tasks through intrusive lists and disposes them on job finalization/destruction. Persistent filesystem effects are performed by task implementations.

## Dependencies and Integration Points

Dependencies include `intrusive_list`, `JobInfo`, loop watchdog, filesystem metadata/node includes, and protocol status codes. It is integrated by remove, snapshot, setgoal, settrashtime, and other long-running filesystem operations.

## Risks and Edge Cases

Callback semantics differ for immediate versus queued completion: caller callback is only used if work remains after the initial batch. `cancelJob` finalizes but does not erase immediately; the next process pass removes finished jobs. Task implementations can push more tasks into the same intrusive list during execution, so iterator validity and task self-finish behavior are critical.

## Test Signals

Unit tests should cover immediate completion, queued completion callback, task-generated subtasks, error finalization, cancellation, job info reporting, rotation fairness across jobs, and watchdog-limited processing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/master/task_manager.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/master/task_manager.h -->
# sources/distributed-fs/lizardfs/src/master/task_manager.h

## Purpose

`task_manager.h` declares `TaskManager`, its abstract `Task`, and nested `Job` container used to process background filesystem work incrementally. The source was read as a complete 178-line header.

## Important APIs, Types, and Functions

`Task` declares pure virtual `execute` and `isFinished`. `Job` owns an intrusive task list, job ID, description, finish callback, and methods to finalize/process/add tasks. `TaskManager` exposes two `submitTask` overloads, `processJobs`, `getCurrentJobsInfo`, `cancelJob`, `workAvailable`, and `reserveJobId`.

## Control Flow

The header defines a cooperative model where each task receives the current timestamp and a work queue to which it may append/prepend more tasks. Jobs group the original task and all generated subtasks.

## State and Persistence Behavior

The manager state is runtime-only. Job descriptions and IDs are exposed for status; filesystem persistence belongs to tasks.

## Dependencies and Integration Points

It depends on intrusive lists, `JobInfo`, callbacks, memory/string/list/vector support, and is included by all task implementations in this subset.

## Risks and Edge Cases

Tasks must be heap-allocated and compatible with intrusive-list ownership. Misbehaving tasks that never finish or generate unbounded work can monopolize job capacity until watchdog/budget stops each processing tick.

## Test Signals

Compile coverage, lifecycle tests with mock tasks, and filesystem integration tests that inspect `JobInfo` while long operations run.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/master/task_manager.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/master/topology.cc -->
# sources/distributed-fs/lizardfs/src/master/topology.cc

## Purpose

`topology.cc` implements master network topology parsing and distance lookup for chunkserver placement. It reads a topology file mapping IP ranges to rack IDs and answers whether two IPs are same machine, same rack, or different racks. The file was read as a complete 456-line implementation.

## Important APIs, Types, and Functions

Important functions are `topology_parsenet`, `topology_distance`, `topology_parseline`, `topology_load`, `topology_reload`, `topology_term`, and `topology_init`. Globals are `racktree`, `TopologyFileName`, and `gPreferLocalChunkserver`.

## Control Flow

`topology_init` initializes globals, loads config, and registers reload/destruct hooks. Reload reads `TOPOLOGY_FILENAME` and `PREFER_LOCAL_CHUNKSERVER`, then loads the topology file. Each non-comment line is parsed into an IP/network/range and rack ID; intervals are added to a new interval tree, then swapped in only after successful read. `topology_distance` returns 0 for identical IPs when local preference is enabled, otherwise compares rack IDs from the interval tree and returns 1 or 2.

## State and Persistence Behavior

The topology is runtime state built from the config file into an interval tree. Missing or unreadable files leave an existing tree unchanged, or disable topology if no previous tree exists. No persistent state is written.

## Dependencies and Integration Points

Dependencies include config, event loop, logging, and `master/itree.h`. Placement code can use `topology_distance` to prefer local or rack-aware chunkserver selections.

## Risks and Edge Cases

Network parsing is manual and supports `*`, single IP, CIDR bits, explicit mask, and IP ranges. Invalid lines are skipped with warnings. `itree_find` behavior for IPs outside configured intervals determines their default rack comparison; if the default ID is shared, unknown hosts may look same-rack. Reload frees/replaces `TopologyFileName` and can keep stale topology on read errors.

## Test Signals

Tests should cover all network syntaxes, invalid octets/masks/ranges, comments/garbage, missing file behavior with and without prior tree, local-preference toggle, interval overlaps if supported by `itree`, and placement integration using distance values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/master/topology.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/master/topology.h -->
# sources/distributed-fs/lizardfs/src/master/topology.h

## Purpose

`topology.h` declares the public topology API: distance lookup between two IP addresses and module initialization. The source was read as a complete 26-line header.

## Important APIs, Types, and Functions

The header declares `uint8_t topology_distance(uint32_t ip1, uint32_t ip2)` and `int topology_init(void)`.

## Control Flow

No implementation flow is present. Callers initialize the module and later query distances.

## State and Persistence Behavior

The header owns no state. The implementation loads topology config into runtime interval-tree state.

## Dependencies and Integration Points

It depends on `common/platform.h` and integer types. It is used by placement logic that wants rack/locality awareness.

## Risks and Edge Cases

Callers should treat return values as coarse classes, not physical distances beyond the implementation's 0/1/2 semantics.

## Test Signals

Compile coverage and placement tests that mock or load topology and observe distance effects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/master/topology.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/metadump/CMakeLists.txt -->
# sources/distributed-fs/lizardfs/src/metadump/CMakeLists.txt

## Purpose

`src/metadump/CMakeLists.txt` builds and installs the `mfsmetadump` executable. The source was read as a complete 6-line CMake file.

## Important APIs, Types, and Functions

It adds the current source directory to include paths, collects all local sources into `METADUMP_SOURCES`, creates `mfsmetadump`, leaves `target_link_libraries` empty, and installs the binary into `${SBIN_SUBDIR}`.

## Control Flow

CMake configure/generate flow discovers sources with `aux_source_directory`, then build flow compiles the executable.

## State and Persistence Behavior

No runtime persistence. Build output is the installed `mfsmetadump` utility.

## Dependencies and Integration Points

It integrates the standalone metadata dump reader with the project install layout. The empty link line implies `mfsmetadump.cc` is intended to compile with only common headers or inherited build defaults.

## Risks and Edge Cases

`aux_source_directory` can accidentally pick up new local files. Empty linking may break if the implementation starts requiring common library objects beyond header-only helpers/macros.

## Test Signals

Build `mfsmetadump`, run install packaging checks, and execute the binary on fixture metadata files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/metadump/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/metadump/mfsmetadump.cc -->
# sources/distributed-fs/lizardfs/src/metadump/mfsmetadump.cc

## Purpose

`mfsmetadump.cc` implements a standalone utility that reads binary LizardFS/MooseFS metadata files and prints a textual dump of headers, nodes, edges, free inode lists, chunks, and unknown sections. The file was read as a complete 540-line implementation.

## Important APIs, Types, and Functions

Important functions are `dispchar`, `chunk_load`, `print_name`, `fs_loadedge`, `fs_loadnode`, `fs_loadnodes`, `fs_loadedges`, `fs_loadfree`, `hexdump`, `fs_load`, `fs_load_2x`, `fs_load_20`, `fs_load_29`, `fs_loadall`, and `main`. It uses metadata signatures and type constants from `MFSCommunication.h` and binary decoding helpers from `datapack.h`.

## Control Flow

`main` requires exactly one metadata filename and calls `fs_loadall`. The loader reads the 8-byte signature, selects legacy 1.5/1.6 layout or sectioned 2.0/2.9 layout, and prints formatted records. Legacy files read global metadata header, nodes, edges, free list, and chunk table. Sectioned files iterate 16-byte section headers until EOF marker, dispatching known sections (`NODE 1.0`, `EDGE 1.0`, `FREE 1.0`, `CHNK 1.0`) or hex-dumping unknown sections. Node parsing branches by type and prints type-specific fields, file chunks, and session IDs.

## State and Persistence Behavior

The utility is read-only: it opens a metadata file and writes formatted text to stdout/stderr. It does not modify metadata. Parsing state is local buffers and file offsets.

## Dependencies and Integration Points

It depends on C stdio, metadata protocol constants, `datapack` endian decoders, and build installation as `mfsmetadump`. It is an operational/debugging tool for inspecting metadata images.

## Risks and Edge Cases

Large stack buffer `unodebuff` reserves space for maximum chunk/session batches. The parser trusts many length fields and reports errors when reads or section offsets do not match. Output replaces non-printable names with dots, so dumps are not lossless for arbitrary byte names. Unknown sections are hex-dumped rather than semantically parsed. `fopen` uses text mode `"r"`, which is safe on POSIX but not portable to newline-transforming platforms.

## Test Signals

Tests should run the tool against fixture metadata signatures 1.5, 1.6, 2.0, and 2.9; corrupt/truncated files; unknown sections; nodes with long chunk lists; symlink/device/trash/reserved entries; and lock-id versus no-lock-id chunk records.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/metadump/mfsmetadump.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/metalogger/CMakeLists.txt -->
# sources/distributed-fs/lizardfs/src/metalogger/CMakeLists.txt

## Purpose

`src/metalogger/CMakeLists.txt` builds the LizardFS metalogger library, tests, and `mfsmetalogger` executable. The source was read as a complete 17-line CMake file.

## Important APIs, Types, and Functions

It sets include directories, defines `METALOGGER`, `APPNAME=mfsmetalogger`, and examples subdir, collects sources, builds a `metalogger` library with local sources plus `../master/changelog.cc` and `../master/masterconn.cc`, links `mfscommon`, creates unit tests, builds `mfsmetalogger` from `${MAIN_SRC}`, optionally links PAM/systemd, and installs the executable.

## Control Flow

CMake configure flow collects source lists and declares library/test/executable targets. Build flow links shared master connection/changelog code into metalogger.

## State and Persistence Behavior

No runtime persistence is defined here. The resulting metalogger binary persists metadata/changelog data according to its source code.

## Dependencies and Integration Points

It integrates metalogger with common code, master connection code, authentication/systemd libraries, and the project install/test macros.

## Risks and Edge Cases

Directly including master source files creates tight coupling between master and metalogger builds. Compile definitions alter shared code behavior, so tests must cover the `METALOGGER` variant. Optional systemd/PAM linking can change deployment dependencies.

## Test Signals

Build target success, `create_unittest(metalogger ...)` execution, packaging/install checks, and smoke tests connecting a metalogger to a master.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/metalogger/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/metalogger/init.h -->
# sources/distributed-fs/lizardfs/src/metalogger/init.h

## Purpose

`metalogger/init.h` defines the metalogger module initialization tables used by the common application startup framework. The source was read as a complete 42-line header.

## Important APIs, Types, and Functions

It defines `runfn`, `run_tab`, and three arrays: `RunTab` containing `masterconn_init` named "connection with master", and empty sentinel-only `LateRunTab` and `EarlyRunTab`.

## Control Flow

At application startup, the common runner walks these tables and calls `masterconn_init` as the metalogger's primary initialization step. Sentinel entries with null function and `"****"` terminate each table.

## State and Persistence Behavior

The header owns no persistent state. Initialization connects the metalogger process to the master through `masterconn_init`.

## Dependencies and Integration Points

It includes `master/masterconn.h` even though it lives under metalogger, reflecting shared connection code. It is tied to the common main/init table convention.

## Risks and Edge Cases

Because the arrays are defined in a header, include discipline matters to avoid multiple-definition problems; the project likely includes this as a generated/app-specific init header in one translation unit. No early or late init hooks are registered here.

## Test Signals

Build/link success for `mfsmetalogger`, startup smoke tests verifying `masterconn_init` runs, and failure-path tests for master connection initialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/metalogger/init.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/metarestore/CMakeLists.txt -->
# sources/distributed-fs/lizardfs/src/metarestore/CMakeLists.txt

## Purpose

`src/metarestore/CMakeLists.txt` builds the `mfsmetarestore` library, tests, and executable used to restore metadata from metadata files plus changelogs. The source was read as a complete 29-line CMake file.

## Important APIs, Types, and Functions

It includes current and master directories, defines `METARESTORE`, `APPNAME=mfsmetarestore`, and docs subdir, collects metarestore sources, globs master filesystem sources, selects hstring storage implementation based on DB availability, builds a `metarestore` library with master metadata/restore/chunks/quota/task/snapshot/setgoal/settrashtime/locks dependencies, links `mfscommon` and optional Judy, creates unit tests, builds `mfsmetarestore`, links PAM, and installs it.

## Control Flow

CMake configure selects the source set and optional libraries; build flow compiles a master-like metadata engine under `METARESTORE` definitions so changelogs can be replayed offline.

## State and Persistence Behavior

The build file itself has no runtime state. It produces an executable that reads metadata/changelogs and writes restored metadata according to metarestore source behavior.

## Dependencies and Integration Points

This target is deeply integrated with master filesystem implementation files, `restore.cc`, quota database, task manager, snapshot and recursive set operations, hstring storage, common code, optional DB/Judy support, PAM, and project test/install macros.

## Risks and Edge Cases

Globbed master filesystem sources can unintentionally include or omit files as the master changes. `METARESTORE` compile definitions disable or alter runtime service integrations, so source code must keep conditional paths correct. Pulling many master files into an offline tool risks link drift when master dependencies change.

## Test Signals

Build `metarestore` and `mfsmetarestore`, run metarestore unit tests, replay fixture changelogs containing snapshot/setgoal/settrashtime/quota/lock operations, and verify restored metadata checksums against master-generated metadata.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/metarestore/CMakeLists.txt -->
