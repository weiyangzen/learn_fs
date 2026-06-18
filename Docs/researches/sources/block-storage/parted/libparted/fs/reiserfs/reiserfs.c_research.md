# File Research: sources/block-storage/parted/libparted/fs/reiserfs/reiserfs.c

Purpose: Detection-only ReiserFS filesystem backend for libparted.

Main interfaces: Registers a `PedFileSystemType` named `reiserfs` with only a `probe` operation. `ped_file_system_reiserfs_init()` registers it; `ped_file_system_reiserfs_done()` unregisters it.

Control flow: `reiserfs_probe()` reads candidate superblock sectors at offsets 128 and 16. If any recognized ReiserFS magic string matches, it computes filesystem length from little-endian block size and block count and returns a new geometry.

Dependencies: `reiserfs.h` for the superblock layout and magic strings, libparted geometry APIs, endian helpers, and UUID/header includes.

Important details and risks: It does not validate checksums or deeper ReiserFS metadata, so detection is signature-and-size based. Geometry sizing assumes superblock block-size fields are sane and divisible by device sector size. Tests should include old/new ReiserFS signatures at both supported offsets and short/truncated geometries.
