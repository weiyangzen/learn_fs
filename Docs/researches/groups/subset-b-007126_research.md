# subset-b-007126 research

Grouped research for GlusterFS performance translator files. Each section preserves the source path and is bounded for reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/performance/md-cache/src/md-cache.c -->
# sources/distributed-fs/glusterfs/xlators/performance/md-cache/src/md-cache.c

Purpose: implements the maintained `md-cache` translator, a client-side metadata, selected xattr, and optional `statfs` cache. It wraps lookup/stat/fstat/read/write/namespace/xattr/directory fops, serves valid cached `iatt` and xattr responses, refreshes cache entries from child callbacks, and invalidates on mutation, stale/ENOENT errors, child-down events, and upcall cache-invalidation events.

Important APIs, types, and functions: `struct mdc_conf` stores timeout, xattr-cache toggles, invalidation mode, statfs cache, generation counter, child-down time, counters, and `mdc_xattr_str`. `struct md_cache` is the per-inode ctx with copied `iatt` fields, validity flags, generation/rollover data, xattr dict, linkname, timestamps, and lock. `struct mdc_local` carries loc/fd/key/xdata and `incident_time` across async fops. Core helpers are `mdc_inode_prep`, `mdc_inode_iatt_set_validate`, `mdc_inode_iatt_get`, `mdc_inode_xatt_set/update/get/unset/invalidate`, `mdc_prepare_request`, `mdc_load_reqs`, and `mdc_xattr_satisfied`. Public translator surfaces are `mdc_fops`, `mdc_cbks`, `mdc_dumpops`, `mdc_options`, and `xlator_api`.

Control flow: lookup/stat/fstat try inode-context cache first, checking TTL and `last_child_down`; misses add requested cacheable xattr keys to xdata and wind to the child. Callbacks update parent and target inode metadata and optionally xattrs. Mutating fops record the incident generation before winding, then callback-side updates are accepted only if their generation and ctime ordering are still current. Directory reads may be forced from `readdir` to `readdirp` to gather entry stats. `getxattr`/`fgetxattr` serve cacheable keys from cache when the xattr dict is valid; set/remove paths update or invalidate cached xattrs and also refresh stat from `GF_PRESTAT`/`GF_POSTSTAT` when available.

State and persistence: state is entirely in memory in per-inode ctx and `this->private`. `ia_time` and `xa_time` implement TTL, and `last_child_down` invalidates older entries after brick disruption. A global atomic generation plus per-inode rollover bits prevents older async callbacks from overwriting newer invalidations. `mdc_statfs_cache` is protected by a pthread mutex and expires by `md-cache-timeout`. `mdc_xattr_str` is intentionally not freed/replaced under readers to avoid global lock contention, creating acceptable process-lifetime leakage on reconfiguration.

Dependencies and integration: depends on Gluster defaults, dict, syncop, ACL constants, upcall-utils, statedump, atomic APIs, inode/fd ctx APIs, `STACK_WIND`/`STACK_UNWIND_STRICT`, and `syncop_ipc` to register xattr invalidation interest with the child/upcall path. It integrates with graph notifications through `mdc_notify`, with statedump/metrics through `mdc_priv_dump` and `mdc_dump_metrics`, and exposes client-settable volume options for cacheable xattr families, timeout, invalidation, forced readdirp, statfs caching, and pass-through.

Risks: coherency depends on complete callback pre/post stat and upcall delivery; missing prebufs can trigger global inode invalidation. Several local static `struct md_cache *mdc` variables are unnecessary and could be misleading in threaded code even though they are only transient assignments. `mdc_inode_xatt_invalidate` returns `-1` even after clearing `xa_time`, which callers mostly ignore but makes error semantics weak. `global-cache-invalidation` can be expensive because it calls `inode_invalidate` on detected stat changes. Reconfiguration can leak old xattr pattern strings by design. Testing should stress races between writes, lookups, upcalls, generation rollover, child-down recovery, ACL/xattr option changes, statfs TTL, and forced readdirp behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/performance/md-cache/src/md-cache.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/performance/nl-cache/Makefile.am -->
# sources/distributed-fs/glusterfs/xlators/performance/nl-cache/Makefile.am

Purpose: top-level Automake fragment for the `performance/nl-cache` translator. It delegates all build work to `src`.

