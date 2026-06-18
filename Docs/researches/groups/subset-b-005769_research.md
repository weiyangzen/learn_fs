# subset-b-005769 UBIFS Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ubifs/compress.c -->
# sources/distributed-fs/ceph-client/fs/ubifs/compress.c

## Purpose
`compress.c` is UBIFS' central compression/decompression adapter. It hides the kernel crypto asynchronous compression API behind UBIFS-specific helpers, chooses the compiled-in compressor implementation, falls back to uncompressed storage when compression is not useful or unavailable, and initializes/free compressor transforms at module lifetime boundaries.

## Important APIs, Types, and Functions
- `union ubifs_in_ptr` lets the shared compression helper accept either a linear buffer or a `struct folio`.
- `struct ubifs_compressor *ubifs_compressors[UBIFS_COMPR_TYPES_CNT]` is the global compressor dispatch table indexed by on-flash compression type.
- Static compressor descriptors exist for `none`, `lzo`, `zlib`, and `zstd`; the non-`none` descriptors only carry `capi_name` when the corresponding `CONFIG_UBIFS_FS_*` option is enabled.
- `ubifs_compress()` and `ubifs_compress_folio()` wrap `ubifs_compress_common()` for linear buffers and folio-backed input.
- `ubifs_decompress()` and `ubifs_decompress_folio()` wrap `ubifs_decompress_common()` for linear and folio-backed output.
- `ubifs_compressors_init()` calls `compr_init()` for LZO, ZSTD, and ZLIB, then installs the fake `none` compressor; `ubifs_compressors_exit()` frees any allocated crypto transforms.

## Control Flow
Compression first rejects `UBIFS_COMPR_NONE` and too-small inputs. For real compressors it caps the destination size to `in_len - UBIFS_MIN_COMPRESS_DIFF`, submits an `acomp` request using either `acomp_request_set_src_folio()` or `acomp_request_set_src_dma()`, and handles `-EAGAIN` by cloning the request, enabling backlog, and waiting synchronously through `crypto_wait_req()`. If compression errors or does not beat the minimum-difference threshold, the input is copied verbatim and `*compr_type` is changed to `UBIFS_COMPR_NONE`.

Decompression validates the numeric compressor type, rejects unavailable compiled-out compressors by checking `capi_name`, directly copies `UBIFS_COMPR_NONE` data, and otherwise submits an `acomp` decompression request. It supports DMA-buffer input and either folio or buffer output. Decompression errors are logged with the compressor name and propagated.

Initialization is ordered so partial failures unwind previously initialized compressors. A compressor with no `capi_name` still gets installed in the table, which allows attempts to decompress that type to return a controlled `-EINVAL` instead of dereferencing a missing transform.

## State and Persistence Behavior
The file does not persist data directly, but it controls on-flash data-node encoding through `compr_type`, compressed length, and fallback-to-none behavior used by journal writes. `dn->compr_type` and node data length written elsewhere depend on these helpers. The global compressor table and each descriptor's `cc` transform are process/module state shared by all UBIFS mounts.

## Dependencies and Integration Points
The implementation depends on `crypto/acompress.h`, crypto wait helpers, `struct folio` highmem helpers, and UBIFS constants from `ubifs.h`. It is consumed by file read/write and journal paths, notably data-node creation and `file.c` reads through `ubifs_decompress_folio()`. Encryption is layered separately: `file.c` decrypts before decompression and `crypto.c` encrypts after compression.

## Risks and Edge Cases
- The output buffer length must be initialized correctly by callers; `ubifs_compress_common()` assumes `*out_len` is the allocated destination size.
- Compiled-out compressor types are represented but not usable; reading media containing such a type fails with `-EINVAL`.
- A compression error silently stores uncompressed data, which is intentional for writes but means callers must trust the returned `compr_type`.
- Folio offsets and lengths must describe a valid source/destination range; this file relies on the caller and folio helpers for bounds correctness.
- Async crypto `-EAGAIN` handling allocates a clone with `GFP_NOFS | __GFP_NOWARN`; allocation failure paths depend on the crypto API's returned error behavior.

## Test Signals
Useful test signals include round-trip data-node read/write with all enabled compressors, fallback behavior for small or incompressible buffers, decompression failure when a compressor is compiled out, folio-offset compression/decompression cases, and fault injection around async crypto backlog/clone paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ubifs/compress.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ubifs/crypto.c -->
# sources/distributed-fs/ceph-client/fs/ubifs/crypto.c

