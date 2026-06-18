# Group Research: group_1693_reactos_sources_windows_reactos_drivers_filesystems_fs_rec_fs_rec_h_b820b72b266b

Scope: `Docs/research_subset_a.md`, ReactOS filesystem driver sources only. Every listed file was read completely.

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/fs_rec/fs_rec.h -->
# File Research: sources/windows/reactos/drivers/filesystems/fs_rec/fs_rec.h

This is the shared header for the ReactOS filesystem recognizer driver. It centralizes recognizer-wide constants, packed on-disk structures, filesystem type/state enums, device-extension layout, and function prototypes used by the individual recognizers.

The header defines allocation tag `FSREC_TAG`, UDFS probing offsets, local `ROUND_UP`/`ROUND_DOWN` helpers, and unaligned copy helpers used for FAT-style BIOS Parameter Block handling. It contains packed and unpacked BPB/boot-sector structures, plus minimal UDF anchor-volume descriptor structures.

`FILE_SYSTEM_TYPE` enumerates all recognizers supported by this driver: VFAT, NTFS, CDFS, UDFS, EXT, BTRFS, REISERFS, FFS, and FATX. `DEVICE_EXTENSION` stores recognizer state, filesystem type, and an alternate device object pointer.

The declared API surface includes per-filesystem FS control dispatchers, block-device helpers (`FsRecGetDeviceSectors`, `FsRecGetDeviceSectorSize`, `FsRecReadBlock`), and `FsRecLoadFileSystem`, which each recognizer uses after returning `STATUS_FS_DRIVER_REQUIRED`.

Important dependency: this header includes `ntifs.h`, so all declarations assume Windows kernel filesystem-driver types and calling conventions.

Research notes:
- This file is infrastructure, not recognition logic by itself.
- The packed structure definitions make unaligned on-disk access explicit.
- UDF descriptor definitions here overlap conceptually with `udfs.h`, which contains the VSD structure used by the UDF recognizer.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/fs_rec/fs_rec.h -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/fs_rec/ntfs.c -->
# File Research: sources/windows/reactos/drivers/filesystems/fs_rec/ntfs.c

This file implements the NTFS recognizer. It detects NTFS by checking whether the boot-sector OEM field is exactly `NTFS    `.

`FsRecIsNtfsVolume` ignores the supplied sector size and sector count and only validates the eight-byte OEM signature in `PACKED_BOOT_SECTOR`.

`FsRecNtfsFsControl` handles two minor functions:
- `IRP_MN_MOUNT_VOLUME`: gets the target device sector size and sector count, then attempts to read 512 bytes at the primary boot sector, midpoint sector, and final sector. If any read succeeds and the signature matches, it returns `STATUS_FS_DRIVER_REQUIRED`.
- `IRP_MN_LOAD_FILE_SYSTEM`: asks the recognizer core to load `\Registry\Machine\System\CurrentControlSet\Services\Ntfs`.

The midpoint and last-sector fallback reflects NTFS backup boot-sector probing. If none of the reads recognize NTFS, the default result is `STATUS_UNRECOGNIZED_VOLUME`.

Research notes:
- Detection is intentionally lightweight and signature-only.
- The recognizer frees the boot-sector buffer after the read attempts.
- The `else if` chain means later offsets are tried only when earlier reads fail, not when earlier reads succeed but do not match NTFS.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/fs_rec/ntfs.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/fs_rec/reiserfs.c -->
# File Research: sources/windows/reactos/drivers/filesystems/fs_rec/reiserfs.c

This file implements the ReiserFS recognizer. It reads the ReiserFS superblock at the fixed 64 KiB disk offset and checks the magic string.

`FsRecIsReiserfsVolume` compares `s_magic` against `REISER2FS_SUPER_MAGIC_STRING` for `MAGIC_KEY_LENGTH` bytes. The current check recognizes `ReIsEr2Fs`, not the older `ReIsErFs` or `ReIsEr3Fs` strings defined in the header.

