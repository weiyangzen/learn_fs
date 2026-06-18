# Group Research: group_1692_reactos_sources_windows_reactos_drivers_filesystems_fastfat_verfysu_9f01ffa4758f

Scope checked against `Docs/research_subset_a.md`: `sources/windows/reactos` is included in subset A. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/fastfat/verfysup.c -->
# File Research: sources/windows/reactos/drivers/filesystems/fastfat/verfysup.c

FastFAT verification and volume-state support. The file owns VCB and FCB condition transitions, media-change handling, dirty/clean marking, and recovery paths that bridge filesystem exceptions back into I/O manager verify behavior. `FatVerifyVcb`, `FatQuickVerifyVcb`, and `FatPerformVerify` are the main volume verification paths: they check `DO_VERIFY_VOLUME`, VCB state, write-protect state, wrong-volume cases, and use `IoVerifyVolume` plus reparsing for absolute creates after remount.

FCB verification is handled by `FatVerifyFcb`, `FatMarkFcbCondition`, `FatResetFcb`, and `FatDetermineAndMarkFcbCondition`. The code propagates bad/needs-verify states down directory trees, preserves real paging-file mappings except on removable ReadyBoost-style media, resets MCB/allocation hints and directory scan hints, rereads the backing dirent, then compares short name, first cluster, attributes, and file size before marking the FCB good or bad.

Dirty/clean media state is split between boot-sector flags, FAT entry compatibility state, and FAT32 FsInfo updates. `FatMarkVolume` pins the boot/FsInfo sectors, validates the boot sector before touching it, writes synchronously through the target device with an event-backed completion routine, and then flips the FAT dirty-bit entry. `FatCleanVolumeDpc` and `FatDeferredCleanVolume` delay marking a volume clean until cache dirty data drains, verify the VCB still exists, and unlock removable media when appropriate. `FatFspMarkVolumeDirtyWithRecover` marks a volume dirty with surface-test request after paging-file I/O errors and completes or signals the originating request.

Other support includes `FatCheckDirtyBit`, which detects mounted-dirty volumes from the boot sector and logs label-aware messages, `FatMarkDevForVerifyIfVcbMounted`, which safely marks the real device for verify under the VPB spinlock, and `FatVerifyOperationIsLegal`, which rejects most post-cleanup file-object operations while allowing paging I/O, close, information calls, and MDL completes. The file is tightly coupled to cache pinning, VPB/device flags, FAT boot structures, global VCB queues, exception filters, and FastFAT resource ordering.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/fastfat/verfysup.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/fastfat/volinfo.c -->
# File Research: sources/windows/reactos/drivers/filesystems/fastfat/volinfo.c

FastFAT volume-information dispatch and implementation. `FatFsdQueryVolumeInformation` and `FatFsdSetVolumeInformation` are standard FSD wrappers: enter the filesystem, create an IRP context, call common routines, run the FastFAT exception path, restore top-level IRP state, and complete through the common helpers.

`FatCommonQueryVolumeInfo` decodes the file object, verifies the root DCB, dispatches by `FS_INFORMATION_CLASS`, and reports bytes filled by subtracting the remaining output length. `FileFsVolumeInformation` takes the VCB shared because it copies the mutable VPB label; size, device, attribute, full-size, and optional sector-size queries use stable VCB/BPB fields or `FsRtlGetSectorSizeInformation`. The size queries expose cluster counts, free clusters, sectors per cluster, and bytes per sector. Attribute queries report case-preserved Unicode-on-disk names, read-only volume state, maximum component length based on Chicago mode, and filesystem name `FAT` or `FAT32` with overflow handling.

`FatCommonSetVolumeInfo` only permits `UserVolumeOpen`, acquires the VCB exclusive, verifies the root DCB, and currently supports `FileFsLabelInformation`. `FatSetFsLabelInfo` validates an 11-character FAT volume label, converts through upcased OEM form, rejects illegal FAT label characters and periods, strips trailing spaces, handles the `0xe5` first-byte escape, creates or updates a root-directory volume-label dirent, or deletes the existing label. It forces write-through semantics, unpins and flushes before changing the VPB label, updates the root free-dirent bitmap on deletion, and relies on repinned BCB cleanup in the common set path.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/fastfat/volinfo.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/fastfat/workque.c -->
# File Research: sources/windows/reactos/drivers/filesystems/fastfat/workque.c

