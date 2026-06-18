# File Research: sources/cow-pools/bcachefs-tools/fs/vfs/fs.h

Purpose: declares the bcachefs VFS inode wrapper and public VFS-layer helpers.

Key contents:
- `struct bch_inode_info` embeds `struct inode` and adds bcachefs state: subvolume inode identity, hash links, cached reserved extent range, update/pagecache/quota locks, quota state, nocow flush device mask, btree inode copy, and delayed writeback work.
- Defines pagecache add/block locking helpers using `two_state_lock_t`.
- Defines inode flag bits: `EI_INODE_ERROR`, `EI_INODE_SNAPSHOT`, and `EI_INODE_HASHED`.
- Provides ordered multi-inode lock/unlock macros that sort inode pointers before acquiring pagecache-block and/or update locks.
- Declares VFS inode lookup/create/write/update helpers, quota transfer, setattr/unlink, fiemap, VFS init/exit, and dirty-inode scheduling.

Important interactions:
- Included by most VFS files as the shared inode contract.
- The cached reserved range comment documents a critical staleness contract: allocation can become more allocated without notification, but deallocation must clear cached state under pagecache blocking.