## Purpose
`crypto.c` connects UBIFS to fscrypt. It stores encryption contexts as UBIFS xattrs, enforces fscrypt directory-empty checks, and encrypts/decrypts UBIFS data-node payloads in place after compression and before decompression.

## Important APIs, Types, and Functions
- `ubifs_crypt_get_context()` and `ubifs_crypt_set_context()` read/write `UBIFS_XATTR_NAME_ENCRYPTION_CONTEXT` through UBIFS xattr helpers.
- `ubifs_crypt_empty_dir()` delegates to `ubifs_check_dir_empty()` for fscrypt policy changes.
- `ubifs_encrypt()` records the pre-encryption compressed length in `dn->compr_size`, pads to `UBIFS_CIPHER_BLOCK_SIZE`, and calls `fscrypt_encrypt_block_inplace()`.
- `ubifs_decrypt()` validates `dn->compr_size`, decrypts a full padded extent using `fscrypt_decrypt_block_inplace()`, then returns the original compressed length.
- `ubifs_crypt_operations` is the fscrypt operations table exported to the superblock/inode setup code.

## Control Flow
On encryption, the caller supplies a data node whose `data` field already contains compressed or raw data. The function rounds the data length up to the UBIFS cipher block size, zero-pads any added bytes, stores the unpadded length in little-endian `compr_size`, and asks fscrypt to encrypt the page containing `dn->data` at the logical block number. The returned output length becomes the padded encrypted length that should be journaled.

On decryption, UBIFS reads `compr_size` first, rejects zero, over-block, or larger-than-buffer values, decrypts the padded data in place, and changes `*out_len` back to the original compressed length so the decompressor sees exactly the bytes it expects.

## State and Persistence Behavior
Encryption context is persistent metadata stored as an xattr. `compr_size` is persistent per data node and is critical because encryption padding changes the stored payload length. The code mutates the data node in memory in place; persistence is handled later by journal writes and earlier by TNC reads.

## Dependencies and Integration Points
This file depends on UBIFS xattr operations, directory emptiness checks in `dir.c`, and fscrypt block helpers. It integrates with inode allocation and lookup through fscrypt operations, with `dir.c` for context setup and inherited encryption policy, and with `file.c` read paths that decrypt before decompression.

## Risks and Edge Cases
- `ubifs_decrypt()` trusts the caller's padded `*out_len` to match the encrypted data payload size; it validates only that `compr_size` is sane relative to it.
- The encryption context is set without inode locking for new inodes because the inode is not visible yet; callers must preserve that creation ordering.
- Incorrect `block` numbers would break fscrypt IV derivation and data recovery.
- Padding bytes are zeroed before encryption, which avoids leaking stale memory but requires `*out_len` to reflect allocated data-node capacity.

## Test Signals
Exercise encrypted regular-file writes and reads across partial-block compressed sizes, invalid `compr_size` values, policy setting on non-empty directories, xattr persistence of encryption contexts, and power-cut scenarios around encrypted inode creation before dentry linking.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ubifs/crypto.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ubifs/debug.c -->
# sources/distributed-fs/ceph-client/fs/ubifs/debug.c

## Purpose
`debug.c` implements UBIFS diagnostic dumping, consistency checking, recovery fault injection, debugfs controls, and assertion handling. Most functionality is gated by debug configuration and runtime flags, but the file is central to validating TNC/index structure, lprops/accounting, inode reference counts, and recovery behavior under simulated power cuts.

