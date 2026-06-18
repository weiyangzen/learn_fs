# Group Research: group_1793_udftools_sources_local_fs_udftools_wrudf_ide_pc_h_sources_local_fs__0f20e0254f06

<!-- BEGIN FILE RESEARCH: sources/local-fs/udftools/wrudf/ide-pc.h -->
# File Research: sources/local-fs/udftools/wrudf/ide-pc.h

## Purpose

`ide-pc.h` is the ATAPI/MMC command interface header used by `wrudf` for CD/DVD media access. It declares packed-ish C structures matching SCSI/MMC response and mode-page layouts, constants for disc/session/write modes, and function prototypes implemented by the lower-level `ide-pc.c` command layer outside this group.

## Main Definitions

The header defines device and media inquiry structures:

- `struct cdrom_inquiry` for SCSI INQUIRY data, including peripheral type constants `INQ_WORM` and `INQ_CDROM`.
- `struct cdrom_discinfo` for READ DISC INFORMATION, with disc/session status constants such as `DS_EMPTY`, `DS_APPENDABLE`, `DS_COMPLETE`, `SS_EMPTY`, `SS_APPENDABLE`, and `SS_COMPLETE`.
- `struct cdrom_trackinfo` for READ TRACK INFORMATION, carrying flags such as `fixpkt`, `packet`, `blank`, `rsrvd_trk`, next-writable-address validity, fixed-packet size, and track size.
- `struct cdrom_buffercapacity`, `struct cdrom_reccapacity`, and `struct cdrom_header` for buffer capacity, recorded capacity, and sector header reads.

It also declares MODE SENSE/SELECT page layouts:

- `mode_hdr` for the mode parameter header.
- `struct read_error_recovery_params` for the read/write error recovery page.
- `struct cdrom_cacheparams` for cache-control settings.
- `struct cdrom_writeparams` for write parameters, including write type, packet/fixed-packet selection, multisession mode, data block type, packet size, MCN/ISRC fields, and XA subheader bytes.
- `struct cdrom_capabilities` for CD/DVD read/write capability and mechanical status.

## Command Surface

The prototypes expose the command operations used by the wrudf code:

- Drive/media control: `blank`, `format`, `close_track_session`, `synchronize_cache`, `test_unit_ready`, `getDriveState`, `mediumRemoval`, `startStopUnit`, `set_cdspeed`.
- Metadata reads: `inquiry`, `read_discinfo`, `read_trackinfo`, `read_buffercapacity`, `read_reccapacity`, `read_header`.
- Data I/O: `readCD`, `writeCD`, and `verify` with an `MMC2`-dependent signature.
- Mode pages: `mode_sense`, `mode_select`, `get_writeparams`, `set_writeparams`, and `get_capabilities`.
- Error reporting: `fail`, `get_sense_data`, and `get_sense_string`.

## Role In This Group

`wrudf-cdrw.c` uses the disc/track/mode-page structures to classify media as CD-R or CD-RW, validate fixed-packet requirements, set write parameters, tune error recovery, and read/write packets. `wrudf-cdr.c` uses buffer-capacity and track-info calls for append-style CD-R writing and next-writable-address management. `wrudf.c` and command code rely on these wrappers indirectly through the I/O layer.

## Notable Details

The structures use implementation-defined bitfields and host integer types such as `u_int` and `u_short`, so their binary layout is compiler and endian sensitive. The surrounding code assumes Linux/GCC-style layout and often uses direct struct reads from device command buffers.

Several comments use C++ `//` comment syntax in a C header, so the code assumes a C99-or-compiler-extension build mode.
<!-- END FILE RESEARCH: sources/local-fs/udftools/wrudf/ide-pc.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/udftools/wrudf/wrudf-cdr.c -->
# File Research: sources/local-fs/udftools/wrudf/wrudf-cdr.c

## Purpose

`wrudf-cdr.c` implements the append-only CD-R path for `wrudf`. It manages the Virtual Allocation Table (VAT), writes new physical sectors at the drive's next writable address, reads logical data through the VAT mapping, verifies written CD-R data, and writes a new VAT file entry when finalizing.

## Main State

The file-local state is:

