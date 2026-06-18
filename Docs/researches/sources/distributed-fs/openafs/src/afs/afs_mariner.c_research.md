# sources/distributed-fs/openafs/src/afs/afs_mariner.c

## Purpose
`afs_mariner.c` implements the legacy Mariner fetch/store monitoring facility. It keeps a small ring of vcache-to-name associations and sends one-line UDP status messages to a configured Mariner host.

## Important APIs, types, and functions
Exported state includes `afs_server`, `afs_mariner`, and `afs_marinerHost`. `afs_AddMarinerName` records a name and vcache pointer in a 10-entry ring. `afs_GetMariner` resolves a vcache back to the last recorded short name. `afs_MarinerLogFetch` logs a fetch message. `afs_MarinerLog` formats and sends the UDP packet. `shutdown_mariner` clears the ring and disables Mariner state.

## Control flow
Callers associate file names with vcaches through `afs_AddMarinerName`. Fetch logging calls `afs_MarinerLogFetch`, which delegates to `afs_MarinerLog` with a fixed `fetch$Fetching` prefix. `afs_MarinerLog` builds a sockaddr for port 2106 on `afs_marinerHost`, allocates a small buffer, concatenates the message, optional file name, and newline with bounds checks, releases the AFS global lock, sends through `rxi_NetSend` on `afs_server->socket`, reacquires the lock, and frees the buffer.

## State and persistence behavior
The only state is in memory: ten names, ten vcache pointers, a ring pointer, and the current Mariner host/enabled flag. It does not persist messages and intentionally ignores send failures.

## Dependencies and integration points
It depends on Rx's kernel socket send path, OSI small-space allocation, global lock macros, and vcache pointers supplied by lookup/fetch code. It is initialized and shut down as part of vnode/cache manager teardown paths and relies on `afs_server` having a valid socket.

## Risks and edge cases
Names are truncated to 19 bytes plus terminator. Ring entries are not reference-counted, so stale vcache pointers are possible until overwritten; callers only use them for equality lookup and logging text. UDP send errors are ignored by design. Buffer concatenation guards prevent overflow but silently drop overlong messages.

## Test signals
Test enabling Mariner host logging, name truncation, ring wraparound, fetch log packet formatting, operation with null vcache, and shutdown clearing vcache slots and flags.