## Important APIs, Types, and Functions
- Formatting helpers: `dbg_snprintf_key()`, `dbg_ntype()`, `dbg_cstate()`, and `dbg_jhead()`.
- Dumpers: `ubifs_dump_inode()`, `ubifs_dump_node()`, `ubifs_dump_budg()`, `ubifs_dump_lprops()`, `ubifs_dump_lpt_info()`, `ubifs_dump_leb()`, `ubifs_dump_znode()`, `ubifs_dump_tnc()`, and `ubifs_dump_index()`.
- Space and inode checks: `dbg_save_space_info()`, `dbg_check_space_info()`, `dbg_check_synced_i_size()`, and `dbg_check_dir()`.
- TNC/index checks: `dbg_check_key_order()`, `dbg_check_znode()`, `dbg_check_tnc()`, `dbg_walk_index()`, and `dbg_check_idx_size()`.
- Filesystem scan structures: `struct fsck_inode` and `struct fsck_data` support `dbg_check_filesystem()`.
- Node order checks: `dbg_check_data_nodes_order()` and `dbg_check_nondata_nodes_order()`.
- Recovery injection wrappers: `dbg_leb_write()`, `dbg_leb_change()`, `dbg_leb_unmap()`, and `dbg_leb_map()`.
- debugfs entry points: `dbg_debugfs_init_fs()`, `dbg_debugfs_exit_fs()`, `dbg_debugfs_init()`, and `dbg_debugfs_exit()`.
- `ubifs_assert_failed()`, `ubifs_debugging_init()`, and `ubifs_debugging_exit()` handle assertion policy and per-mount debug allocation.

## Control Flow
Dump functions print structured views of in-memory and on-flash objects. `ubifs_dump_node()` first validates UBIFS magic/type and clamps printable length against node type ranges before printing type-specific fields. `ubifs_dump_leb()` scans a whole LEB into a temporary buffer and dumps each scanned node. TNC dumpers traverse either the in-memory TNC or the on-flash index via `dbg_walk_index()`.

Consistency checks are opt-in through global or per-filesystem debug flags. Space checking snapshots lprops/budgeting state, normalizes `freeable_cnt`, and later compares calculated free space with the saved value. Directory checks rebuild directory size and nlink from dent nodes. TNC checks traverse znodes, validate parent/child relationships, dirty propagation, key ordering, collision ordering, and zbranch address/length invariants. Filesystem checks walk all index leaves, validate leaf nodes, build an RB tree of inode summaries, account dent/xent/data references, then compare calculated counts and sizes against inode metadata.

Recovery testing wraps UBI LEB operations. `power_cut_emulated()` randomly chooses delay mode and failure probability based on the target LEB class, sets `pc_happened`, may corrupt write buffers through `corrupt_data()`, and then returns `-EROFS` to simulate a sudden failure. Once a simulated power cut happened, later wrapped operations fail immediately.

debugfs setup creates both global UBIFS knobs and per-mount knobs. Writes to dump files trigger immediate dumps; writes of `0` or `1` toggle check/recovery/RO-error flags. Assertion failure honors `c->assert_action`: panic, switch to read-only error mode, or report with stack dump.

## State and Persistence Behavior
Debug state is held in `struct ubifs_debug_info` per mount and `ubifs_dbg` globally. It includes saved accounting snapshots, power-cut counters, flags controlling optional checks, and debugfs dentries. The debug code normally does not create persistent UBIFS metadata, except that fault-injection wrappers can intentionally corrupt or partially apply UBI writes to test recovery. The filesystem checker reads persistent index leaves and compares them with live VFS cache state when cached inodes exist.

## Dependencies and Integration Points
The file depends on debugfs, UBI LEB operations, random number generation, TNC/index walking/loading, lprops/statistics helpers, scan helpers, journal/accounting structures, and VFS inode lookup. It is referenced broadly through macros and prototypes in `debug.h`; many production paths call check helpers conditionally to validate assumptions during mount, commit, GC, replay, directory operations, writeback, and lprops updates.

## Risks and Edge Cases
- Many checks are heavy and read the whole index; enabling them on large filesystems can materially affect latency.
- `dbg_walk_index()` loads znodes into the TNC and explicitly notes that it does not perfectly mimic non-debug behavior.
- Fault injection deliberately mutates write buffers despite `const void *` by casting away const in `corrupt_data()`, which is acceptable for testing but dangerous if enabled unintentionally.
- debugfs read/write dispatch compares dentries directly; stale or missing debugfs dentries can produce `-EINVAL`.
- Filesystem checking may use cached VFS inode state instead of on-flash inode state, which is intentional after replay but makes results dependent on cache residency.

## Test Signals
Key signals include enabling each debugfs knob and verifying checks fire, running `dbg_check_tnc()` across clean/dirty/colliding-key indexes, running `dbg_check_filesystem()` after directory/xattr/data mutations, validating dump functions on truncated/corrupt nodes, exercising power-cut recovery with `tst_recovery`, and verifying assertion actions produce panic/RO/report behavior as configured.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ubifs/debug.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ubifs/debug.h -->
# sources/distributed-fs/ceph-client/fs/ubifs/debug.h