- `blockBuffer`: one 2048-byte read/verify buffer.
- `newVATindex`: next logical VAT entry to allocate.
- `sizeVAT`: allocated VAT byte size.
- `prevVATlbn`: physical block number of the previous VAT file entry.
- `CDRuniqueID`: exported unique ID from the VAT file entry, later copied into the logical volume header by `wrudf.c`.

It uses global state from `wrudf.h`, including `vat`, `device`, `devicetype`, `pd`, `ti`, `lastTrack`, `sectortype`, `ignoreReadError`, and `medium`.

## VAT Allocation And Addressing

`newVATentry()` ensures there is spare VAT capacity for the allocation entries plus VAT trailer data, grows the VAT by one 2048-byte block when needed, records the current next writable physical location relative to the partition start, and returns the new virtual logical block index.

`getNWA()` returns the next writable address. For disk images it uses file length divided by 2048. For devices it refreshes `ti` through `read_trackinfo()` and returns `ti.nwa` only if `ti.nwa_v` is set, otherwise `INVALID`.

`readCDR()` maps logical block plus partition to a physical block through `getPhysical()`, then reads either from a disk image by `lseek`/`read` or from optical media with `readCD()`. It suppresses sense logging when `ignoreReadError` is set.

## Writing

`writeHD()` writes one 2048-byte block to a disk-image physical block. `writeCDR()` writes one 2048-byte block at `getNWA()`, either through `writeHD()` for images or `writeCD()` for devices, and returns the physical block written.

`syncCDR()` flushes device cache for real devices. `writeHDlink()` writes seven link blocks to disk images after CD-R-style writes, emulating the link-block behavior that real packet writing leaves between variable packets.

## Verification And Bad-Block Handling

`verifyCDR()` verifies a just-written file entry and its data extents using strict read settings. It walks long allocation descriptors and reads data blocks that are physically after the file entry. On read failure it calls `flagError()` to split the affected extent into good and bad ranges. Bad ranges are represented by extents whose logical block number is zero, then later reassigned to future rewrite locations.

If data verification succeeds, `verifyCDR()` verifies the file entry itself up to three times. A failed file-entry verification causes it to write a replacement file entry and update the VAT entry for the file entry's virtual logical block.

After any data verification failures, it rewrites allocation descriptors so bad ranges point to future physical blocks after the current NWA. The caller can then rewrite only the defective data ranges and the updated file entry.

## VAT Read/Write

`readVATtable()` finds the previous VAT file entry near the end of the appendable track, validates that it is a VAT file entry, records its unique ID, allocates the in-memory VAT, and reads either embedded VAT data or VAT data extents.

`writeVATtable()` appends the VAT trailer regid (`UDF_ID_ALLOC` plus UDF revision and OS identifiers), creates a VAT file entry with type `ICBTAG_FILE_TYPE_VAT15`, writes VAT payload blocks followed by the file entry, and verifies the whole written sequence. It retries up to eight times before reporting a failed VAT rewrite.

## Cross-File Role

`wrudf-cmnd.c` calls `newVATentry()`, `writeCDR()`, `verifyCDR()`, `getMaxVarPktSize()`, and `writeHDlink()` while copying files and updating directories on CD-R media. `wrudf.c` calls `readVATtable()` during initialization and `writeVATtable()` during finalization.

## Notable Details

`flagError()` performs in-place extent-array splitting with `memmove()` expressions that depend on fixed available descriptor capacity. The function is tightly coupled to the file-entry allocation descriptor area and assumes enough room for splits.

The CD-R path depends on long allocation descriptors because file data is written in physical partition space while file entries are addressed through virtual VAT space.
<!-- END FILE RESEARCH: sources/local-fs/udftools/wrudf/wrudf-cdr.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/udftools/wrudf/wrudf-cdrw.c -->
# File Research: sources/local-fs/udftools/wrudf/wrudf-cdrw.c

## Purpose

`wrudf-cdrw.c` is the shared low-level I/O layer for rewritable UDF media, append-only CD-R media, and disk-image testing. For CD-RW it implements a small 32-sector packet buffer cache, space bitmap allocation, sparing-table support, descriptor checksum/CRC helpers, extent reads/writes, and device initialization/finalization.

## Packet Buffer Model

The file defines four normal packet buffers plus one special buffer:

- `struct packetbuf` tracks `inuse` bits, `dirty` bits, buffer number, packet start block, and a 32-sector memory buffer.
- `findBuf()` locates a cached packet by aligned packet start.
- `getFreePacketBuffer()` chooses a clean unused buffer, or writes a dirty unused buffer before reuse. If every buffer is in use, it returns `NULL` after printing a panic-style message.
- `readPacket()` reads a 32-sector packet from the device or disk image, applying sparing-table remapping.
- `writePacket()` writes a 32-sector packet, verifies real optical writes by strict reread, and creates a new sparing-table mapping on retry.

`readBlock()`, `dirtyBlock()`, `freeBlock()`, and `writeBlock()` expose block-sized operations over the packet cache. CD-R bypasses the cache and delegates reads to `readCDR()`.

## Space Allocation

`markBlock()` updates the UDF space bitmap and the free-space count stored in the LVID partition data. `ALLOC` clears a bitmap bit and decrements free count; `FREE` sets the bit and increments free count.

`getExtents()` allocates short allocation descriptors. For CD-R it returns a synthetic extent at the current append position. For CD-RW it scans `spaceMap->bitmap`, coalesces free blocks into up to 32 extents, and returns the byte length of the descriptor array.

`freeShortExtents()` and `freeLongExtents()` mark previously allocated short or long extents free. Long extents are required to belong to the writable partition.

`getUnallocSpaceExtent()` allocates from the Unallocated Space Descriptor, used primarily for extending the Logical Volume Integrity Descriptor sequence.

## Descriptor And Timestamp Helpers

`setChecksum()` computes a descriptor CRC over the descriptor body and computes the 16-byte UDF tag checksum with the checksum byte cleared.

`updateTimestamp()` fills the global UDF `timeStamp` from either current time or a provided `time_t` plus microsecond value, including local timezone offset and subsecond fields.

`readTaggedBlock()` reads a descriptor, tolerates all-zero non-UDF blocks and sparing-table blocks with tag identifier zero, verifies the tag checksum, verifies descriptor CRC, and returns the block pointer.

## Address Translation And Sparing

`getPhysical()` handles three address modes:

- `ABSOLUTE` returns the block number unchanged.
- A virtual partition maps through `vat[lbn]`.
- Other partitions add `pd->partitionStartingLocation`.

`lookupSparingTable()` maps packet starts through the sparing table when present. `newSparingTableEntry()` inserts a new sorted sparing entry, preserving the next available mapped location and marking the table dirty. `updateSparingTable()` writes all sparing-table copies listed in the sparable partition map without verification to avoid recursively changing the table.

## Extent I/O

`readExtents()` and `writeExtents()` read or write byte streams described by either short or long allocation descriptors. They walk descriptor chains, switch to the next descriptor at extent boundaries, and operate in 2048-byte block units.

These helpers are used for directory data, VAT payloads, and file data that is not embedded in a file entry.

## Initialization

`initIO()` detects whether the path is a regular file disk image or an optical device:

- Disk images are opened read-write and classified heuristically as CDR or CDRW based on the descriptor identifier at block 512.
- Optical devices are opened nonblocking read-only, checked with `CDROM_DRIVE_STATUS`, queried with `read_discinfo()` and `read_trackinfo()`, and classified by the erasable bit.
- CD-RW must use fixed 32-sector packets. CD-R must be variable-packet appendable with a valid next writable address.
- The function derives `trackStart`, `trackSize`, and `sectortype`, reads error-recovery and cache mode pages, and sets write parameters for either fixed-packet CD-RW or variable-packet CD-R.

For CD-RW, it allocates packet buffers and a 32-sector verification buffer. For all modes it allocates `blockBuffer`.

## Finalization

`closeIO()` writes any dirty unused CD-RW packet buffers, reports still-in-use or dirty buffers, frees packet and verification buffers, synchronizes real device cache, closes the device, and returns success.

## Notable Details

The code assumes 2048-byte logical blocks and 32-sector CD-RW packets throughout. Disk-image support is built into the same paths, including optional debug sparing.

Some checks compare `device` rather than `devicetype` against `DISK_IMAGE` in `setStrictRead()` and `syncCDR()` is implemented elsewhere with similar concerns. Since `DISK_IMAGE` is a sentinel devicetype, not a file descriptor, those branches are fragile.
<!-- END FILE RESEARCH: sources/local-fs/udftools/wrudf/wrudf-cdrw.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/udftools/wrudf/wrudf-cmnd.c -->
# File Research: sources/local-fs/udftools/wrudf/wrudf-cmnd.c

