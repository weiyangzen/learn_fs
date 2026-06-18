# Group Research: group_1087_linux_stable_sources_os_linux_linux_stable_fs_ubifs_compress_c_sour_5d84992a8874

Scope checked against `Docs/research_subset_a.md`: all files are within `sources/os/linux/linux-stable`, which is included in subset A. Each listed source file was read completely.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ubifs/compress.c -->
# File Research: sources/os/linux/linux-stable/fs/ubifs/compress.c

## Purpose
Centralizes UBIFS compression and decompression handling. It hides compressor selection, fallback-to-uncompressed behavior, folio/buffer variants, and Linux Crypto API async-compression object lifecycle behind UBIFS-facing helpers.

## Main Responsibilities
- Defines UBIFS compressor descriptors for `none`, `lzo`, `zlib`, and `zstd`.
- Maintains the global `ubifs_compressors[]` table indexed by UBIFS compression type.
- Compresses data from either a linear buffer or a folio.
- Decompresses data into either a linear buffer or a folio.
- Initializes and tears down compiled-in crypto `acomp` compressor instances.

## Key Functions
- `ubifs_compress_common()`: shared compression path. It refuses compression for `UBIFS_COMPR_NONE`, too-small inputs, failed compression, or ineffective compression, then copies the input and returns `UBIFS_COMPR_NONE`.
- `ubifs_compress()`: buffer wrapper around `ubifs_compress_common()`.
- `ubifs_compress_folio()`: folio-input wrapper around `ubifs_compress_common()`.
- `ubifs_decompress_common()`: validates compressor type/availability, handles `UBIFS_COMPR_NONE` as a copy, and invokes `crypto_acomp_decompress()` otherwise.
- `ubifs_decompress()`: buffer-output wrapper.
- `ubifs_decompress_folio()`: folio-output wrapper.
- `compr_init()`: allocates a crypto async compression transform when the compressor has a `capi_name`, then registers it in `ubifs_compressors[]`.
- `ubifs_compressors_init()` / `ubifs_compressors_exit()`: module-level compressor lifecycle.

## Important Behavior
- Compression is opportunistic. If compression does not save at least `UBIFS_MIN_COMPRESS_DIFF`, UBIFS stores the node uncompressed.
- Compression failure is non-fatal: data is stored uncompressed.
- Decompression failure is fatal to the caller and logs an error.
- Missing compiled-in compressor support is detected during decompression via absent `capi_name`.
- The code supports both stack `ACOMP_REQUEST_ON_STACK()` requests and cloned async requests when the crypto backend returns `-EAGAIN`.

## Dependencies and Interactions
- Called by `file.c` when reading/writing data nodes.
- Works with encrypted data ordering indirectly: file paths compress before encryption on write, and decrypt before decompressing on read.
- Depends on UBIFS constants and compressor enum definitions from `ubifs.h`.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ubifs/compress.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ubifs/crypto.c -->
# File Research: sources/os/linux/linux-stable/fs/ubifs/crypto.c

## Purpose
Integrates UBIFS with fscrypt and provides block encryption/decryption helpers for UBIFS data nodes.

## Main Responsibilities
- Stores and retrieves fscrypt encryption contexts using UBIFS xattrs.
- Implements fscrypt empty-directory check.
- Encrypts and decrypts UBIFS data-node payloads in place.
- Publishes `ubifs_crypt_operations` for fscrypt.

## Key Functions
- `ubifs_crypt_get_context()`: reads `UBIFS_XATTR_NAME_ENCRYPTION_CONTEXT`.
- `ubifs_crypt_set_context()`: writes the encryption context xattr for a new inode without requiring normal inode locking.
- `ubifs_crypt_empty_dir()`: delegates to `ubifs_check_dir_empty()`.
- `ubifs_encrypt()`: pads compressed data to `UBIFS_CIPHER_BLOCK_SIZE`, records original compressed length in `dn->compr_size`, and encrypts in place.
- `ubifs_decrypt()`: validates `compr_size`, decrypts in place, and restores the compressed length through `out_len`.
- `ubifs_crypt_operations`: provides fscrypt offsets, legacy key prefix, and callbacks.

## Important Behavior
- `dn->compr_size` records pre-padding compressed length so decompression receives the correct size after decryption.
- Encryption length is rounded up to a cipher block boundary.
- Decryption validates that `compr_size` is nonzero, no larger than `UBIFS_BLOCK_SIZE`, and no larger than the encrypted data length.
- Errors are logged through UBIFS diagnostics and returned to callers.

