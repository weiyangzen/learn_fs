# subset-b-007097 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/sdfs/src/sdfs.c -->
# sources/distributed-fs/glusterfs/xlators/features/sdfs/src/sdfs.c

## Purpose
`sdfs.c` implements the GlusterFS `sdfs` translator, identified as "dentry-fop-serializer". It serializes operations that create, remove, rename, link, or inspect dentries by taking child `entrylk` locks before winding the real FOP to its single child translator. It is marked `GF_TECH_PREVIEW` and exposes a settable `pass-through` option, although this source always installs the serializer FOP table regardless of the option value.

## Important APIs, types, and functions
The translator FOP table handles `mkdir`, `rmdir`, `create`, `unlink`, `symlink`, `link`, `mknod`, `rename`, `lookup`, and `readdirp`. Common support functions include `sdfs_get_new_frame_common()`, `sdfs_get_new_frame()`, `sdfs_build_parent_loc()`, `sdfs_local_init()`, `sdfs_entrylk_cbk()`, and `sdfs_common_entrylk_cbk()`. The simple one-name write paths follow a repeated wrapper shape: allocate/copy a frame, allocate `sdfs_local_t`, store a call stub such as `fop_mkdir_stub()`, lock parent/name with `ENTRYLK_WRLCK`, resume the helper, wind the child FOP, unwind the original frame, unlock, then destroy the copied stack.

`link` and `rename` use `sdfs_lock_t` arrays from `sdfs.h`. `sdfs_entry_lock_cmp()` orders locks by parent GFID then basename so multi-entry operations acquire locks deterministically. `lookup` uses `ENTRYLK_RDLCK` on the target basename when the lookup has a parent; root lookup tail-winds directly. `readdirp` takes a read lock on the directory inode with a NULL basename.

## Control flow
Most FOPs are asynchronous two-stage calls. The public FOP creates a copied frame with a unique lock owner, saves the original frame in `local->main_frame`, saves a call stub in `local->stub`, then winds `entrylk` to the child. `sdfs_entrylk_cbk()` records lock status and resumes the stub; helpers check `local->op_ret`, wind the actual child FOP on success, or unwind failure to `main_frame` and destroy the copied frame. Child FOP callbacks first unwind the original caller and then wind the unlock request. The second `entrylk` callback has no stub and destroys the copied stack.

For `rename`, two lock records are initialized for old and new locations, sorted, and locked in parallel using `local->call_cnt` as an atomic countdown. After both lock callbacks return, `sdfs_rename_helper()` either winds the rename or unwinds failure and unlocks only acquired locks. `link` uses the same common callback machinery but currently initializes only the new location lock.

## State and persistence behavior
All state is in-memory and per-call. `sdfs_local_t` stores copied `loc_t` values, parent locations, a pending call stub, optional lock array, operation status, and atomic callback count. Translator-wide state is limited to `this->local_pool` and option state on `this`. There is no durable metadata written by this translator; persistence effects are entirely the downstream FOPs it serializes. Lock ownership is deliberately changed on copied frames through `set_lk_owner_from_ptr()` so internal locks are isolated per serialized request.

## Dependencies and integration points
This file depends on GlusterFS stack-wind/unwind macros, call stubs, `entrylk`, inode/location helpers, UUID utilities, atomics, translator option parsing, memory pools, and message IDs from `sdfs-messages.h`. It requires exactly one child translator at `init()` and logs a warning for dangling volumes. It integrates into Gluster via `xlator_api`, `fops`, `cbks`, and `volume_options`.

## Risks and edge cases
There is a serious-looking client reference bug in `sdfs_link()` and `sdfs_rename()`: both declare `client_t *client = NULL`, call `gf_client_ref(client)`, and assign the NULL client to `new_frame->root->client` instead of using `frame->root->client`, unlike `sdfs_get_new_frame_common()`. Multi-lock callbacks set `locks->entrylk->locked[lk_index]` rather than `locks->entrylk[lk_index].locked[lk_index]`, which is easy to misread and likely wrong for index 1. Some error paths count only contiguous acquired locks and mutate `lock_count` while iterating, which should be stress-tested. `sdfs_build_parent_loc()` stores `dirname(path)` in `parent->path`; this is valid only because `loc_wipe()` later owns/frees that buffer, so future changes must preserve ownership assumptions. `sdfs_symlink_cbk()` and error paths unwind with the `link` strict signature rather than `symlink`, which is another high-risk signal. The `pass-through` option is parsed but not used to bypass the serializer.