## Purpose
`debug.h` declares UBIFS debug state, logging/check macros, dump/check APIs, debugfs lifecycle hooks, and recovery-testing LEB wrappers. It is the interface between normal UBIFS code and the implementations in `debug.c` plus subsystem-local debug checkers.

## Important APIs, Types, and Functions
- Callback types `dbg_leaf_callback` and `dbg_znode_callback` are used by `dbg_walk_index()`.
- `struct ubifs_debug_info` stores per-mount old-index snapshots, power-cut injection state, lprops/budget snapshots, check flags, recovery-test flags, and per-mount debugfs dentries.
- `struct ubifs_global_debug_info` stores global default debug flags.
- `ubifs_assert()` and `ubifs_assert_cmt_locked()` provide UBIFS-specific assertion behavior.
- `dbg_gen()`, `dbg_jnl()`, `dbg_tnc()`, `dbg_find()`, and related macros produce typed dynamic debug messages.
- Inline flag readers such as `dbg_is_chk_gen()`, `dbg_is_chk_index()`, `dbg_is_chk_fs()`, and `dbg_is_tst_rcvry()` combine global and per-mount settings.
- The header declares all debug dump, consistency check, LEB wrapper, and debugfs lifecycle functions.

## Control Flow
Callers use cheap inline flag checks before invoking expensive debug checks. `ubifs_assert()` routes failed expressions to `ubifs_assert_failed()`, which applies runtime assertion policy. Debug message macros format messages with UBIFS category tags and current pid; key-aware variants use `dbg_snprintf_key()` into a stack buffer.

## State and Persistence Behavior
The header defines the shape of per-mount debug state allocated during mount debugging initialization and freed at unmount. Saved old index and lprops/budget values are transient validation snapshots. Power-cut fields track simulated failure progress across wrapped UBI operations during a mounted test run. No persistent media layout is defined here, but these declarations control wrappers that can affect media writes under recovery testing.

## Dependencies and Integration Points
It depends on UBIFS core types such as `struct ubifs_info`, `struct ubifs_zbranch`, `struct ubifs_znode`, lprops/budget structures, and kernel `debugfs` dentries. It is included by UBIFS source files to access assertions, debug logging, optional checks, debugfs initialization, and I/O wrappers.

## Risks and Edge Cases
- Debug flags are bitfields without locking in the inline readers; they are runtime diagnostics and tolerate simple races.
- Assertion behavior depends on `c->assert_action`; callers should not assume a failed assertion always terminates execution.
- Key debug printing macros require a visible `c` variable in scope for `dbg_snprintf_key()`.
- Per-mount debugfs directory name length is bounded by `UBIFS_DFS_DIR_LEN`; unexpected UBI numbering beyond the documented pattern causes debugfs init to skip the instance directory.

## Test Signals
Compile-time and runtime signals include building with UBIFS debug enabled, toggling global and per-mount check flags through debugfs, verifying `ubifs_assert()` policy handling, confirming debug message categories appear under dynamic debug, and checking that recovery wrappers replace raw UBI operations when recovery testing is active.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ubifs/debug.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ubifs/dir.c -->
# sources/distributed-fs/ceph-client/fs/ubifs/dir.c

## Purpose
`dir.c` implements UBIFS VFS directory and namespace operations: inode creation, lookup, readdir, link/unlink, mkdir/rmdir, mknod, symlink, tmpfile, rename/exchange/whiteout, directory open/seek/release, and stat attribute reporting. It also enforces UBIFS budgeting and journaling rules for metadata changes.

## Important APIs, Types, and Functions
- `inherit_flags()` and `ubifs_new_inode()` initialize UBIFS inode state, compression defaults, fscrypt context, orphan protection, and VFS operations.
- Lookup/create helpers: `dbg_check_name()`, `ubifs_lookup()`, `ubifs_prepare_create()`, and `ubifs_create()`.
- Directory iteration state: `struct ubifs_dir_data`, `ubifs_dir_open()`, `ubifs_dir_llseek()`, `ubifs_readdir()`, and `ubifs_dir_release()`.
- Namespace mutators: `ubifs_link()`, `ubifs_unlink()`, `ubifs_check_dir_empty()`, `ubifs_rmdir()`, `ubifs_mkdir()`, `ubifs_mknod()`, `ubifs_symlink()`, `ubifs_tmpfile()`, `do_rename()`, `ubifs_xrename()`, and `ubifs_rename()`.
- Exported operation tables: `ubifs_dir_inode_operations` and `ubifs_dir_operations`.
- `ubifs_getattr()` maps UBIFS inode flags and size/block accounting into `kstat`.

