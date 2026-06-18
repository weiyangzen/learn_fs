# sources/distributed-fs/coda/coda-src/venus/9pfs.h

## Purpose
This header defines the Venus 9P protocol constants, wire structs, and `plan9server` class interface used by `9pfs.cc`.

## Important APIs, Types, and Functions
It lists legacy and dotl message opcodes, protocol flags, special tag/fid values, permission bits, qid types, open flags, dotl open/unlink flags, getattr/setattr masks, and `V9FS_MAGIC`. `plan9_qid`, `plan9_stat`, `plan9_stat_dotl`, and `plan9_statfs` model wire payloads. `plan9server` owns the mariner connection, fid list, packet buffer, negotiated message size, protocol variant, all receive handlers, fid helpers, stat/read helpers, public `main_loop`, `pack_dirent`, and `fidmap_replace_cfid`.

## Control Flow
The header has no executable flow but documents the full dispatcher surface. The handler declarations show which requests can yield outside transactions and which unsupported operations are explicit.

## State and Persistence Behavior
Class state is per-client transient protocol state. Persistent effects occur only through handler implementations. Constants such as qid and stat masks define how Venus state is exposed to clients.

## Dependencies and Integration Points
It includes C system types, `dlist`, and `mariner`; after C declarations it exposes C++ Venus integration. It is included by `9pfs.cc`, mariner code that creates a server, and worker code that updates fids.

## Risks and Test Signals
Risks are protocol drift against Linux 9p clients, macro arrays defined in a header causing duplicate definitions if included by multiple translation units, and inconsistent constants between header and handlers. Build tests should include all users; runtime tests should negotiate 9P2000, 9P2000.u, and 9P2000.L and verify stat/open flag encodings.