FastFAT FSP work-queue support. `FatOplockComplete` is the oplock callback: successful oplock breaks resume by queueing the IRP context, while failed breaks complete the IRP with its status. `FatPrePostIrp` performs pre-pending setup for posted IRPs, including clearing stack-owned `FatIoContext`, probing and locking user buffers for read/write, directory query, EA query/set, and selected FSCTL output paths, then marking the IRP pending.

`FatFsdPostRequest` asserts the originating IRP matches, runs `FatPrePostIrp`, queues the request, and returns `STATUS_PENDING`. `FatAddToWorkque` is the queueing primitive. For volume-backed requests it uses the volume device object's overflow spinlock and throttles active worker items with `FSP_PER_DEVICE_THRESHOLD`; excess requests are linked to the per-volume overflow queue. Otherwise it initializes the IRP context work item for `FatFspDispatch` and queues it to `CriticalWorkQueue`. The file is small but important for keeping nonblocking FSD paths, oplock callbacks, and cache-manager deferred writes on the same worker dispatch path.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/fastfat/workque.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/fastfat/write.c -->
# File Research: sources/windows/reactos/drivers/filesystems/fastfat/write.c

FastFAT write implementation. `FatFsdWrite` handles the dispatch wrapper, including a paging-file fast path that bypasses normal common-write processing and calls `FatPagingFileIo`, top-level IRP setup, modified-page-writer top-level adjustment, MDL-complete dispatch to `FatCompleteMdl`, and exception processing. `FatCommonWrite` contains the full write state machine for virtual volume writes, raw DASD writes, user-file cached/noncached writes, metadata paging writes, and user-directory rejection.

Early common-write logic rejects zero-byte writes, defers cached writes through `CcCanIWrite`/`CcDeferWrite`, decodes the open type, forces raw volume writes noncached, validates FAT 32-bit file-size limits, allocates or initializes `FAT_IO_CONTEXT` for noncached I/O, and rejects writes after shutdown. The virtual volume path writes only dirty FAT sectors tracked in `Vcb->DirtyFatMcb`, coalesces dirty runs, mirrors writes across all FAT copies via `FatMultipleAsync`, waits synchronously, and clears dirty MCB ranges on success. The user-volume path enforces restricted writes to unlocked disk volumes, allows special dismount/format-unit cases, flushes and purges cached volume state once per DASD CCB, clamps writes to volume size unless extended DASD I/O is allowed, performs direct device I/O, and updates synchronous file position.

The user-file path manages cache coherency and file growth. Noncached nonpaging writes against cached files acquire the FCB exclusive, hold paging I/O, flush and purge cache ranges, and optionally fail purge-failure-mode requests. Paging writes acquire paging I/O and are clipped to file size. Nonpaging writes acquire the FCB shared or exclusive depending on EOF/VDL extension needs, handle lazy-writer and recursive write-through cases, check oplocks and byte-range locks, extend allocation with cluster-chunking heuristics, update `FileSize`, and inform Cc via `CcSetFileSizes` when cached. VDL gaps are zeroed with `FatZeroData`; noncached writes are sector-aligned and issued via `FatNonCachedIo`, while cached writes initialize the cache map lazily, optionally schedule deferred floppy/hotplug flushes, and use `CcCopyWrite`/`CcCopyWriteEx` or `CcPrepareMdlWrite`.

