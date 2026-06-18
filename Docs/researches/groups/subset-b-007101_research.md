# subset-b-007101 Research

Grouped research for GlusterFS meta translator files and glusterd management service/operation files. Each source file section preserves the source path in its title and is delimited for deterministic source-tree-aligned splitting.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/meta/src/meta-defaults.c -->
# sources/distributed-fs/glusterfs/xlators/meta/src/meta-defaults.c

Purpose: implements the default file-operation table used by the GlusterFS `meta` translator once a hook has attached `struct meta_ops` to an inode. The defaults make the virtual `.meta` tree behave mostly read-only while still allowing generated files, directories, symlinks, and a few tunable files to be read, listed, opened, truncated, or written through hook-specific callbacks.

Important APIs/types/functions: `meta_defaults_init()` fills missing `struct xlator_fops` entries with `meta_default_*` handlers. Read paths include `meta_default_lookup()`, `meta_default_readdir()`, `meta_default_readv()`, `meta_default_readlink()`, `meta_default_stat()`, and `meta_default_fstat()`. Mutating or unsupported operations generally call Gluster default failure callbacks with `EPERM`; the exception is `meta_default_writev()`, which dispatches to `ops->file_write` when a virtual file intentionally supports writes. Directory and file content are cached in `meta_fd_t` through `meta_dir_fill()` and `meta_file_fill()`.

Control flow: lookup starts from the parent inode's `meta_ops`, searches fixed dirents, optionally asks `ops->dir_fill()` for dynamic entries, calls the selected dirent hook to attach child inode behavior, synthesizes iatt data, and unwinds. Readdir combines fixed entries with cached dynamic entries and emits `gf_dirent_t` records bounded by the caller's size/off cookie. Readv lazily materializes file text through `strfd`, copies the requested slice into an iobuf/iobref, and unwinds with the byte count. Readlink similarly asks `ops->link_fill()` to produce a target string. `open()` forces `direct-io-mode` so clients do not cache stale synthetic content.

State and persistence behavior: state is volatile and scoped to inode/fd contexts. `meta_fd_t` caches generated text or dynamic dirents for an open fd; nothing is persisted to disk. Most metadata timestamps are synthesized on demand by helper code, so repeated stats can observe changing times. `file_write` callbacks may change live in-memory translator state, but this file does not itself persist those changes.

Dependencies and integration points: depends on Gluster's default FOP failure callbacks, stack unwind macros, iobuf/iobref allocation, `gf_dirent_*` helpers, `meta_ops_get()`, `meta_iatt_fill()`, and the hook modules that populate `meta_ops`. It is integrated by `meta_ops_set()`, which calls `meta_defaults_init()` before storing an ops table on an inode.

Risks and edge cases: `meta_default_lookup()` assumes dynamically allocated dirent names can always be freed after lookup, so hook implementations must match that ownership contract. Readdir cookies are simple synthetic offsets (`i + 1`) and inode numbers (`i + 42`), suitable for a synthetic tree but fragile if clients rely on stable inode numbers. `meta_default_readv()` does not recompute content after the first fd read, so long-lived fds can see stale dynamic data. Missing ops typically yield `EPERM` or `ENOENT`, making hook setup failures user-visible as permission or lookup errors.

Test signals: useful coverage includes lookup and readdir of fixed and dynamic entries, repeated reads with offsets and small buffers, readlink generation, write attempts on read-only files, writev on tunable files with `file_write`, direct-io xdata behavior on open, and fd release freeing generated dirents/data without leaks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/meta/src/meta-defaults.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/meta/src/meta-helpers.c -->
# sources/distributed-fs/glusterfs/xlators/meta/src/meta-helpers.c

Purpose: provides the shared context, fd-cache, xdata, stat synthesis, and content-fill helpers used by every `meta` hook and default FOP. It is the glue between Gluster inode/fd context APIs and the translator's per-file `meta_ops` model.

Important APIs/types/functions: `meta_fd_get()` allocates or returns per-fd `meta_fd_t`; `meta_fd_release()` frees cached data and dirents. `meta_ops_get()`, `meta_ops_set()`, `meta_fops_get()`, `meta_ctx_get()`, and `meta_ctx_set()` manage two inode-context slots: one for ops and one for arbitrary hook payload. `meta_direct_io_mode()` prepares xdata for direct I/O. `meta_iatt_fill()` and `default_meta_iatt_fill()` synthesize file attributes. `meta_file_fill()`, `meta_dir_fill()`, and `fixed_dirents_len()` materialize and count virtual content.

Control flow: `meta_ops_set()` initializes a hook's fop table with defaults and stores the ops pointer in inode context. Later FOP wrappers call `meta_fops_get()` to dispatch to that ops table or `default_fops` if no meta ops exist. File reads call `meta_file_fill()`, which opens a `strfd`, invokes `ops->file_fill()`, transfers ownership of the generated buffer to the fd cache, and closes the `strfd`. Directory reads call `meta_dir_fill()` once per fd and keep returned dirents until release.

State and persistence behavior: all state is in memory. Inode context stores raw pointers to static `struct meta_ops` tables and hook-selected live objects such as `xlator_t`, `glusterfs_graph_t`, or `data_t`. Fd context owns generated buffers and dynamically allocated names. `meta_local_t` owns an optional xdata dict and is cleaned during stack unwind.

Dependencies and integration points: uses Gluster memory accounting types, inode/fd context APIs, `dict_new()`/`dict_unref()`, UUID helpers, `gfid_to_ino()`, realtime timestamp helpers, and `strfd`. The public prototypes are declared in `meta.h` and consumed by `meta.c`, `meta-defaults.c`, and all hook modules.

Risks and edge cases: context values are untyped `void *`/integer casts, so mismatched hook payloads can crash fill callbacks. `meta_iatt_fill()` returns without populating iatt if no ops are attached, so callers must ensure hooks ran before stat/read replies. Cached dynamic content can become stale while a fd remains open. `default_meta_iatt_fill()` generates a UUID when the inode gfid is null, which can create non-stable synthetic identities.

Test signals: verify fd allocation/release under repeated open/read/close, directory fill ownership, direct-io xdata allocation and cleanup through `META_STACK_UNWIND`, stat modes for dirs/symlinks/read-only/tunable files, and hook context propagation from parent to child.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/meta/src/meta-helpers.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/meta/src/meta-hooks.h -->
# sources/distributed-fs/glusterfs/xlators/meta/src/meta-hooks.h

Purpose: central declaration header for all virtual `.meta` tree hook functions. It gives every file/dir/link module a uniform `meta_<name>_hook(call_frame_t *, xlator_t *, loc_t *, dict_t *)` prototype.

Important APIs/types/functions: `DECLARE_HOOK(name)` expands to a hook declaration. The declarations cover root, graph, xlator, logging, process, volfile, subvolume, option, diagnostic, memory, history, latency, and profile nodes.

