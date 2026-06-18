# sources/distributed-fs/lustre-release/lustre/llite/pcc.c

## Purpose

`pcc.c` implements Lustre llite Persistent Client Cache support. It manages client-local cache backends, policy parsing, automatic and ioctl-driven attachment, detachment, open/read/write/getattr/setattr/fsync/splice/mmap interception, and local copy lifecycle. The file supports two caching modes: PCC-RW, where a single client uses a local read-write copy synchronized through HSM archive semantics, and PCC-RO, where read-only local copies can be attached on multiple clients after setting/observing read-only layout state.

## Important APIs, types, and functions

The public entry points are declared in `pcc.h` and implemented here: `pcc_super_init()`, `pcc_super_fini()`, `pcc_cmd_handle()`, `pcc_super_dump()`, `pcc_readwrite_attach()`, `pcc_readwrite_attach_fini()`, `pcc_ioctl_attach()`, `pcc_ioctl_detach()`, `pcc_ioctl_state()`, `pcc_file_open()`, `pcc_file_release()`, `pcc_file_read_iter()`, `pcc_file_write_iter()`, `pcc_inode_getattr()`, `pcc_inode_setattr()`, `pcc_file_splice_read()`, `pcc_fsync()`, `pcc_file_mmap()`, `pcc_vm_open()`, `pcc_vm_close()`, `pcc_fault()`, `pcc_page_mkwrite()`, `pcc_inode_create()`, `pcc_inode_create_fini()`, `pcc_create_attach_cleanup()`, `pcc_dataset_match_get()`, `pcc_dataset_put()`, `pcc_inode_free()`, and `pcc_layout_invalidate()`.

The configuration path parses commands of the form `add <absolute path> <rule> key=value...`, `del <absolute path>`, and `clear`. Match rules are parsed as disjunctions of conjunctions, with expressions over `uid`, `gid`, `projid`, `fname`/`filename`, `size`, and `mtime`. Operators are `=`, `<`, and `>`, with equality list support for IDs, sizes, and names. `pcc_dataset_add()` validates server support and dataset flags, resolves the backend path with `kern_path()`, copies rule state, checks duplicate path/archive IDs, and installs the dataset under `pccs_rw_sem`. `pcc_super_dump()` emits YAML-like state for proc/debug consumers.

Attachment helpers include `pcc_dataset_get()`, `pcc_try_dataset_attach()`, `pcc_try_datasets_attach()`, `pcc_try_auto_attach()`, `pcc_try_readonly_open_attach()`, `pcc_readonly_attach_sync()`, `pcc_readonly_attach_async()`, and `pcc_readwrite_attach()`. Local object helpers include `pcc_fid2dataset_path()`, `pcc_lookup()`, `pcc_mkdir_p()`, `pcc_create()`, `pcc_inode_remove()`, `pcc_attach_data_archive()`, and `pcc_copy_data()`.

The I/O interceptors redirect operations to `struct pcc_file::pccf_file` when `pcc_io_init()` finds or auto-attaches a valid `struct pcc_inode`. `pcc_io_fini()` decrements `pcci_active_ios`, wakes detach/mmap waiters, and decides whether a failed PCC operation can be tolerated by falling back to normal Lustre I/O.

## Control flow

Mount/superblock setup calls `pcc_super_init()`, preparing a restricted credential used for backend filesystem operations and initializing the dataset list, generation, async threshold, and permission mode. Configuration writes call `pcc_cmd_handle()`, which parses a command into `struct pcc_cmd`, applies add/delete/clear, and frees command-owned rule state.

Open starts in `pcc_file_open()`. Regular files are considered only if encryption policy allows PCC. If an attach is already in progress the file is marked fallback. Otherwise existing `pcc_inode` layout is used, `pcc_try_auto_attach()` is attempted when generation/dataset flags allow it, and read-only policy attach may be attempted for read-only opens. On success the local backend file is opened with `dentry_open()` and stored in per-file data.

For read, write, stat, setattr, splice, fsync, mmap fault, and page-mkwrite paths, the common pattern is: initialize cached/fallback decision with `pcc_io_init()` or `pcc_mmap_io_init()`, call the backing file or backing vm operation when cached, then run `pcc_io_fini()`. RO cached files detach on write/setattr/page-mkwrite. RW write failures for `-ENOSPC` or `-EDQUOT` are not tolerated; most other eligible failures detach/fallback according to mode and operation.

