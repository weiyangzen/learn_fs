# File Research: sources/block-storage/parted/libparted/libparted.c

## Purpose

`libparted.c` is the library initialization and teardown unit for libparted. It registers disk-label and filesystem handlers at load time, frees global device state at unload time, exposes the version string, and provides libparted allocation wrappers.

## Main Responsibilities

- Registers disk types in constructor `_init()`.
- Registers filesystem types in constructor `_init()`.
- Sets gettext domain when NLS is enabled.
- Calls `ped_set_architecture()`.
- Deregisters disk and filesystem types in destructor `_done()`.
- Frees all cached devices in `_done()`.
- Exposes `ped_get_version()`.
- Implements `ped_malloc()` and `ped_calloc()`.

## Disk Type Registration

`init_disk_types()` registers disk labels in an order chosen because probing happens in reverse registration order. `loop` is initialized first so it probes last. S390 DASD is registered only on S390 builds. PC-98 registration is controlled by `ENABLE_PC98`.

Registered labels include loop, DASD, Atari, Sun, PC-98, msdos, mac, GPT, DVH, BSD, Amiga, and AIX.

## Filesystem Registration

`init_file_system_types()` registers Amiga, XFS, UFS, ReiserFS, NTFS, Linux swap, JFS, HFS, FAT, F2FS, ext2, NILFS2, Btrfs, and UDF.

The destructor calls the corresponding `*_done()` functions, mostly in reverse-ish order.

## Notable Details

`ped_malloc()` throws a fatal libparted exception on allocation failure and returns `NULL`. `ped_calloc()` calls `ped_malloc()` then zeroes the returned buffer without checking for `NULL`, relying on fatal exception behavior.

A disabled DEBUG section contains old allocation debugging scaffolding that the comments explicitly describe as harmful and not useful.
