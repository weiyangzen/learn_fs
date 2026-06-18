# sources/distributed-fs/ceph-client/fs/jfs/jfs_imap.h

Purpose: defines the JFS inode allocation map disk/in-core structures, geometry constants, conversion macros, and exported inode-map APIs.

Important APIs and types: defines `struct iag`, `struct iagctl_disk`, `struct iagctl`, `struct dinomap_disk`, `struct dinomap`, and `struct inomap`. Constants include `EXTSPERIAG`, `IMAPBLKNO`, `SMAPSZ`, `EXTSPERSUM`, `PGSPERIEXT`, `MAXIAGS`, `MAXAG`, `AMAPSIZE`, and `SMAPSIZE`. Macros include `INOTOIAG`, `IAGTOLBLK`, `INOPBLK`, and shorthand aliases for `struct inomap` fields. Exports allocation, free, mount, unmount, read/write, persistent-map, extendfs, and special-inode functions.

Control flow: this header has no executable flow, but the structures define how `jfs_imap.c` walks from inode number to IAG page, to inode extent PXD, to dinode page and slot. The exported functions form the mount/read/allocate/free/write lifecycle for JFS inodes.

State and persistence behavior: `struct iag` is a 4 KiB persistent page containing AG list links, summary maps, counts, working and persistent bitmaps, and inode extent addresses for 4096 inodes. `dinomap_disk` is the persistent imap control page; `dinomap` and `inomap` are in-core mirrors with locks and atomics. The split between `wmap` and `pmap` is central to transaction recovery.

Dependencies and integration: includes `jfs_txnmgr.h` for transaction-related declarations and relies on JFS type/PXD helpers. Used by inode allocation, inode read/write, mount setup, dmap interaction, and transaction commit code.

Risks and edge cases: the on-disk structure sizes and endian fields must remain stable. Summary-map polarity is subtle: a set bit in `inosmap` means no free backed inodes are available for that extent, while `extsmap` tracks free extents. `MAXAG` and `MAXIAGS` bound online growth and allocation loops.

Test signals: structure-size/layout checks, inode number-to-IAG conversion, allocation/free count consistency, working versus persistent bitmap recovery, max AG/IAG boundary handling, and endian-safe mount/unmount of the control page.
