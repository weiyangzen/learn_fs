# sources/distributed-fs/glusterfs/xlators/cluster/afr/src/afr.c

## Purpose
`afr.c` is the translator entry point for GlusterFS AFR/replicate. It initializes and reconfigures `afr_private_t`, parses volume options, allocates child arrays and inode tables, initializes self-heal-daemon state, exports the AFR FOP/callback/dump operation tables, and registers the translator API as `"replicate"`.

## Important APIs, Types, And Functions
Top-level translator hooks are `init()`, `fini()`, `reconfigure()`, `notify()`, and `mem_acct_init()`, all referenced from `xlator_api`. The `fops` table binds lookup, locks, statfs, inode reads, inode writes, open/opendir, directory reads, and directory writes to AFR implementations in included/adjacent modules. `cbks` supplies release, releasedir, and forget callbacks; `dumpops` exposes `afr_priv_dump()`.

Important initialization helpers are `xlator_subvolume_index()`, `fix_quorum_options()`, `afr_set_favorite_child_policy()`, `set_data_self_heal_algorithm()`, `afr_handle_anon_inode_options()`, `afr_pending_xattrs_init()`, and `afr_ta_init()`. Self-heal cleanup uses `afr_selfheal_daemon_fini()` and `afr_destroy_healer_object()`.

## Control Flow
`init()` validates that the translator has children, allocates `afr_private_t`, initializes locks and lists, counts subvolumes, parses arbiter/thin-arbiter settings, initializes read-selection and self-heal options, configures quorum, eager-lock, pre-op, durability, HALO, favorite-child, consistent-metadata/IO, anonymous inode, and changelog xattr options, and allocates arrays for children, up/down state, local flags, anonymous-inode flags, child latency, pending reads, pending keys, and last events. It then stores child pointers, creates a self-heal domain string, creates an inode table with different sizing when running as SHD, initializes the self-heal daemon if requested, and creates the local frame pool.

`reconfigure()` updates the same runtime-tunable fields from a new options dict. It resolves read-subvolume by object or index, recalculates quorum behavior, resets read-child discovery when `choose-local` changes, disables `consistent_io` if quorum is enabled, updates anonymous-inode naming, and wakes self-heal when SHD enablement or timeout changes. `fini()` tears down SHD healer threads, cancels pending parent-up timers, destroys the local mempool, frees private state via `afr_priv_destroy()`, and destroys the inode table.

## State And Persistence
The file owns allocation and option population of `afr_private_t`. Persistent translator configuration includes child count, child pointers, arbiter/thin-arbiter mode, pending xattr names, dirty xattr name, self-heal parameters, quorum mode/count, read selection policy, eager-lock/post-op delay/pre-op compatibility, HALO latency limits, consistency flags, and anonymous-inode names derived from `volume-id`. Runtime state initialized here includes child-up/halo-up arrays, latency arrays, local flags, pending-read counters, heal queues, saved locks, thin-arbiter wait/on-wire queues, event generation fields, and SHD structures.

The file itself does not write disk data. Its persistent effects are the option-selected xattr names and translator runtime structures that later transaction and self-heal code use to write trusted AFR xattrs and maintain replica consistency.

## Dependencies And Integration Points
`afr.c` includes `afr-common.c` directly, making many common helper definitions part of the same compilation unit. It depends on GlusterFS xlator APIs, option parsing macros (`GF_OPTION_INIT`/`GF_OPTION_RECONF`), memory accounting, inode-table creation, timers, thread cleanup, self-heal-daemon helpers, and all AFR FOP implementations named in the operation table. The automake build for AFR must compile this as the module entry source that exports `xlator_api`.

## Risks
Initialization has many partially allocated resources and a single `out` path; failures depend on later private cleanup to avoid leaks. Thin-arbiter setup deliberately decrements `child_count` while pending-key allocation may account for the thin-arbiter file name, so off-by-one mistakes can corrupt child arrays or pending xattr names. Quorum options override each other, and enabling quorum disables consistent-IO, so reconfiguration tests must check the final effective policy rather than raw option values. Direct inclusion of `afr-common.c` can hide symbol-boundary issues and makes compile order important.

## Test Signals
Signals include successful volume graph load with normal replica, arbiter, and thin-arbiter configurations; invalid `read-subvolume` and `read-subvolume-index` rejection; live reconfigure of quorum, eager-lock, self-heal, HALO, favorite-child, and read policies; clean translator unload without leaked timers or healer threads; correct `distribute.so`-style operation exposure through xlator API; and option table validation through Gluster volume set/get tests. SHD-specific tests should verify inode table sizing and healer object cleanup.
