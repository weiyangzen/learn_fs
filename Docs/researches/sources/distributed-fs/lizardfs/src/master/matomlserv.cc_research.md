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