## Purpose

`wrudf-cmnd.c` implements the interactive shell commands for modifying a UDF volume: copying files/directories from the host filesystem, removing entries, creating/removing directories, changing the current UDF or host directory, and listing UDF or host contents. It also owns most in-memory `Directory` loading and dirty directory serialization.

## Copying Files

`copyFile()` imports one regular host file into a UDF directory:

- Opens the source file and prompts for overwrite if the destination FID exists.
- Creates a new FID and File Entry.
- Copies uid, gid, POSIX mode bits into UDF permission bits, setuid/setgid flags, size, and timestamps.
- For CD-R, uses long allocation descriptors, reserves a virtual file-entry VAT entry, writes the file entry first, then file data in variable packet chunks, syncs, and verifies with `verifyCDR()`.
- For CD-RW, allocates a short extent for the file entry, allocates short extents for file data from the space bitmap, writes the file entry and blocks through the packet-cache layer.
- Inserts the new FID into the destination directory and increments the LVID implementation-use file count.

CD-R file data descriptors point into the physical writable partition while the file entry itself is referenced through the virtual partition/VAT.

## Copying Directories

`copyDirectory()` recursively imports host directory contents when `OPT_RECURSIVE` is set. It skips `.` and `..`, uses `lstat()` so symlinks are not followed, creates or reuses destination directories, recursively imports child directories, and imports regular files with `copyFile()`.

It changes the process working directory while traversing and then changes back upward; `cpCommand()` later restores `hdWorkingDir`.

## Removing Entries

`deleteDirectory()` recursively deletes directory contents by reading the child directory, walking FIDs, deleting regular children with `deleteFID()`, recursively deleting directories, and deleting the directory FID when empty.

`rmCommand()` deletes files directly and deletes directories only with `OPT_RECURSIVE`. `rmdirCommand()` requires exactly one directory argument, verifies it is empty, rejects root directory removal, and then deletes the directory FID.

## Directory Loading

`readDirectory()` materializes a UDF directory into a `Directory` object:

- Reuses the single cached child directory under the parent when it already matches the requested ICB.
- Flushes a dirty cached directory before replacing it.
- Reads the directory file entry through `readTaggedBlock()`.
- If allocation descriptors are embedded in the ICB, copies FID bytes out of the file entry into `dir->data`.
- Otherwise reads directory data through `readExtents()`.
- On CD-RW, frees the old directory data extents after loading because rewritten directories will get fresh extents.

The design keeps at most one active child chain from root to current directory, rather than a general directory cache.

## Directory Serialization

`updateDirectory()` recursively flushes dirty child directories first, then serializes the current dirty directory:

- If all FIDs fit inside the file entry, it switches to `ICBTAG_FLAG_AD_IN_ICB`, embeds directory data, and updates FID tag locations to the directory ICB location.
- If external allocation is needed on CD-R, it uses long descriptors at the next append location and sets FID tag locations to future physical directory-data blocks.
- If external allocation is needed on CD-RW, it allocates short extents, builds a block list for tag-location assignment, and writes directory data through `writeExtents()`.
- It recomputes descriptor CRC lengths and checksums.
- It writes the directory file entry in place for CD-RW or appends a replacement file entry and updates VAT for CD-R.

## Directory Creation

`makeDir()` creates a child directory with:

- A parent/back-reference FID with `FID_FILE_CHAR_DIRECTORY | FID_FILE_CHAR_PARENT`.
- A directory file entry with embedded allocation descriptors.
- A forward FID inserted into the parent.
- CD-R virtual ICB allocation through `newVATentry()` or CD-RW physical file-entry allocation through `getExtents()`.
- Parent file-link-count increment and LVID directory-count increment.

It constructs or reuses the parent's cached child `Directory` structure and marks it dirty.

## Path Analysis And Commands

`analyzeDest()` resolves slash-separated UDF paths against `curDir`, supports absolute paths, `.`, `..`, trailing slash removal, and returns an `enum RV` state describing whether the final component is an existing directory, existing file, deleted entry, missing entry, or invalid path.

Command handlers:

- `cpCommand()` parses destination state, handles deleted/overwrite cases, imports each source argument, and supports recursive directory copy.
- `mkdirCommand()` creates one directory and changes into it.
- `cdcCommand()` changes current UDF directory by relying on `analyzeDest()`.
- `lscCommand()` lists UDF directory entries with type, uid/gid permissions, link count, information length, and decoded filename.
- `cdhCommand()` changes host working directory and updates `hdWorkingDir`.
- `lshCommand()` shells out to `ls -l` plus an optional argument.

## Notable Details

Several directory iteration loops use `fid` in the increment expression before assigning it inside the loop body; the intended pattern works after the first body assignment but is fragile C and easy to misread.

`copyFile()` treats `open()` returning file descriptor `0` as failure, although `0` is a valid descriptor. It should check `< 0`; as written, copying can fail incorrectly if stdin is closed.

`lshCommand()` builds a shell command with `strncat()` and `system()`, so host-path listing arguments are shell-interpreted.
<!-- END FILE RESEARCH: sources/local-fs/udftools/wrudf/wrudf-cmnd.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/udftools/wrudf/wrudf-desc.c -->
# File Research: sources/local-fs/udftools/wrudf/wrudf-desc.c

## Purpose

`wrudf-desc.c` contains helper routines for UDF File Identifier Descriptors and File Entries. It creates FIDs and file entries, finds named entries in a directory, inserts and physically removes FIDs from directory data, and deletes FIDs with associated file-entry/data-space cleanup.

## FID Removal And Deletion

`removeFID()` physically removes an FID from a directory's linear `dir->data` buffer. It computes the padded FID length, subtracts it from the directory file entry's `informationLength`, moves following bytes down, and marks the directory dirty.

`deleteFID()` performs semantic deletion:

- Reads the target file entry through `readTaggedBlock()`.
- Releases the target file-entry block from the packet cache with `freeBlock()`.
- If `fileLinkCount > 1`, decrements it and either marks the block dirty on CD-RW or writes a replacement file entry and updates VAT on CD-R.
- If this is the final link on CD-R, it decrements the parent directory link count for directories and marks the VAT entry invalid.
- If this is the final link on CD-RW, it decrements LVID file/directory counts, frees file data extents based on the file entry allocation descriptor type, and marks the file-entry block free.
- Finally removes the FID from the containing directory.

The function explicitly does not implement extended allocation descriptors.

## FID Lookup

`findFileIdentDesc()` encodes the requested locale filename into UDF dchars and scans the directory's FID stream until `informationLength` or a terminal entry. It skips parent entries, reports indirect entries as unimplemented, fails on unknown tag identifiers, and returns the first FID with matching encoded name bytes.

## File Entry Creation

`makeFileEntry()` allocates a zeroed 2048-byte block and initializes a regular-file UDF File Entry:

- Descriptor tag identity/version/serial.
- ICB strategy type and default regular file type.
- User read/write/delete/change/execute permissions plus group/other read/execute.
- Link count, access/modification/attribute timestamps.
- Implementation identifier.
- Unique ID from the logical volume header, post-incremented.

Callers specialize the returned file entry for directories, VAT entries, allocation descriptor mode, sizes, and checksums.

## FID Creation And Insertion

`makeFileIdentDesc()` allocates a zeroed FID buffer, initializes tag identity/version/serial, file version, and default ICB extent length. For non-parent entries it encodes the provided locale name into UDF dchars, falling back to a one-byte placeholder if encoding fails.

`insertFileIdentDesc()` computes padded FID length, sets descriptor CRC length, recomputes checksum, grows the directory data buffer in 2048-byte increments if needed, appends the FID bytes, updates the directory file entry's `informationLength`, and marks the directory dirty.

## Cross-File Role

`wrudf-cmnd.c` uses these helpers for all create, copy, delete, overwrite, directory lookup, and insertion operations. `wrudf-cdr.c` uses `makeFileEntry()` for VAT file entries. The helpers depend on globals initialized in `wrudf.c`, especially `lvd`, `lvid`, `pd`, `vat`, `medium`, and `entityWRUDF`.

## Notable Details

Deletion behavior differs sharply between CD-R and CD-RW: CD-R cannot reclaim physical space and instead invalidates VAT entries or appends replacement file entries, while CD-RW frees bitmap blocks and extents.