## Dependencies and Interactions
- Used by `file.c` read/write paths around data-node compression.
- Uses xattr helpers from UBIFS xattr code.
- Uses `ubifs_check_dir_empty()` from `dir.c` for fscrypt policy checks.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ubifs/crypto.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ubifs/debug.c -->
# File Research: sources/os/linux/linux-stable/fs/ubifs/debug.c

## Purpose
Implements UBIFS debug-only diagnostics, integrity checkers, fault injection for recovery testing, debugfs controls, and assertion handling.

## Main Responsibilities
- Human-readable formatting for keys, node types, commit states, journal heads, and LEB categories.
- Dump routines for inodes, raw nodes, budgets, lprops, LPT state, LEB contents, znodes, heaps, pnodes, TNC, and on-flash index.
- Consistency checks for space accounting, synced inode size, directory size/link counts, TNC ordering/structure, index size, and full filesystem metadata.
- Power-cut emulation and UBI LEB operation wrappers for recovery testing.
- Per-filesystem and global debugfs knobs.
- Runtime assertion failure policy.

## Key Diagnostic Routines
- `dbg_snprintf_key()`, `dbg_ntype()`, `dbg_cstate()`, `dbg_jhead()`: stringify UBIFS internals.
- `ubifs_dump_inode()`: dumps in-memory inode state and directory entries for directories.
- `ubifs_dump_node()`: safely dumps each UBIFS node type after validating magic/type/length boundaries.
- `ubifs_dump_budg()`: prints budget state, dirty/clean znode counters, journal heads, buds, index-GC list, and available-space predictions.
- `ubifs_dump_lprops()`, `ubifs_dump_lpt_info()`, `ubifs_dump_leb()`: inspect LEB property and flash contents.
- `ubifs_dump_tnc()` and `ubifs_dump_index()`: dump in-memory and on-flash index structures.

## Key Checking Routines
- `dbg_save_space_info()` / `dbg_check_space_info()`: snapshot and compare free-space accounting, with special handling for lazily known freeable LEBs.
- `dbg_check_synced_i_size()`: verifies clean regular inodes have `ui_size == synced_i_size`.
- `dbg_check_dir()`: recomputes directory size and link count from TNC entries.
- `dbg_check_key_order()`: validates binary name order for colliding dent/xent hash keys.
- `dbg_check_znode()` / `dbg_check_tnc()`: validate znode parentage, levels, dirty-state propagation, key ordering, branch consistency, and znode counters.
- `dbg_walk_index()`: loads and walks the full on-flash index in postorder and invokes callbacks.
- `dbg_check_idx_size()`: recomputes serialized index size.
- `dbg_check_filesystem()`: heavyweight full check that walks all leaves, validates nodes, builds an inode RB-tree, and checks link counts, directory sizes, xattr counts/sizes, and data-node bounds.
- `dbg_check_data_nodes_order()` and `dbg_check_nondata_nodes_order()`: verify sorted scan-node lists used by recovery/commit paths.

## Recovery Fault Injection
- `power_cut_emulated()`: probabilistically decides when to emulate a power cut, with different probabilities for superblock, master, log, LPT, orphan, index-head, GC-head, non-bud, and bud LEBs.
- `corrupt_data()`: corrupts a write buffer span with `0xFF` or random bytes.
- `dbg_leb_write()`, `dbg_leb_change()`, `dbg_leb_unmap()`, `dbg_leb_map()`: wrap UBI operations and return `-EROFS` after simulated failure.

## Debugfs Interface
- Per-mount debugfs directory is named `ubi%d_%d`.
- Per-filesystem files include dump triggers and boolean knobs: `chk_general`, `chk_index`, `chk_orphans`, `chk_lprops`, `chk_fs`, `tst_recovery`, and `ro_error`.
- Global debugfs files expose default check/recovery toggles for all mounts.
- Inputs are simple `0`/`1`; output is `0\n` or `1\n`.

## Important Behavior
- Many checkers are gated by `dbg_is_chk_*()` so they are cheap when disabled.
- Some checks intentionally use VFS cached inode state when available, because on-flash inode nodes can lag during recovery.
- On assertion failure, behavior depends on `c->assert_action`: panic, switch UBIFS read-only, or dump stack.
- Dump paths use `dbg_lock` to avoid interleaved diagnostic output.