## Test signals
Useful tests should exercise concurrent same-name `mkdir/create/unlink/rmdir/mknod/symlink`, cross-directory and same-directory `rename`, hard-link creation, failed lock acquisition cleanup, root and non-root lookup, and `readdirp` under concurrent directory mutation. Tests should include sanitizer or fault-injection runs around allocation failure, child `entrylk` failure, and multi-lock partial success. A regression test should directly cover the `sdfs_link()`/`sdfs_rename()` client-reference paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/sdfs/src/sdfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/sdfs/src/sdfs.h -->
# sources/distributed-fs/glusterfs/xlators/features/sdfs/src/sdfs.h

## Purpose
`sdfs.h` declares the private call-state structures and stack-destroy helper used by the `sdfs` dentry serializer translator.

## Important APIs, types, and functions
`SDFS_LOCK_COUNT_MAX` fixes the maximum number of entry locks at two, matching rename-style operations. `sdfs_entry_lock_t` stores a parent `loc_t`, a basename, and a small `locked` array. `sdfs_lock_t` contains up to two entry-lock records and the active count. `sdfs_local_t` is the per-frame context: original `main_frame`, copied target and parent locations, pending `call_stub_t`, optional lock array, operation status, and atomic callback count. `SDFS_STACK_DESTROY(frame)` detaches `frame->local`, unreferences the client, destroys the stack root, and calls `sdfs_local_cleanup()`.

## Control flow and state
This header is tightly coupled to `sdfs.c`: public FOPs allocate `sdfs_local_t` from `this->local_pool`; callbacks inspect `stub`, `main_frame`, and `call_cnt`; cleanup frees copied locations, stubs, lock arrays, and the local object. No persistent state is declared here.

## Dependencies and integration points
It includes `glusterfs/call-stub.h`, `glusterfs/atomic.h`, and `sdfs-messages.h`, and assumes GlusterFS core types such as `loc_t`, `call_frame_t`, and `gf_atomic_t`.

## Risks and test signals
The nested `locked[SDFS_LOCK_COUNT_MAX]` array inside each entry record is unusual because common callback code indexes through `locks->entrylk->locked[index]`; reviewers should verify that this models intended per-lock status. `SDFS_STACK_DESTROY` assumes a valid `frame->root->client`, so callers must not install NULL clients in copied frames. Tests should target cleanup after partial lock acquisition and ensure all copied loc/stub resources are released.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/sdfs/src/sdfs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/selinux/Makefile.am -->
# sources/distributed-fs/glusterfs/xlators/features/selinux/Makefile.am

## Purpose
This Automake fragment is the top-level build entry for the `features/selinux` translator directory. It delegates all build work to `src`.

## Important APIs and control flow
`SUBDIRS = src` makes recursive Automake enter `xlators/features/selinux/src`. `CLEANFILES =` is present but empty, so the parent directory contributes no generated cleanup targets.

## State, dependencies, and integration
There is no runtime state. The file integrates the SELinux translator into the larger GlusterFS recursive build by making the `src/Makefile.am` visible from the feature directory.

## Risks and test signals
The main risk is omission: if `src` is removed or renamed, the SELinux translator will silently stop building from this branch. Build validation should run autoreconf/configure or the project build system and confirm `selinux/src` is traversed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/selinux/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/selinux/src/Makefile.am -->
# sources/distributed-fs/glusterfs/xlators/features/selinux/src/Makefile.am

## Purpose
This Automake file builds the SELinux feature translator module.

## Important APIs and build outputs
When `WITH_SERVER` is enabled, it builds `selinux.la` as an xlator module installed under `$(libdir)/glusterfs/$(PACKAGE_VERSION)/xlator/features`. The module source is `selinux.c`; private headers are `selinux.h`, `selinux-messages.h`, and `selinux-mem-types.h`. It links against `libglusterfs.la` and uses default xlator module flags.

## Dependencies and integration
`AM_CPPFLAGS` adds libglusterfs and RPC XDR include paths from both source and build trees. `AM_CFLAGS` enables `-Wall` plus project C flags. The conditional `WITH_SERVER` means packaging or client-only builds may omit the module.

## Risks and test signals
Because this file names only `selinux.c`, any new implementation file must be added here or it will not compile into the module. Build tests should cover both `WITH_SERVER` true and false, confirm the module install path, and verify the listed noinst headers are included in distribution/build dependencies as intended.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/selinux/src/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/selinux/src/selinux-mem-types.h -->
# sources/distributed-fs/glusterfs/xlators/features/selinux/src/selinux-mem-types.h

## Purpose
This header assigns memory-accounting IDs for allocations made by the SELinux translator.

