# Group Research: group_1811_winbtrfs_sources_windows_winbtrfs_src_btrfs_c_sources_windows_winbt_55c4ca6259ae

Scope: `Docs/research_subset_a.md`, specifically the WinBtrfs files listed for this work item. I read each source file completely.

<!-- BEGIN FILE RESEARCH: sources/windows/winbtrfs/src/btrfs.c -->
# File Research: sources/windows/winbtrfs/src/btrfs.c

## Role

`btrfs.c` is the central WinBtrfs filesystem-driver entry and mount orchestration unit. It wires the Windows driver object to dispatch routines implemented across the driver, owns global driver state, mounts and verifies Btrfs volumes, loads superblock/root/chunk/device metadata, manages file-reference/FCB lifetimes, handles shutdown/power/unload, and supplies shared helpers for names, attributes, notifications, physical I/O, checksums, and range locking.

## Main Responsibilities

- Defines supported Btrfs feature masks: `INCOMPAT_SUPPORTED` allows mixed backrefs, default subvols, mixed groups, LZO/ZSTD, big metadata, RAID56, extended irefs, skinny metadata, no-holes, metadata UUID, and RAID1C3/C4; `COMPAT_RO_SUPPORTED` allows free-space cache/tree validity, verity, and block-group tree.
- Declares global driver state: control and bus device objects, `VcbList`, UID/GID mapping lists, mount option defaults, registry/logging state, PnP notification handles, PDO list/mapping locks, degraded-mount timing state, boot lock, and dynamically resolved kernel routine pointers.
- Provides debug logging paths in `_DEBUG`: `DbgPrint`, serial-device writes, or log-file appends, protected by `log_lock`.
- Provides CPU feature selection for CRC32C and RAID XOR: SSE4.2 CRC32C, SSE2/AVX2 XOR on x86/x64, and ARM64 CRC32C where available; fallback XOR is `do_xor_basic`.
- Implements Windows IRP dispatchers present in this file: close, cleanup, flush buffers, query/set volume information, filesystem control, lock control, shutdown, power, and system control. Other major functions are assigned in `DriverEntry` but implemented in companion files.
- Implements mount/verify lifecycle: `mount_vol`, `verify_volume`, `verify_device`, `uninit`, `do_shutdown`, `DriverUnload`, `AddDevice`, and `DriverEntry`.

## Driver Entry And Global Setup

- `DriverEntry` reads OS version, initializes global locks/lists, copies `RegistryPath`, reads registry settings, optionally initializes debug logging, selects CPU-specific helpers, dynamically resolves optional Windows APIs, assigns all `DriverObject->MajorFunction` entries, initializes fast I/O dispatch, creates the `\Btrfs` control device and `\DosDevices\Btrfs` link, initializes caches, registry watching, and a private bus device.
- It reports/registers a Btrfs bus interface, invalidates bus relations, starts a three-second `degraded_wait_thread`, initializes `boot_lock`, registers PnP notifications for volume, hidden volume, and disk interfaces, starts the mount-manager thread, registers the filesystem with I/O manager, and calls `check_system_root`.
- `AddDevice` handles PDOs discovered by PnP code in other files. It finds the matching `pdo_device_extension`, creates a named volume device using `BTRFS_VOLUME_PREFIX` plus the filesystem UUID, creates an `\ArcName\btrfs(<uuid>)` symlink, registers a volume interface, attaches to the physical device stack, records the `volume_device_extension`, propagates removable/boot flags, enables the device interface, and returns success if already initialized.

## Mount Path