Important APIs, types, and functions: declares `SUBDIRS = src` and an empty `CLEANFILES`. There are no runtime APIs or C symbols in this file.

Control flow: during recursive Automake builds, the parent performance tree enters this directory and then descends into `src/Makefile.am`, where the actual `nl-cache.la` module is defined.

State and persistence: build-only metadata; it creates no runtime state and persists no generated files beyond normal Automake outputs.

Dependencies and integration: integrates with GlusterFS's recursive build layout. Its only dependency is the presence of the `src` subdirectory.

Risks and test signals: low risk, but omission from a parent `SUBDIRS` list or a missing `src` directory would prevent `nl-cache` from building. Build validation should include `make`/`make distcheck` coverage that confirms recursive descent.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/performance/nl-cache/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/performance/nl-cache/src/Makefile.am -->
# sources/distributed-fs/glusterfs/xlators/performance/nl-cache/src/Makefile.am

Purpose: builds the `nl-cache.la` GlusterFS performance xlator module.

Important APIs, types, and functions: `xlator_LTLIBRARIES = nl-cache.la`; installs under `$(libdir)/glusterfs/$(PACKAGE_VERSION)/xlator/performance`; compiles `nl-cache.c` and `nl-cache-helper.c`; ships private headers `nl-cache.h`, `nl-cache-mem-types.h`, and `nl-cache-messages.h`.

Control flow: Automake compiles the two C files with Gluster CPP/C flags, links against `libglusterfs.la`, and produces a loadable module using `$(GF_XLATOR_DEFAULT_LDFLAGS)`.

State and persistence: build metadata only. It contributes no runtime cache state.

Dependencies and integration: includes `libglusterfs/src`, generated and source XDR include paths, and `$(CONTRIBDIR)/timer-wheel`, which is required by `nl-cache-helper.c` for cache expiry timers.

Risks and test signals: the timer-wheel include path is a specific integration requirement; removing it would break helper compilation. Build tests should verify module link, installed path, and distribution packaging of the noinst headers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/performance/nl-cache/src/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/performance/nl-cache/src/nl-cache-helper.c -->
# sources/distributed-fs/glusterfs/xlators/performance/nl-cache/src/nl-cache-helper.c

Purpose: implements the cache-state engine for `nl-cache`: per-directory positive and negative dentry lists, timer expiry, LRU pruning, memory accounting, lookup helpers, and statedump support.

Important APIs, types, and functions: operates on `nlc_ctx_t` inode contexts containing `pe`, `ne`, state bits, `cache_time`, timer data, size, and ref counts. Main exported helpers are `nlc_local_init/wipe`, `nlc_set_dir_state`, `nlc_dir_add_ne`, `nlc_dir_add_pe`, `nlc_dir_remove_pe`, `nlc_is_negative_lookup`, `nlc_get_real_file_name`, `nlc_inode_clear_cache`, `nlc_lru_prune`, `nlc_clear_all_cache`, `nlc_update_child_down_time`, and `nlc_dump_inodectx`.

Control flow: `nlc_inode_ctx_get_set` creates a directory ctx, starts a timer, links it into the global LRU, and accounts memory. Add/remove helpers update PE/NE lists under `nlc_ctx->lock`; deleting a positive entry also adds a negative entry. `nlc_is_negative_lookup` returns true when a matching NE exists or a directory has a full PE list that lacks the name. `nlc_get_real_file_name` performs case-insensitive PE lookup for `GF_XATTR_GET_REAL_FILENAME_KEY`. Timer callbacks mark `cache_time = 0`; the next access clears stale entries and restarts timer/LRU membership.

State and persistence: all cache state is in memory, split between per-inode ctx, child inode ctx slot 1 for positive-entry backreferences, and `nlc_conf` global LRU/counters. `cache_time` is compared with `last_child_down`; timer expiry invalidates lazily to avoid locking deadlocks. Memory and inode references are tracked through atomics `current_cache_size` and `refd_inodes`.

Dependencies and integration: uses Gluster inode ctx two-slot APIs, inode refs, timer-wheel (`gf_tw_*`), list primitives, statedump, atomics, and translator private config. It is tightly coupled to declarations in `nl-cache.h` and to fop decisions in `nl-cache.c`.