## Control Flow
Creation paths first budget space, prepare fscrypt names, allocate a new inode, initialize security/xattrs, update link counts and parent directory size under UBIFS inode mutexes, then journal the combined directory/inode update through `ubifs_jnl_update()`. New non-xattr inodes start with zero nlink and an orphan record so a power cut before dentry journaling does not leave an unreachable live inode.

Lookup prepares fscrypt lookup state, handles no-key encrypted names via hash lookup, reads dent nodes from the TNC, validates debug names when enabled, instantiates the target inode, and verifies encrypted child context compatibility for directories and symlinks.

`ubifs_readdir()` maps directory offsets to UBIFS name hashes. Because key hash collisions prevent full Unix seekdir/telldir semantics, it stores the last full dent node in `file->private_data` and uses a cookie to detect seeks. It emits dots, then iterates with `ubifs_tnc_next_ent()`, decrypting names for encrypted directories.

Deletion paths attempt to budget but continue on `-ENOSPC` for unlink/rmdir because UBIFS reserves deletion space. They purge xattrs, update nlink and directory size, journal deletion, and clear no-space flags when deletion succeeded without a normal budget.

Rename is the most complex path. It budgets dent deletion/creation, dirty inode updates, optional whiteout creation, and dirty old-inode writeback separately. It locks involved UBIFS inodes through `lock_4_inodes()`, adjusts directory sizes and link counts, journals the atomic rename or exchange, then marks the moved inode dirty for ctime persistence.

## State and Persistence Behavior
All namespace mutations journal affected inodes and dent nodes immediately rather than relying on delayed dirty inode writeback, simplifying recovery. Directory `i_size`/`ui_size`, link counts, orphan list state, fscrypt contexts, xattrs, special-device encoded data, symlink inline data, and dent nodes are persistent effects. Rename may leave the moved inode dirty for later ctime writeback, but the namespace operation itself is journaled atomically.

## Dependencies and Integration Points
This file integrates with VFS inode/file operation tables, TNC dent lookup/iteration, journal update/rename/xrename functions, budgeting, orphan handling, fscrypt, security initialization, xattr purge/listing, ioctl/fileattr helpers, and file operations from `file.c`. `crypto.c` depends on `ubifs_check_dir_empty()` for fscrypt policy behavior.

## Risks and Edge Cases
- Directory offsets are hash based, so NFS-style stable arbitrary seekdir/telldir is explicitly unsupported.
- Error paths must reverse size and nlink updates exactly; rename/whiteout paths have many separate budget and inode-state rollback cases.
- New inode orphan handling is essential for power-cut safety; creation callers must set nlink and journal linking in the expected sequence.
- Encrypted no-key lookups use hashes and minor hashes, so name preparation and validation are critical.
- Unlink/rmdir continuing after `-ENOSPC` depends on reserved deletion space and correct clearing of no-space flags.

## Test Signals
High-value tests include encrypted and unencrypted lookup/readdir, hash-collision directory entries, create/unlink/rmdir under low-space conditions, power cuts between inode creation and dentry journaling, rename over files/directories, `RENAME_EXCHANGE`, `RENAME_WHITEOUT`, tmpfile creation, symlink encryption, and stat attributes for UBIFS flags.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ubifs/dir.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ubifs/file.c -->
# sources/distributed-fs/ceph-client/fs/ubifs/file.c

## Purpose
`file.c` implements UBIFS regular-file, symlink, device-node inode operations and address-space operations. It handles data-node reads, decompression/decryption, page-cache budgeting, writes, writeback, truncation, fsync, mmap write faults, atime/mtime/ctime updates, and exported VFS operation tables.