Completion logic updates current byte offset, `FO_FILE_MODIFIED`, dirent file size for write-through or noncached extending writes, change notifications, valid data length, and cache-manager file sizes for noncached VDL extension. Posting or abnormal termination rolls back file size/VDL and cache file-size state as needed, unwinds outstanding async write counts, releases FCB and paging resources, unpins repinned BCBs, and completes the request unless posted. The tail implements `FatDeferredFlushDpc` and `FatDeferredFlush`, which queue a worker after small deferred-flush-device writes and flush the file under main and paging resources with an FSP top-level IRP marker.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/fastfat/write.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/fs_rec/CMakeLists.txt -->
# File Research: sources/windows/reactos/drivers/filesystems/fs_rec/CMakeLists.txt

Build definition for the ReactOS filesystem recognizer driver. It appends the recognizer sources for block-device helpers and the individual filesystem probes (`btrfs`, `cdfs`, `ext`, `fat`, `fatx`, `ffs`, `ntfs`, `reiserfs`, `udfs`) plus `fs_rec.c` and `fs_rec.h`, builds them as the `fs_rec` kernel-mode driver module with `fs_rec.rc`, imports `ntoskrnl` and `hal`, enables `fs_rec.h` as the precompiled header, and installs the driver to `reactos/system32/drivers`.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/fs_rec/CMakeLists.txt -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/fs_rec/blockdev.c -->
# File Research: sources/windows/reactos/drivers/filesystems/fs_rec/blockdev.c

Generic block-device helper routines for filesystem recognizers. `FsRecGetDeviceSectors` works only on disk devices, sends `IOCTL_DISK_GET_PARTITION_INFO` with `SL_OVERRIDE_VERIFY_VOLUME`, waits synchronously when pending, and divides partition length by the caller's sector size to return a sector count. `FsRecGetDeviceSectorSize` selects disk or CD-ROM geometry IOCTLs based on device type, also overrides verify, waits for completion, and returns `BytesPerSector` only if nonzero.

`FsRecReadBlock` is the shared probe reader. It rounds reads up to at least one sector and to a sector boundary, allocates a nonpaged page-rounded buffer when the caller did not provide one, builds a synchronous `IRP_MJ_READ`, overrides volume verification, waits for pending completion, and optionally reports storage-stack failure through `DeviceError`. All recognizer files use this helper to keep mount-time signature checks synchronous and independent of normal filesystem verification state.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/fs_rec/blockdev.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/fs_rec/btrfs.c -->
# File Research: sources/windows/reactos/drivers/filesystems/fs_rec/btrfs.c

Btrfs filesystem recognizer. `FsRecIsBtrfsVolume` checks only the superblock magic field against `BTRFS_MAGIC`. `FsRecBtrfsFsControl` handles mount and load requests: on `IRP_MN_MOUNT_VOLUME` it gets the target sector size, reads `BTRFS_SB_SIZE` bytes at `BTRFS_SB_OFFSET`, tests the magic, and returns `STATUS_FS_DRIVER_REQUIRED` when recognized. Device-read or geometry failures set a device-error flag, and floppy media are allowed to fall through to the real filesystem driver despite probe failure. On `IRP_MN_LOAD_FILE_SYSTEM` it calls `FsRecLoadFileSystem` for the `btrfs` service; other minor functions return `STATUS_INVALID_DEVICE_REQUEST`.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/fs_rec/btrfs.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/fs_rec/btrfs.h -->
# File Research: sources/windows/reactos/drivers/filesystems/fs_rec/btrfs.h

Packed partial Btrfs superblock definition for the recognizer. It defines a 16-byte `BTRFS_UUID` and the early fields of `BTRFS_SUPER_BLOCK`: checksum, UUID, physical superblock address, flags, and magic. Compile-time offset assertions pin `uuid` at `0x20`, `sb_phys_addr` at `0x30`, and `magic` at `0x40`. Constants define the little-endian Btrfs magic value, primary superblock offset `0x10000`, and probe size `0x1000`.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/fs_rec/btrfs.h -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/fs_rec/cdfs.c -->
# File Research: sources/windows/reactos/drivers/filesystems/fs_rec/cdfs.c