Control flow: `meta-defaults.c` lookup uses `struct meta_dirent.hook` pointers declared here. Directory modules include this header to refer to hooks for their child entries; hook implementations then attach `meta_ops` and optional inode context to the looked-up inode.

State and persistence behavior: the header defines no state. Its contract is that hook implementations mutate inode context through `meta_ops_set()` and `meta_ctx_set()` during lookup.

Dependencies and integration points: depends on types declared through `meta.h`/Gluster headers and is included by most `xlators/meta/src/*` modules that define static dirent tables.

Risks and edge cases: adding a new hook implementation without declaring it here breaks modules that reference it in dirent tables. A declaration can also hide missing implementation until link time.

Test signals: build/link coverage for all declared hooks and traversal tests that touch each fixed dirent referencing a hook.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/meta/src/meta-hooks.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/meta/src/meta-mem-types.h -->
# sources/distributed-fs/glusterfs/xlators/meta/src/meta-mem-types.h

Purpose: defines memory-accounting identifiers for the `meta` translator. These identifiers let Gluster attribute allocations for private state, fd caches, generated strings, dirents, and frame-local state.

Important APIs/types/functions: `enum gf_meta_mem_types_` starts at `gf_common_mt_end + 1` and defines `gf_meta_mt_priv_t`, `gf_meta_mt_fd_t`, `gf_meta_mt_fd_data_t`, `gf_meta_mt_strfd_t`, `gf_meta_mt_dirents_t`, `gf_meta_mt_local_t`, and `gf_meta_mt_end`.

Control flow: `meta.c::mem_acct_init()` passes `gf_meta_mt_end` to `xlator_mem_acct_init()`. Allocation sites in helper and hook code use these enum values with `GF_MALLOC()`/`GF_CALLOC()`.

State and persistence behavior: no runtime state is stored here; the enum indexes runtime allocation counters. Values must remain in range and unique for accounting accuracy.

Dependencies and integration points: includes `<glusterfs/mem-types.h>` for `gf_common_mt_end`. Integrated by all `meta` source files that allocate translator-specific memory.

Risks and edge cases: adding new allocation categories after `gf_meta_mt_end` or reordering values can break accounting interpretation. Missing use of these types makes leak diagnostics less precise.

Test signals: successful `mem_acct_init()`, leak reports grouped under the expected meta categories, and allocation/failure-path tests for fd and dirent caches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/meta/src/meta-mem-types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/meta/src/meta.c -->
# sources/distributed-fs/glusterfs/xlators/meta/src/meta.c

Purpose: top-level Gluster translator implementation for the synthetic `.meta` namespace. It intercepts lookup of the configured meta root, installs root metadata hooks, and forwards all later operations to the per-inode FOP table selected by hook modules.

Important APIs/types/functions: translator FOPs include `meta_lookup()`, `meta_opendir()`, `meta_open()`, `meta_readv()`, `meta_readdir()`, `meta_readdirp()`, `meta_readlink()`, `meta_writev()`, `meta_stat()`, truncation and fsync wrappers. Lifecycle functions are `mem_acct_init()`, `init()`, and `fini()`. Global exports are `struct xlator_fops fops`, `struct xlator_cbks cbks`, `struct volume_options options[]`, and `xlator_api_t xlator_api`.

Control flow: `meta_lookup()` special-cases lookup of the configured meta directory under the real root or lookup by the fixed meta-root GFID. It calls `meta_root_dir_hook()`, fills a directory iatt with `META_ROOT_GFID`, and replies directly. For all other lookups it chooses the parent inode when available and dispatches through `META_FOP`, which resolves `meta_fops_get()` and calls the inode-specific lookup implementation. All other FOP wrappers dispatch based on `loc->inode` or `fd->inode`.

State and persistence behavior: `init()` allocates `meta_priv_t`, reads the `meta-dir-name` option with default `.meta`, parses a fixed root GFID, and stores the private struct on the translator. No persistent files are created by this translator; it exposes runtime graph/process state through synthetic entries.

Dependencies and integration points: depends on Gluster xlator/default APIs, `meta.h`, `meta-mem-types.h`, and `meta-hooks.h`. It integrates into the Gluster translator stack through `xlator_api` with identifier `meta`, tech-preview category, fops/cbks, and one option.

Risks and edge cases: the dispatch macros assume an ops table or `default_fops` is valid; missing hooks can route operations to generic defaults. Root lookup synthesizes a zeroed parent iatt, which may be acceptable for virtual roots but should be tested with clients expecting parent attributes. `fini()` frees `this->private` but does not null it. The translator is category `GF_TECH_PREVIEW`, signaling a less stable integration surface.

Test signals: mount with default and custom `meta-dir-name`, lookup by name and GFID, traversal into all virtual subtrees, read/open/readdir/readlink/write dispatch, release/releasedir cleanup, mem accounting initialization failure handling, and absence of interference with non-meta paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/meta/src/meta.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/meta/src/meta.h -->
# sources/distributed-fs/glusterfs/xlators/meta/src/meta.h

Purpose: public internal contract for the `meta` translator. It defines the virtual entry model, hook signature, per-translator private state, per-frame local state, per-fd cache, operation table extension, and dispatch/unwind macros used by all meta modules.

Important APIs/types/functions: key types are `meta_hook_t`, `meta_local_t`, `meta_priv_t`, `struct meta_dirent`, `struct meta_ops`, and `meta_fd_t`. Constants include `DEFAULT_META_DIR_NAME`, `META_ROOT_GFID`, `DOT_DOTDOT`, and `COUNT()`. Macros `META_STACK_UNWIND` and `META_FOP` centralize cleanup and per-inode dispatch. Function prototypes cover iatt fill, inode discovery, ops/context storage, fd caching, default initialization, direct-io xdata, file/dir fill, and fixed-dirent counting.

Control flow: directory modules declare fixed or dynamic `struct meta_dirent` arrays whose hook functions call `meta_ops_set()` and optional `meta_ctx_set()`. FOP wrappers call `META_FOP` to dispatch to the current inode's fops. Default handlers call `META_STACK_UNWIND` so any `meta_local_t` xdata is detached and freed after the Gluster stack reply.

State and persistence behavior: the header describes runtime-only state. `meta_priv_t` stores translator options and root GFID; `meta_fd_t` stores generated content for an fd; inode context stores ops and arbitrary per-entry payloads.

Dependencies and integration points: includes `glusterfs/strfd.h` and relies on Gluster core types from surrounding includes. Every source file in `xlators/meta/src` shares this header, so its structs are the ABI within the translator.

