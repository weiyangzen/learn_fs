# sources/distributed-fs/moosefs/mfsmaster/topology.c

## Purpose
`topology.c` loads the master network topology configuration and maps IP address intervals to rack/path ids. It provides rack id lookup and a distance metric used by chunk placement/read selection to prefer closer or more failure-independent chunkservers.

## Important APIs, Types, And Functions
The module stores IP intervals in an `itree` and maps rack names to numeric ids through a local hash table plus id array. `rackhashentry` stores rack name, id, hash, and chain link.

Key internal functions include `topology_parsenet()`, rack-name hash/id helpers, stash/restore/cleanup helpers for safe reload, `topology_parseline()`, `topology_load()`, `topology_reload()`, and `topology_term()`.

Exported APIs are `topology_get_rackid()`, `topology_distance()`, and `topology_init()`.

## Control Flow
`topology_reload()` chooses `TOPOLOGY_FILENAME` or the default `ETC_PATH "/mfs/mfstopology.cfg"`, with a compatibility check for the older `ETC_PATH "/mfstopology.cfg"`. It then calls `topology_load()`.

`topology_load()` opens the file, stashes the current rack-name map, parses non-empty non-comment lines, adds intervals to a new tree, and only swaps the live tree after a successful read. On read error it frees the new tree and restores the previous rack-name map, leaving the current topology active.

`topology_parsenet()` accepts `*`, single IPv4 addresses, CIDR bit counts, dotted masks, and address ranges. `topology_parseline()` expects `network rack_path`, where the rack path is a non-whitespace token and path hierarchy is represented by `|`.

`topology_distance()` returns 0 for identical IPs, 1 for different IPs with the same rack id, and higher values based on divergent rack-path hierarchy depth for different rack ids.

## State, Persistence, And Dependencies
Runtime state is `racktree`, `TopologyFileName`, `rackhashtab`, `rackidtab`, and stash copies used during reload. The topology file is external configuration, not MooseFS metadata. No changelog or metadata persistence is involved.

Dependencies include `itree.h` for interval lookup/storage, `hashfn.h` for rack-name hashing, `cfg.h` for configuration, `main.h` lifecycle hooks, `mfsalloc.h` for realloc, POSIX file APIs, and logging/assertions.

## Integration Points
`chunks.c` calls `topology_get_rackid()` and `topology_distance()` for chunk placement, rack-awareness, and client/server distance ranking. `init.h` registers `topology_init()` as the net topology module. `main_reload_register()` enables runtime reloads and `main_destruct_register()` cleans up at shutdown.

## Risks
`topology_rackid_to_rackname()` returns `rackidtab[rackid]->rackname` without checking for a null slot when `rackid < rackidnext`. The current allocation path fills ids densely, but corrupted state would crash distance calculation.

Overlapping intervals are delegated to `itree_add_interval()` semantics; the file does not explicitly detect or warn about overlap conflicts.

Rack ids are assigned in file-parse order and are not persisted. They are safe for runtime comparisons but should not be treated as stable external identifiers across reloads.

## Test Signals
Tests should cover every accepted network syntax, malformed IP/mask/range handling, comments and trailing garbage, missing file behavior with and without existing topology, reload read-error rollback, overlap behavior, default path fallback warning, rack hierarchy distance values, and chunk placement behavior using same host/same rack/different rack inputs.
