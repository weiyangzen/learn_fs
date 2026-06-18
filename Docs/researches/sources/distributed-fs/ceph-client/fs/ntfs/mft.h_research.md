# sources/distributed-fs/ceph-client/fs/ntfs/mft.h

## Purpose
`mft.h` declares the MFT record handling interface used by the NTFS driver and provides small wrappers for dirty marking, extent unmapping, and locked writeout.

## Important APIs and Types
The header exports record mapping (`map_mft_record()`, `map_extent_mft_record()`, `unmap_mft_record()`), dirty marking (`mark_mft_record_dirty()`, `__mark_mft_record_dirty()`), persistence (`write_mft_record()`, `write_mft_record_nolock()`, `ntfs_sync_mft_mirror()`, `ntfs_mft_writepages()`, `ntfs_mft_mark_dirty()`), allocation/free (`ntfs_mft_record_alloc()`, `ntfs_mft_record_free()`), validation (`ntfs_mft_record_check()`), and a declared but not locally implemented `ntfs_mft_records_write()`.

## Control Flow and State
`mark_mft_record_dirty()` atomically tests and sets the `NInoDirty` bit and calls the implementation only on the clean-to-dirty transition. `write_mft_record()` locks the folio stored in `ni->folio`, calls `write_mft_record_nolock()`, and unlocks, serializing explicit MFT writes against page-cache writeback and reads.

## Dependencies and Integration
The header includes `highmem`, `pagemap`, and `inode.h`, and is consumed by inode, attribute, directory, and MFT implementation code. It exposes the contract that callers must mark mapped records dirty before unmapping after modification.

## Risks
The wrapper assumes `ni->folio` is valid and associated with the mapped `mrec`. The declaration of `ntfs_mft_records_write()` has no implementation in the searched NTFS subtree, which is a build or stale API risk if referenced. Dirty marking is skipped if already dirty, so code that mutates a mapped record must not rely on repeated calls for extra side effects.

## Test Signals
Compile/link tests should catch stale declarations. Runtime tests should confirm `write_mft_record()` is only called for mapped records, lockdep stays clean, and dirty MFT changes reach disk through both explicit write and writeback paths.