## Important APIs, Types, and Functions
- Read path: `read_block()`, `do_readpage()`, `populate_page()`, `ubifs_do_bulk_read()`, `ubifs_bulk_read()`, and `ubifs_read_folio()`.
- Write budgeting: `release_new_page_budget()`, `release_existing_page_budget()`, `write_begin_slow()`, `allocate_budget()`, `ubifs_write_begin()`, `cancel_budget()`, and `ubifs_write_end()`.
- Writeback: `do_writepage()`, `ubifs_writepage()`, and `ubifs_writepages()`.
- Attribute and truncation paths: `do_attr_changes()`, `do_truncation()`, `do_setattr()`, and `ubifs_setattr()`.
- Synchronization/time/mmap: `ubifs_fsync()`, `ubifs_update_time()`, `update_mctime()`, `ubifs_write_iter()`, `ubifs_vm_page_mkwrite()`, and `ubifs_file_mmap_prepare()`.
- Folio lifecycle: `ubifs_invalidate_folio()`, `ubifs_dirty_folio()`, and `ubifs_release_folio()`.
- Symlink helpers: `ubifs_get_link()` and `ubifs_symlink_getattr()`.
- Exported tables: `ubifs_file_address_operations`, `ubifs_file_inode_operations`, `ubifs_symlink_inode_operations`, and `ubifs_file_operations`.

## Control Flow
Reads derive data keys from inode number and block number, look up data nodes in the TNC, treat `-ENOENT` as holes, decrypt encrypted data nodes, decompress into the destination folio, and zero any short-block tail. `do_readpage()` walks all UBIFS blocks covered by the folio. Sequential reads may switch on bulk-read after repeated adjacent page reads; bulk-read gathers consecutive zbranches, reads them in one UBI operation, and populates multiple folios.

Writes use UBIFS-specific folio flags. `PG_private` means a dirty folio already has budget. `PG_checked` means the folio represents a hole or skipped read and needs full new-page budgeting. The fast `ubifs_write_begin()` path locks the folio first and tries a no-writeback budget. On `-ENOSPC`, it unlocks and falls back to `write_begin_slow()`, which budgets before taking the folio lock to avoid writeback deadlock. `ubifs_write_end()` marks the folio dirty, attaches private state, increments dirty page count, and updates inode size under `ui_mutex` for appends.

Writeback writes only data within the current inode size and ensures the synchronized inode size reaches pages being flushed. If a folio extends beyond `i_size`, the tail is zeroed before writing. `do_writepage()` writes one UBIFS data node per block with `ubifs_jnl_write_data()`, releases page budget, detaches private state, clears `PG_checked`, and ends writeback.

Truncation to smaller size budgets a truncation node and optionally the final partial block, updates page cache size, writes a dirty partial folio if needed, updates `ui_size` and timestamps, and journals the truncate. Non-shrinking setattr marks the inode dirty and may synchronously write it for `IS_SYNC`.

`fsync()` waits for dirty pages, writes the inode when required by datasync rules, and flushes UBIFS write buffers for that inode. `page_mkwrite` pre-budgets for mmap writes before locking the folio, then amends budget after inspecting the actual folio state.

## State and Persistence Behavior
Persistent data is represented as UBIFS data nodes written by the journal, with compression and encryption handled by adjacent modules. `ui_size`, `synced_i_size`, inode timestamps, inline symlink data, dirty folio private flags, `dirty_pg_cnt`, and budget reservations coordinate between VFS page cache state and on-flash journal/index state. The synchronized inode size rule is a recovery invariant: data beyond the on-flash inode size must remain replay-recoverable.

## Dependencies and Integration Points
This file depends on TNC lookup and bulk-read APIs, journal data/truncate writes, budgeting, compression, encryption, fscrypt file/symlink helpers, VFS writeback and folio APIs, mmap fault handling, ioctl/fileattr declarations, and debug checks. Operation tables are installed for regular files, symlinks, and special files by `dir.c` inode creation.

## Risks and Edge Cases
- Budget release must match how a folio was classified; mismatched `PG_private`/`PG_checked` handling risks budget leaks or accounting underflow.
- Fast-path write budgeting cannot trigger writeback while holding a locked folio; slow-path fallback is required for low-space safety.
- Writeback races with truncation are managed through page locks and `ui_size`/`synced_i_size`; changes here are high risk.
- Bulk-read is opportunistic and must degrade safely on allocation or TNC errors.
- mmap writes can dirty pages outside normal write_iter flow, so `ubifs_vm_page_mkwrite()` must preserve the same budgeting and timestamp invariants.