## Dependencies and Interactions
- Used throughout UBIFS through `ubifs_assert()`, `dbg_*()` macros, debugfs controls, and optional consistency checks.
- Reads TNC, LPT, lprops, journal, inode, and UBI layers.
- Provides the debug wrappers declared in `debug.h`.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ubifs/debug.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ubifs/debug.h -->
# File Research: sources/os/linux/linux-stable/fs/ubifs/debug.h

## Purpose
Declares UBIFS debugging data structures, debug macros, check gates, dump/check APIs, debug UBI wrappers, and debugfs lifecycle functions.

## Main Responsibilities
- Defines callback types for index walking.
- Defines per-filesystem debug state in `struct ubifs_debug_info`.
- Defines global debug defaults in `struct ubifs_global_debug_info`.
- Provides assertion and debug-message macros.
- Provides inline predicates for active debug features.
- Declares dump, checker, fault-injection wrapper, and debugfs functions.

## Key Structures
- `struct ubifs_debug_info`: stores old index root snapshot, power-cut emulation state, LPT checker state, saved budgeting/lprops snapshots, per-mount check toggles, recovery-testing toggle, and per-mount debugfs dentries.
- `struct ubifs_global_debug_info`: stores global defaults for general, index, orphan, lprops, filesystem, and recovery-test checks.

## Key Macros and Helpers
- `ubifs_assert()`: routes failed conditions to `ubifs_assert_failed()`.
- `ubifs_assert_cmt_locked()`: verifies commit semaphore is write-locked.
- `dbg_gen()`, `dbg_jnl()`, `dbg_tnc()`, `dbg_find()`, and related macros: typed `pr_debug()` wrappers.
- `dbg_is_chk_gen()`, `dbg_is_chk_index()`, `dbg_is_chk_orph()`, `dbg_is_chk_lprops()`, `dbg_is_chk_fs()`, `dbg_is_tst_rcvry()`: combine global and per-FS debug flags.
- `dbg_is_power_cut()`: reports whether simulated failure has happened.

## Exported Surface
- Dump routines for nodes, inodes, lprops, LPT, TNC, index, budget, and LEBs.
- Check routines for space accounting, lprops, old index, categories, LPT, inode sizes, directories, TNC, filesystem contents, and scan ordering.
- Debug UBI wrappers: `dbg_leb_write()`, `dbg_leb_change()`, `dbg_leb_unmap()`, `dbg_leb_map()`.
- Debugfs init/exit functions for global and per-filesystem state.

## Dependencies and Interactions
- Included by `ubifs.h` or UBIFS compilation units that need debug support.
- Implemented mainly by `debug.c`, with some subsystem-local checkers implemented elsewhere.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ubifs/debug.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ubifs/dir.c -->
# File Research: sources/os/linux/linux-stable/fs/ubifs/dir.c

## Purpose
Implements UBIFS VFS directory and namespace operations: inode creation, lookup, readdir, link/unlink, mkdir/rmdir, mknod, symlink, rename, tmpfile, getattr, and directory file operations.

## Main Responsibilities
- Allocate and initialize new UBIFS inodes.
- Handle fscrypt-aware filename preparation and lookup.
- Maintain directory sizes and link counts.
- Budget space before journal mutations.
- Journal namespace changes atomically.
- Preserve recovery invariants around newly created inodes and renames.
- Provide directory inode/file operation tables.

## Key Creation and Lookup Paths
- `inherit_flags()`: copies compression/sync/dirsync policy flags from parent directories.
- `ubifs_new_inode()`: allocates a VFS inode, assigns UBIFS operations, assigns inode number and creation sequence number, applies fscrypt setup, initializes compression type, and for non-xattr inodes starts with zero nlink plus orphan registration.
- `ubifs_lookup()`: prepares encrypted filename lookup, searches TNC by name/hash, validates found name in debug mode, instantiates target inode, and checks encryption-context compatibility.
- `ubifs_prepare_create()`: rejects nokey encrypted dentries and prepares a disk filename.

## Directory Iteration
- `ubifs_readdir()`: maps UBIFS directory keys to VFS directory offsets using hash values, emits `.` and `..`, handles encrypted filename presentation, stores the current dent node in `file->private_data`, and uses a cookie to detect seek invalidation.
- `ubifs_dir_open()`, `ubifs_dir_release()`, `ubifs_dir_llseek()`: manage saved readdir state and cookie-based seeking.

