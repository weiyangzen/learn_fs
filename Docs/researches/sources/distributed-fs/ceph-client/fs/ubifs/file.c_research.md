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