## Test Signals
Test signals include sparse-file reads and writes, compressed/encrypted data-node reads, partial-page writes with short copy retries, low-space fallback from fast to slow write_begin, writeback after append and crash recovery, truncation with dirty partial final folio, mmap write faults, bulk-read sequential access, fsync/datasync behavior, and symlink getattr under encryption.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ubifs/file.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ubifs/find.c -->
# sources/distributed-fs/ceph-client/fs/ubifs/find.c

## Purpose
`find.c` selects logical eraseblocks for UBIFS allocation, garbage collection, and index commit work. It searches lprops heaps/lists first, falls back to LPT scans when necessary, marks chosen LEBs as taken, and maintains the dirty-index LEB list used by in-the-gaps index commit.

## Important APIs, Types, and Functions
- `struct scan_data` carries scan criteria and the selected LEB number.
- `valuable()` decides whether lprops found during scans should be cached in memory.
- Dirty-space selection: `scan_for_dirty_cb()`, `scan_for_dirty()`, and `ubifs_find_dirty_leb()`.
- Data free-space selection: `scan_for_free_cb()`, `do_find_free_space()`, and `ubifs_find_free_space()`.
- Index free-LEB selection: `scan_for_idx_cb()`, `scan_for_leb_for_idx()`, and `ubifs_find_free_leb_for_idx()`.
- Dirty-index reuse: `cmp_dirty_idx()`, `ubifs_save_dirty_idx_lnums()`, `scan_dirty_idx_cb()`, `find_dirty_idx_leb()`, `get_idx_gc_leb()`, `find_dirtiest_idx_leb()`, and `ubifs_find_dirty_idx_leb()`.

## Control Flow
Dirty GC selection optionally tries empty/freeable LEBs when the caller allows it and index reservations are safe. It then compares the dirty and dirty-index heaps, preferring the LEB with most free+dirty space while avoiding reserved index LEBs. If heaps and in-memory lists fail, it scans the LPT from `c->lscan_lnum`, adds valuable lprops to memory, and returns a matching LEB. The selected lprops is updated with `LPROPS_TAKEN`.

Free-space selection calculates whether empty LEBs may be consumed without violating minimum index reservations. It may temporarily increments `taken_empty_lebs` under `space_lock` before dropping the lock, then looks for empty, free, dirty-heap, uncategorized, or scanned LPT candidates. Empty or freeable LEBs selected for writing are unmapped before use.

Index allocation only accepts empty/freeable LEBs because commit assumes empty index LEBs and cannot trust free tails after unclean unmount. It marks selected LEBs as both `LPROPS_TAKEN` and `LPROPS_INDEX`, then unmaps them; on unmap failure it clears those flags.

Dirty-index reuse snapshots the dirty-index heap at commit start, sorts by dirty+free space, converts pointers to LEB numbers, then later tries those saved LEBs, a full dirty-index scan, and finally trivial index-GC LEBs.

## State and Persistence Behavior
The file mutates in-memory and on-flash lprops through `ubifs_change_lp()` and `ubifs_change_one_lp()`, updates `c->lscan_lnum`, manipulates `taken_empty_lebs`, consumes `c->dirty_idx`, and may unmap UBI LEBs. Its choices affect persistent allocation layout, GC behavior, commit index placement, and space budgeting accuracy.

## Dependencies and Integration Points
It depends on the LPT/lprops subsystem, lprops category heaps/lists, budgeting counters in `c->bi` and `c->lst`, UBI unmap through UBIFS wrappers, `space_lock`, and index GC helpers. It is used by journal reservation/allocation, garbage collection, and commit/TNC index writing.

## Risks and Edge Cases
- Index reservation logic must avoid stealing LEBs needed for commit; errors can cause later `-ENOSPC` or commit failure.
- `taken_empty_lebs` is adjusted optimistically while locks are dropped; every error path must undo it.
- LPT scanning is skipped when all pnodes are already loaded, so heap/list categorization accuracy matters.
- Free+dirty LEBs are excluded for normal data allocation because they may be unmapped or contain obsolete data still referenced by write buffers.
- Dirty-index saved arrays store LEB numbers cast through `void *`, so users must remember the array no longer contains lprops pointers after `ubifs_save_dirty_idx_lnums()`.

## Test Signals
Exercise GC dirty LEB selection with and without `pick_free`, index reservation pressure, empty/freeable/free/dirty/uncategorized category transitions, LPT scan fallback, unmap failure rollback, dirty-index commit reuse, trivial index GC fallback, and low-space races involving `taken_empty_lebs`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ubifs/find.c -->