Risks: many operations are O(n) list scans, so huge directories can be costly. The code intentionally updates `cache_time` outside the ctx lock in the timer callback, allowing brief false negatives. Hardlink handling and rename logic depend on correct inode/name availability. `__nlc_add_pe` calls `inode_ctx_get2(entry_ino, ...)` even when some call sites allow NULL `entry_ino`, which deserves focused null-path testing. Tests should cover duplicate negative lookups, create/unlink/rename/rmdir transitions, timer expiry, LRU pruning by size and inode count, child-down invalidation, get-real-filename case-insensitive lookup, and statedump lock failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/performance/nl-cache/src/nl-cache-helper.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/performance/nl-cache/src/nl-cache-mem-types.h -->
# sources/distributed-fs/glusterfs/xlators/performance/nl-cache/src/nl-cache-mem-types.h

Purpose: defines memory accounting IDs for the `nl-cache` translator.

Important APIs, types, and functions: `enum gf_nlc_mem_types_` begins at `gf_common_mt_end + 1` and assigns IDs for `nlc_conf`, `nlc_ctx`, `nlc_local`, positive entries, negative entries, timer data, LRU nodes, and `gf_nlc_mt_end`.

Control flow: no runtime control flow; IDs are consumed by `GF_CALLOC`, `GF_MALLOC`, and `xlator_mem_acct_init(this, gf_nlc_mt_end)`.

State and persistence: contributes accounting categories only. Runtime allocation state is managed by Gluster's memory accounting subsystem.

Dependencies and integration: includes `<glusterfs/mem-types.h>` and is included by `nl-cache.h` and implementation files.

Risks and test signals: IDs must remain unique and ordered after `gf_common_mt_end`; adding new allocations requires appending before `gf_nlc_mt_end`. Test signal is successful memory-account initialization and useful statedump/accounting labels under nl-cache workloads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/performance/nl-cache/src/nl-cache-mem-types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/performance/nl-cache/src/nl-cache-messages.h -->
# sources/distributed-fs/glusterfs/xlators/performance/nl-cache/src/nl-cache-messages.h

Purpose: reserves structured log message IDs for `nl-cache`.

Important APIs, types, and functions: `GLFS_MSGID(NLC, NLC_MSG_NO_MEMORY, NLC_MSG_EINVAL, NLC_MSG_NO_TIMER_WHEEL, NLC_MSG_DICT_FAILURE)` defines stable IDs used by allocation, argument, timer-wheel, and dictionary failure paths.

Control flow: none; preprocessor metadata only.

State and persistence: no runtime state.

Dependencies and integration: includes `<glusterfs/glfs-message-id.h>` and must match the `NLC` component namespace.

Risks and test signals: IDs should only be appended, never removed or reused, to preserve log compatibility. Compile-time use in `gf_msg` calls is the primary validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/performance/nl-cache/src/nl-cache-messages.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/performance/nl-cache/src/nl-cache.c -->
# sources/distributed-fs/glusterfs/xlators/performance/nl-cache/src/nl-cache.c

Purpose: wires negative lookup and optional positive entry caching into Gluster fops, notifications, statedump, metrics, init/reconfigure/fini, and the xlator API.

Important APIs, types, and functions: `NLC_FOP` and `NLC_FOP_CBK` macros wrap mutating fops with local allocation and callback cache updates. `nlc_lookup` can unwind ENOENT from cache. `nlc_getxattr` handles `GF_XATTR_GET_REAL_FILENAME_KEY` from PE cache. `nlc_dentry_op` updates PE/NE lists for create/mkdir/mknod/symlink/link/unlink/rmdir/rename. `nlc_invalidate`, `nlc_notify`, `nlc_forget`, `nlc_priv_dump`, `nlc_dump_metrics`, `nlc_init`, and `nlc_reconfigure` provide lifecycle integration.

Control flow: lookup ignores nameless locations, checks existing inode links, queries `nlc_is_negative_lookup`, and either unwinds ENOENT or winds to child; ENOENT callbacks add an NE. Create-like callbacks add PE entries when positive caching is enabled; unlink/rmdir remove PE and add NE; rename manipulates old and new parent entries. `unlink` requests `GET_LINK_COUNT` in xdata so callback can avoid unsafe PE removal for multi-link files. Upcall invalidation clears affected directory and parent caches for directory time or parent-dentry changes.