ISO-9660/CDFS recognizer. `FsRecIsCdfsVolume` reads the primary volume descriptor header at byte offset `32768`, then validates descriptor type, the `CD001` identifier, and version `1`; any failed read or field mismatch returns false after freeing the probe buffer. `FsRecCdfsFsControl` dispatches mount requests by obtaining sector size and calling that validator, returning `STATUS_FS_DRIVER_REQUIRED` when recognized. Load requests call `FsRecLoadFileSystem` for the `Cdfs` service, while unsupported minor functions return `STATUS_INVALID_DEVICE_REQUEST`.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/fs_rec/cdfs.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/fs_rec/cdfs.h -->
# File Research: sources/windows/reactos/drivers/filesystems/fs_rec/cdfs.h

Minimal ISO-9660 volume descriptor header for the CDFS recognizer. `VD_HEADER` contains the descriptor type byte, five-byte identifier, and version byte. Constants define the primary descriptor offset `32768`, expected identifier `CD001`, identifier length, primary descriptor type `1`, and volume descriptor version `1`. The header intentionally contains only the signature fields needed for recognition.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/fs_rec/cdfs.h -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/fs_rec/ext.c -->
# File Research: sources/windows/reactos/drivers/filesystems/fs_rec/ext.c

EXT filesystem recognizer for ext-family superblocks. `FsRecIsExtVolume` checks the superblock magic field for `0xEF53`. `FsRecExtFsControl` handles mount by obtaining the sector size, reading the superblock at byte offset `0x400` with size `0x400`, checking the magic, and returning `STATUS_FS_DRIVER_REQUIRED` on success. As with other disk recognizers, device errors on floppy media cause the recognizer to request the real filesystem driver anyway. Load requests target the `Ext2fs` service, and unsupported minor functions fail with `STATUS_INVALID_DEVICE_REQUEST`.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/fs_rec/ext.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/fs_rec/ext.h -->
# File Research: sources/windows/reactos/drivers/filesystems/fs_rec/ext.h

Packed partial EXT superblock layout used only for recognition. The structure includes the leading ext2/3/4 fields through default reserved UID/GID, including counts, block sizing fields, timestamps, mount counts, magic, state, errors, revision, and creator OS. Compile-time assertions verify representative offsets through `DefResUid` at `0x50`. Constants define the EXT magic `0xEF53`, superblock byte offset `0x400`, and read size `0x400`.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/fs_rec/ext.h -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/fs_rec/fat.c -->
# File Research: sources/windows/reactos/drivers/filesystems/fs_rec/fat.c

FAT/VFAT recognizer. `FsRecIsFatVolume` unpacks the packed BPB with `FatUnpackBios`, normalizes the small-versus-large sector count, and validates the boot jump opcode, bytes per sector, sectors per cluster, nonzero reserved sectors, nonzero total sector count, accepted media byte values, and FAT12/16 root-entry consistency. It does not fully mount or classify FAT type; it only decides whether the boot sector is plausible enough to load FastFAT.

`FsRecVfatFsControl` handles mount by reading the first 512 bytes of the target device after retrieving sector size. A successful FAT signature check returns `STATUS_FS_DRIVER_REQUIRED`. Geometry/read failures set `DeviceError`, and floppy failures are treated permissively by requesting the filesystem driver anyway. Load requests call `FsRecLoadFileSystem` for the `fastfat` service.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/fs_rec/fat.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/fs_rec/fatx.c -->
# File Research: sources/windows/reactos/drivers/filesystems/fs_rec/fatx.c

FATX recognizer. The file defines a packed FATX boot-sector shape with `SysType`, volume id, sectors per cluster, FAT count, reserved field, and padding to 4096 bytes. `FsRecIsFatxVolume` checks the leading `FATX` signature and validates sectors per cluster as a power-of-two value from 1 through 128. `FsRecFatxFsControl` reads the first 512 bytes on mount, recognizes FATX with that validator, and returns `STATUS_FS_DRIVER_REQUIRED`; load requests target the `vfatfs` service. Unlike several other recognizers in this group, this file does not apply a floppy-device-error fallback after failed sector-size/read probing.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/fs_rec/fatx.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/fs_rec/ffs.c -->
# File Research: sources/windows/reactos/drivers/filesystems/fs_rec/ffs.c

