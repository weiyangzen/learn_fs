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
