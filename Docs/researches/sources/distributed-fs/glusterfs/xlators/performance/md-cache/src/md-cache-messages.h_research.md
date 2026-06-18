# sources/distributed-fs/glusterfs/xlators/performance/md-cache/src/md-cache-messages.h

## Purpose
Defines structured log message IDs for the md-cache translator.

## Important APIs, types, and functions
`GLFS_MSGID(MD_CACHE, ...)` declares IDs for no memory, discard update, cache update, IPC upcall failure, and missing xattr-cache support.

## Control flow
No logic is implemented. The md-cache C implementation includes this header for structured logging.

## State and persistence behavior
Message IDs are stable external log identifiers and should be appended rather than removed or reordered.

## Dependencies and integration points
Depends on `glfs-message-id.h` and the global `MD_CACHE` message component. Integrates with logging, upcall diagnostics, and support tooling.

## Risks and test signals
Risks are ID reuse, missing IDs for new warning/error paths, and component mismatch. Test signals include compile coverage and runtime log assertions for cache update, discard update, upcall failure, and no-xattr-cache paths.