`FsRecReiserfsFsControl` handles:
- `IRP_MN_MOUNT_VOLUME`: gets sector size, reads one sector at `REISERFS_DISK_OFFSET_IN_BYTES`, validates the superblock, and returns `STATUS_FS_DRIVER_REQUIRED` on match.
- `IRP_MN_LOAD_FILE_SYSTEM`: loads `\Registry\Machine\System\CurrentControlSet\Services\reiserfs`.

If sector-size discovery or the read path reports a device error on a floppy device, the recognizer returns `STATUS_FS_DRIVER_REQUIRED` to let the filesystem driver attempt handling.

Research notes:
- Several comments still say Btrfs; behavior is ReiserFS-specific.
- The recognizer reads only one sector, so it assumes the magic field is within that first sector of the superblock area.
- Magic matching is narrower than the header constants suggest.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/fs_rec/reiserfs.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/fs_rec/reiserfs.h -->
# File Research: sources/windows/reactos/drivers/filesystems/fs_rec/reiserfs.h

This header defines the packed ReiserFS superblock subset used by `reiserfs.c`. It includes journal parameters, block counters, root block, block size, object-id metadata, mount state, magic string, filesystem state, hash function, tree height, bitmap count, version, and reserved journal size.

It uses `pshpack1.h`/`poppack.h` to enforce on-disk packing and has `C_ASSERT` checks for the expected offsets of `s_blocksize` and `s_magic`.

Constants:
- `REISERFS_DISK_OFFSET_IN_BYTES`: 64 KiB.
- Magic strings: `ReIsErFs`, `ReIsEr2Fs`, `ReIsEr3Fs`.
- `MAGIC_KEY_LENGTH`: 9.

Research notes:
- Header comment metadata says Btrfs, but the structure and constants are ReiserFS.
- Only `REISER2FS_SUPER_MAGIC_STRING` is currently used by the recognizer.
- This is a recognizer-only structure, not a complete ReiserFS format definition.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/fs_rec/reiserfs.h -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/fs_rec/udfs.c -->
# File Research: sources/windows/reactos/drivers/filesystems/fs_rec/udfs.c

This file implements the UDF recognizer. It scans volume structure descriptors beginning at sector 16 and looks for UDF namespace identifiers.

`FsRecIsUdfsVolume` reads up to 16 sector-sized descriptors starting at `16 * SectorSize`. For each descriptor, it logs recognized identifiers and sets success if it sees either `NSR03` or `NSR02`. Other identifiers (`BEA01`, `TEA01`, `CD001`, `CDW02`, `BOOT2`) are logged but do not independently recognize UDF.

`FsRecUdfsFsControl` handles:
- `IRP_MN_MOUNT_VOLUME`: gets the sector size and calls `FsRecIsUdfsVolume`.
- `IRP_MN_LOAD_FILE_SYSTEM`: loads `\Registry\Machine\System\CurrentControlSet\Services\Udfs`.

Research notes:
- The file comment says `USFS Recognizer`, but implementation is UDFS/UDF.
- Recognition depends on the VSD sequence rather than anchor-volume descriptors.
- The loop stops on the first failed descriptor read and frees only the last allocated descriptor buffer.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/fs_rec/udfs.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/fs_rec/udfs.h -->
# File Research: sources/windows/reactos/drivers/filesystems/fs_rec/udfs.h

This header contains UDF/ECMA volume-structure descriptor identifiers and the descriptor layout used by the recognizer.

It defines standard identifiers:
- `NSR02` for ECMA-167 revision 2 UDF namespace.
- `NSR03`, `BEA01`, `BOOT2`, `CD001`, `CDW02`, and `TEA01` for ECMA-167 revision 3 / related descriptor recognition.

`VOLSTRUCTDESC` is a 2048-byte descriptor with one-byte type, five-byte identifier, one-byte version, and remaining data payload.