## Important APIs and state
`enum gf_selinux_mem_types_` starts at `gf_common_mt_end + 1` and currently defines `gf_selinux_mt_selinux_priv_t` followed by `gf_selinux_mt_end`. `selinux.c` uses this ID when allocating `selinux_priv_t` and passes `gf_selinux_mt_end` to `xlator_mem_acct_init()`.

## Dependencies and integration
The header depends on `glusterfs/mem-types.h` for the common allocation namespace. It integrates with GlusterFS memory accounting through `mem_acct_init()`.

## Risks and test signals
The enum must remain append-only relative to memory-accounting expectations. Adding new SELinux-private allocations should add IDs before `gf_selinux_mt_end` and use them in allocation calls. Tests should include translator initialization with memory accounting enabled and fault injection for `GF_CALLOC`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/selinux/src/selinux-mem-types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/selinux/src/selinux-messages.h -->
# sources/distributed-fs/glusterfs/xlators/features/selinux/src/selinux-messages.h

## Purpose
This header defines stable GlusterFS log/message IDs for the SELinux translator.

## Important APIs
`GLFS_MSGID(SL, ...)` registers IDs for invalid volfile configuration, out-of-memory paths, memory-accounting initialization failure, missing `trusted.glusterfs.selinux` xattr, and missing `security.selinux` xattr. The comments explicitly require append-only maintenance to avoid ID reuse.

## Dependencies and integration
It includes `glusterfs/glfs-message-id.h` and is consumed by `selinux.c` for `gf_msg()` calls in init and xattr rename paths.

## Risks and test signals
Removing or reordering IDs can break log compatibility and diagnostics. New log points should append IDs, not repurpose existing names. Tests are mainly compile-time plus log-path validation for invalid volfiles, memory-accounting failure, and xattr rename failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/selinux/src/selinux-messages.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/selinux/src/selinux.c -->
# sources/distributed-fs/glusterfs/xlators/features/selinux/src/selinux.c

## Purpose
`selinux.c` implements a GlusterFS feature translator that remaps the public SELinux xattr name `security.selinux` to Gluster's internal trusted xattr `trusted.glusterfs.selinux` while requests pass through the translator stack.

## Important APIs, types, and functions
The FOP table provides `getxattr`, `fgetxattr`, `setxattr`, and `fsetxattr`. `selinux_getxattr()` and `selinux_fgetxattr()` rewrite requested name `SELINUX_XATTR` to `SELINUX_GLUSTER_XATTR` when enabled, wind to the child, then their callbacks rename the returned dictionary key back to `security.selinux`. `selinux_setxattr()` and `selinux_fsetxattr()` rename dictionary keys from public to internal form before forwarding. `selinux_priv_t` stores only `selinux_enabled`.

## Control flow
Each FOP validates `this->private`, performs name/dictionary rewriting when enabled, winds the request to `FIRST_CHILD(this)`, and strict-unwinds in the callback. A NULL xattr name is treated as listxattr-style input and forwarded without rewriting. `init()` requires exactly one child, warns on no parents, allocates private state, reads the `selinux` option, creates a local pool, and stores `this->private`. `reconfigure()` reloads the option, `fini()` frees private state and destroys the pool, and `mem_acct_init()` registers memory types.

## State and persistence behavior
The translator keeps only in-memory configuration in `selinux_priv_t`; it does not persist state itself. Persistence impact is indirect: on setxattr/fsetxattr it changes which backend xattr key is stored.

## Dependencies and integration points
The file depends on GlusterFS xlator APIs, dictionaries, stack macros, option parsing, memory accounting, and message IDs. It integrates through `xlator_api` with identifier `selinux`, category `GF_MAINTAINED`, and the settable `selinux` boolean option defaulting to on.

## Risks and edge cases
Both setxattr paths use `if (!priv->selinux_enabled && !dict) goto off;`; this means a disabled translator with a non-NULL dict still attempts to rename keys, likely contrary to the intended "disabled means pass through" behavior. If `dict` is NULL while enabled, `dict_rename_key()` may be called with NULL unless the dictionary API tolerates it. Rewriting mutates caller dictionaries in place before forwarding, which can affect later translators if they expect the original key. Error paths return `EINVAL` for validation and dictionary failures rather than preserving richer causes.

## Test signals
Tests should cover enabled and disabled get/set/fget/fset flows, NULL names for listxattr, dictionaries with and without `security.selinux`, missing internal xattr on get, and reconfigure toggling. A regression test should assert disabled mode leaves xattr names unchanged for non-NULL dictionaries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/selinux/src/selinux.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/selinux/src/selinux.h -->
# sources/distributed-fs/glusterfs/xlators/features/selinux/src/selinux.h

