# sources/distributed-fs/ceph-client/fs/ntfs/inode.h

## Purpose
`inode.h` defines the NTFS driver's private in-memory inode model and the exported inode lifecycle, lookup, writeback, truncate, attribute I/O, and initialized-size APIs used by the rest of `fs/ntfs`. It is the bridge between Linux VFS `struct inode` objects and NTFS-specific metadata such as MFT record number, attribute identity, runlists, MFT-record buffers, extent records, initialized size, allocation size, and NTFS state flags.

## Important APIs, Types, and Functions
The central type is `struct ntfs_inode`. It stores synchronization (`size_lock`, `mrec_lock`, `extent_lock`), persistent identity (`mft_no`, `seq_no`, `type`, `name`, `name_len`), volume linkage (`vol`), mapping state (`runlist`), on-disk size copies (`data_size`, `initialized_size`, `allocated_size`), resident MFT record state (`mrec`, `folio`, `folio_ofs`, `mft_lcn`, `mft_lcn_count`), attribute-list data, index/compression geometry, extent linkage, delayed-allocation accounting (`i_dealloc_clusters`), and symlink target storage.

`enum ntfs_inode_mutex_lock_class` provides lockdep classes for parent/child, extend, and EA locking paths. The `NI_*` bit enum describes inode state such as dirty MFT records, attribute-list presence, fake attribute inode status, MST protection, non-residency, index allocation presence, compressed/encrypted/sparse modes, full runlist mapping, filename dirtiness, deletion/creation, EA presence, and runlist dirtiness. `NINO_FNS` and `TAS_NINO_FNS` generate inline bit operations such as `NInoNonResident()`, `NInoSetDirty()`, and `NInoTestClearFileNameDirty()`.

`struct big_ntfs_inode` embeds `struct ntfs_inode` before the VFS inode; `NTFS_I()` and `VFS_I()` convert between the two. `struct ntfs_attr` is a compact key for iget/test/init paths for named streams and fake attribute inodes. Exported prototypes include inode acquisition (`ntfs_iget`, `ntfs_attr_iget`, `ntfs_index_iget`), allocation/free/eviction (`ntfs_alloc_big_inode`, `ntfs_free_big_inode`, `ntfs_evict_big_inode`), mount-time inode loading, setattr/getattr, MFT record lookup/writeback, extent attachment/destruction, initialized-size extension, attribute pread/pwrite, and VFS operation setup.

## Control Flow and State
The header establishes the normal flow for all NTFS inode users: a VFS inode is converted with `NTFS_I()`, state bits are tested to choose resident versus non-resident behavior, locks serialize access to mutable MFT/runlist/size fields, and exported helpers perform metadata lookup or mutation. Fake attribute inodes are identified with `NInoAttr()` and point back to the base inode through `ext.base_ntfs_ino`; real base inodes may own loaded extent inode arrays through `ext.extent_ntfs_inos`.

## State and Persistence Behavior
Most fields are cached copies of on-disk MFT or attribute-record state. `data_size`, `initialized_size`, `allocated_size`, `flags`, `i_crtime`, `attr_list`, and `runlist` mirror persistent NTFS structures and must stay synchronized with dirty-bit writeback paths. `NI_Dirty`, `NI_AttrListDirty`, `NI_FileNameDirty`, and `NI_RunlistDirty` mark metadata requiring persistence. The header does not perform persistence itself, but it defines the state consumed by MFT writeback, attribute expansion/truncation, iomap, and allocation code.

## Dependencies and Integration Points
This file depends directly on `debug.h` and Linux kernel types used transitively through the NTFS headers. It is included by the iomap, allocation, attribute, MFT, directory, and VFS layers. `NTFS_I()` is the common integration point for code that starts with VFS objects; `ntfs_extend_initialized_size()` is a key integration point for write paths; `ntfs_inode_attr_pread()` and `ntfs_inode_attr_pwrite()` expose attribute stream I/O to metadata consumers.

## Risks
The main risk is stale or inconsistently locked cached metadata. Callers must respect `size_lock`, `mrec_lock`, `runlist.lock`, and `extent_lock` or they can race truncation, writeback, allocation, or extent loading. Fake attribute inodes share base-record state, so lock ordering and `base_ntfs_ino` handling are critical. State bits are plain bit flags; setting a dirty bit without later writeback, or clearing it too early, risks persistent metadata loss.

## Test Signals
Useful signals include mount/read tests for base and extent MFT records, alternate data stream lookup, resident and non-resident file I/O, truncation and initialized-size extension, hard-link/name dirty writeback, EA and reparse attributes, and lockdep coverage for parent/child inode operations. Compile-time coverage should catch prototype drift through users of `NTFS_I()`, `VFS_I()`, and the exported inode APIs.