State and persistence: state is in `nlc_conf` and per-inode ctx managed by `nl-cache-helper.c`. `nlc_init` allocates config, computes `inode_limit` from inode table LRU capacity, initializes atomics/LRU, and obtains a global timer wheel. `nlc_fini` frees config and returns the timer wheel, while `forget` clears per-inode cache and ctx.

Dependencies and integration: depends on `nl-cache.h`, statedump, upcall-utils, default fop helpers, inode table lookup, atomics, timer-wheel, dict xdata conventions, and Gluster xlator registration. Exposes options `nl-cache`, `nl-cache-positive-entry`, `nl-cache-limit`, `nl-cache-timeout`, and `pass-through`; category is `GF_TECH_PREVIEW`.

Risks: positive-entry caching is disabled by default and only partially implemented; readdir/readdirp/opendir hooks are TODOs, so full PE state is mostly from mkdir/create flows. Several callbacks dereference returned `buf`/`preparent` for `ia_type` after only checking `op_ret`, so malformed child callbacks can crash. Rename handling has TODOs about atomicity and destination replacement. Tests should exercise lookup ENOENT hits/misses, link-count xdata absence, get-real-filename, upcall invalidation, parent-down clearing, option reconfigure, and lifecycle cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/performance/nl-cache/src/nl-cache.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/performance/nl-cache/src/nl-cache.h -->
# sources/distributed-fs/glusterfs/xlators/performance/nl-cache/src/nl-cache.h

Purpose: shared interface and data model for `nl-cache.c` and `nl-cache-helper.c`.

Important APIs, types, and functions: defines state bits `NLC_PE_FULL`, `NLC_PE_PARTIAL`, `NLC_NE_VALID`, validation macros, `NLC_STACK_UNWIND`, `nlc_ne_t`, `nlc_pe_t`, `nlc_timer_data_t`, `nlc_lru_node_t`, `nlc_ctx_t`, `nlc_local_t`, `nlc_statistics`, and `nlc_conf_t`. Declares helper functions for dentry additions/removals, negative lookup checks, real filename lookup, cache clearing, LRU pruning, child-down time, local management, and statedump.

Control flow: the macros and prototypes establish the contract that fop wrappers allocate `nlc_local_t`, helper functions mutate per-directory ctx under locks, and unwind paths must wipe locals.

State and persistence: declares all in-memory state used by the translator, including per-directory PE/NE lists, cache timers, cache size, ref counts, global LRU, and counters. No disk persistence.

Dependencies and integration: includes nl-cache memory/message headers, Gluster defaults, and atomics. It is the compile-time coupling point between the front-end fop file and the helper engine.

Risks and test signals: changing struct layout or state bits affects both implementation files and statedump interpretation. Tests should compile both files together and validate that each declared helper has one implementation with consistent lock/memory ownership.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/performance/nl-cache/src/nl-cache.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/performance/open-behind/Makefile.am -->
# sources/distributed-fs/glusterfs/xlators/performance/open-behind/Makefile.am

Purpose: top-level Automake fragment for the `open-behind` translator directory.

Important APIs, types, and functions: declares `SUBDIRS = src`; no C APIs.

Control flow: recursive build descends into `src` to compile the translator module.

State and persistence: build-only metadata with no runtime state.

Dependencies and integration: depends on the `src` subdirectory and parent Automake recursion.

Risks and test signals: low risk; recursive build and dist packaging should confirm the directory is included.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/performance/open-behind/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/performance/open-behind/src/Makefile.am -->
# sources/distributed-fs/glusterfs/xlators/performance/open-behind/src/Makefile.am

Purpose: builds the `open-behind.la` performance translator module.

Important APIs, types, and functions: compiles `open-behind.c`, links `libglusterfs.la`, installs to the performance xlator directory, and lists private headers `open-behind-mem-types.h` and `open-behind-messages.h`.

Control flow: Automake compiles the single source with Gluster include paths and `-Wall`, then links as a loadable xlator module.

State and persistence: build metadata only.

Dependencies and integration: depends on `libglusterfs/src`, RPC XDR include paths, and Gluster xlator linker flags.

Risks and test signals: source/header list drift would break packaging or module build. Validation should include module compilation and install path checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/performance/open-behind/src/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/performance/open-behind/src/open-behind-mem-types.h -->
# sources/distributed-fs/glusterfs/xlators/performance/open-behind/src/open-behind-mem-types.h

Purpose: defines memory accounting IDs for `open-behind`.

