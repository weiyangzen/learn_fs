# File Research: sources/block-storage/parted/libparted/fs/Makefile.am

Automake definition for libparted filesystem support. It builds an internal `libfs.la` with probe modules for Amiga filesystems, btrfs, ext2/3/4, FAT, f2fs, HFS/HFS+/HFSX, JFS, linux swap, NILFS2, NTFS, reiserfs, UDF, UFS, and XFS.

It also builds public `libparted-fs-resize.la`, versioned with libtool `0:5:0`, using `fsresize.sym` as the linker version script. The resize library source list is separate under `r/`, including FAT resize implementation and HFS/HFS+ resize/relocation/cache/journal support. `libfs.la` links UUID, intl, and OS libraries; the resize library links UUID.

The file encodes an architectural split: normal libparted filesystem support is mostly probe and registration code, while the `r/` subtree contains resizing-capable implementations exported through the fs-resize shared library.