## Mutation Operations
- `ubifs_create()`: budgets new inode, new dentry, and parent inode update; initializes security; sets nlink; updates parent size/time; journals update.
- `ubifs_tmpfile()`: creates a tmpfile with separate dirty-inode budget and journals the temporary dentry operation.
- `ubifs_link()`: checks fscrypt link rules, budgets new dentry and two dirty inodes, increments target nlink, updates parent size/time, and journals update.
- `ubifs_unlink()`: purges xattrs, allows deletion even when budgeting returns `-ENOSPC`, decrements nlink, updates parent, journals deletion, and clears no-space flags when deletion used reserve behavior.
- `ubifs_check_dir_empty()`: uses TNC next-entry lookup to test whether a directory has entries.
- `ubifs_rmdir()`: checks empty directory, purges xattrs, tolerates `-ENOSPC` budget failure like unlink, clears child nlink, drops parent nlink, and journals deletion.
- `ubifs_mkdir()`: creates a directory, adjusts child and parent link counts, updates parent size/time, and journals creation.
- `ubifs_mknod()`: handles special inode device encoding and journals creation.
- `ubifs_symlink()`: prepares fscrypt symlink data, stores encrypted or plain link data in `ui->data`, updates parent, and journals creation.

## Rename Handling
- `do_rename()`: handles normal rename and `RENAME_WHITEOUT`, including budgeting for dentry changes, target inode dirtiness, optional whiteout inode, parent link-count changes for directories, unlink overwrite behavior, journal rename, and dirtying the moved inode for ctime.
- `create_whiteout()`: creates an in-memory whiteout inode to be persisted atomically by rename journaling.
- `ubifs_xrename()`: implements `RENAME_EXCHANGE`, including parent link-count adjustment when exchanged entries have different directory-ness.
- `ubifs_rename()`: validates supported flags, runs fscrypt rename preparation, and dispatches to exchange or normal rename.

## Other Operations
- `ubifs_getattr()`: reports UBIFS file attributes, actual `ui_size`, UBIFS block size, and a UBIFS/JFFS2-style block count policy: regular files get rounded data+xattr blocks; non-regular files report zero blocks.
- Operation tables: `ubifs_dir_inode_operations` and `ubifs_dir_operations`.

## Important Behavior
- Most operations write changed inodes immediately through journal updates rather than relying on later dirty inode writeback, simplifying recovery.
- Non-xattr new inodes are initially orphaned with zero nlink to survive power cuts between inode/xattr initialization and dentry journaling.
- Delete operations intentionally proceed under `-ENOSPC` using reserved space.
- VFS inode locks define ordering; UBIFS adds `ui_mutex` wrappers for two- and four-inode operations.
- Readdir offsets are hash-based and not fully NFS-compatible due to possible key collisions.

## Dependencies and Interactions
- Uses `crypto.c` through fscrypt operations and `ubifs_check_dir_empty()`.
- Uses journal functions such as `ubifs_jnl_update()`, `ubifs_jnl_rename()`, and `ubifs_jnl_xrename()`.
- Uses TNC lookup/iteration functions for lookup and directory scanning.
- Uses budgeting APIs before flash-affecting namespace mutations.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ubifs/dir.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ubifs/file.c -->
# File Research: sources/os/linux/linux-stable/fs/ubifs/file.c

## Purpose
Implements UBIFS regular-file, symlink, address-space, mmap, writeback, truncate, setattr, fsync, and file operation behavior.

## Main Responsibilities
- Read UBIFS data nodes into folios.
- Decrypt and decompress data-node payloads.
- Budget page and inode changes before dirtying memory.
- Write dirty folios through UBIFS journal.
- Preserve recovery invariants around inode size and writeback ordering.
- Implement truncation, setattr, atime/mtime/ctime updates, mmap page dirtying, fsync, and symlink resolution.
- Provide file, inode, symlink, VM, and address-space operation tables.

## Read Path
- `read_block()`: looks up a data node by inode/block key, treats `-ENOENT` as a hole, validates stored size, decrypts if needed, decompresses into a folio, and zero-fills unused block tail.
- `do_readpage()`: reads all UBIFS blocks belonging to a folio, handles holes and beyond-EOF regions, marks hole pages with `PG_checked`, and marks successful folios uptodate.
- `populate_page()`: bulk-read equivalent that copies multiple pre-read data nodes into a folio.
- `ubifs_bulk_read()` / `ubifs_do_bulk_read()`: detect sequential reads, collect adjacent data-node keys, bulk-read consecutive nodes in one LEB, and populate multiple folios.
- `ubifs_read_folio()`: uses bulk-read when possible, otherwise `do_readpage()`.