- `mount_vol` accepts only the master control device, rejects attempts to mount the driver's own PDO, and distinguishes normal Windows volume devices from private WinBtrfs volume devices by querying mountdev names and Btrfs PnP state.
- For PnP-backed multi-device filesystems, it validates child devices still contain Btrfs superblocks before mounting, chooses the first child for metadata reads, and refuses incomplete device sets unless degraded mounting is allowed and probing/wait conditions permit it.
- It creates the filesystem `DEVICE_OBJECT`, initializes the `device_extension`, resources, lists, lookaside lists, notification sync, and VCB pointers, reads the newest valid superblock copy, loads per-volume registry options, applies boot-subvolume override, rejects ignored volumes and unsupported incompat flags, converts unknown compatible-read-only flags into read-only mounts, increments the in-memory generation, clears an unreplayed log tree pointer, and sets checksum size based on superblock checksum type.
- It seeds the primary `device` from the superblock `DEV_ITEM`, detects readonly/removable/TRIM/flush support, adds the chunk root and system chunks, loads the chunk tree, validates device count/readonly state, loads the root tree and all root items, optionally finds chunk usage, clears invalid/outdated free-space cache state, and commits the mount-time batch list.
- It creates the volume FCB, dummy directory FCB, root FCB, root file reference, root stream file object, Cc cache map, loads root directory children, reads the root inode item, loads root security descriptor, computes root attributes, computes per-device free space holes, sets VPB mounted state, starts the flush thread and calculation worker threads, marks the registry volume mounted, looks for any persisted balance item, inserts the VCB into `VcbList`, and notifies `FSRTL_VOLUME_MOUNT`.

## Key Notes

- `uninit` stops balance/scrub/send/calculation/flush activity and reclaims VCB-owned roots, chunks, devices, FCBs, filerefs, resources, and lookaside lists.
- `drv_cleanup` handles delete-on-close/POSIX delete, share access, locks, directory notifications, cache flush/purge, and cache-map uninitialization.
- `check_superblock_checksum` supports CRC32C, XXHASH, SHA256, and BLAKE2.
- Notable TODOs include missing transaction-log replay, several cleanup/locking FIXMEs, and compatibility behavior that can report the FS name as `NTFS` for selected Windows callers.

<!-- END FILE RESEARCH: sources/windows/winbtrfs/src/btrfs.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/winbtrfs/src/btrfs.h -->
# File Research: sources/windows/winbtrfs/src/btrfs.h

## Role

`btrfs.h` is a public-domain, packed on-disk Btrfs format header for WinBtrfs. It defines constants, key/item type IDs, root IDs, feature flags, checksum/compression/encryption identifiers, block profile flags, and packed C structures matching Btrfs metadata and send-stream records.

## Contents

- Defines superblock locations, `BTRFS_MAGIC`, label/root constants, item type IDs, root IDs, compression IDs, extent types, block profile flags, inode/subvolume flags, feature flags, checksum types, and device-stat indexes.
- Defines packed on-disk structures including `BTRFS_UUID`, `KEY`, tree headers/nodes, `DEV_ITEM`, `superblock_backup`, `superblock`, directory/inode/root records, chunk/stripe records, extent/ref records, free-space records, block-group records, root/device extent records, and balance records.
- Defines Btrfs send-stream command IDs, TLV IDs, `BTRFS_SEND_MAGIC`, and send header/command/TLV structures.
- Includes a static assertion that `INODE_ITEM` is exactly `0xa0` bytes.

## Consumers

`btrfs.c` and companion WinBtrfs files use this header for disk parsing, feature validation, root/chunk/device loading, metadata writes, send/receive behavior, checksums, extents, balance, scrub, and ioctl handling.

<!-- END FILE RESEARCH: sources/windows/winbtrfs/src/btrfs.h -->

<!-- BEGIN FILE RESEARCH: sources/windows/winbtrfs/src/btrfs.rc.in -->
# File Research: sources/windows/winbtrfs/src/btrfs.rc.in

## Role

`btrfs.rc.in` is a CMake-configured Windows resource script template for the WinBtrfs kernel driver binary, `btrfs.sys`.

## Contents

- Includes `@CMAKE_CURRENT_SOURCE_DIR@/src/resource.h` and `<winresrc.h>`.
- Declares English UK resources using code page 1252.
- Defines `VS_VERSION_INFO` with CMake-substituted project version fields.
- Sets debug file flags under `_DEBUG`.
- Stamps metadata such as `FileDescription`/`ProductName` `WinBtrfs`, `InternalName` `btrfs`, `OriginalFilename` `btrfs.sys`, and copyright `Copyright (c) Mark Harmstone 2016-24`.
- Adds translation `0x809, 1200`.

## Notes

This file contains no driver logic; it exists for build-time version/resource metadata and requires CMake substitution before resource compilation.

<!-- END FILE RESEARCH: sources/windows/winbtrfs/src/btrfs.rc.in -->