Research notes:
- This file is narrowly scoped to recognition.
- The descriptor size implicitly matches common optical-media sector sizing.
- `VSD_STD_ID_LEN` is five, matching all identifiers used by `udfs.c`.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/fs_rec/udfs.h -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/msfs/CMakeLists.txt -->
# File Research: sources/windows/reactos/drivers/filesystems/msfs/CMakeLists.txt

This build file defines the ReactOS mailslot filesystem driver module `msfs`.

It builds from `create.c`, `finfo.c`, `fsctrl.c`, `msfs.c`, `msfssup.c`, `rw.c`, and `msfs.h`, adds `msfs.rc`, marks the target as a kernel-mode driver, links against `ntoskrnl` and `hal`, configures `msfs.h` as the precompiled header, installs the driver under `reactos/system32/drivers`, and registers `msfs_reg.inf`.

Research notes:
- The module is self-contained inside the listed MSFS files.
- No external filesystem library is linked beyond kernel/HAL imports.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/msfs/CMakeLists.txt -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/msfs/create.c -->
# File Research: sources/windows/reactos/drivers/filesystems/msfs/create.c

This file implements mailslot create/open and close paths.

`MsfsCreate` opens the client side of an existing mailslot. It allocates a CCB, searches the global FCB list by case-insensitive filename, inserts the CCB into the matching FCB’s CCB list, increments the FCB reference count, and attaches FCB/CCB to the file object. If no mailslot exists, it returns `STATUS_UNSUCCESSFUL`.

`MsfsCreateMailslot` creates the server side. It allocates an FCB, copies the mailslot name, allocates a server CCB, initializes CCB/message/pending-IRP lists and locks, initializes the cancel-safe queue, checks for duplicate names, inserts the FCB globally, and attaches the server CCB to the file object.

`MsfsClose` decrements the FCB reference count, removes and frees the CCB, and if the closing handle is the server CCB, it drains queued messages and clears `ServerCcb`. When the reference count reaches zero, it removes and frees the FCB and name buffer.

Research notes:
- Global FCB list access is serialized with a mutex.
- Per-FCB CCB and message lists use spin locks.
- Duplicate mailslot creation fails with `STATUS_UNSUCCESSFUL`, not a more specific collision status.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/msfs/create.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/msfs/finfo.c -->
# File Research: sources/windows/reactos/drivers/filesystems/msfs/finfo.c

This file implements mailslot query and set information dispatch.

`MsfsQueryMailslotInformation` fills `FILE_MAILSLOT_QUERY_INFORMATION` with max message size, read timeout, available message count, and next message size. If no message is queued, it reports `MAILSLOT_NO_MESSAGE` as `MAXULONG`.

`MsfsSetMailslotInformation` updates the FCB read timeout from `FILE_MAILSLOT_SET_INFORMATION`.

`MsfsQueryInformation` and `MsfsSetInformation` both require the caller to be the server side of the mailslot. Client-side callers receive `STATUS_ACCESS_DENIED`. Supported information classes are `FileMailslotQueryInformation` and `FileMailslotSetInformation`; other classes return `STATUS_NOT_IMPLEMENTED`.

Research notes:
- Buffer-size failures return `STATUS_BUFFER_OVERFLOW`.
- Query information length is reported as bytes consumed from the caller’s original buffer length.
- The file locally undefines and redefines mailslot constants to `MAXULONG`.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/msfs/finfo.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/msfs/fsctrl.c -->
# File Research: sources/windows/reactos/drivers/filesystems/msfs/fsctrl.c

This file provides `MsfsFileSystemControl`, the MSFS filesystem-control dispatcher.

The implementation obtains the file object and FCB for logging, switches on `FsControlCode`, and currently returns `STATUS_NOT_IMPLEMENTED` for every code.