Risks and edge cases: macros hide control flow and assume fop names exist in the selected table. `struct meta_ops` embeds full fops/cbks, so static ops instances are modified by `meta_defaults_init()` on first use; this is intentional but means ops tables should not be treated as immutable. Context payloads are not type checked.

Test signals: compile all hook modules against the header, exercise `META_STACK_UNWIND` cleanup with allocated xdata, and verify every static `meta_ops` table remains valid after repeated `meta_ops_set()` calls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/meta/src/meta.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/meta/src/name-file.c -->
# sources/distributed-fs/glusterfs/xlators/meta/src/name-file.c

Purpose: implements the virtual `name` file for an xlator entry in `.meta`, returning the target translator's runtime name.

Important APIs/types/functions: `name_file_fill()` retrieves an `xlator_t *` from inode context and writes `xl->name` plus newline to `strfd`. `meta_name_file_hook()` attaches `name_file_ops` and copies the parent xlator context to the child file.

Control flow: lookup of `name` under an xlator directory invokes the hook, then default readv calls `meta_file_fill()`, which calls `name_file_fill()`.

State and persistence behavior: no state is persisted. The file reflects the live `xlator_t` pointer stored by the parent `xlator-dir` hook and cached per open fd after read.

Dependencies and integration points: depends on `meta_ctx_get/set()`, `meta_ops_set()`, `strfd`, and the parent `xlator-dir.c` context contract.

Risks and edge cases: a missing or stale xlator context will dereference null or freed memory. Long-lived fds can cache an old name if graph state changes.

Test signals: traverse `.meta/.../<xlator>/name`, verify output matches the translator name, and test behavior across graph reloads or fd reopen.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/meta/src/name-file.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/meta/src/option-file.c -->
# sources/distributed-fs/glusterfs/xlators/meta/src/option-file.c

Purpose: implements one virtual file per xlator option, exposing the option value as text.

Important APIs/types/functions: `option_file_fill()` formats `data_to_str(data)` from a `data_t *` stored in inode context. `meta_option_file_hook()` looks up the option by `loc->name` in the parent xlator's `options` dict, stores the `data_t *`, and attaches `option_file_ops`.

Control flow: `options-dir.c` creates dynamic dirents with `meta_option_file_hook`. On lookup, this hook binds the matched dictionary value. On read, the default file path calls `option_file_fill()`.

State and persistence behavior: the file holds a raw pointer to a dictionary value owned by the xlator options dict; it does not copy or persist option data. Fd reads cache the rendered string.

Dependencies and integration points: depends on Gluster dict/data APIs, `meta_ctx_get/set()`, and `data_to_str()`. It integrates with `options-dir.c`.

Risks and edge cases: if an option disappears or has a null value between lookup and read, `data_to_str()` usage can fail. The value is not escaped beyond `data_to_str()`, so binary or unusual option data may render poorly.

Test signals: list `options`, read scalar options, test missing option lookup failure, and verify reopened fds reflect changed option values while already-open fds keep cached content.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/meta/src/option-file.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/meta/src/options-dir.c -->
# sources/distributed-fs/glusterfs/xlators/meta/src/options-dir.c

Purpose: implements the virtual `options` directory beneath each xlator entry, dynamically listing every key in the target translator's options dictionary.

Important APIs/types/functions: `options_dir_fill()` allocates an array of `struct meta_dirent` sized by `xl->options->count`. `dict_key_add()` fills each entry with a duplicated key name, regular-file type, and `meta_option_file_hook`. `meta_options_dir_hook()` propagates parent xlator context and attaches `options_dir_ops`.

Control flow: lookup or readdir of `options` first installs `options_dir_ops`. Readdir calls `options_dir_fill()` via the default directory path, then each returned dirent can be looked up as an option file.

State and persistence behavior: dynamic dirents are generated from the live options dict and cached per directory fd until release. The directory itself persists no state.

Dependencies and integration points: depends on Gluster dict iteration, `GF_CALLOC`, `gf_strdup`, `meta_option_file_hook`, and the xlator context installed by `xlator-dir.c`.

Risks and edge cases: allocation size uses the dict count and assumes `dict_foreach()` visits exactly that many entries. Option mutations while a directory fd is open can make listings stale. `dict_key_add()` does not handle `gf_strdup()` failure per entry.

Test signals: readdir on xlator `options`, lookup/read each generated option file, memory cleanup on releasedir, and option dictionary mutation followed by reopen.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/meta/src/options-dir.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/meta/src/private-file.c -->
# sources/distributed-fs/glusterfs/xlators/meta/src/private-file.c

Purpose: implements the virtual `private` file for an xlator, dumping translator-private state through Gluster's statedump formatter.

Important APIs/types/functions: `private_file_fill()` retrieves the target `xlator_t *` from inode context and calls `gf_proc_dump_xlator_private(xl, strfd)`. `meta_private_file_hook()` installs `private_file_ops` and copies parent xlator context.

Control flow: lookup under an xlator directory binds the same xlator context to the file. Readv uses the default generated-file path to invoke the statedump callback and cache its text.

State and persistence behavior: output reflects volatile in-memory private state at first read on an fd. Nothing is stored by this module.

Dependencies and integration points: depends on `glusterfs/statedump.h`, `strfd`, and each xlator's statedump/private dump support. Integrated through `xlator-dir.c` fixed dirents.

Risks and edge cases: private dumps may expose sensitive or large operational state. A translator without safe private dump behavior could produce incomplete output or fail. Cached fd output may not track changing private state.

Test signals: read `private` for representative xlators, compare with statedump expectations, test large output reads with offsets, and verify no crash for xlators with minimal private state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/meta/src/private-file.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/meta/src/process_uuid-file.c -->
# sources/distributed-fs/glusterfs/xlators/meta/src/process_uuid-file.c

Purpose: implements the root-level virtual `process_uuid` file, exposing `this->ctx->process_uuid`.

Important APIs/types/functions: `process_uuid_file_fill()` writes the process UUID plus newline. `meta_process_uuid_file_hook()` attaches `process_uuid_file_ops`.

Control flow: `root-dir.c` exposes the `process_uuid` dirent. Lookup calls the hook, and readv calls the default file fill path.

State and persistence behavior: reads reflect the current Gluster process context UUID, cached for each open fd after materialization. No persistent storage is changed.

Dependencies and integration points: depends on Gluster xlator context and `strfd`.

Risks and edge cases: assumes `this->ctx` and `process_uuid` are valid. UUID value can reveal process identity useful for diagnostics and correlation.

Test signals: read `.meta/process_uuid`, verify it matches process context, and validate repeated offset reads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/meta/src/process_uuid-file.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/meta/src/profile-file.c -->
# sources/distributed-fs/glusterfs/xlators/meta/src/profile-file.c

Purpose: implements the virtual `profile` file under each xlator, exposing profiling counters through Gluster's statedump profile formatter.

