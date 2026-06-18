# sources/distributed-fs/glusterfs/xlators/cluster/dht/src/dht-shared.c

## Purpose
Provides shared DHT translator lifecycle, options, state dumping, reconfiguration, decommission handling, regex initialization, rebalance setup, and method-table initialization used by distribute, NUFA, and switch variants.

## Important APIs and Functions
- `dht_priv_dump` and `dht_inodectx_dump`: statedump hooks for translator private state and per-inode layout state.
- `dht_fini`: releases layouts, subvolume arrays/status, DU stats, decommission state, xattr-name strings, regexes, locks, pools, and private config.
- `mem_acct_init`: initializes DHT memory accounting.
- `dht_reconfigure`: updates runtime options including lookup behavior, min-free thresholds, layout spread, readdir optimization, migration/durability, rebalance stats/throttle, decommissioned bricks, regexes, weighting, and readdirp.
- `dht_init`: allocates `dht_conf_t`, initializes locks/pools, parses rebalance options, discovers subvolumes/local subvolumes, initializes layouts, xattr names, regexes, methods, and reachable-leaf mapping.
- `dht_options`: declares the volume option table exported as `options`.

## Control Flow
Initialization validates child presence, allocates `dht_conf_t`, optionally builds `gf_defrag_info_t` for rebalance commands, parses base options, initializes child subvolume arrays and optional local-subvolume lists, parses decommissioned bricks, compiles rsync/extra hash regexes, initializes file/dir layouts, creates local and lock pools, derives xattr keys from `xattr-name`, stores `this->private`, then initializes subvolume range and DHT method callbacks. Any error frees partially allocated state.

Reconfiguration mirrors a subset of init: it validates boolean/string options, updates thresholds and flags in place, adjusts active defrag thread count/stats, parses or clears decommissioned bricks, recompiles regexes under `conf->lock`, and updates weighting/readdirp. Dump functions take `subvolume_lock` when walking mutable subvolume state.

## State and Persistence
All state is in-memory translator state except child xattrs used by other files. `dht_conf_t` holds subvolume lists, status arrays, layouts, generation, DU stats, decommissioned brick pointers, regex objects, xattr key strings, lock pools, defrag queues, option flags, and method callbacks. Reconfigure changes affect future placement/lookup/heal behavior without persisting by itself.

## Dependencies and Integration Points
Depends on libglusterfs dict/options/statedump/mem-pool/logging APIs, DHT layout/subvolume initialization helpers, defrag/rebalance structures, regex library, and child translator graph traversal. `dht.c`, `nufa.c`, and `switch.c` all reuse this init/fini/reconfigure/options surface.

## Risks
- Error cleanup is manual and not identical to `dht_fini`; future allocations can leak unless added to both paths.
- Reconfigure mutates live fields while operations may be active; only regex updates take `conf->lock`.
- Decommission parsing fails on unknown brick names and keeps stateful counters that must be reset exactly.
- `dht_priv_dump` uses `TRY_LOCK`; dump output can be skipped under contention.
- Rebalance pattern parsing stores pointers into duplicated strings owned by list nodes, making ownership subtle.

## Test Signals
No direct tests in this subset. Expected coverage should come from volume-option parsing, rebalance, decommission/remove-brick, statedump, and translator init tests. Useful targeted tests would validate xattr-name derivation, reconfigure decommission add/remove, invalid child names, regex `"none"`, throttle parsing, and cleanup after partial init failure.