Research notes:
- This is a placeholder dispatch path.
- It still completes the IRP consistently with status and zero information.
- No MSFS-specific FSCTLs are implemented here.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/msfs/fsctrl.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/msfs/msfs.c -->
# File Research: sources/windows/reactos/drivers/filesystems/msfs/msfs.c

This file contains the MSFS `DriverEntry`.

It registers major functions for create, create mailslot, close, read, write, query/set information, and filesystem control. Directory control, flush, shutdown, and security dispatchers are present only as commented placeholders.

`DriverEntry` creates `\Device\MailSlot` as a `FILE_DEVICE_MAILSLOT` device, enables `DO_DIRECT_IO`, initializes the device extension’s global FCB list and mutex, and returns success.

Research notes:
- The driver has no unload routine (`DriverUnload = NULL`).
- The device extension is only the global FCB list plus lock.
- MSFS is a kernel-mode driver module, not a user-mode service.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/msfs/msfs.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/msfs/msfs.h -->
# File Research: sources/windows/reactos/drivers/filesystems/msfs/msfs.h

This is the private MSFS header. It defines all driver-private structures and dispatch prototypes.

Key structures:
- `MSFS_DEVICE_EXTENSION`: global FCB list and mutex.
- `MSFS_FCB`: mailslot state, name, server CCB, reference count, timeout, max message size, message queue, CCB list, and cancel-safe pending read queue.
- `MSFS_CCB`: per-open context pointing back to the FCB.
- `MSFS_MESSAGE`: queued message with variable-length payload.
- `MSFS_DPC_CTX`: timer/DPC/event context used for pending read timeouts.

The header also wraps mutex operations with `KeLockMutex` and `KeUnlockMutex` macros, declares all dispatch routines, and declares cancel-safe queue callbacks plus the timeout DPC.

Research notes:
- The FCB combines persistent mailslot metadata with synchronization and pending I/O state.
- Message payload uses a trailing one-byte array idiom.
- The design is small and direct, with no separate namespace or security abstraction.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/msfs/msfs.h -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/msfs/msfssup.c -->
# File Research: sources/windows/reactos/drivers/filesystems/msfs/msfssup.c

This file implements support routines for the MSFS cancel-safe queue and read timeout handling.

Cancel-safe queue callbacks:
- `MsfsInsertIrp`: appends an IRP to the FCB pending queue.
- `MsfsRemoveIrp`: removes an IRP from that queue.
- `MsfsPeekNextIrp`: returns the next pending IRP, optionally filtered by file object.
- `MsfsAcquireLock` / `MsfsReleaseLock`: protect the queue with `Fcb->QueueLock`.
- `MsfsCompleteCanceledIrp`: completes canceled IRPs with `STATUS_CANCELLED`.

`MsfsTimeout` runs as a DPC, removes the timed-out IRP from the cancel-safe queue, completes it with `STATUS_IO_TIMEOUT`, and frees its context. If the IRP was already removed by a writer, it signals the event so the writer can safely free the context.

Research notes:
- Timeout handling explicitly manages the race between timer DPC and writer wake-up.
- The DPC context is allocated per pending read in `rw.c`.
- Canceled IRPs report zero information.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/msfs/msfssup.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/msfs/rw.c -->
# File Research: sources/windows/reactos/drivers/filesystems/msfs/rw.c

This file implements MSFS read and write behavior.

`MsfsRead` is server-side only. If messages are queued, it removes the oldest message, copies up to the caller’s requested length into the target buffer, frees the message, and completes successfully. If no messages are queued, a zero timeout completes immediately with `STATUS_IO_TIMEOUT`; otherwise it allocates a DPC context, inserts the IRP into the cancel-safe queue, starts a timer unless the timeout is infinite, marks the IRP pending, and returns `STATUS_PENDING`.

`MsfsWrite` is client-side only. It copies the caller buffer into a newly allocated message, appends it to the mailslot queue, then removes one pending read IRP if present. For a pending reader, it cancels or synchronizes with the timeout timer, frees the context, and calls `MsfsRead` again to satisfy the read from the newly queued message.