Important APIs/types/functions: `profile_file_fill()` calls `gf_proc_dump_xlator_profile(xl, strfd)` for the xlator stored in inode context. `meta_profile_file_hook()` attaches `profile_file_ops` and propagates parent context.

Control flow: lookup of `profile` beneath an xlator directory binds that xlator. Reads invoke the profile dump and cache the generated text per fd.

State and persistence behavior: no state is persisted; output is a snapshot of volatile profile counters at first read.

Dependencies and integration points: depends on statedump/profile support and `xlator-dir.c` fixed entries. The output quality depends on profiling instrumentation in the target xlator.

Risks and edge cases: profile data may be large or change rapidly. Long-lived fd caching can hide updates. Missing context causes unsafe dereference.

Test signals: read profile for active translators, compare with enabled profiling counters, and test behavior when profiling data is absent or zero.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/meta/src/profile-file.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/meta/src/root-dir.c -->
# sources/distributed-fs/glusterfs/xlators/meta/src/root-dir.c

Purpose: defines the fixed top-level contents of the `.meta` root directory.

Important APIs/types/functions: `root_dir_dirents` contains entries for `graphs`, `frames`, `logging`, `process_uuid`, `version`, `cmdline`, `mallinfo`, `root`, `measure_latency`, and dot entries. `meta_root_dir_hook()` attaches `meta_root_dir_ops` with that fixed dirent array.

Control flow: `meta.c::meta_lookup()` calls `meta_root_dir_hook()` when the synthetic root is looked up. Subsequent lookup/readdir uses default directory behavior over `root_dir_dirents`, and each child hook installs its own ops/context.

State and persistence behavior: no mutable state in this file. It statically defines root layout; runtime data is produced by child modules.

Dependencies and integration points: depends on `meta-hooks.h` declarations for child hooks. It is the entry point connecting top-level meta lookup to the rest of the virtual tree.

Risks and edge cases: fixed entries must match available hook implementations. Adding/removing entries changes user-visible meta ABI. `measure_latency` is writable in its own module, so exposing it at root creates a tuning surface.

Test signals: top-level readdir ordering/content, lookup of every root entry, and link/build checks for all referenced hooks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/meta/src/root-dir.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/meta/src/subvolume-link.c -->
# sources/distributed-fs/glusterfs/xlators/meta/src/subvolume-link.c

Purpose: implements symlinks in an xlator's `subvolumes` directory. Each numeric entry points to a child translator by relative path.

Important APIs/types/functions: `subvolume_link_fill()` formats `../../<child-name>`. `meta_subvolume_link_hook()` parses the numeric dirent name with `strtol()`, walks the parent xlator's `children` list to that index, stores the selected child `xlator_t *`, and attaches `subvolume_link_ops`.

Control flow: `subvolumes-dir.c` creates numeric symlink entries. Lookup of one entry calls this hook; readlink invokes `subvolume_link_fill()`.

State and persistence behavior: stores a live child xlator pointer in inode context and persists nothing. Link target is generated on demand and cached per fd/readlink call by default logic.

Dependencies and integration points: depends on xlator child-list ordering and context propagated by `subvolumes-dir.c`.

Risks and edge cases: invalid numeric names or child-list changes can leave `subvol` null, and fill then dereferences it. The relative path assumes the meta tree layout remains `xlator/subvolumes/N -> ../../name`.

Test signals: readlink for every child index, behavior with no children, graph reload while entries are open, and invalid manual lookup names.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/meta/src/subvolume-link.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/meta/src/subvolumes-dir.c -->
# sources/distributed-fs/glusterfs/xlators/meta/src/subvolumes-dir.c

Purpose: implements the virtual `subvolumes` directory beneath each xlator, listing child translators as numeric symlinks.

Important APIs/types/functions: `subvolumes_dir_fill()` counts `xl->children`, allocates `struct meta_dirent` entries, names them `0`, `1`, etc., sets type `IA_IFLNK`, and uses `meta_subvolume_link_hook`. `meta_subvolumes_dir_hook()` propagates parent xlator context and attaches `subvolumes_dir_ops`.

Control flow: readdir of `subvolumes` materializes numeric dirents from the current child list. Lookup/readlink of each numeric entry resolves to the corresponding child xlator.

State and persistence behavior: generated dirents are cached per directory fd; the directory mirrors live in-memory graph topology but does not persist it.

Dependencies and integration points: depends on `xlator_t.children`, `gf_strdup`, `GF_MALLOC`, and `subvolume-link.c`.

Risks and edge cases: allocation uses `count` without an explicit null terminator because dynamic dirent count is returned separately; callers must respect the count. Child-list changes after readdir can make numeric entries stale or point to different children on later lookup.

Test signals: readdir for xlators with zero, one, and many children; readlink targets; fd release cleanup of numeric names; and graph reload/reopen behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/meta/src/subvolumes-dir.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/meta/src/top-link.c -->
# sources/distributed-fs/glusterfs/xlators/meta/src/top-link.c

Purpose: implements a symlink exposing the top translator of a graph.

Important APIs/types/functions: `top_link_fill()` retrieves a `glusterfs_graph_t *` from inode context and formats the top xlator's name. `meta_top_link_hook()` installs `top_link_ops` and copies the parent graph context.

Control flow: graph directory modules expose a `top` link. Lookup binds graph context to the link inode; readlink asks `top_link_fill()` for the target.

State and persistence behavior: no persistent state. The symlink points to the top member of the graph snapshot stored in inode context.

Dependencies and integration points: depends on the graph context installed by graph-related hooks and on `graph->top` being a valid xlator pointer.

Risks and edge cases: null graph or top pointers crash fill. If graph topology changes while a fd/inode is cached, the target may become stale.

Test signals: readlink on graph top links for active and historical graphs, and behavior when graph top is absent in synthetic/test graphs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/meta/src/top-link.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/meta/src/type-file.c -->
# sources/distributed-fs/glusterfs/xlators/meta/src/type-file.c

Purpose: implements the virtual `type` file under each xlator, exposing the translator type string.

Important APIs/types/functions: `type_file_fill()` writes `xl->type` plus newline. `meta_type_file_hook()` attaches `type_file_ops` and copies parent xlator context.

Control flow: `xlator-dir.c` exposes `type`; lookup binds the parent xlator and readv renders the type through `strfd`.

State and persistence behavior: no persistent state; output reflects the target xlator's live `type` field at first read on the fd.

Dependencies and integration points: depends on xlator context from `xlator-dir.c` and the default generated-file FOPs.

Risks and edge cases: null context or type field causes unsafe access. Cached output can be stale after graph replacement.

Test signals: read type for multiple translators and verify it matches volfile/graph type.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/meta/src/type-file.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/meta/src/version-file.c -->
# sources/distributed-fs/glusterfs/xlators/meta/src/version-file.c