Important APIs, types, and functions: `enum gf_ob_mem_types_` assigns `gf_ob_mt_fd_t`, `gf_ob_mt_conf_t`, `gf_ob_mt_inode_t`, and `gf_ob_mt_end`.

Control flow: no runtime control flow; IDs are passed to allocation helpers and `xlator_mem_acct_init`.

State and persistence: no state beyond memory-accounting categories.

Dependencies and integration: includes `<glusterfs/mem-types.h>` and is included by `open-behind.c`.

Risks and test signals: `gf_ob_mt_fd_t` appears reserved but not used in this implementation; adding allocations should use or extend this enum before `gf_ob_mt_end`. Successful mem-account initialization validates the header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/performance/open-behind/src/open-behind-mem-types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/performance/open-behind/src/open-behind-messages.h -->
# sources/distributed-fs/glusterfs/xlators/performance/open-behind/src/open-behind-messages.h

Purpose: reserves structured log message IDs and short strings for `open-behind`.

Important APIs, types, and functions: `GLFS_MSGID(OPEN_BEHIND, ...)` defines IDs for child misconfiguration, dangling volume, no memory, failed fop submission, and bad state. Also defines `OPEN_BEHIND_MSG_FAILED_STR` and `OPEN_BEHIND_MSG_BAD_STATE_STR`.

Control flow: preprocessor-only; consumed by `gf_msg`/`gf_smsg` calls in `open-behind.c`.

State and persistence: no runtime state.

Dependencies and integration: includes `<glusterfs/glfs-message-id.h>` and must match the OPEN_BEHIND namespace.

Risks and test signals: log IDs must remain stable and append-only. Compile coverage through error paths validates symbol availability.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/performance/open-behind/src/open-behind-messages.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/performance/open-behind/src/open-behind.c -->
# sources/distributed-fs/glusterfs/xlators/performance/open-behind/src/open-behind.c

Purpose: implements the maintained `open-behind` translator, which replies to selected `open` calls before the backend open is issued and delays or cancels that backend open until a later operation requires it.

Important APIs, types, and functions: `ob_conf_t` stores `use_anonymous_fd`, `lazy_open`, and `read_after_open`. `ob_inode_t` tracks per-inode pending first open, first fd, open count, trigger state, and queued stubs. `ob_open_and_resume_inode/fd`, `ob_open_behind`, `ob_open_dispatch`, `ob_stub_dispatch`, `ob_open_completed`, and `ob_fdclose` implement the state machine. `OB_POST_FD`, `OB_POST_INODE`, and `OB_POST_FLUSH` decide whether to use anonymous fds, queue a stub, trigger the first open, or forward directly.

Control flow: first non-synchronous `open` stores a referenced fd and a copied-frame stub, immediately unwinds success to the caller, and either dispatches the backend open immediately or keeps it lazy. Later reads/fstats/seeks may proceed on anonymous fds if configured, while writes, locks, fsync, truncate, xattr mutations, unlink/rename/setattr, or read-after-open trigger the backend open and queue their call stubs until open completion. If the fd is closed before a lazy open is triggered, `ob_fdclose` cancels and destroys the pending open stub.

State and persistence: all state is in memory in per-inode ctx and fd ctx error values. `open_count` resets behavior once all fds close. Backend open failures are stored via `fd_ctx_set`; future fd operations see the error through `ob_open_and_resume_fd`. No disk persistence.

Dependencies and integration: depends on Gluster defaults/call-stub APIs, inode/fd ctx, frame copy/destroy, anonymous fd helpers, ACL xattr constants, statedump, and xlator registration. It requires exactly one child and exposes `open-behind`, `use-anonymous-fd`, `lazy-open`, `read-after-open`, and `pass-through` options.

Risks: correctness depends on careful lock boundaries because stubs are allocated outside inode locks and resumed after state changes. `OB_POST_FLUSH` contains a suspicious switch layout where the common macro is unreachable-looking after `break`, so flush behavior needs close regression coverage. Anonymous fd reads/fstats avoid backend open but may not preserve all fd side effects. Setxattr bypasses open-behind for POSIX ACL and SELinux xattrs. Tests should cover open-read-close cancellation, read-after-open on/off, use-anonymous-fd on/off, backend open failure propagation, concurrent operations while first open is preparing, fdclose races, and operations that must force synchronous open.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/performance/open-behind/src/open-behind.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/performance/quick-read/Makefile.am -->
# sources/distributed-fs/glusterfs/xlators/performance/quick-read/Makefile.am