## Purpose
`selinux.h` defines the xattr names and private configuration type used by the SELinux translator.

## Important APIs and state
`SELINUX_XATTR` is the public key `security.selinux`; `SELINUX_GLUSTER_XATTR` is the backend key `trusted.glusterfs.selinux`. `struct selinux_priv` contains `gf_boolean_t selinux_enabled`, which is loaded from the translator option and read by all xattr FOPs.

## Dependencies and integration
The header assumes GlusterFS boolean types are available through including source context. It is included by `selinux.c` and indirectly defines the translator's external behavior for xattr key remapping.

## Risks and test signals
Changing either macro changes on-disk/backend xattr compatibility. Tests should assert public clients see `security.selinux` while storage-facing operations use `trusted.glusterfs.selinux`, and that reconfigure changes only `selinux_enabled`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/selinux/src/selinux.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/shard/Makefile.am -->
# sources/distributed-fs/glusterfs/xlators/features/shard/Makefile.am

## Purpose
This top-level Automake fragment delegates the shard translator feature directory to `src`.

## Important APIs and control flow
`SUBDIRS = src` causes recursive builds to enter `xlators/features/shard/src`. `CLEANFILES =` is empty and contributes no local cleanup.

## State, dependencies, and integration
There is no runtime state. The file integrates the shard feature into the larger GlusterFS build traversal.

## Risks and test signals
If the `src` directory is not traversed, the shard translator will not be built. Build verification should check recursive Automake output includes `features/shard/src`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/shard/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/shard/src/Makefile.am -->
# sources/distributed-fs/glusterfs/xlators/features/shard/src/Makefile.am

## Purpose
This Automake file builds the shard feature translator module.

## Important APIs and build outputs
It builds `shard.la` unconditionally as an xlator module under the versioned GlusterFS feature xlator directory. The only implementation source listed is `shard.c`; private headers are `shard.h`, `shard-mem-types.h`, and `shard-messages.h`. It links against `libglusterfs.la` and uses `GF_XLATOR_DEFAULT_LDFLAGS`.

## Dependencies and integration
The module inherits GlusterFS CPP/C flags and includes libglusterfs plus RPC XDR source/build include directories. It integrates shard into the normal module install layout.

## Risks and test signals
Unlike the SELinux module, there is no `WITH_SERVER` guard here, so build environments must always be able to compile shard. Adding new source files requires updating `shard_la_SOURCES`. Build tests should confirm the module links and installs to the feature xlator path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/shard/src/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/shard/src/shard-mem-types.h -->
# sources/distributed-fs/glusterfs/xlators/features/shard/src/shard-mem-types.h

## Purpose
This header defines memory-accounting categories for the shard translator.

## Important APIs and state
`enum gf_shard_mem_types_` starts at `gf_common_mt_end + 1` and defines categories for private translator state, inode list nodes, inode context, int64 allocations, uint64 allocations, and the terminal `gf_shard_mt_end`.

## Dependencies and integration
It includes `glusterfs/mem-types.h` and is intended for `xlator_mem_acct_init()` plus `GF_CALLOC`/`GF_MALLOC` calls in shard implementation code.

## Risks and test signals
The enum should remain append-only before `gf_shard_mt_end` to preserve accounting consistency. Tests should include shard initialization with memory accounting and allocation-failure paths for each allocation class.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/shard/src/shard-mem-types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/shard/src/shard-messages.h -->
# sources/distributed-fs/glusterfs/xlators/features/shard/src/shard-messages.h

## Purpose
This header defines stable log/message IDs for the shard translator.

## Important APIs
`GLFS_MSGID(SHARD, ...)` declares IDs for lookup failures, dictionary failures, missing `.shard` directory, fd/inode context errors, internal xattr issues, invalid volfiles and FOPs, stat/truncate/file-size update failures, memory allocation failure, generic FOP failure, shard deletion failure, and shard deletion completion. The header comments require appending IDs rather than removing or reusing them.

## Dependencies and integration
It includes `glusterfs/glfs-message-id.h` and is consumed by the shard implementation for structured logging. These IDs are part of operator-facing diagnostics and compatibility expectations.

## Risks and test signals
Reordering or deleting IDs can break message stability. New diagnostics should append IDs after `SHARD_MSG_SHARD_DELETION_COMPLETED`. Compile tests should include all users of the message constants, and behavioral tests should force representative shard errors such as missing `.shard`, lookup failure, invalid FOP, and deletion failure to validate logging paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/shard/src/shard-messages.h -->
