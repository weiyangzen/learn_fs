# sources/distributed-fs/glusterfs/xlators/cluster/ec/src/ec-heald.c

## Purpose
Implements the EC self-heal daemon worker side: per-subvolume index healers, full-sweep healers, management-operation dispatch, thread initialization, wakeups, and teardown. It turns CLI/management SHD operations and dirty-index entries into explicit `EC_XATTR_HEAL` getxattr calls on the EC xlator.

## Important APIs, types, and functions
Public functions are `ec_xl_op()`, `ec_selfheal_daemon_init()`, `ec_shd_index_healer_wake()`, and `ec_selfheal_daemon_fini()`. Locality and naming helpers are `ec_shd_is_subvol_local()` and `ec_subvol_name()`. Thread lifecycle is handled by `ec_shd_healer_init()`, `ec_shd_healer_spawn()`, `ec_shd_full_healer_spawn()`, `ec_shd_index_healer_spawn()`, `ec_shd_healer_wait()`, and `__ec_shd_healer_wait()`. Index healing uses `ec_shd_index_inode()`, `ec_shd_index_sweep()`, `ec_shd_index_heal()`, and `ec_shd_index_purge()`. Full traversal uses `ec_shd_full_sweep()` and `ec_shd_full_heal()`. `ec_shd_selfheal()` performs the actual explicit heal request and updates SHD attempted/completed counters. `ec_heal_op()` maps management heal operations to per-brick status strings and worker spawns.

## Control flow
Initialization allocates `index_healers` and `full_healers` arrays sized by `ec->nodes`, initializes each mutex/condition pair, and records the subvolume id. A spawn either signals an existing worker or creates a new `ecshd` thread, then sets `rerun`. Worker loops wait until rerun, timeout, shutdown, SHD enablement, and EC up state allow work. Index workers obtain the brick's xattrop index directory GFID from the root, resolve it to an inode, and scan the directory concurrently. Each UUID-named index entry is converted to a path/inode and healed through `syncop_getxattr(EC_XATTR_HEAL)`; stale ENOENT/ESTALE entries are unlinked from the index directory. Full workers heal the root first, then walk the entire brick namespace with `syncop_ftw()` and heal each entry with a non-null GFID.

Management calls arrive through `ec_xl_op()`, which reads `"xl-op"` and the xlator id from input, writes per-child status keys to output, and for full/index heal starts workers only for connected, local bricks while reporting remote/down states.

## State and persistence behavior
Runtime state lives in `ec->shd`: enabled flag, timeout, max thread count, wait queue length, per-subvolume `subvol_healer` arrays, `running`, `rerun`, mutexes, conditions, and threads. SHD stats increment attempted and completed counts. Persistent effects are indirect: explicit heal getxattrs mutate EC xattrs and data through `ec-heal.c`, while index purge removes stale entries from brick xattrop index directories. `EC_XATTR_HEAL_NEW` returned from directory heals forces another index sweep when new dirty entries may have been generated.

## Dependencies and integration points
Depends on `ec-heal.c` through the `EC_XATTR_HEAL` interface and on `ec-heald.h` declarations. It uses Gluster syncop helpers for locality checks, getxattr, inode find, GFID-to-path, unlink, multithreaded directory scans, and full tree walks. It integrates with management op enums `GF_SHD_OP_HEAL_FULL` and `GF_SHD_OP_HEAL_INDEX`, `protocol-common.h`, the xattrop index `GF_XATTROP_INDEX_GFID`, and `GF_CLIENT_PID_SELF_HEALD`.

## Risks and test signals
Risks include incorrect local-brick detection causing duplicate or missing work, stale index entries not purged when GFID resolution fails differently than ENOENT/ESTALE, worker threads sleeping indefinitely if rerun/condition signaling is lost, teardown destroying cond/mutex objects while threads still run, and fragile parsing of heal completion strings. Tests should exercise management output for local/remote/down bricks, index sweep stale-entry purge, directory heal causing `EC_XATTR_HEAL_NEW` rerun, full sweep cancellation/cleanup, disabled SHD wait behavior, shutdown wakeup, and stats increments only on completed heals.