BSD FFS/UFS recognizer. Small helpers check disklabel magic, UFS1 superblock magic, and UFS2 superblock magic. `FsRecFfsFsControl` handles mount by getting sector size, reading the BSD disklabel from `LABELSECTOR`, and, when a valid disklabel is found, scanning up to `MAXPARTITIONS` for `FS_BSDFFS` partitions. For each candidate partition it computes the byte filesystem offset, reads the UFS1 superblock at `FSOffset + SBLOCK_UFS1`, and if that fails magic validation retries the UFS2 superblock at `FSOffset + SBLOCK_UFS2`.

If the disklabel is absent or invalid, the recognizer also probes UFS1 and UFS2 superblocks at the base device offset. Successful UFS1 or UFS2 recognition returns `STATUS_FS_DRIVER_REQUIRED`; probe buffers are freed after each attempt. Device errors on floppy media use the same permissive fallback as several other recognizers. Load requests target the `ffs` service, and unsupported minor functions return `STATUS_INVALID_DEVICE_REQUEST`.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/fs_rec/ffs.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/fs_rec/ffs.h -->
# File Research: sources/windows/reactos/drivers/filesystems/fs_rec/ffs.h

Packed BSD FFS/UFS on-disk structure definitions for recognition. The header imports a large FreeBSD-compatible `fs` superblock layout as `FFSD_SUPER_BLOCK`, including legacy UFS fields, cylinder-group summary data, mount and volume names, snapshot fields, size/address fields, flags, maximum file size, masks, and final `fs_magic`. It also defines a packed BSD `disklabel` as `FFSD_DISKLABEL`, including geometry, boot names, checksums, and an array of partition entries with filesystem type and UFS fragment/cylinder metadata.

Recognition constants define UFS1 and UFS2 superblock offsets (`8192` and `65536`), superblock read size `8192`, UFS magic values, disklabel magic, label sector, maximum partitions, and the `FS_BSDFFS` partition type. Compile-time assertions pin selected superblock offsets such as `fs_cgsize`, `fs_fmod`, and `fs_ocsp`, protecting the recognizer's use of native on-disk layouts.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/fs_rec/ffs.h -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/fs_rec/fs_rec.c -->
# File Research: sources/windows/reactos/drivers/filesystems/fs_rec/fs_rec.c

Main ReactOS filesystem recognizer driver. `FsRecLoadFileSystem` serializes load attempts with the global `FsRecLoadSync` event, checks linked recognizer device state, calls `ZwLoadDriver` for the requested service, walks alternate recognizer devices into unloading state, unregisters the recognizer filesystem, and marks it loaded. This prevents repeated load attempts across recognizer aliases for the same filesystem family.

The dispatch routines are minimal. `FsRecCreate` only allows opens of the recognizer device itself, rejecting nonempty file names with `STATUS_OBJECT_PATH_NOT_FOUND`; `FsRecClose` completes cleanup/close successfully; `FsRecFsControl` switches on the recognizer device extension's filesystem type and delegates to the specific recognizer for VFAT, NTFS, CDFS, UDFS, EXT, BTRFS, REISERFS, FFS, or FATX before completing the IRP.

`FsRecRegisterFs` first checks whether the real filesystem device name already exists; if so, it returns `STATUS_IMAGE_ALREADY_LOADED`. Otherwise it creates a recognizer device with a `DEVICE_EXTENSION`, records filesystem type and pending state, links alternates through the parent recognizer when applicable, and registers it with the I/O manager. `DriverEntry` pages the driver, allocates the load-sync event, installs dispatch routines, and registers recognizers for CDFS CD/disk, UDFS CD/disk, FAT disk/CD, NTFS, EXT disk/CD, BTRFS, ReiserFS, FFS, and FATX. It succeeds if at least one recognizer was registered.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/fs_rec/fs_rec.c -->