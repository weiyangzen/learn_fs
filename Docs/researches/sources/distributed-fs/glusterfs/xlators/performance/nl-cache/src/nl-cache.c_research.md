# sources/distributed-fs/glusterfs/xlators/performance/nl-cache/src/nl-cache.c

Purpose: wires negative lookup and optional positive entry caching into Gluster fops, notifications, statedump, metrics, init/reconfigure/fini, and the xlator API.

Important APIs, types, and functions: `NLC_FOP` and `NLC_FOP_CBK` macros wrap mutating fops with local allocation and callback cache updates. `nlc_lookup` can unwind ENOENT from cache. `nlc_getxattr` handles `GF_XATTR_GET_REAL_FILENAME_KEY` from PE cache. `nlc_dentry_op` updates PE/NE lists for create/mkdir/mknod/symlink/link/unlink/rmdir/rename. `nlc_invalidate`, `nlc_notify`, `nlc_forget`, `nlc_priv_dump`, `nlc_dump_metrics`, `nlc_init`, and `nlc_reconfigure` provide lifecycle integration.

Control flow: lookup ignores nameless locations, checks existing inode links, queries `nlc_is_negative_lookup`, and either unwinds ENOENT or winds to child; ENOENT callbacks add an NE. Create-like callbacks add PE entries when positive caching is enabled; unlink/rmdir remove PE and add NE; rename manipulates old and new parent entries. `unlink` requests `GET_LINK_COUNT` in xdata so callback can avoid unsafe PE removal for multi-link files. Upcall invalidation clears affected directory and parent caches for directory time or parent-dentry changes.

State and persistence: state is in `nlc_conf` and per-inode ctx managed by `nl-cache-helper.c`. `nlc_init` allocates config, computes `inode_limit` from inode table LRU capacity, initializes atomics/LRU, and obtains a global timer wheel. `nlc_fini` frees config and returns the timer wheel, while `forget` clears per-inode cache and ctx.

Dependencies and integration: depends on `nl-cache.h`, statedump, upcall-utils, default fop helpers, inode table lookup, atomics, timer-wheel, dict xdata conventions, and Gluster xlator registration. Exposes options `nl-cache`, `nl-cache-positive-entry`, `nl-cache-limit`, `nl-cache-timeout`, and `pass-through`; category is `GF_TECH_PREVIEW`.

Risks: positive-entry caching is disabled by default and only partially implemented; readdir/readdirp/opendir hooks are TODOs, so full PE state is mostly from mkdir/create flows. Several callbacks dereference returned `buf`/`preparent` for `ia_type` after only checking `op_ret`, so malformed child callbacks can crash. Rename handling has TODOs about atomicity and destination replacement. Tests should exercise lookup ENOENT hits/misses, link-count xdata absence, get-real-filename, upcall invalidation, parent-down clearing, option reconfigure, and lifecycle cleanup.