PCC-RO attach first sets or verifies the Lustre read-only layout with `pcc_layout_rdonly_set()`, copies data from Lustre into a newly created PCC file, installs a `pcc_inode`, writes `user.PCC.layout`, and optionally records encrypted cleartext size in `user.PCC.encsize`. Large RO attachments may run in a kthread via `pcc_readonly_attach_async()`. PCC-RW attach creates/copies the local file, installs `pcc_inode`, then `pcc_readwrite_attach_fini()` records the layout generation after the HSM/layout side succeeds.

Detach uses `pcc_ioctl_detach()`. RW detach may request HSM remove/restore cleanup; RO detach clears the layout, may unlink the local copy, and drops the `pcc_inode` reference. `pcc_layout_invalidate()` performs similar detach when Lustre layout locks are revoked.

## State and persistence behavior

`struct pcc_super` persists client-side dataset configuration in memory and increments `pccs_generation` on removal/clear. Each `ll_inode_info` tracks `lli_pcc_inode`, `lli_pcc_state`, cached dataset flags, generation, mmap count, and fallback mmap-negative count. `struct pcc_inode` holds a backend `struct path`, refcount, PCC type, layout generation, active I/O count, waitqueue, and flags for attribute validity and unlink state.

On-disk state lives in backend filesystem paths derived from FID and HSM tool layout. `user.PCC.layout` stores the Lustre layout generation for auto reattach validation. `user.PCC.encsize` stores cleartext file size for encrypted PCC-RO copies whose local file contains ciphertext aligned to encryption units. Dataset rules and backend paths are not persisted by this file beyond the live `pcc_super` list.

Mmap is stateful and high-risk: for PCC mmap, Lustre may temporarily switch the Lustre inode mapping operations and host to the PCC inode mapping so page faults operate on the local backend. Detach waits for active I/O and resets mapping state, writes dirty pages, truncates page cache, restores `ll_aops`, and returns the PCC inode to its own `i_data` mapping.

## Dependencies and integration points

This file depends on llite internals (`ll_i2info`, `ll_i2sbi`, `ll_i2pccs`, `ll_layout_refresh`, `ll_layout_restore`, `ll_layout_write_intent`, stats counters), CLIO layout inspection (`cl_object_layout_get`), HSM ioctl paths (`LL_IOC_HSM_REQUEST`), VFS helpers (`dentry_open`, `lookup_noperm`, `vfs_create`, `vfs_unlink`, `notify_change`, xattrs), kernel credentials, kthreads, mmap `vm_operations_struct`, and Lustre encryption helpers (`llcrypt_decrypt_block_inplace`, `ll_has_encryption_key`, `S_PCCCOPY`). It integrates with llite file private data through `struct pcc_file`, with inode teardown through `pcc_inode_free()`, and with layout lock cancellation via `pcc_layout_invalidate()`.

## Risks and edge cases

Major risks are races among attach, detach, layout revocation, mmap faults, and open. These are mitigated by `lli_pcc_lock`, `PCC_STATE_FL_ATTACHING`, layout generation checks, `pcci_active_ios`, and waitqueues, but the code still contains explicit race failpoints. Backend filesystem semantics are another risk: project quota support may be absent and is disabled after `-EOPNOTSUPP`/`-ENOTTY`; mmap private data conflicts cause `-EOPNOTSUPP`; direct user access to PCC backend files is called out as a FIXME because shared mappings can be unsafe. Encrypted PCC-RO needs careful ciphertext/cleartext size handling and page-cache truncation to avoid stale plaintext. Auto attach can mark `PCC_DATASET_NONE` after misses, suppressing later attempts until generation changes or manual attach.

## Test signals

Useful test signals include proc command parsing for add/delete/clear, rule matching by UID/GID/project/name/size/mtime, duplicate dataset rejection, generation bumping, PCC-RO attach on read-only open, async attach threshold behavior, RW attach/fini with layout generation mismatch, detach with and without `PCC_DETACH_FL_UNCACHE`, encrypted PCC-RO read/decrypt and `encsize`, mmap attach/fault/page_mkwrite/detach retry behavior, failpoints such as `OBD_FAIL_LLITE_PCC_FAKE_ERROR`, `OBD_FAIL_LLITE_PCC_MKWRITE_PAUSE`, `OBD_FAIL_LLITE_PCC_DETACH_MKWRITE`, and stats counters `LPROC_LL_PCC_ATTACH`, `LPROC_LL_PCC_ATTACH_BYTES`, `LPROC_LL_PCC_HIT_BYTES`, `LPROC_LL_PCC_AUTOAT`, and `LPROC_LL_PCC_DETACH`.