Research notes:
- Server handles cannot write, and client handles cannot read.
- Reads copy `min(Message->Size, Length)` but set `IoStatus.Information` to the full message size.
- The driver supports MDL-backed direct I/O and falls back to `UserBuffer`.
- Message size limits are stored in the FCB but not enforced in this write path.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/msfs/rw.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/mup/CMakeLists.txt -->
# File Research: sources/windows/reactos/drivers/filesystems/mup/CMakeLists.txt

This build file defines the ReactOS Multi UNC Provider driver module `mup`.

It builds `dfs.c`, `mup.c`, `dfs.h`, and `mup.h` into a kernel-mode driver, links the PSEH library plus `ntoskrnl` and `hal`, uses `mup.h` as the precompiled header, and installs the resulting driver under `reactos/system32/drivers`.

Research notes:
- The MUP module includes DFS stubs, but DFS is not functionally implemented in this group.
- PSEH is needed because `mup.c` uses structured exception handling macros.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/mup/CMakeLists.txt -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/mup/dfs.c -->
# File Research: sources/windows/reactos/drivers/filesystems/mup/dfs.c

This file contains DFS entry points used by MUP when DFS support is enabled, but all functionality is currently stubbed.

`DfsVolumePassThrough`, `DfsFsdFileSystemControl`, `DfsFsdCreate`, `DfsFsdCleanup`, and `DfsFsdClose` return `STATUS_NOT_IMPLEMENTED`. `DfsUnload` is also unimplemented. `DfsDriverEntry` logs that DFS is not implemented and returns `STATUS_NOT_IMPLEMENTED`.

Research notes:
- `mup.c` attempts DFS initialization if registry policy allows it, but disables DFS if `DfsDriverEntry` fails.
- These stubs keep DFS dispatch boundaries visible without enabling DFS behavior.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/mup/dfs.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/mup/dfs.h -->
# File Research: sources/windows/reactos/drivers/filesystems/mup/dfs.h

This header declares the DFS stub interface consumed by MUP.

It defines context marker constants such as `DFS_OPEN_CONTEXT`, `DFS_DOWNLEVEL_OPEN_CONTEXT`, `DFS_CSCAGENT_NAME_CONTEXT`, and `DFS_USER_NAME_CONTEXT`, plus `DFS_NAME_CONTEXT` containing a UNC filename, context type, and flags.

It declares DFS pass-through, filesystem-control, create, cleanup, close, unload, and driver-entry routines.

Research notes:
- The constants are used by `mup.c`, especially `DFS_DOWNLEVEL_OPEN_CONTEXT`, to decide whether to bypass DFS logic and perform regular provider resolution.
- The declared API is broader than the stubbed implementation in `dfs.c`.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/mup/dfs.h -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/mup/mup.c -->
# File Research: sources/windows/reactos/drivers/filesystems/mup/mup.c

This file implements the ReactOS Multi UNC Provider driver. It routes UNC opens to registered network redirectors, maintains known-prefix caching, supports provider registration, broadcasts mailslot opens, and fans out mailslot writes.

Global state includes locks for global data, prefix table, CCB list, and VCB access; provider, prefix, and master-query lists; a Unicode prefix table; a known-prefix timeout; provider count/order flags; DFS enablement; and the MUP device object.

Initialization:
- `MupInitializeData` creates resources/lists and initializes the prefix table.
- `MuppIsDfsEnabled` reads `DisableDfs` under the MUP service key; DFS is attempted unless explicitly disabled.
- `DriverEntry` initializes data, attempts DFS initialization, creates `\Device\Mup`, registers dispatchers, and initializes the VCB.

Provider management:
- Provider order is read from `Control\NetworkProvider\Order`.
- Each provider’s `NetworkProvider\DeviceName` is used to create unregistered provider records.
- `FSCTL_MUP_REGISTER_PROVIDER` registers a redirector, opens its device, stores object references, and inserts it in provider-order order.