## Write-Begin and Dirtying
- `release_new_page_budget()` / `release_existing_page_budget()`: release page budgets for new page growth or existing page modification.
- `write_begin_slow()`: budgets before locking a folio when writeback may be forced, then adjusts budget after reading/identifying actual page state.
- `allocate_budget()`: fast-path budgeting based on whether the folio is already dirty, a hole, existing media data, and whether write appends to inode size.
- `ubifs_write_begin()`: optimized write-begin path. It may skip reading full overwritten folios and mark them checked, then falls back to slow path on `-ENOSPC`.
- `cancel_budget()`: releases budget on partial-copy retry paths.
- `ubifs_write_end()`: marks folio dirty with private budget marker, updates inode size for appends, marks inode datasync dirty, and unlocks folio.

## Writeback
- `do_writepage()`: writes one folio as one or more UBIFS data nodes through `ubifs_jnl_write_data()`, releases page budget, clears private/checked state, and handles errors by setting mapping error and read-only mode.
- `ubifs_writepage()`: enforces the UBIFS synced-size invariant before writing pages. If a page extends beyond `synced_i_size`, it first writes the inode so recovery will not see committed data nodes beyond on-flash inode size.
- `ubifs_writepages()`: iterates writeback folios through `writeback_iter()`.

## Truncation and Setattr
- `do_attr_changes()`: applies UID/GID/time/mode changes with setgid stripping rules.
- `do_truncation()`: handles shrinking truncate, budgets inode/truncation node/last block rewrite, calls `truncate_setsize()`, writes dirty partial last folio if needed, updates `ui_size`, and journals truncate.
- `do_setattr()`: handles non-shrinking setattr and growing truncate by budgeting dirty inode, applying attributes, marking inode dirty, and synchronously writing when needed.
- `ubifs_setattr()`: VFS entry point with permission checks, synced-size debug check, fscrypt setattr prep, and dispatch to truncation or generic setattr path.

## Fsync and Time Updates
- `ubifs_fsync()`: waits dirty file range, writes inode when required, and flushes UBIFS write buffers containing nodes for that inode.
- `ubifs_update_time()`: UBIFS-specific atime update path, gated by `CONFIG_UBIFS_ATIME_SUPPORT`.
- `update_mctime()`: budgets and marks inode dirty when write should update mtime/ctime.
- `ubifs_write_iter()`: updates mtime/ctime before generic write.

## MM and Folio Lifecycle
- `ubifs_invalidate_folio()`: releases full-folio budget when a dirty private folio is invalidated.
- `ubifs_dirty_folio()`: asserts that generic dirtying without UBIFS budgeting should not happen.
- `ubifs_release_folio()`: releases budget for private non-writeback folios.
- `ubifs_vm_page_mkwrite()`: budgets mmap writes before locking folio, marks folio dirty/private, updates time, and returns locked folio for write fault handling.
- `ubifs_file_mmap_prepare()`: installs UBIFS VM ops after generic mmap preparation.

## Symlink and Operation Tables
- `ubifs_get_link()`: returns plain symlink data or asks fscrypt to decrypt encrypted symlinks.
- `ubifs_symlink_getattr()`: combines UBIFS getattr with fscrypt symlink size reporting.
- Defines `ubifs_file_address_operations`, `ubifs_file_inode_operations`, `ubifs_symlink_inode_operations`, and `ubifs_file_operations`.

## Important Behavior
- `PG_private` marks folios with UBIFS-reserved dirty-page budget.
- `PG_checked` distinguishes pages/folios treated as holes or full overwrites requiring new-page budget.
- Budgeting is deliberately done before operations that can dirty pages or inodes; slow paths avoid deadlock by budgeting before folio locking.
- The writeback path protects recovery by ensuring inode size reaches flash before committed data pages beyond the old size.
- UBIFS disables normal VFS cmtime updates through `S_NOCMTIME`; it controls timestamp dirtying explicitly.

## Dependencies and Interactions
- Uses compression helpers from `compress.c`.
- Uses encryption helpers from `crypto.c`.
- Uses journal functions for data nodes and truncate nodes.
- Uses budgeting, TNC lookup, write-buffer flush, and debug checks from the wider UBIFS subsystem.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ubifs/file.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ubifs/find.c -->
# File Research: sources/os/linux/linux-stable/fs/ubifs/find.c

## Purpose
Implements UBIFS LEB selection logic for garbage collection, journal/data allocation, index allocation, and dirty index reuse. It primarily searches LEB property categories, heaps, lists, and finally scans the LPT.

