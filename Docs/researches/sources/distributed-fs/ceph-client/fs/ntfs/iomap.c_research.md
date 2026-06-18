# sources/distributed-fs/ceph-client/fs/ntfs/iomap.c

## Purpose
`iomap.c` adapts NTFS resident and non-resident attribute storage to Linux's iomap read, buffered write, mmap write-fault, direct-I/O, zero-range, and writeback paths. It maps NTFS runlist entries and resident attribute values into `struct iomap` extents, handles delayed allocation and real cluster allocation, zeroes unwritten or partially initialized regions, and updates resident attribute data after inline writes.

## Important APIs, Types, and Functions
The file exports operation tables: `ntfs_read_iomap_ops`, `ntfs_write_iomap_ops`, `ntfs_seek_iomap_ops`, `ntfs_page_mkwrite_iomap_ops`, `ntfs_dio_iomap_ops`, `ntfs_writeback_ops`, and `ntfs_iomap_folio_ops`. `ntfs_dio_zero_range()` issues sector-aligned block-device zeroout for direct-I/O allocation edges.

Read mapping is split between `ntfs_read_iomap_begin_resident()` for resident attributes and `ntfs_read_iomap_begin_non_resident()` for runlist-backed attributes. Resident reads copy the attribute value into a temporary page and return `IOMAP_INLINE`; `ntfs_read_iomap_end()` releases that page. Non-resident reads translate file offsets to VCNs and LCNs, use `ntfs_attr_vcn_to_rl()`, return `IOMAP_HOLE`, `IOMAP_DELALLOC`, `IOMAP_MAPPED`, or conditionally `IOMAP_UNWRITTEN`, and clamp mappings around `initialized_size`.

Write mapping flows through `__ntfs_write_iomap_begin()`. For non-resident files, `ntfs_write_iomap_begin_non_resident()` may first expand the attribute and extend initialized size. `ntfs_write_simple_iomap_begin_non_resident()` marks holes as `LCN_DELALLOC` for buffered writes, reserves dirty clusters, merges runlists, and zeroes edge clusters when exposure would cross initialized data. `ntfs_write_da_iomap_begin_non_resident()` calls `ntfs_attr_map_cluster()` to allocate real clusters for delayed allocation, direct I/O, mmap write faults, or writeback. Resident writes use `ntfs_write_iomap_begin_resident()` and `ntfs_write_iomap_end_resident()` to copy inline data through a temporary page and back into the MFT attribute record.

Zeroing and validation use `ntfs_zero_range()`, `ntfs_zero_read_iomap_ops`, `ntfs_zero_iomap_folio_ops`, and `ntfs_iomap_valid()`. `ntfs_iomap_valid()` rejects stale cached iomaps if the runlist no longer contains `LCN_DELALLOC` at the mapped VCN.

## Control Flow and State
Read control flow first checks `NInoNonResident()`. Resident attributes are looked up under an NTFS attribute search context and represented as a single inline extent. Non-resident attributes are mapped under `ni->runlist.lock`, with `IOMAP_REPORT` returning `-ENOENT` for holes to support FIEMAP/seek-style reporting.

Write control flow starts by rejecting shutdown volumes, expanding attributes beyond `data_size`, and selecting resident or non-resident handling. Non-resident buffered writes can create delayed-allocation runlist elements and increment `ni->i_dealloc_clusters`; direct-I/O, mmap, and writeback paths allocate real clusters immediately through `ntfs_attr_map_cluster()`. Writeback reuses `wpc->iomap` until the folio range falls outside it, then remaps using `NTFS_IOMAP_FLAGS_WRITEBACK`.

## State and Persistence Behavior
This file mutates in-memory runlists, delayed allocation state, dirty cluster reservations, initialized size, and resident attribute bytes. Persistent metadata updates are delegated to attribute and MFT helpers such as `ntfs_attr_expand()`, `ntfs_attr_map_cluster()`, `ntfs_attr_set_initialized_size()`, and `mark_mft_record_dirty()`. Zeroing behavior is persistence-sensitive: before exposing newly allocated or previously uninitialized cluster edges, the code zeroes buffered folios or issues block-device zeroout for direct-I/O paths.

## Dependencies and Integration Points
It depends on Linux `iomap`, folio, writeback, and block-device zeroout APIs plus NTFS `attrib.h`, `mft.h`, `ntfs.h`, and `iomap.h`. It integrates with VFS address-space operations through exported iomap operation tables, with the allocator through delayed/real cluster states (`LCN_DELALLOC`, `LCN_HOLE`, LCN values), with inode state through `initialized_size` and `i_dealloc_clusters`, and with MFT writeback for resident data.

## Risks
The largest risks are stale cached iomaps, initialized-size boundary mistakes, and delayed-allocation accounting errors. A stale runlist while `iomap_zero_range()` iterates can zero data written through another path, which is why `ntfs_iomap_valid()` exists. Partial-cluster writes before `initialized_size` require edge zeroing; missed zeroing could expose stale disk contents. Locking is subtle: several error paths unlock `mrec_lock` after runlist operations, and direct/writeback flags control whether allocation updates mapping pairs immediately. The file also assumes resident inline iomaps are backed by temporary pages that are always released on end paths.

## Test Signals
High-value tests include buffered writes into holes, writes crossing `initialized_size`, direct-I/O writes with unaligned cluster edges but sector-aligned zeroout, mmap page faults beyond initialized size, writeback of delayed allocations, SEEK_DATA/SEEK_HOLE behavior over preallocated ranges, resident file read/write, and races between zero-range, truncate, and buffered writes. Fault-injection should cover allocation failure after dirty-cluster reservation and runlist merge failure.