The commented-out partition check in `deleteFID()` suggests incomplete enforcement around writable-partition boundaries.
<!-- END FILE RESEARCH: sources/local-fs/udftools/wrudf/wrudf-desc.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/udftools/wrudf/wrudf.c -->
# File Research: sources/local-fs/udftools/wrudf/wrudf.c

## Purpose

`wrudf.c` is the main program for the interactive `wrudf` tool. It defines global process state, initializes the target UDF volume, opens the volume for modification, runs the command loop, and finalizes metadata updates before closing.

## Global State

The file owns key globals declared in `wrudf.h`:

- Device state: `devicename`, `device`, `devicetype`, `medium`, and `ignoreReadError`.
- Command parser state: `line`, `cmndc`, `cmndvSize`, `cmndv`, and `options`.
- Descriptor discovery bitmask `found`.
- Directory state: `rootDir`, `curDir`, and global `timeStamp`.
- UDF descriptors/extents: main/reserve/next volume descriptor sequence extents, logical volume integrity sequence state, `pd`, `lvd`, `usd`, `spaceMap`, `lvid`, `fsd`, `st`, `vat`, and `virtualPartitionNum`.
- Dirty flags for space bitmap, USD, and sparing table.
- `entityWRUDF`, the implementation identifier written into metadata.

## Initialization Flow

`initialise()` begins by calling `initIO()`, then reads and validates the UDF Volume Recognition Sequence from blocks 16 through 255, accepting `BEA01`, `NSR02`, and `TEA01`.

It locates the Anchor Volume Descriptor Pointer:

- CD-R requires an AVDP at block 512.
- Other media try block 256, then `trackSize - 1`, then `trackSize - 256`.

It reads the Volume Descriptor Sequence, following `TAG_IDENT_VDP` continuations, selecting prevailing descriptors by volume descriptor sequence number:

- Primary Volume Descriptor presence is noted.
- The writable Partition Descriptor is stored for rewritable or write-once access types.
- The Logical Volume Descriptor is stored.
- The Unallocated Space Descriptor is stored when present.

The code requires a Logical Volume Descriptor, Partition Descriptor, and 2048-byte logical block size.

## Partition Maps And VAT

`initialise()` walks LVD partition maps:

- A sparable partition map loads the first sparing table copy and counts used entries.
- A virtual partition map records `virtualPartitionNum`.

For CD-R, a virtual partition map is mandatory and `readVATtable()` loads the VAT. For non-CD-R media, an Unallocated Space Descriptor is mandatory.

## Fileset, Space Bitmap, And Integrity Sequence

The File Set Descriptor sequence is read from `lvd->logicalVolContentsUse`, and the prevailing FSD is copied. The unallocated space bitmap is loaded from the partition header descriptor when present.

The user is prompted to confirm updates to the decoded file set identifier. After confirmation, the Logical Volume Integrity Descriptor sequence is read, following continuation extents if present. A closed CD-R volume is rejected.

For CD-R, the logical volume header unique ID is restored from the VAT file entry's unique ID. For CD-RW, if the LVID is already open, the user is prompted before proceeding.

For rewritable media, the code reserves/sets up the next LVID location, marks the current LVID open, writes it into the packet cache, and records a continuation extent if the integrity sequence is near exhaustion.

Finally it creates the root `Directory` structure and loads the root directory with `readDirectory()`.

## Finalization

`finalise()` flushes dirty directories first. Then:

- On CD-R, it writes a new VAT table with `writeVATtable()`.
- On CD-RW, it rewrites the space bitmap if dirty, writes sparing tables if dirty, writes a closed LVID, writes a terminating descriptor, and rewrites dirty USD data in both main and reserve volume descriptor sequences.

It then calls `closeIO()` and frees allocated descriptor/global buffers.

## Command Parsing

`parseCmnd()` tokenizes an input line in place, recognizes `cp`, `rm`, `mkdir`, `rmdir`, `lsc`, `lsh`, `cdc`, `cdh`, `quit`, `exit`, and `help`, and rejects ambiguous `cd`/`ls` in favor of explicit harddisk or compact-disc commands.

It supports double-quoted arguments in a limited way, parses `-f` and `-r` options into the global `options` bitmask, removes option entries from `cmndv`, and returns a command enum or error code.

## Main Loop

`main()` sets locale, prints version, chooses `/dev/cdrom` unless one device/image argument is supplied, tries to raise priority, records the current host working directory, initializes the volume, and enters an interactive prompt loop.