Open routing:
- `MupCreate` treats empty root opens as MUP volume opens and named opens as redirected opens.
- `CreateRedirectedFile` first checks the known-prefix table. If a valid prefix is found, `MupRerouteOpen` rewrites the file object name to prepend the provider device path and returns `STATUS_REPARSE`.
- On a cache miss, it sends `IOCTL_REDIR_QUERY_PATH` to registered providers and waits through a master query context. Completion chooses the best provider by success, accepted-prefix length, and provider order, then caches accepted prefixes.

Mailslot handling:
- Mailslot paths are detected before regular redirector resolution.
- `BroadcastOpen` opens the mailslot against every provider that supports mailslots and attaches resulting CCBs under one MUP FCB.
- `MupForwardIoRequest` forwards writes to every CCB associated with the FCB, using lower IRPs and a master I/O context to complete the original IRP when all forwarded writes finish.

I/O forwarding:
- `BuildAndSubmitIrp` constructs lower write IRPs for buffered, direct, or neither I/O devices, copying stack parameters and installing a completion routine.
- Completion frees MDLs/buffers/lower IRPs, dereferences CCBs, and updates the master I/O context.

Cleanup/close:
- `MupCleanup` handles VCB cleanup, provider deregistration/close, and FCB cleanup.
- `MupClose` clears file-object contexts and dereferences VCB/FCB nodes.
- `MupUnload` deletes the MUP device, unloads DFS if enabled, and deletes resources.

Research notes:
- DFS is effectively disabled because `DfsDriverEntry` currently returns `STATUS_NOT_IMPLEMENTED`.
- Known-prefix timeout logic appears inverted in comments versus condition: the code reroutes when `ValidityTimeout < CurrentTime`, which normally means expired.
- Error selection for provider query failures uses `MupOrderedErrorList` to prefer more critical failures.
- The code uses many manual reference-count paths; provider, prefix, FCB, CCB, and master-context lifetimes are central to correctness.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/mup/mup.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/mup/mup.h -->
# File Research: sources/windows/reactos/drivers/filesystems/mup/mup.h

This is the private MUP header. It includes WDM/NTIFS, PSEH, MUP NDK types, section attributes, and DFS declarations.

It defines helper macros, allocation tag `TAG_MUP`, node type/status constants, and internal node structures:
- `MUP_VCB`: root MUP volume context and share access.
- `MUP_FCB`: MUP file context with associated file object and CCB list.
- `MUP_CCB`: per-provider open context for forwarded operations.
- `MUP_MIC`: master I/O context for fan-out write completion.
- `MUP_UNC`: registered or pending UNC provider state.
- `MUP_PFX`: cached accepted prefix and provider association.
- `MUP_MQC`: master query context for provider prefix-resolution fan-out.
- `FORWARDED_IO_CONTEXT` and `QUERY_PATH_CONTEXT`: per-lower-IRP contexts.

Research notes:
- The node header fields are repeated in every structure rather than embedded as a common base struct.
- `MUP_UNC` carries both registration metadata and opened device/file object references.
- Prefix nodes track whether the accepted-prefix buffer is externally allocated and whether the node is present in the prefix table.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/mup/mup.h -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/nfs/CMakeLists.txt -->
# File Research: sources/windows/reactos/drivers/filesystems/nfs/CMakeLists.txt

This build file defines the ReactOS NFSv4.1 mini-redirector driver module `nfs41_driver`.

It builds `nfs41_driver.c`, `nfs41_debug.c`, `nfs41_driver.h`, and `nfs41_debug.h`, includes headers from `dll/np/nfs`, defines `RDBSS_TRACKER`, and links against `ntoskrnl_vista`, `rdbsslib`, `rxce`, `copysup`, `memcmp`, PSEH, `ntoskrnl`, and `hal`.