Purpose: implements the root-level virtual `version` file, reporting the build `PACKAGE_VERSION` in a small JSON-like object.

Important APIs/types/functions: `version_file_fill()` writes `Package Version`; `meta_version_file_hook()` attaches `version_file_ops`.

Control flow: root directory lookup of `version` installs the file ops. Readv invokes the default file generation path.

State and persistence behavior: no mutable state. The value is compile-time package metadata rendered at runtime.

Dependencies and integration points: depends on the build-defined `PACKAGE_VERSION` macro and `strfd`.

Risks and edge cases: output is JSON-like but not followed by a newline and should be treated as diagnostic text unless consumers validate it. Package version may not uniquely identify downstream patches.

Test signals: read `.meta/version`, parse expected package version string, and verify offset reads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/meta/src/version-file.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/meta/src/view-dir.c -->
# sources/distributed-fs/glusterfs/xlators/meta/src/view-dir.c

Purpose: provides the placeholder `view` directory beneath an xlator entry. In this source it contains only dot entries and no dynamic fill callback.

Important APIs/types/functions: `view_dir_dirents` contains `.` and `..`; `meta_view_dir_hook()` propagates parent context and attaches `view_dir_ops`.

Control flow: lookup of `view` under an xlator directory installs a directory whose readdir returns only dot entries through default directory handling.

State and persistence behavior: no persistent or dynamic state is maintained. Parent xlator context is stored even though this file does not currently use it.

Dependencies and integration points: included as a fixed child in `xlator-dir.c`, likely reserving a namespace for future or external view entries.

Risks and edge cases: users may expect meaningful contents from `view` because it is exposed, but this implementation is empty. Future additions must preserve existing lookup semantics.

Test signals: lookup and readdir of `view`, ensuring it behaves as an empty directory and does not return errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/meta/src/view-dir.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/meta/src/volfile-file.c -->
# sources/distributed-fs/glusterfs/xlators/meta/src/volfile-file.c

Purpose: implements a virtual file that reconstructs a graph's volume-file-style configuration from live xlator graph structures.

Important APIs/types/functions: `xldump_options()` emits `option` lines for each xlator option, `xldump_subvolumes()` emits a `subvolumes` line from children, `xldump()` prints one `volume` block, and `volfile_file_fill()` traverses the graph depth-first with `xlator_foreach_depth_first()`. `meta_volfile_file_hook()` binds graph context and attaches `volfile_file_ops`.

Control flow: lookup of the graph's volfile entry stores the parent graph pointer on the file inode. Readv materializes all xlator blocks into a `strfd`, then default readv slices it to the caller's requested offset/size.

State and persistence behavior: generated output is a snapshot of the in-memory graph and options at first fd read. It is not a persisted volfile and may omit comments, original ordering details, or build/runtime defaults not present in the graph dict.

Dependencies and integration points: depends on `glusterfs_graph_t`, xlator traversal helpers, option dict iteration, and graph directory hooks that install graph context.

Risks and edge cases: `xldump_options()` uses `value->data` directly, so non-string data or values needing quoting may render incorrectly. Graphs with dynamic changes can produce stale output on open fds. The reconstructed file may be diagnostic rather than faithfully reloadable.

Test signals: compare generated output against known graphs, verify option/subvolume lines, test graphs without children, and read large graphs with offset slicing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/meta/src/volfile-file.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/meta/src/xlator-dir.c -->
# sources/distributed-fs/glusterfs/xlators/meta/src/xlator-dir.c

Purpose: defines the virtual directory layout for one translator and provides hooks to bind either a named graph xlator or the process root xlator.

Important APIs/types/functions: `xlator_dir_dirents` exposes `view`, `type`, `name`, `subvolumes`, `options`, `private`, `history`, `meminfo`, and `profile`. `meta_xlator_dir_hook()` retrieves a graph pointer from the parent inode, searches `graph->first` by `loc->name`, stores the matching `xlator_t *`, and attaches `xlator_dir_ops`. `meta_root_hook()` binds `this->ctx->root` as the special root xlator directory.

Control flow: graph directories use `meta_xlator_dir_hook()` for each translator child. Once an xlator directory is looked up, its fixed dirents route to specialized files and directories that all inherit the xlator context. The top-level `root` entry bypasses graph-name lookup and directly uses the process root xlator.

State and persistence behavior: stores live `xlator_t *` pointers in inode context. No persistent data is written.

Dependencies and integration points: depends on graph hooks that supply `glusterfs_graph_t *`, `xlator_search_by_name()`, and all child hook declarations in `meta-hooks.h`.

Risks and edge cases: failed name lookup can store null xlator context, causing later child fills to crash. Graph replacement can invalidate stored xlator pointers. The fixed directory layout is a user-visible diagnostic ABI.

Test signals: lookup every xlator by graph name, traverse every fixed child, test special `.meta/root`, and validate behavior after graph reload or missing names.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/meta/src/xlator-dir.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/mgmt/Makefile.am -->
# sources/distributed-fs/glusterfs/xlators/mgmt/Makefile.am

Purpose: top-level Automake dispatcher for management xlators. It delegates the `mgmt` subtree build to `glusterd`.

Important APIs/types/functions: `SUBDIRS = glusterd` and an empty `CLEANFILES` definition.

Control flow: Automake descends into `xlators/mgmt/glusterd` during build, install, and clean phases.

State and persistence behavior: no runtime state. Build state is limited to generated make artifacts in the build tree.

Dependencies and integration points: integrated by the parent GlusterFS Automake hierarchy; the existence of `glusterd/Makefile.am` is required.

Risks and edge cases: omitting additional management subdirectories here would exclude them from builds. Empty `CLEANFILES` is harmless but redundant.

Test signals: `make` traversal from the repository root and distribution tarball checks include the glusterd subtree.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/mgmt/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/Makefile.am -->
# sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/Makefile.am

Purpose: Automake dispatcher for the glusterd management translator subtree.

Important APIs/types/functions: `SUBDIRS = src` and empty `CLEANFILES`.

Control flow: build/install/clean traversal descends into `xlators/mgmt/glusterd/src`, where the actual translator module is defined.

State and persistence behavior: no runtime state.

Dependencies and integration points: depends on `src/Makefile.am`; included by `xlators/mgmt/Makefile.am`.

Risks and edge cases: any new glusterd subdirectories must be added here or they will be skipped by Automake recursion.

Test signals: full Automake build traversal and `make distcheck`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/Makefile.am -->
# sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/Makefile.am

Purpose: defines how the `glusterd` management translator shared module is compiled, linked, installed, and given generated preprocessor paths.

