# sources/distributed-fs/lizardfs/src/master/masterconn.cc

## Purpose

`masterconn.cc` owns the outbound connection from a metalogger or shadow master to the active master. It registers the process with the master, receives metadata changelog updates, downloads full metadata/changelog/session images when needed, and integrates with the event loop for reconnects, packet I/O, reloads, shutdown, and shadow promotion cleanup.

The file is compiled in two distinct modes. With `METALOGGER`, it behaves as a metalogger client that stores metadata and changelog files locally. Without `METALOGGER`, it is the shadow-master replication client and applies changelog entries into in-memory filesystem state with `restore()`.

## Important APIs, Types, And Functions

- `struct masterconn`: singleton connection state, including socket/mode, packet buffers, outbound packet queue, resolved master address, download state, temp metadata fd, file offsets, event-loop handles, master version, replication state, and changelog-apply-error retry timer.
- `MasterConnectionState`: high-level replication state: none, synchronized, downloading, dump request pending, or limbo after the master refuses/fails to dump metadata.
- `masterconn_init()`: configures `MASTER_HOST`, `MASTER_PORT`, `BIND_HOST`, timeouts, metadata backup count, optional metalogger changelog state, creates the singleton, starts the initial connection, and registers event-loop callbacks.
- `masterconn_is_connected()`: reports true only after the socket is in header/data mode and shadow registration has returned a nonzero master version.
- `masterconn_sendregister()`, `masterconn_registered()`: build and process registration messages. Shadow registrations include local metadata version when synchronized; metaloggers register with package version and last changelog version.
- `masterconn_metachanges_log()`: validates and applies `MATOML_METACHANGES_LOG`, detects changelog gaps, restores entries into shadow memory when synchronized, appends to changelog, and advances `lastlogversion`.
- `masterconn_download_init()`, `masterconn_download_start()`, `masterconn_download_data()`, `masterconn_download_next()`, `masterconn_download_end()`: implement the metadata/changelog/session download pipeline with offsets, CRC checks, temp files, fsync, retries, renames, and shadow `fs_loadall()` after a complete set.
- `masterconn_handle_changelog_apply_error()`, `masterconn_request_metadata_dump()`, `masterconn_changelog_apply_error()`: recover from malformed or inconsistent changelogs by forcing a fresh download for old masters or asking newer masters to prepare an up-to-date metadata image.
- `masterconn_read()`, `masterconn_write()`, `masterconn_desc()`, `masterconn_serve()`, `masterconn_reconnect()`: nonblocking packet I/O and event-loop integration.
- `masterconn_reload()`, `masterconn_become_master()`, `masterconn_term()`: config reload, promotion cleanup, and destruction.

## Control Flow

Initialization is gated by personality in non-metalogger builds: only shadow masters start this module. The module reads config, optionally initializes metalogger changelog state, creates `masterconnsingleton`, attempts `masterconn_initconnect()`, and registers poll/time/reload/exit callbacks.

Connection setup resolves bind and master addresses, creates a nonblocking TCP socket, optionally binds to `BIND_HOST`, and either completes immediately or enters `CONNECTING`. `masterconn_connecttest()` finalizes async connect. `masterconn_connected()` switches to header-read mode, initializes packet queues, sends registration, and starts a metadata download if `lastlogversion` is zero.

Packet reads use a two-state framing loop: read 8-byte header, allocate a payload if the declared size is nonzero and below `MaxPacketSize`, then dispatch by type in `masterconn_gotpacket()`. Unknown packet types and deserialization failures kill the session. Writes drain a linked list of packet buffers and update byte counters.

Metadata synchronization proceeds as a fixed sequence: metadata image, first changelog, second changelog, sessions. Each `DOWNLOAD_DATA` reply is checked for expected offset, bounded length, file-size limits, write result, CRC, and fsync success. On completion, temp files are renamed into their live names. For shadow masters, after sessions are downloaded the module loads all downloaded state with `fs_loadall()`, sets `lastlogversion` to filesystem version minus one, and enters synchronized state.

Changelog streaming is linear. If the incoming version is not `lastlogversion + 1`, the module considers changes lost and requests recovery. Shadow masters apply entries through `restore()` only while synchronized; metaloggers primarily persist the changelog.

The periodic reconnect hook starts a new connection while free and running. If in `kLimbo`, it periodically resends the metadata dump request when the timer expires.

## State And Persistence Behavior

Persistent effects are centered on metadata, changelog, and sessions files. File names are selected by build mode: normal master metadata names for shadow masters, `_ml` names for metaloggers. Downloads write `*.tmp` files first, then rename into live paths. Metadata downloads are verified with `metadataGetVersion()`, and successful metadata replacement rotates old copies according to `BACK_META_KEEP_PREVIOUS`.

`lastlogversion` is the replication cursor. Metaloggers recover it by scanning the tail of the changelog file and truncating garbage after the last complete newline if needed. Shadow masters update it from loaded filesystem metadata and every accepted changelog entry.

In-memory connection state is singleton-based and manually owns packet buffers, file descriptors, event-loop handles, address resolution cache, and temp download progress. `masterconn_beforeclose()` closes the metadata fd and unlinks temp files on disconnect.

## Dependencies And Integration Points

This module depends on the common event loop, TCP helpers, config, datapack encoding, CRC, metadata validation, file rotation, slogger, watchdogs, and protocol serializers from `protocol/matoml.h`, `protocol/mltoma.h`, and `protocol/MFSCommunication.h`.

For shadow masters it integrates with `filesystem.h`, `restore.h`, and `personality.h`: it unloads/loads metadata, applies changelog entries, erases lockfile messages before download, and unregisters itself when promoted to master. It also sends the client-listen port to newer masters via `mltoma::matoclport` so the active master can know the shadow's client endpoint.

For metaloggers it integrates with changelog initialization, changelog migration, forced log rotation, and periodic metadata downloads.

## Risks And Edge Cases

- Packet parsing is manual and stateful. Header/payload size mismatches, payloads above `MaxPacketSize`, and unknown packet types correctly kill the session, but malformed inputs exercise raw allocation/free paths.
- Download retry logic retries failed writes, CRC mismatches, and fsync failures up to five times, but the same offset is requested again. Tests should cover partial writes and repeated bad chunks.
- `fsync()` is called after each downloaded block, which favors safety but can make large metadata downloads expensive.
- Changelog gap handling depends on master version. Old masters force local metadata discard immediately; newer masters require the dump-request/limbo flow.
- The singleton/event-loop lifecycle is delicate during promotion. `masterconn_become_master()` unregisters selected time hooks and calls `masterconn_term()`.
- Several paths are build-mode dependent under `METALOGGER`; behavior should be tested in both build configurations.
- `masterconn_is_connected()` is stricter than socket connected: it also requires a successful registration response.

## Test Signals

Useful tests include registration against old and new master protocol versions, shadow metadata-version mismatch forcing a download, changelog gap recovery, malformed changelog restore error paths, full metadata/changelog/session download with CRC and offset checks, temp-file cleanup on disconnect, config reload changing master address, NOP keepalive timeout behavior, and promotion from shadow to master. Fault injection around `write`, `pwrite`, `fsync`, `rename`, and metadata validation would exercise the highest-risk branches.