Purpose: top-level Automake fragment for `quick-read`.

Important APIs, types, and functions: declares `SUBDIRS = src` and an empty `CLEANFILES`.

Control flow: recursive build enters `src` for actual module compilation.

State and persistence: build-only metadata.

Dependencies and integration: relies on parent Automake recursion and the `src` directory.

Risks and test signals: low risk; validate with recursive build and dist checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/performance/quick-read/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/performance/quick-read/src/Makefile.am -->
# sources/distributed-fs/glusterfs/xlators/performance/quick-read/src/Makefile.am

Purpose: builds the `quick-read.la` performance translator module.

Important APIs, types, and functions: compiles `quick-read.c`, links `libglusterfs.la`, installs under the performance xlator directory, and lists private headers `quick-read.h`, `quick-read-mem-types.h`, and `quick-read-messages.h`.

Control flow: Automake compiles the single C implementation with Gluster include paths and links a module with `$(GF_XLATOR_DEFAULT_LDFLAGS)`.

State and persistence: build metadata only.

Dependencies and integration: depends on libglusterfs and RPC XDR include paths.

Risks and test signals: module build breaks if header or source lists drift. Compile and install packaging tests are sufficient for this file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/performance/quick-read/src/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/performance/quick-read/src/quick-read-mem-types.h -->
# sources/distributed-fs/glusterfs/xlators/performance/quick-read/src/quick-read-mem-types.h

Purpose: defines memory accounting IDs for `quick-read`.

Important APIs, types, and functions: `enum gf_qr_mem_types_` assigns IDs for `qr_inode`, cached content, priority rules, private config/table, and `gf_qr_mt_end`.

Control flow: no runtime control flow; allocation and memory-account initialization consume the IDs.

State and persistence: no state except category definitions for Gluster memory accounting.

Dependencies and integration: includes `<glusterfs/mem-types.h>` and is included by `quick-read.h`.

Risks and test signals: new allocation classes must be appended before `gf_qr_mt_end`. Validation is successful `qr_mem_acct_init` and useful memory stats during quick-read cache activity.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/performance/quick-read/src/quick-read-mem-types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/performance/quick-read/src/quick-read-messages.h -->
# sources/distributed-fs/glusterfs/xlators/performance/quick-read/src/quick-read-messages.h

Purpose: reserves structured log message IDs for `quick-read`.

Important APIs, types, and functions: `GLFS_MSGID(QUICK_READ, ...)` covers enforcement failures, invalid arguments/config, child/volume misconfiguration, no memory, dict-set failures, and non-empty LRU notices.

Control flow: preprocessor-only; IDs are used by `gf_msg` calls in `quick-read.c`.

State and persistence: no runtime state.

Dependencies and integration: includes `<glusterfs/glfs-message-id.h>` and must remain aligned with the QUICK_READ component.

Risks and test signals: IDs must be append-only. Build and error-path tests validate use.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/performance/quick-read/src/quick-read-messages.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/performance/quick-read/src/quick-read.c -->
# sources/distributed-fs/glusterfs/xlators/performance/quick-read/src/quick-read.c

Purpose: implements the maintained `quick-read` translator, an entire-small-file client cache populated from lookup/readdirp content and served directly for readv when fresh.

Important APIs, types, and functions: `qr_local_t` carries inode/fd and incident generation. Per-inode state is `qr_inode_t`; global state is `qr_private_t` with `qr_conf_t`, LRU table, child-down time, lock, counters, and generation. Core helpers are `qr_inode_ctx_get_or_new`, `qr_content_extract`, `qr_content_update`, `qr_content_refresh`, `qr_readv_cached`, `qr_inode_prune`, `qr_cache_prune`, `qr_get_priority_list`, and `qr_invalidate`.

Control flow: `qr_lookup` requests `GF_CONTENT_KEY` up to `max-file-size` when content is not already cached; callback extracts content and stores it with stat/timestamps, or refreshes/prunes existing content using returned stat. `qr_readv` serves from cached bytes if data exists, offset is in range, and `last_refresh` is within timeout and newer than child-down time; otherwise it winds to child. Write/truncate/fallocate/discard/zerofill callbacks prune cached content. `qr_open` sets priority from path patterns, and `readdirp` refreshes known cached entries from directory stats.