Important APIs/types/functions: guarded by `WITH_SERVER`, `xlator_LTLIBRARIES = glusterd.la`; module install path is `$(libdir)/glusterfs/$(PACKAGE_VERSION)/xlator/mgmt`. `glusterd_la_SOURCES` lists core daemon, op-state-machine, volume, brick, bitrot, geo-rep, snapshot, service, connection, ganesha, and snapshot backend sources. `noinst_HEADERS` lists internal headers. `AM_CPPFLAGS` defines include paths and runtime constants such as `SBIN_DIR`, `DATADIR`, `CONFDIR`, `GANESHA_PREFIX`, and `SYNCDAEMON_COMPILE`.

Control flow: Automake compiles all listed sources into `glusterd.la`, links libglusterfs, RPC/XDR libraries, XML, crypto, userspace-RCU, dl, and management-specific libs. `install-data-hook` optionally moves existing `/etc/glusterd` state into `GLUSTERD_WORKDIR` and symlinks the old config path.

State and persistence behavior: the build file itself has no runtime state, but it defines paths that glusterd code uses for persistent workdir/config, shared storage ganesha config, and libexec helpers. The install hook can mutate installation-time glusterd state layout.

Dependencies and integration points: integrates many glusterd source files into one xlator module and binds external dependencies (`libglusterfs`, `libgfrpc`, `libgfxdr`, XML, OpenSSL, URCU). Ganesha code depends on `CONFDIR` and `GANESHA_PREFIX` from this file.

Risks and edge cases: source/header list drift causes missing symbols or stale files in dist builds. Hard-coded generated path macros must match deployment packaging. The install hook uses shell commands with `DESTDIR`/`sysconfdir`/`GLUSTERD_WORKDIR`; packaging should validate symlink behavior.

Test signals: build with and without `WITH_SERVER`, `make distcheck`, link checks for all glusterd symbols, install tests for workdir migration, and package tests validating generated path macros.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-bitd-svc.c -->
# sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-bitd-svc.c

Purpose: manages the BitD daemon service used by Gluster bitrot signing. It builds the service object, initializes it, creates the service volfile, starts/stops the process, connects RPC, and decides between live reconfigure and restart.

Important APIs/types/functions: `glusterd_bitdsvc_build()` installs service callbacks. `glusterd_bitdsvc_init()` calls `glusterd_svc_init()` with `bitd`. `glusterd_bitdsvc_create_volfile()` writes the global BitD volfile via `glusterd_create_global_volfile(build_bitd_graph, ...)`. `glusterd_bitdsvc_manager()` initializes and either stops BitD when no local started bitrot volume needs it, or recreates volfile, kills old process, starts it, and connects `svc->conn`. `glusterd_bitdsvc_reconfigure()` compares volfiles/topology and either notifies existing daemons or delegates to the manager.

Control flow: service manager lazily initializes `svc`; `glusterd_should_i_stop_bitd()` gates stop-vs-start. Reconfigure first avoids work when the rendered volfile is identical, then checks topology identity. If only options changed it writes a fresh volfile and sends `glusterd_fetchspec_notify()`. If topology changed, it restarts through the manager.

State and persistence behavior: BitD service state is held in `glusterd_svc_t` (`inited`, callbacks, connection). Persistent/observable artifacts include the generated BitD volfile under glusterd workdir and the running bitd process. No volume options are modified here.

Dependencies and integration points: depends on bitrot policy from `glusterd-bitrot.c`, service helpers, volfile generation (`build_bitd_graph`), generic service start/stop, connection management, and event emission.

Risks and edge cases: killing with `SIGKILL` before start is blunt and can disrupt in-flight work. Incorrect topology identity detection can notify when a restart is needed or restart unnecessarily. RPC connect failure after process start leaves partial service state and emits `EVENT_SVC_MANAGER_FAILED`.

Test signals: enable/disable bitrot across local/nonlocal bricks, reconfigure option-only vs topology-changing cases, no-op identical volfile path, service start/stop failures, and RPC connection establishment.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-bitd-svc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-bitd-svc.h -->
# sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-bitd-svc.h

Purpose: declares the BitD service management interface for glusterd.

Important APIs/types/functions: defines `bitd_svc_name` as `"bitd"` and declares `glusterd_bitdsvc_build()`, `glusterd_bitdsvc_init()`, `glusterd_bitdsvc_manager()`, `glusterd_bitdsvc_stop()`, and `glusterd_bitdsvc_reconfigure()`.

Control flow: glusterd initialization uses the build/init declarations to wire a `glusterd_svc_t`; bitrot option changes use the manager/reconfigure declarations.

State and persistence behavior: no state is stored in the header. The functions operate on `glusterd_svc_t` and generated service volfiles/processes.

Dependencies and integration points: includes `glusterd-svc-mgmt.h` for `glusterd_svc_t`. Used by bitrot and service initialization code.

Risks and edge cases: service name macro must match volfile path naming, process management, and logs. Prototype drift breaks callers at compile time.

Test signals: compile/link glusterd with bitd service enabled and exercise all declared functions through bitrot operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-bitd-svc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-bitrot.c -->
# sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-bitrot.c

Purpose: implements glusterd CLI/RPC handling, staging, commit, option mutation, and daemon orchestration for bitrot and scrub features.

Important APIs/types/functions: `gd_bitrot_op_list` maps option enum values to strings. Request entry points are `__glusterd_handle_bitrot()` and `glusterd_handle_bitrot()`. Option handlers include `glusterd_bitrot_enable()`, `glusterd_bitrot_disable()`, scrub throttle/frequency/state handlers, expiry-time, and signer-thread handlers. Service policy functions are `glusterd_should_i_stop_bitd()` and `glusterd_manage_bitrot()`. Operation phases are `glusterd_op_stage_bitrot()` and `glusterd_op_bitrot()`.

Control flow: the handler decodes the CLI dict, extracts volume/type, routes scrub status and ondemand commands to specialized ops, and otherwise starts the `GD_OP_BITROT` synctask. Stage validates volume existence, started status, bitrot enablement for non-enable commands, op-version for ondemand handled earlier, and duplicate scrub state. Commit finds the volume, switches on operation type, mutates `volinfo->dict`, reconfigures bitd or scrub services when needed, manages bitd/scrub daemon start/stop for enable/disable, recreates volfiles, notifies services, and stores `volinfo` with version increment.

State and persistence behavior: persistent volume options include `features.bitrot`, `features.scrub`, `features.scrub-throttle`, `features.scrub-freq`, `features.expiry-time`, and `features.signer-threads`. Service side effects include BitD and scrub daemon restarts/reconfigures and generated volfiles. Runtime decisions inspect `conf->volumes`, brick locality, brick status, and cluster op-version.

Dependencies and integration points: depends on glusterd op-state-machine, store, utils, volgen, scrub service, bitd service, RPC/XDR decode, dict APIs, compatibility errno, and op-version constants. It integrates CLI commands with management transaction phases and service managers.