## Main Responsibilities
- Decide which LEB properties are worth caching in memory.
- Find dirty LEBs for garbage collection.
- Find free data LEBs for journal/data writes.
- Find empty/freeable LEBs for index writes.
- Save and consume dirty-index LEB candidates for in-the-gaps commit.
- Maintain `LPROPS_TAKEN` and `LPROPS_INDEX` state while selecting LEBs.

## Shared Concepts
- `struct scan_data`: carries minimum space, whether empty/freeable LEBs may be selected, selected LEB number, and whether index LEBs are excluded.
- `valuable()`: decides whether scanned lprops should be pulled into memory based on category, heap capacity, dirty/free usefulness, empty/freeable tracking, and index state.
- Search order generally favors in-memory category structures, then falls back to LPT scanning when pnodes are not all loaded.

## Dirty LEB Selection
- `scan_for_dirty_cb()`: scan callback for GC candidates. It excludes taken LEBs, optionally excludes index LEBs, respects minimum space, and requires enough dirty space unless selecting a fully free/freeable LEB is allowed.
- `scan_for_dirty()`: checks free heap, uncategorized list, and LPT scan for dirty/freeable candidates.
- `ubifs_find_dirty_leb()`: public GC selection API. It may pick empty/freeable LEBs depending on caller mode, protects reserved index space, considers dirty data and dirty index heaps, scans if needed, marks the selected LEB taken, and returns a copied lprops snapshot.

## Free Data LEB Selection
- `scan_for_free_cb()`: scan callback for data-space allocation. It excludes taken/index LEBs, too-small free space, optionally empty LEBs, and LEBs that are fully free+dirty but not safe for data allocation due to possible wbuf-obsoleted data.
- `do_find_free_space()`: tries fast free/empty lookup, dirty heap, uncategorized list, then LPT scan.
- `ubifs_find_free_space()`: public data allocation API. It accounts for reserved index LEBs, may temporarily increment `taken_empty_lebs`, marks the selected LEB taken, computes write offset from remaining free space, and unmaps empty/freeable LEBs before use.

## Index LEB Selection
- `scan_for_idx_cb()`: finds non-index, untaken LEBs that can be made empty (`free + dirty == leb_size`).
- `scan_for_leb_for_idx()`: scans LPT for an index-suitable LEB.
- `ubifs_find_free_leb_for_idx()`: selects an empty/freeable LEB for index commit, marks it taken and index, sets free/dirty to an empty state, and unmaps it. On unmap failure it rolls back lprops flags.

## Dirty Index Reuse
- `cmp_dirty_idx()`: sorts dirty index candidates by free+dirty amount.
- `ubifs_save_dirty_idx_lnums()`: snapshots dirty-index heap at commit time, sorts by dirty/free amount, and stores LEB numbers for later in-the-gaps allocation.
- `scan_dirty_idx_cb()`: finds untaken index LEBs with enough free+dirty space for an index node.
- `find_dirty_idx_leb()`: searches in-memory structures and then scans the whole LPT for a dirty index LEB.
- `get_idx_gc_leb()`: obtains an index LEB from trivial index GC and marks it as index.
- `find_dirtiest_idx_leb()`: consumes the saved dirty-index array from dirtiest to least dirty, skipping stale/taken/non-index entries.
- `ubifs_find_dirty_idx_leb()`: tries saved dirty-index candidates, then full LPT dirty-index scan, then trivial index GC.

## Important Behavior
- Selection is tightly coupled to budgeting: data allocation avoids consuming empty LEBs needed for reserved index growth.
- `LPROPS_TAKEN` prevents concurrent reuse of selected LEBs.
- Empty/freeable LEBs are unmapped before reuse to guarantee clean flash state after unclean unmounts.
- Index allocation only uses empty/freeable LEBs, because commit sizing assumes empty LEBs and free tails in index LEBs may contain stale in-the-gaps data.
- LPT scans opportunistically add “valuable” pnodes/lprops to memory to improve future searches.

## Dependencies and Interactions
- Uses lprops locking via `ubifs_get_lprops()` / `ubifs_release_lprops()`.
- Uses fast category helpers such as `ubifs_fast_find_empty()`, `ubifs_fast_find_freeable()`, and `ubifs_fast_find_free()`.
- Updates lprops through `ubifs_change_lp()` and `ubifs_change_one_lp()`.
- Calls `ubifs_leb_unmap()` before reusing empty/freeable LEBs.
- Feeds garbage collection, journal space allocation, and TNC commit index allocation.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ubifs/find.c -->