State and persistence: cache is process memory only. Cached content bytes live in `qr_inode->data`; LRU buckets are partitioned by configured priority. `cache_used`, `files_cached`, hit/miss counters, and invalidation counters are maintained in memory. Generation and rollover logic prevent stale async callbacks from repopulating after invalidation. Child-down time invalidates older cache entries.

Dependencies and integration: uses Gluster dict/content conventions, iobuf/iobref for readv responses, inode ctx, list/lock/atomic helpers, upcall-utils, statedump, and xlator options. Options include `quick-read`, `priority`, `cache-size`, `cache-timeout`, `max-file-size`, `quick-read-cache-invalidation`, and `ctime-invalidation`.

Risks: entire-file caching is sensitive to invalidation completeness; without quick-read-cache-invalidation, freshness relies on TTL and fop callbacks. `qr_local_get` uses `gf_common_mt_char` instead of a qr-specific local type, reducing accounting clarity. `qr_forget` frees the inode ctx object without deleting/resetting the inode ctx slot in this file, which relies on forget semantics and deserves leak/UAF scrutiny. Cache-size validation uses total memory fallback and max option metadata. Tests should cover lookup content population, cached partial reads, stale timeout, mtime vs ctime invalidation, child-down invalidation, write/truncate pruning, priority LRU pruning, upcall write invalidation, and large-file non-caching.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/performance/quick-read/src/quick-read.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/performance/quick-read/src/quick-read.h -->
# sources/distributed-fs/glusterfs/xlators/performance/quick-read/src/quick-read.h

Purpose: declares the data structures shared by the quick-read implementation.

Important APIs, types, and functions: defines `qr_inode_t` for cached bytes, size, priority, mtime/ctime, stat buffer, last refresh, LRU node, generation, and invalidation time; `qr_priority_t` for pattern priority rules; `qr_conf_t` for cache limits/timeouts/options; `qr_inode_table_t` for cache usage and LRU buckets; `qr_statistics`; and `qr_private_t`.

Control flow: no functions are declared here beyond data contracts; `quick-read.c` uses these structures for lookup population, read serving, pruning, and lifecycle.

State and persistence: describes all quick-read runtime state, which is in-memory and per-process.

Dependencies and integration: includes Gluster logging, dict, list, compat/defaults, POSIX headers, `fnmatch`, and quick-read memory types.

Risks and test signals: changes to `qr_inode_t` affect locking and LRU accounting in `quick-read.c`. Because cached content is a raw `void *`, callers must preserve size and stat invariants. Compile tests and cache-behavior tests validate this contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/performance/quick-read/src/quick-read.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/performance/read-ahead/Makefile.am -->
# sources/distributed-fs/glusterfs/xlators/performance/read-ahead/Makefile.am

Purpose: top-level Automake fragment for the `read-ahead` performance translator.

Important APIs, types, and functions: declares `SUBDIRS = src` and an empty `CLEANFILES`.

Control flow: recursive build descends to `src` where the module is built.

State and persistence: build-only metadata.

Dependencies and integration: depends on the `src` subdirectory and parent build recursion.

Risks and test signals: low risk; recursive build and packaging checks should ensure this translator remains included.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/performance/read-ahead/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/performance/read-ahead/src/Makefile.am -->
# sources/distributed-fs/glusterfs/xlators/performance/read-ahead/src/Makefile.am

Purpose: builds the `read-ahead.la` performance translator module.

Important APIs, types, and functions: compiles `read-ahead.c` and `page.c`, links `libglusterfs.la`, installs under the performance xlator directory, and lists private headers `read-ahead.h`, `read-ahead-mem-types.h`, and `read-ahead-messages.h`.

Control flow: Automake compiles the two implementation files with Gluster and RPC XDR include paths, applies `-Wall`, and links a loadable module with standard xlator flags.

State and persistence: build metadata only; runtime read-ahead state lives in the C files referenced here, not in this Makefile.

Dependencies and integration: depends on libglusterfs, generated/source XDR include paths, and the consistency of source/header lists with the read-ahead implementation.

Risks and test signals: missing either `read-ahead.c` or `page.c` would break translator functionality at link time. Build validation should confirm module compilation, install path, and distribution inclusion of private headers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/performance/read-ahead/src/Makefile.am -->