Risks and edge cases: service reconfiguration can partially succeed before store failure. `is_bitd_configure_noop()` skips restart unless a local started brick needs bitrot; wrong locality/status data can leave BitD stopped incorrectly. Duplicate code artifacts in this snapshot show repeated lines around scrub frequency and switch, which deserve syntax/build validation. Scrub resume maps to `Active`, so string comparisons must remain compatible with stored values.

Test signals: enable/disable bitrot on stopped/started volumes, repeat enable/disable, scrub pause/resume/status/ondemand with op-version gating, throttle/frequency/expiry/signer thread changes, local vs remote brick service decisions, store failure injection, and volfile regeneration/reconfigure behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-bitrot.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-brick-ops.c -->
# sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-brick-ops.c

Purpose: implements glusterd add-brick, remove-brick, tier-brick stubs, and barrier operations. It spans CLI request decoding, topology validation, staging, commit-time volume mutations, service/volfile regeneration, rebalance/decommission orchestration, and related geo-rep/snapshot/quorum safeguards.

Important APIs/types/functions: add-brick helpers include `add_brick_at_right_order()`, `gd_addbr_validate_replica_count()`, `__glusterd_handle_add_brick()`, `glusterd_op_stage_add_brick()`, `glusterd_op_perform_add_bricks()`, and `glusterd_op_add_brick()`. Remove-brick helpers include `gd_rmbr_validate_replica_count()`, `subvol_matcher_*()`, `glusterd_remove_brick_validate_arbiters()`, `__glusterd_handle_remove_brick()`, `glusterd_remove_brick_validate_bricks()`, `glusterd_op_stage_remove_brick()`, `glusterd_op_perform_remove_brick()`, `glusterd_set_rebalance_id_for_remove_brick()`, and `glusterd_op_remove_brick()`. Other exported operations are `glusterd_post_commit_brick_operation()`, `glusterd_op_stage_barrier()`, `glusterd_op_barrier()`, and no-op tier handlers.

Control flow: add-brick request handling decodes the CLI dict, validates volume/count/replica/arbiter semantics, possibly changes volume type, then launches the v3 management transaction. Stage validates volume ID, brick order, quorum, rebalance state, snapshot warning, path length, duplicate/new brick constraints, local brick path creation, and mount-dir collection into the response dict. Commit parses brick strings, creates brickinfo records, assigns brick IDs, resolves UUIDs, inserts bricks in replica-aware order, updates replica/arbiter/dist/subvol counts and options, regenerates volfiles, starts new local bricks, handles replicate dummy client volfiles and self-heal daemon restart, restarts geo-rep sessions if local bricks were added, and runs service managers.

State and persistence behavior: add/remove operations mutate `glusterd_volinfo_t` fields: brick list/count, type, replica/arbiter/dist leaf/subvol counts, brick ids, brick status/decommission flags, `performance.client-io-threads`, rebal task state, and `decommission_in_progress`. Persistent side effects include generated brick/client volfiles and `glusterd_store_volinfo(...AC_INCREMENT)`. Remove-brick start stores a dict of bricks in `volinfo->rebal.dict` and a task UUID; commit/stop clears task state.

Dependencies and integration points: depends on glusterd op-sm, geo-rep, store, management v3 framework, utils, volgen, service helpers, server quorum, snapshots, rebalance/defrag, peer RCU lookup, PID/service checks, and RPC/XDR CLI response. It integrates with CLI `add-brick`, `remove-brick`, barrier volume option flow, geo-rep restart, self-heal daemon, NFS/service reconfigure, and volume store.

Risks and edge cases: topology math is safety-critical for replica/arbiter conversion; wrong counts can cause data loss. Remove-brick requires careful distinction between start/stop/commit/commit-force and migration status. Partial failures after brick list mutation but before volfile/store can leave in-memory and persistent state divergent. Local brick liveness and peer connectivity checks rely on current status/PID data. Snapshot warning text does not block operation. Some comments note disabled callback behavior for remove-brick migration completion, so commit-force/decommission cleanup paths should be scrutinized.

Test signals: add bricks to distribute, replicate, distributed-replicate, arbiter, and disperse volumes; increase replica count; reject invalid brick order unless forced; local path validation and mount-dir response; quorum failure; rebalance-in-progress rejection; remove-brick start/status/stop/commit/commit-force; replica reduction including arbiter conversions; offline/dead/local/remote brick validation; task ID persistence; volfile/store failure injection; service restart and geo-rep restart coverage; barrier set/stage behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-brick-ops.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-conn-helper.c -->
# sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-conn-helper.c

Purpose: provides a small container-of helper that maps a `glusterd_conn_t *` back to its owning `glusterd_svc_t`.

Important APIs/types/functions: `glusterd_conn_get_svc_object()` uses `cds_list_entry(conn, glusterd_svc_t, conn)`.

Control flow: connection initialization calls this helper to obtain the service name and object from the embedded connection field.

State and persistence behavior: no state is stored. It relies on struct embedding layout.

Dependencies and integration points: includes `glusterd-conn-mgmt.h`, `glusterd-svc-mgmt.h`, and userspace-RCU list macros. It is used by `glusterd-conn-mgmt.c`.

Risks and edge cases: passing a connection not embedded in `glusterd_svc_t` yields invalid memory. The helper is tightly coupled to `glusterd_svc_t` layout.

Test signals: initialize service connections for every daemon type and verify the derived service name/object is correct under sanitizers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-conn-helper.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-conn-helper.h -->
# sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-conn-helper.h

Purpose: declares the connection-to-service helper used by glusterd connection management.

Important APIs/types/functions: `glusterd_conn_get_svc_object(glusterd_conn_t *conn)` returns the owning `glusterd_svc_t *`.

Control flow: included by connection management code before creating RPC clients so the service name can be passed to RPC setup.

State and persistence behavior: no state.

Dependencies and integration points: includes `glusterd-conn-mgmt.h` and exposes a helper whose return type is `glusterd_svc_t`.

Risks and edge cases: the header assumes `glusterd_svc_t` is visible from included dependencies or caller context. Prototype drift with the implementation will break builds.

Test signals: compile all connection-management users and exercise service connection initialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-conn-helper.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-conn-mgmt.c -->
# sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-conn-mgmt.c

Purpose: manages RPC client connections from glusterd to managed service daemons, including initialization, start/disable, socket path generation, and notification dispatch under appropriate locks.

Important APIs/types/functions: `glusterd_conn_init()` builds Unix transport options, creates `rpc_clnt`, registers `glusterd_conn_common_notify()`, stores socket path, and records the service-specific notify callback. `glusterd_conn_term()`, `glusterd_conn_connect()`, and `glusterd_conn_disconnect()` wrap RPC lifecycle. `glusterd_conn_build_socket_filepath()` maps rundir and UUID to a socket path. Notification functions include `__glusterd_conn_common_notify()`, `glusterd_conn_common_notify()`, `__glusterd_muxsvc_conn_common_notify()`, and `glusterd_muxsvc_conn_common_notify()`.

