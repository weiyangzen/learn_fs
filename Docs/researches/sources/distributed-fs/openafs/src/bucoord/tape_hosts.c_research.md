# sources/distributed-fs/openafs/src/bucoord/tape_hosts.c

## Purpose
Implements tape-host command handlers and BUDB text-block persistence. It adds, deletes, lists, parses, saves, and refreshes the tape coordinator host list stored in `bc_globalConfig->tapeHosts`.

## Important APIs, Types, And Functions
Command handlers are `bc_AddHostCmd`, `bc_DeleteHostCmd`, and `bc_ListHostsCmd`. Support functions are `bc_ClearHosts`, `bc_ParseHosts`, `bc_SaveHosts`, and `bc_UpdateHosts`.

## Control Flow
Add/delete commands lock `TB_TAPEHOSTS`, refresh the local list from BUDB, parse the optional port offset, call `bc_AddTapeHost` or `bc_DeleteTapeHost`, save the text block back through `bc_SaveHosts`, and unlock. Listing refreshes and prints every host/offset pair. Parsing rewinds the text stream, reads `hostname port` lines, resolves host names, allocates `bc_hostEntry` nodes, and replaces the global host list. Saving truncates the stream, writes one line per host, calls `bcdb_SaveTextFile`, increments local version, and updates size. Updating compares BUDB text version, locks if needed, opens a temp stream, downloads text, fetches version, parses, and unlocks if it acquired the lock.

## State And Persistence
The in-memory tape host list mirrors BUDB configuration text type `TB_TAPEHOSTS`. Persistent writes require a BUDB text lock. On Unix, downloaded text streams are temporary unlinked files managed by `ubik_db_if.c`.

## Dependencies And Integration Points
Depends on `config.c` host add/delete helpers, BUDB text locking/versioning, OpenAFS command/com_err APIs, and `bc_globalConfig`. `dump.c` uses the resulting host list to connect to butc by port offset.

## Risks And Test Signals
`bc_ParseHosts` does not validate `sscanf` return count and can reuse previous `port` values on malformed lines. Resolver failures still create entries with zero address, later producing `BC_NOHOSTENTRY`. Some refresh error returns bypass unlock paths. Duplicate prevention happens in `config.c` by port offset, not by hostname. Test signals include add/delete/list with default and nonzero offsets, malformed text lines, unresolved host entries, stale version refresh, save failure session-only warning, lock contention, and butc connection lookup by offset.
