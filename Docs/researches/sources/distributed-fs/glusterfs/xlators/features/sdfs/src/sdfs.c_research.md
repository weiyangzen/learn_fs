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