Compiler-specific suppressions disable `-Wno-switch` for GCC/Clang and `-Wno-unused-value` for Clang. The module is installed under `reactos/system32/drivers` and registers `nfs41_reg.inf`.

Research notes:
- This is an RDBSS-based network mini-redirector, not a standalone local filesystem.
- The debug file in this group is auxiliary support for the broader NFS driver.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/nfs/CMakeLists.txt -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/nfs/nfs41_debug.c -->
# File Research: sources/windows/reactos/drivers/filesystems/nfs/nfs41_debug.c

This file implements debug and trace helpers for the ReactOS/Windows NFSv4.1 mini-redirector.

Core printing:
- `DbgP` and `print_error` format messages into fixed 512-byte buffers using `RtlStringCbVPrintfA` and emit via `DbgPrintEx`.
- Optional timestamp code is present behind `INCLUDE_TIMESTAMPS`.
- `dprintk` provides a Toaster-style formatted trace helper with a 1024-byte buffer and explicit debug flags.

Data dump helpers:
- `print_hexbuf` dumps buffers in hex.
- `print_basic_info`, `print_std_info`, `print_ea_info`, and `print_get_ea` print common file information structures.
- `print_file_object`, `print_fo_all`, `print_srv_call`, `print_net_root`, `print_v_net_root`, `print_fcb`, `print_srv_open`, and `print_fobx` print selected RDBSS object state, with many deeper fields compiled out under `#if 0`.

Operation decoders:
- `print_ioctl` decodes major device/filesystem/internal-control IRP categories.
- `print_fs_ioctl` decodes NFS driver IOCTLs such as invalidate cache, read/upcall, write/downcall, add/delete connection, get state, start, and stop.
- `print_driver_state` maps driver state constants to names.
- `print_file_information_class` and `print_fs_information_class` convert information-class IDs to strings.
- `opcode2string` maps NFS upcall/downcall opcodes such as mount, open, read, write, lock, directory query, ACL query, and ACL set.

Request diagnostics:
- `print_irp_flags`, `print_irps_flags`, and `print_nt_create_params` expand flags, create disposition/options, share access, desired access, and file attributes.
- `print_caching_level` decodes cache policy flags.
- `print_acl_args` prints selected security-information bits.
- `print_open_error` maps common open failure statuses to readable labels.
- `print_wait_status` explains wait results and optionally includes opcode, entry pointer, and transaction ID.

Research notes:
- This file has no core NFS protocol implementation; it is diagnostic support.
- Most helpers are gated by an `on` parameter, so callers can cheaply disable verbose output.
- The file bridges ReactOS compatibility by declaring UTF-8 conversion routines for older NTDDI targets.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/nfs/nfs41_debug.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/nfs/nfs41_debug.h -->
# File Research: sources/windows/reactos/drivers/filesystems/nfs/nfs41_debug.h

This header declares the NFSv4.1 driver debug helper API and tracing macros.

It declares debug printers, RDBSS object printers, IRP/IOCTL decoders, create-parameter and information-class decoders, hex dumping, opcode/status helpers, ACL argument printing, and `dprintk`.

Macros:
- `_DRIVER_NAME_` is `NFS4.1 Driver`.
- `DbgEn`, `DbgEx`, and `DbgR` wrap function entry/exit logging with PSEH exception handling.
- `DBG_ERROR`, `DBG_WARN`, `DBG_TRACE`, `DBG_INFO`, `DBG_DISP_IN`, and `DBG_DISP_OUT` define debug flag bits.
- `PNFS_TRACE_TAG` and `PNFS_FLTR_ID` identify the mini-redirector trace stream.
- `DbgEnter` and `DbgExit` emit dispatch entry/exit traces.

Research notes:
- The `DbgEx` macro assumes a local `status` variable exists.
- The macros use PSEH blocks, matching the driver’s ReactOS kernel build environment.
- This header is coupled to RDBSS types and NFS driver constants declared outside this file.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/nfs/nfs41_debug.h -->