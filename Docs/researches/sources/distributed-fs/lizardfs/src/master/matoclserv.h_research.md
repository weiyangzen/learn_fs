# sources/distributed-fs/lizardfs/src/master/matoclserv.h

## Purpose

`matoclserv.h` declares the public interface for the master-to-client service implemented by `matoclserv.cc`. It exposes statistics, chunk-operation callbacks, session/open-file helpers, startup/shutdown hooks, and admin broadcast notifications used by other master subsystems.

## Important APIs

- `void matoclserv_stats(uint64_t stats[5])`: returns and resets packet/byte counters. The implementation fills received packets, sent packets, received bytes, and sent bytes; the fifth array slot is currently unused by the implementation.
- `void matoclserv_chunk_status(uint64_t chunkid, uint8_t status)`: callback from the chunk layer when a delayed write/truncate-related chunk operation finishes. It finds the waiting connection and serializes the delayed client response.
- `void matoclserv_add_open_file(uint32_t sessionid, uint32_t inode)`: records an open inode for a session, creating a session entry for old filesystem-created sessions if necessary.
- `void matoclserv_remove_open_file(uint32_t sessionid, uint32_t inode)`: removes an inode from a session open-file list and logs corruption if the session is absent.
- `int matoclserv_sessionsinit(void)`: loads or initializes persisted client session state and session timeout configuration.
- `int matoclserv_networkinit(void)`: initializes the listening socket, reloadable configuration, I/O limits, and event-loop callbacks.
- `void matoclserv_session_unload(void)`: frees all session records and their open-file/info allocations.
- `void matoclserv_broadcast_metadata_saved(uint8_t status)`: sends delayed admin save-metadata responses to clients waiting for completion.
- `void matoclserv_broadcast_metadata_checksum_recalculated(uint8_t status)`: sends delayed admin checksum-recalculation responses.

Several older notify declarations are left commented out, suggesting previous or planned client notification hooks for attribute/link/unlink/parent changes that are not part of the active interface.

## Control Flow And Integration

Startup code calls `matoclserv_sessionsinit()` before or alongside master metadata startup, then `matoclserv_networkinit()` to expose the client/admin port. Chunkserver or filesystem code calls `matoclserv_chunk_status()` after operations that were delayed in `matoclserv.cc`. Filesystem/session code can call the open-file helpers to keep persisted sessions aligned with acquired inodes.

Metadata dumping/checksum code calls the broadcast helpers when background admin-requested operations finish. Shutdown code can call `matoclserv_session_unload()` through the event-loop destructor path, though `matoclserv_term()` also invokes it.

## State And Persistence Behavior

The header declares no concrete state, but the APIs expose stateful behavior. Session initialization and unload manage the global session list and the sessions file. Chunk status and open-file helpers mutate live sessions/connections in `matoclserv.cc`. Broadcast helpers scan live client connections for matching admin tasks.

## Dependencies And Risks

The header depends only on `common/platform.h` and integer types, keeping callers decoupled from the large protocol implementation. The main API risk is callback ordering: `matoclserv_chunk_status()` and broadcast functions assume the network module is initialized and live connection/session lists are valid. `matoclserv_stats()` requires callers to pass an array with at least five entries even though only four counters are populated.

## Test Signals

Compile tests should include this header from chunk, filesystem, and startup modules. Integration tests should verify chunk-status callbacks after client disconnect, stats reset behavior, open-file add/remove on restored and missing sessions, session init with absent/corrupt sessions files, and admin broadcast delivery only to clients waiting for the corresponding task.