Control flow: service initialization calls `glusterd_conn_init()`, which derives the owning service object, creates an RPC client named after the service, and registers a notify trampoline. Regular notifications are routed through `glusterd_big_locked_notify()` then to `conn->notify`. Multiplexed service notifications free `glusterd_svc_proc_t` and unref volume data on `RPC_CLNT_DESTROY`; other events run under `conf->attach_lock`.

State and persistence behavior: `glusterd_conn_t` stores the `rpc_clnt *`, service notify callback, and socket path. This is volatile runtime state. No persistent files are written, though socket paths point to runtime sockets.

Dependencies and integration points: depends on RPC client APIs, transport option builders, dict APIs, glusterd global locking, service helper, attach-lock state, and socket path utilities. Used by service managers such as BitD.

Risks and edge cases: `options` ownership is transferred to rpc transport but also unrefed locally; correctness depends on RPC API ref semantics. `glusterd_conn_term()` assumes `conn->rpc` is non-null. Notification callbacks silently ignore null connection/proc data. Multiplex destroy deliberately avoids locks to prevent deadlock, so lifetime ordering is critical.

Test signals: connection init failure injection at dict/transport/rpc/register stages, connect/disconnect, notify delivery under big lock, mux destroy freeing volume refs, socket filepath length handling, and repeated term/init cycles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-conn-mgmt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-conn-mgmt.h -->
# sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-conn-mgmt.h

Purpose: declares the glusterd service RPC connection abstraction and notification APIs.

Important APIs/types/functions: `glusterd_conn_t` contains `struct rpc_clnt *rpc`, a `glusterd_conn_notify_t notify` callback, and `sockpath[PATH_MAX]`. The header declares init/term/connect/disconnect, regular and mux notification trampolines, and socket filepath construction.

Control flow: service code embeds `glusterd_conn_t`, initializes it with a Unix socket and callback, then uses connect/disconnect wrappers while RPC events call the declared notify functions.

State and persistence behavior: describes volatile connection state only. Socket path strings refer to runtime filesystem sockets.

Dependencies and integration points: includes `rpc-clnt.h`; implemented by `glusterd-conn-mgmt.c`; consumed by service management modules.

Risks and edge cases: callback type only receives `conn` and event, so service-specific data must be recovered from embedding/context. Fixed `PATH_MAX` buffer requires careful path generation.

Test signals: compile service modules against the header and run lifecycle tests for each service connection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-conn-mgmt.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-errno.h -->
# sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-errno.h

Purpose: defines glusterd-specific operation error numbers for management-layer failures.

Important APIs/types/functions: `enum glusterd_op_errno` assigns values starting at 30800 for internal error, unsupported op, transaction in progress, brick/node down, hard limit, missing volume/snapshot, rebalance running, volume running/stopped/existing, snapshot existing, snap volume, geo-rep running, thin provisioning mismatch, and NFS-Ganesha not enabled.

Control flow: operation code can use these enum values in CLI/RPC responses or error mapping to represent domain-specific failures beyond generic `errno`.

State and persistence behavior: no state. Values are part of the management protocol surface and should be stable.

Dependencies and integration points: standalone header included by glusterd operation modules where needed.

Risks and edge cases: changing numeric values can break clients or logs that interpret these codes. Adding values requires avoiding collisions.

Test signals: CLI/RPC error response tests should verify expected codes for representative management failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-errno.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-ganesha.c -->
# sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-ganesha.c

Purpose: manages global NFS-Ganesha enablement and per-volume `ganesha.enable` export operations from glusterd. It coordinates shared HA config parsing, external helper scripts, service manager commands, dbus export updates, cache-invalidation option updates, and persistent global/volume option storage.

Important APIs/types/functions: config/service helpers include `parsing_ganesha_ha_conf()`, `manage_service()`, `check_host_list()`, `start_ganesha()`, `stop_ganesha()`, `setup_cluster()`, `tear_down_cluster()`, `teardown()`, and `pre_setup()`. Public operation functions include `glusterd_is_ganesha_cluster()`, `glusterd_check_ganesha_export()`, `glusterd_check_ganesha_cmd()`, `glusterd_op_stage_set_ganesha()`, `glusterd_op_set_ganesha()`, `gd_ganesha_send_dbus()`, `manage_export_config()`, `ganesha_manage_export()`, and `glusterd_handle_ganesha_op()`.

Control flow: global `nfs-ganesha` staging rejects no-op values and starts or stops local Ganesha service paths as validation. Commit calls `glusterd_handle_ganesha_op()`, updates `priv->opts`, bumps the global option version, and stores options. Global enable runs HA setup only on the originator and requires that node to be listed in `HA_CLUSTER_NODES`; disable tears down HA and resets every volume's `ganesha.enable` and `features.cache-invalidation` to `off`. Per-volume `ganesha.enable=on` validates global enablement, creates export config on the originator, sends a dbus update on ganesha hosts, updates cache invalidation when requested, and stores volinfo.

State and persistence behavior: reads `CONFDIR/ganesha-ha.conf`, mutates shared Ganesha config files through scripts, manages system service state through `systemctl`/`invoke-rc.d`/`service`, stores global option `GLUSTERD_STORE_KEY_GANESHA_GLOBAL` and `GLUSTERD_GLOBAL_OPT_VERSION`, and stores per-volume `ganesha.enable` plus `features.cache-invalidation`. `tear_down_cluster()` removes generated files under `CONFDIR` except `ganesha.conf` and `ganesha-ha.conf`.

Dependencies and integration points: depends on glusterd store/utils/volgen/messages, runner API, syscall wrappers, generated macros `CONFDIR` and `GANESHA_PREFIX`, external scripts `ganesha-ha.sh`, `create-export-ganesha.sh`, and `dbus-send.sh`, system service managers, and the volume/global option dictionaries.

Risks and edge cases: many effects are external and partially ordered; script or service-manager failures can leave config, service, and stored options inconsistent. Config parsing assumes shell-like `KEY=value` lines with no spaces around `=`, and host list parsing mutates the allocated string. `manage_service()` chooses the first available manager path and may not match distro policy. Directory cleanup must not remove the two preserved config files. Per-volume export changes depend on dbus and service liveness only on nodes listed in HA config.

Test signals: global enable/disable from originator and non-ganesha host, missing/malformed `ganesha-ha.conf`, service manager fallback paths, script failure injection, per-volume export on/off idempotency, dbus failure, cache-invalidation updates, teardown cleanup preservation, and persistent option version/store checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-ganesha.c -->
