# sources/distributed-fs/ceph-client/drivers/md/md-autodetect.c

## Purpose

`md-autodetect.c` implements early boot setup for built-in Linux MD RAID arrays. It parses `raid=` and `md=` kernel command-line options, optionally autodetects marked RAID partitions after device probing, and assembles explicitly configured arrays before normal userspace is available.

## Important APIs, Types, and Functions

`struct md_setup_args` records one command-line array definition. `md_setup()` parses `md=` options, including partitionable devices, persistent-superblock arrays, RAID0, and linear legacy forms. `md_setup_drive()` resolves component devices, allocates and locks an `mddev`, sets non-persistent array info, adds disks, and runs the array. `raid_setup()` parses autodetect flags. `autodetect_raid()` waits for device probing and autostarts arrays. `md_run_setup()` runs autodetect and all stored explicit setups.

## Control Flow

`__setup("md=", md_setup)` stores definitions in `md_setup_args`, replacing duplicates for the same minor/partitioned pair. `__setup("raid=", raid_setup)` configures autodetect. Later `md_run_setup()` optionally calls `autodetect_raid()`, then iterates all stored entries. Drive setup resolves comma-separated devices, allocates the MD array, skips arrays already autodetected, sets array metadata for non-persistent definitions, adds component disks, calls `do_md_run()`, and unlocks/releases the device.

## State and Persistence Behavior

All state is boot-only `__initdata`: autodetect flags, setup array, and setup count. The file does not persist RAID metadata. Persistent arrays rely on MD superblocks; non-persistent command-line arrays are constructed from `mdu_array_info_s` and `mdu_disk_info_s`.

## Dependencies and Integration Points

It integrates with kernel command-line `__setup`, early block-device lookup/stat helpers, MD core allocation/locking/configuration/run functions, and RAID UAPI structures. It is relevant when MD and personalities are built into the kernel rather than loaded later as modules.

## Risks and Test Signals

Device-name parsing mutates the command-line string, unresolved devices stop parsing, autodetected arrays cause explicit setup to skip, and legacy chunk-factor parsing can be surprising. Test `raid=noautodetect`, `raid=autodetect`, partitionable arrays, duplicate `md=`, persistent and non-persistent forms, unresolved devices, already-autodetected arrays, and successful boot-time `do_md_run()`.