The prompt is built from the current UDF directory chain. Each parsed command dispatches to the corresponding command handler in `wrudf-cmnd.c`. Return values are translated into user-facing messages. `quit` or `exit` breaks the loop, frees `hdWorkingDir`, and calls `finalise()`.

## Notable Details

The program is intentionally interactive and asks for confirmation before modifying the volume. It supports disk images and real optical media through the same global I/O interfaces.

`parseCmnd()` mutates the input line and has limited quote handling; it does not implement escaping. The readline and non-readline paths differ in line storage but share the same parser.
<!-- END FILE RESEARCH: sources/local-fs/udftools/wrudf/wrudf.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/udftools/wrudf/wrudf.h -->
# File Research: sources/local-fs/udftools/wrudf/wrudf.h

## Purpose

`wrudf.h` is the central internal header for the `wrudf` program. It includes UDF/ECMA structure headers, declares global state shared by all wrudf source files, defines command/result enums and option bits, defines the in-memory directory cache structure, and declares cross-file functions.

## Included Interfaces

The header includes:

- Standard time/string/integer headers.
- `ecma_167.h`, `osta_udf.h`, and `libudffs.h`, which provide the UDF descriptor structures, constants, CRC/string helpers, and allocation descriptor types used throughout these files.

It defines `struct generic_desc` as a common prefix for tagged descriptors with `descTag` and `volDescSeqNum`.

## Shared Global State

The header declares globals for:

- Host working directory: `hdWorkingDir`.
- Device and mode: `ignoreReadError`, `device`, `devicetype`, `DISK_IMAGE`, `medium`, and `trackSize`.
- Command input: `line`, `cmndc`, `cmndv`, and `options`.
- Dirty metadata flags: `spaceMapDirty`, `usdDirty`, `sparingTableDirty`.
- Loaded UDF metadata: `lvd`, writable partition `pd`, `virtualPartitionNum`, `vat`, `usd`, `spaceMap`, `lvid`, `fsd`, `usedSparingEntries`, and `st`.
- Current implementation and timestamp: `entityWRUDF` and `timeStamp`.

The medium enum distinguishes `CDR` and `CDRW`; disk images are represented separately by `devicetype == DISK_IMAGE` while still emulating either medium behavior.

## Result And Command Enums

`enum RV` standardizes command return states such as `CMND_OK`, `CMND_FAILED`, bad argument counts, invalid directories, existing/deleted files or directories, permission denial, and directory/file type mismatches.

`enum CMND` assigns command IDs for `cp`, `rm`, `mkdir`, `rmdir`, compact-disc and harddisk list/change-directory operations, and quit.

Option bits include:

- `OPT_DUMMY`
- `OPT_FORCE`
- `OPT_RECURSIVE`

Only recursive behavior is materially used in this group.

## Directory Structure

`Directory` is the in-memory representation of a loaded UDF directory:

- `parent` and `child` model a single active directory chain.
- `dataSize` and `data` hold the linear FID byte stream.
- `icb` identifies the directory file entry.
- `name` is the decoded/local directory name.
- `dirDirty` tracks whether directory data/file entry must be rewritten.
- `fe[2048]` stores a copy of the directory's file entry block.

`rootDir` and `curDir` point into this chain.

## Cross-File Function Contracts

The header groups declarations by implementation file:

- `wrudf-cmnd.c`: directory update/read and command handlers.
- `wrudf-desc.c`: FID/FileEntry creation, lookup, insertion, and deletion.
- `wrudf-cdrw.c`: bitmap/extent allocation, timestamp/checksum helpers, address translation, sparing-table update, block and extent I/O, and device open/close.
- `wrudf-cdr.c`: VAT allocation, next-writable-address helpers, CD-R read/write/verify, and VAT table read/write.
- `ide-pc.h`: `fail()` declaration, with the detailed ATAPI/MMC command interface included separately by implementation files that need it.

## Notable Details

The header exposes many mutable globals rather than encapsulating volume/session state. This matches the small interactive utility design but tightly couples all source files and makes reentrancy or concurrent operation impossible.

`ABSOLUTE` uses `0xFFFF` as a sentinel partition number even though the comment notes it can be a valid UDF partition number.
<!-- END FILE RESEARCH: sources/local-fs/udftools/wrudf/wrudf.h -->