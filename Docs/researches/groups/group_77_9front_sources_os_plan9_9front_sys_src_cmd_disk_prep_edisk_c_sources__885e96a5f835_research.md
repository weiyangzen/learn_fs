# Group Research: group_77_9front_sources_os_plan9_9front_sys_src_cmd_disk_prep_edisk_c_sources__885e96a5f835

Scope: `Docs/research_subset_a.md`, source tree `sources/os/plan9/9front`.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/disk/prep/edisk.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/disk/prep/edisk.c

## Purpose
Implements `disk/edisk`, the GPT partition-table editor. It plugs GPT-specific parsing, mutation, printing, and writeback into the shared partition editor in `edit.c`.

## Key Behavior
- Defines on-disk GPT header and entry layouts, little-endian helpers, CRC32 calculation, UUID formatting/generation, GPT type-name mapping, and attribute flag formatting.
- Opens a disk or regular file, optionally overrides sector size, reads an existing GPT unless `-b` requests a blank table, and then runs the shared interactive command loop.
- Validates the protective MBR, detects dangerous hybrid MBR/GPT layouts, and refuses to edit when non-protective DOS partitions are present.
- Reads primary or backup GPT headers, validates header/table CRCs, restores a missing/mismatched counterpart header, and builds sorted in-memory `Gptpart` entries.
- Creates a blank GPT with 128 entries, a protective MBR, new disk GUID, primary header at LBA 1, backup header at the last LBA, and table areas around both headers.
- Writes primary and backup partition entry arrays, recalculates table/header CRCs, flushes changed cached sectors, and attempts to roll back already-written sectors on write failure.
- Implements auto partitioning that adds an ESP capped at 550 MB and a Plan 9 partition in the largest free span when missing.
- Provides GPT-specific editor commands: `t` sets partition type, `f` toggles GPT attributes, and `l` sets the UTF-16LE partition label.
- Prints user-facing summaries with attribute letters, GPT slot names (`pN`), LBAs, byte-scaled sizes, type aliases, and labels.
- Generates unique Plan 9 kernel partition names from GPT type aliases for `ctl` updates, avoiding duplicate names by suffixing.

## Interfaces And Dependencies
- Uses the shared `Edit` API from `edit.h`: `.add`, `.del`, `.ext`, `.help`, `.okname`, `.sum`, `.write`, and `.printctl`.
- Uses Plan 9 disk helpers from `<disk.h>` such as `opendisk()` and disk geometry/ctl fields.
- Uses `<mp.h>` and `<libsec.h>` for random UUID generation through `genrandom()`.
- Updates the active kernel disk partition table via `ctldiff()` after successful GPT writes.

## Notes
This file is deliberately conservative around MBR/GPT coexistence and backup-header recovery. The cached-sector writeback path is important because GPT writes span multiple sectors and a partial write would leave a conflicting table pair.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/disk/prep/edisk.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/disk/prep/edit.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/disk/prep/edit.c

## Purpose
Provides the shared interactive partition editing engine used by `prep`, `fdisk`, and `edisk`.

## Key Behavior
- Reads commands from stdin with `getline()`, warning on EOF if changes are unwritten.
- Maintains an ordered in-memory partition list, supports lookup by name, duplicate-name checks, insertion sorted by start offset, and deletion.
- Implements generic commands: set/display dot (`.`), add (`a`), delete (`d`), help (`h`/`?`), print table (`p`), print/update kernel ctl commands (`P`), write (`w`), and quit (`q`).
- Uses `parseexpr()` for start/end expressions with dot, end, total size, and unit scaling supplied by each caller.
- Validates add ranges against current partitions and limits default end prompts to the next partition boundary.
- Delegates storage-specific behavior through callbacks in `Edit`: command extensions, table writes, summaries, kernel partition naming, and name validation.
- Reads the current Plan 9 disk `ctl` partition list, filters to the disk region being edited, and builds `ctlpart` entries for diffing.
- `ctldiff()` deletes changed kernel partitions and emits `part name start end` lines for current in-memory partitions, applying the disk offset.

## Interfaces And Dependencies
- Exposes `getline`, `runcmd`, `findpart`, `addpart`, `delpart`, `editwrite`, `editctlprint`, `ctldiff`, `emalloc`, and `estrdup`.
- Depends on `edit.h` for `Part`/`Edit` and on `<disk.h>` for `Disk`.
- Relies on an external `parseexpr()` implementation declared in `edit.h`.

## Notes
Overlap detection currently formats an error string but does not return it in `addpart()`, so callers primarily prevent overlaps before insertion. `ctldiff()` is the bridge between on-disk table edits and the live `/dev/sd*/ctl` namespace.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/disk/prep/edit.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/disk/prep/edit.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/disk/prep/edit.h

## Purpose
Defines the shared partition editor data model and function prototypes.

## Key Contents
- `Part` holds editor-visible partition metadata: display name, kernel ctl name, logical start/end, optional ctl start/end overrides, and changed flag.
- `Edit` holds the active `Disk`, current kernel ctl partitions, current editable partitions, callback table, unit label, dot/end/unit sizing state, and private command-loop flags.
- `Maxpart` caps the generic editor’s partition arrays at 32 entries.
- Declares the shared command loop, partition list helpers, expression parser, kernel ctl diff writer, and allocation helpers.

## Notes
The header is intentionally callback-oriented so MBR, GPT, and Plan 9 partition table tools can share one interactive editor while preserving their own on-disk formats.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/disk/prep/edit.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/disk/prep/fdisk.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/disk/prep/fdisk.c

## Purpose
Implements `disk/fdisk`, the DOS/MBR partition-table editor, including primary and extended partition chains.

## Key Behavior
- Parses options for auto Plan 9 partitioning, blank mode, file mode, read-only mode, sector-size override, CHS verbosity, print mode, and write mode.
- Uses disk geometry to expose editor units as cylinders while preserving sector offsets for kernel `ctl` commands.
- Reads the MBR signature, recursively reads extended boot records, records recovery copies of every table touched, and rejects GPT protective MBRs with a pointer to `disk/edisk`.
- Models entries as `Dospart`, combining `Part` with raw MBR fields, EBR start/type, and primary-vs-secondary state.
- Auto-partitioning finds the largest usable gap with room in primary slots, creates an active Plan 9 partition if no primary is active, and skips LBA 0/track boot sectors.
- Enforces DOS slot constraints: at most four primary-slot consumers, with secondary partitions represented by extended partition chains.
- Provides fdisk-specific commands: `A` sets the active primary partition, `t` changes the DOS partition type, and `R` restores original partition tables and exits.
- Writes primary entries and nested EBRs, recalculating CHS fields and LBA-relative fields for each table.
- On write failure, restores all saved original table sectors and attempts to restore the kernel partition namespace.
- Prints summaries with changed/active markers, cylinder ranges, byte-scaled sizes, and DOS type names.

## Interfaces And Dependencies
- Uses `edit.c` through an `Edit` callback table for generic command handling and `ctldiff()` for live partition updates.
- Uses `<disk.h>` disk geometry and raw fd/wfd/ctlfd fields.
- Uses Plan 9 FIS constants indirectly only through included disk environment; the MBR format is local to this file.

## Notes
This file treats error recovery as part of the write path: `diskfatal()` invokes `recover()` after any table write has occurred. The code keeps historical CHS compatibility even though LBA fields are the operative values.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/disk/prep/fdisk.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/disk/prep/prep.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/disk/prep/prep.c

## Purpose
Implements `disk/prep`, the editor for Plan 9 partition tables stored in sector 1 of a Plan 9 partition.

## Key Behavior
- Opens a disk, optionally overrides sector size, checks that sector 1 is not a FAT boot sector, and reads an existing text partition table unless blank mode is selected.
- Uses the shared editor with sector units and simple partition names, rejecting control characters, `/`, and NUL-like bytes in names.
- Reads/writes lines of the form `part name start end` from/to one sector at disk sector 1.
- Saves the original sector and original in-kernel partitions so failed writes can be restored.
- Supports automatic subpartition layouts selected with repeated `-a partname`, using weighted allocation plus min/max constraints for known names such as `9fat`, `nvram`, `fscfg`, `fs`, `fossil`, `arenas`, `isect`, `bloom`, `swap`, and cache variants.
- Aligns automatic partitions to physical-sector stride using disk physical alignment metadata.
- Prevents non-`9fat` partitions from overlapping the Plan 9 boot sector/partition-table area at the start of the region.
- Writes the new text table and calls `ctldiff()` to update the live Plan 9 disk partition namespace.

## Interfaces And Dependencies
- Uses `edit.c` callbacks for add/delete/write/summary/name checks.
- Uses `<disk.h>` for `Disk`, sector size, physical sector size, offset, and alignment metadata.
- Uses the kernel disk `ctl` file through `ctldiff()`.

## Notes
The FAT boot-sector guard protects users from accidentally running `prep` on a whole FAT-containing disk instead of a Plan 9 partition. Automatic layout allocation is order-sensitive because the `autox` array is also the desired on-disk order.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/disk/prep/prep.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/disk/qcowfs.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/disk/qcowfs.c

## Purpose
Provides a small 9P server exposing a qcow2 image as a single writable `data` file, and can create a new qcow2 v3 image.

## Key Behavior
- Defines qcow2 header fields, big-endian serialization helpers, cluster/refcount/L1/L2 constants, and a Plan 9 `ftruncate()` wrapper using `dirfwstat`.
- `qc2create()` creates a qcow2 v3 image with 64 KiB clusters, an L1 table, refcount table/block, and initial refcounts for metadata clusters.
- `qc2open()` reads and validates qcow2 v2/v3 headers, rejects unsupported refcount order, loads and byte-swaps the L1 table, and records the current file length as allocation end.
- `xlate()` maps virtual offsets to physical image offsets through L1/L2 tables, returning zero for unallocated clusters and rejecting compressed clusters.
- `mkcluster()` allocates L2 tables and data clusters, updates L1 entries, refcounts, and optionally copies data from an existing physical cluster before write.
- `fsread()` serves reads by translating each cluster; holes read as zeroes and reads are capped at virtual disk size.
- `fswrite()` rejects writes past the virtual disk size and allocates clusters for holes or non-inplace mappings before writing.
- `main()` accepts `-n size` to create, `-m mntpt`, `-s srv`, and `-D` for 9P tracing, then posts/mounts a 9P tree containing `data`.

## Interfaces And Dependencies
- Uses Plan 9 `thread` and `9p` libraries, with `Srv.read`/`Srv.write` handlers.
- Exposes only one file named `data` with length equal to qcow2 virtual disk size.
- The `Disk.base` field and `copy_cluster()` support copy-on-write shape but this program opens only one image as its own base for writes.

## Notes
Feature support is intentionally narrow: no compression, no encryption handling beyond storing the header value, no snapshots, no backing-file opening, and only 16-bit refcounts. Allocation/refcount updates are fatal on I/O failures rather than recoverable 9P errors.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/disk/qcowfs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/disk/rd9660.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/disk/rd9660.c

## Purpose
Debugging tool that reads an ISO 9660 image and dumps primary/Joliet volume descriptor, root directory, and path table information.

## Key Behavior
- Defines ISO volume descriptor, directory record, and path table record layouts.
- Installs custom formatters for little-endian, big-endian, dual-endian numeric fields, ISO directory records, path records, ASCII text fields, and Joliet UCS-2 text fields.
- Reads 2048-byte sectors through `Biobuf`, starting at sector 16 for the primary volume descriptor and sector 17 for the Joliet descriptor.
- Prints descriptor fields including IDs, volume size, block size, path table locations, root directory, publisher/preparer/application strings, timestamps, and filesystem version.
- Dumps the first five root directory records and the full little-endian and big-endian path tables.
- Switches text decoding between ASCII and Joliet rune decoding before dumping each descriptor.

## Interfaces And Dependencies
- Uses Plan 9 libc/Bio and `<disk.h>` for conventions.
- Command line is `rd9660 file`; it does not mount or validate a filesystem beyond direct structure decoding.

## Notes
The tool is explicitly for debugging and assumes fixed sector size 2048. It is useful for inspecting image metadata but not a general ISO reader.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/disk/rd9660.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/disk/sacfs/mksacfs.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/disk/sacfs/mksacfs.c

## Purpose
Builds a SAC filesystem image from a directory tree or single file.

## Key Behavior
- Accepts `-o output`, optional `-b blocksize`, and `-u` to force uncompressed blocks.
- Writes a `SacHeader` followed by a root `SacDir`, then recursively emits file/directory block tables and data blocks.
- Stores all multi-byte metadata using big-endian `putl()` fields defined by the SAC format headers.
- For regular files, writes an offset table of block starts plus a final end offset, compressing each block with `sac()` when it saves space.
- Marks compressed blocks by storing the block offset as a negative value in the offset table.
- For directories, recursively builds child `SacDir` records, packs them into blocks, optionally compresses each directory block, and stores directory length as entry count.
- `setsd()` copies names/owners/groups, assigns monotonically increasing qid values with directory mode bits, and records mode/time/length/block-table offset.

## Interfaces And Dependencies
- Uses `sac.h` for `sac()` and `sacfs.h` for `SacHeader`/`SacDir` layouts.
- Uses Plan 9 `Dir`, `dirreadall`, and normal filesystem reads.

## Notes
The `seen()` cache is implemented but not used in traversal, so hard-link/cycle suppression is not active. The program currently requires `-o`; the temp-file path is left as a fatal “still to do” branch.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/disk/sacfs/mksacfs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/disk/sacfs/sac.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/disk/sacfs/sac.c

## Purpose
Implements the SAC block compressor used by `mksacfs`.

## Key Behavior
- Compresses one block with a Burrows-Wheeler transform driven by `ssortbyte()`, move-to-front encoding, zero-run encoding, and custom length-limited Huffman coding.
- Emits the BWT primary index, a compact character-presence map, Huffman table descriptions, and encoded symbol stream into a caller-supplied destination buffer.
- Tracks output bounds with `bitput()` and returns `-1` through `longjmp` when compressed data would exceed the source block size.
- Encodes runs of zero MTF symbols with a binary run-length representation using `ZBase`/`LitBase`.
- Builds Huffman code lengths with a fast in-place minimum-redundancy path when possible, falling back to a package-merge style length-limited algorithm for `MaxHuffBits`.
- Serializes Huffman tables with nested Huffman coding over move-to-front code lengths.
- Includes local sorting for leaf frequency maps and canonical Huffman code assignment.

## Interfaces And Dependencies
- Public entry point is `int sac(uchar *dst, uchar *src, int n)`.
- Uses `ssortbyte()` from `ssort6.c` declared in `ssort.h`.
- Shares constants and the corresponding decompressor format with `unsac.c`.

## Notes
The compressor mutates global static encoder state for one block at a time and is not reentrant. Compression failure is expected and simply causes the image builder to store the original block.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/disk/sacfs/sac.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/disk/sacfs/sac.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/disk/sacfs/sac.h

## Purpose
Declares the SAC compressor and decompressor entry points.

## Key Contents
- `int sac(uchar *dst, uchar *src, int blocksize);`
- `int unsac(uchar *dst, uchar *src, int n, int nsrc);`

## Notes
This header is the minimal API shared by the image builder, filesystem server, compressor, and decompressor.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/disk/sacfs/sac.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/disk/sacfs/sacfs.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/disk/sacfs/sacfs.c

## Purpose
Implements a read-only 9P server for SAC filesystem images.

## Key Behavior
- Loads the entire SAC image into memory, validates magic and length, records block size, initializes the root `SacDir`, and allocates a small decompressed-block cache.
- Can serve over stdio (`-i`), post a service file (`-s`), or mount at a mountpoint (`-m`, default `/n/c:`).
- Implements legacy 9P request handlers for attach, clone, walk, clwalk, open, read, clunk, stat, session, flush, and erroring write/create/remove/wstat as read-only.
- Maintains `Fid` objects with user, qid, open state, and a copy of the current `Sac` directory entry.
- Tracks parent paths with reference-counted `Path` nodes so `..` can reconstruct parent directory entries from stored directory blocks.
- `loadblock()` reads uncompressed blocks directly or decompresses negative-offset blocks with `unsac()`, caching decompressed results by image offset.
- `saclookup()` performs directory lookup, currently using a linear search over directory entries; a binary-search implementation remains disabled in unreachable code.
- `sacdirread()` converts directory entries into Plan 9 `Dir` records, with SAC directory length interpreted as number of entries.
- Permission checks are simple owner/group/other mode comparisons, assuming each group name corresponds directly to a user.

## Interfaces And Dependencies
- Uses legacy `<fcall.h>` message conversion and direct pipe/service-file mounting rather than the newer `9p` library.
- Uses `sacfs.h` on-disk structures and `unsac()` from `unsac.c`.

## Notes
The server is intentionally read-only and memory-resident. It trusts the image more than a hardened filesystem would: malformed offsets or directory metadata can lead to fatal errors during block load/decompression.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/disk/sacfs/sacfs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/disk/sacfs/sacfs.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/disk/sacfs/sacfs.h

## Purpose
Defines the on-disk SAC filesystem metadata structures.

## Key Contents
- `Magic = 0x5acf5` identifies SAC images.
- `NAMELEN = 28` fixes stored name, uid, and gid field lengths.
- `SacDir` stores fixed-size name/uid/gid plus big-endian qid, mode, atime, mtime, length, and block-table offset fields.
- `SacHeader` stores magic, total image length, block size, and an MD5 field.

## Notes
Although `SacHeader.md5` exists in the format, the builder and server in this group do not compute or validate it.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/disk/sacfs/sacfs.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/disk/sacfs/ssort.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/disk/sacfs/ssort.h

## Purpose
Declares suffix sorting routines used by the SAC compressor.

## Key Contents
- `ssortbyte()` computes a suffix array for byte buffers with a unique end marker and returns the BWT identity permutation index.
- `ssort()` sorts integer alphabets and can optionally compute shared-prefix lengths.

## Notes
The implementation lives in `ssort6.c` and is tailored for compression preprocessing.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/disk/sacfs/ssort.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/disk/sacfs/ssort6.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/disk/sacfs/ssort6.c

## Purpose
Implements suffix-array sorting primitives used to compute the Burrows-Wheeler transform for SAC compression.

## Key Behavior
- `ssort()` sorts integer sequences with dense alphabets, using bucket labeling, iterative doubling, and optional shared-prefix interval tracking.
- `ssortbyte()` specializes suffix sorting for byte buffers, bucketed by two-byte prefixes and with a unique end-of-string marker lower than all input bytes.
- Returns the identity permutation index used by the compressor as the BWT primary index.
- Uses `BUCK` high-bit markers to represent unresolved buckets during iterative refinement.
- `ssortit()` repeatedly refines buckets using successor labels at increasing offsets until all suffixes are ordered.
- Optional shared-length support uses `lift()` and `sharedlen()` with a compact auxiliary tree.
- Includes a custom quicksort/insertion-sort hybrid (`qsort2`) specialized for sorting permutation entries by successor label, with median-of-three/pseudomedian pivoting.

## Interfaces And Dependencies
- Exports `ssort()` and `ssortbyte()` declared in `ssort.h`.
- Operates on caller-supplied arrays for output permutation and optional shared-length data.

## Notes
This is performance-oriented compression support code rather than a general library; several error returns indicate bad input alphabet shape or allocation failure.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/disk/sacfs/ssort6.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/disk/sacfs/unsac.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/disk/sacfs/unsac.c

## Purpose
Implements SAC block decompression, the inverse of `sac.c`.

## Key Behavior
- `unsac()` decodes one compressed block from a source buffer into a fixed-size destination block.
- Reads the BWT primary index and character-presence map, reconstructs the initial move-to-front alphabet, decodes Huffman tables, and then decodes the symbol stream.
- Uses an optimized MTF list with comb indices for faster indexed removal/move-to-front operations.
- Reverses the custom zero-run encoding used by the compressor.
- `hdecblock()` combines Huffman decode, move-to-front decode, character counting, and LF-mapping predecessor construction.
- Reconstructs the original byte order by walking predecessor links backward from the BWT primary index.
- Builds canonical Huffman decoding tables including flat prefix tables for fast short-code decoding.
- Uses `setjmp`/`longjmp` for corruption/allocation/EOF failures and returns `-1` to the caller.

## Interfaces And Dependencies
- Public entry point is `int unsac(uchar *dst, uchar *src, int n, int nsrc)`.
- Shares format constants with `sac.c` through duplicated local enums and `sac.h`.
- Called by `sacfs.c` when a block-table offset is negative.

## Notes
The decompressor prints some corruption messages via `fatal()` before jumping back. It assumes the caller knows the uncompressed block size and compressed byte length from the SAC block offset table.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/disk/sacfs/unsac.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/disk/smart/ata.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/disk/smart/ata.c

## Purpose
Implements ATA/SATA SMART probing, enabling, and status checks for `disk/smart`.

## Key Behavior
- Defines ATA passthrough request/reply structures matching Plan 9 sd raw command handling.
- `issueata()` writes an ATA command wrapper, performs the requested data phase, reads the returned status FIS, and tolerates non-ATA kernels during probes.
- `issueatat()` builds common ATA commands from a table: NOP, identify, identify packet, SMART, and signature.
- `ataprobe()` reads the device signature, runs identify, extracts features with FIS helpers, and succeeds only when SMART is advertised.
- `smartfis()` and `smartrsfis()` build SMART enable and return-status FIS commands.
- `ataenable()` enables SMART with subcommand `0xd8`.
- `atastatus()` issues SMART return status and reports `normal` when returned cylinder values are `0x4f/0xc2`, otherwise `threshold exceeded`.

## Interfaces And Dependencies
- Uses `<fis.h>` helpers and embeds `Sfis` in `Sdisk` from `smart.h`.
- Called through the `Dtype` dispatch table in `smart.c`.

## Notes
The implementation is specific to Plan 9 sd ATA passthrough conventions and treats many transfer failures during probing as “not this transport” rather than fatal.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/disk/smart/ata.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/disk/smart/scsi.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/disk/smart/scsi.c

## Purpose
Implements SCSI health probing, enabling, and status checks for `disk/smart`.

## Key Behavior
- Builds SCSI CDBs for test-unit-ready, request-sense, mode-sense(10), and mode-select(10).
- `issuescsi()` writes the CDB, performs the data phase, reads sd status, and on nonzero status issues request sense to capture detailed sense bytes.
- `scsiprobe()` verifies SCSI command support with TUR and confirms the Informational Exceptions mode page (`0x1c`) is readable.
- `scsienable()` writes mode page `0x1c` to enable background functions, warnings, logging, and request-sense-only reporting.
- `scsistatus()` requests sense and reports `normal` when ASC/ASCQ are zero, otherwise maps them through `scsierror()`.

## Interfaces And Dependencies
- Uses Plan 9 scuzz SCSI definitions from `/sys/src/cmd/scuzz/scsireq.h`.
- Called through `smart.c`'s `Dtype` dispatch table.

## Notes
This path uses SCSI informational exceptions rather than ATA SMART return-status semantics. Sense tracing code exists but is disabled.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/disk/smart/scsi.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/disk/smart/smart.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/disk/smart/smart.c

## Purpose
Main program for periodic SMART/health monitoring across ATA and SCSI disks.

## Key Behavior
- Supports explicit disk paths or auto-probing `/dev/sdctl`; `-p` probes in addition to explicit paths, `-a` logs all devices, `-t` runs in test/foreground mode, and `-v` enables verbose stderr output.
- Opens each candidate `path/raw`, tries ATA and SCSI probe/enable dispatch entries, and records supported disks in a linked list.
- Periodically checks each disk at `Checksec` intervals, reopening only for the check and closing afterward.
- Logs prolonged open failures, health status changes, repeated failures after a relog interval, and optionally all new/status messages.
- In test mode, exits after one run with failure status if any disk reports an error.
- Uses `/dev/sdctl` controller names to probe `/dev/<controller><hex-unit>` candidates until devices stop existing.

## Interfaces And Dependencies
- Uses `Dtype` implementations from `ata.c` and `scsi.c`.
- Uses Plan 9 `syslog()` unless in test mode.

## Notes
The program is a long-running monitor by default, sleeping 30 seconds between scheduler passes while each disk has a 10-minute check interval.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/disk/smart/smart.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/disk/smart/smart.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/disk/smart/smart.h

## Purpose
Shared declarations for the SMART monitor and transport-specific implementations.

## Key Contents
- Defines disk transport types (`Tscsi`, `Tata`) and status constants.
- `Dtype` dispatch table entries hold transport name plus probe, enable, and status callbacks.
- `Sdisk` stores linked-list state, active transport, fd, embedded `Sfis`, path/name strings, current status, silent flag, and last check/log timestamps.
- Declares ATA/SCSI probe/enable/status functions and `eprint()`.

## Notes
The embedded `Sfis` lets ATA code cache signature/features directly in each `Sdisk`, while SCSI code ignores those fields.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/disk/smart/smart.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/disk/vblade/aoe.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/disk/vblade/aoe.h

## Purpose
Defines ATA over Ethernet protocol constants and packet structures for `vblade`.

## Key Contents
- Enumerates AoE command classes (`ACata`, `ACconfig`), query-config subcommands, and error codes.
- Defines Ethernet AoE type `0x88a2`, fixed sizes, version, response/error flags, and ATA command flag bits.
- `Aoehdr` models the Ethernet/AoE common header with destination/source MACs, type, version flags, shelf/slot, command, and tag.
- `Aoeata` models AoE ATA command fields: flags, error/features, sector count, command/status, LBA, and reserved bytes.
- `Aoeqc` models query-config response/request fields including buffer count, firmware version, sector count, command, and config string length.

## Notes
The header assumes `Eaddrlen` is defined before inclusion; `vblade.c` provides it locally because the userspace code does not get the kernel definition.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/disk/vblade/aoe.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/disk/vblade/vblade.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/disk/vblade/vblade.c

## Purpose
Implements a virtual ATA over Ethernet target serving one or more backing files as AoE shelves/slots.

## Key Behavior
- Parses per-blade options for initialization/raw mode, virtual size, AoE shelf.slot address, config string, and one or more ethernet interfaces.
- Uses a `Vbhdr` header at the start of non-raw backing files to persist magic, byte size, shelf.slot address, config length, and config data.
- `checkfile()`, `chkvblade()`, `recheck()`, and `savevblade()` validate/persist backing metadata and determine usable LBA count after header overhead.
- Opens Plan 9 ethernet AoE data endpoints by connecting clone files to EtherType `0x88a2`; one process is launched per interface.
- Serves AoE config commands: read, test, prefix, set, and force-set, including config-length validation and firmware/buffer metadata.
- Serves ATA commands: identify device, 28/48-bit reads, and 28/48-bit writes. Unsupported commands return ATA abort.
- Synthesizes IDENTIFY data with model `Plan 9 Vblade`, serial `serial#`, version `2`, and 28/48-bit LBA capacity fields.
- Checks sector count against interface MTU-derived limit and validates accesses against the virtual max LBA.
- Swaps Ethernet source/destination addresses and sets response shelf/slot in replies; broadcasts initial config discovery packets.
- Supports multiple blades and dispatches incoming requests by shelf/slot, including wildcard broadcasts.

## Interfaces And Dependencies
- Uses Plan 9 `thread`/`proccreate`, ethernet device files, `<ip.h>` byte helpers, and `<fis.h>` ATA status/error constants.
- Uses `aoe.h` for wire structures and constants.

## Notes
The code uses processes rather than threads for blocking network reads/writes. Raw mode skips the persistent `Vbhdr` and exposes the whole backing file; non-raw mode reserves 128 sectors for metadata.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/disk/vblade/vblade.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/dossrv/chat.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/dossrv/chat.c

## Purpose
Provides diagnostic logging and fatal panic handling for `dossrv`.

## Key Behavior
- `chat()` prints formatted diagnostics to stderr only when global `chatty` is nonzero.
- `panic()` prints program name, pid, formatted message, and current error string, optionally aborts when `doabort` is set, then exits.

## Interfaces And Dependencies
- Uses globals `chatty` and `doabort`.
- Declared through `fns.h` and used across the dossrv implementation.

## Notes
This is the common debugging path for both expected verbose tracing and unrecoverable internal consistency failures.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/dossrv/chat.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/dossrv/dat.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/dossrv/dat.h

## Purpose
Central data-structure and constant header for the FAT-backed `dossrv` 9P server.

## Key Contents
- Defines DOS partition type constants for FAT12/FAT16/FAT32 variants and related values.
- Defines on-disk structures: `Dospart`, FAT boot sectors (`Dosboot`, `Dosboot32`), optional `Fatinfo`, and `Dosdir`.
- Defines `Dosbpb`, the in-memory BIOS parameter block and FAT state, including cluster geometry, FAT location, root/data addresses, FAT width, free-cluster tracking, and lock.
- Defines FAT directory constants, attributes, endian access macros, and file-size/name limits.
- `Dosptr` tracks the current directory entry location, parent location, cluster cache, previous/next directory sectors, and held `Iosect`.
- `Xfs` tracks an attached FAT filesystem/device with file name, qids, refcount, sector geometry, byte offset, open mode, and `Dosbpb`.
- `Xfile` tracks a 9P fid, open flags, qid, attached filesystem, and current DOS pointer.
- Enumerates xfile cleanup modes, filename classification results, xfile open flags, and internal errno codes.

## Interfaces And Dependencies
- Assumes `MLock` and `Iosect` are already declared from `iotrack.h`.
- Exposes global declarations for `chatty`, `errno`, `readonly`, `deffile`, and `trspaces`.

## Notes
This header is the integration point for disk format parsing, sector cache state, and 9P fid state. Many modules depend on its exact struct fields.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/dossrv/dat.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/dossrv/devio.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/dossrv/devio.c

## Purpose
Implements raw sector read/write helpers for a mounted FAT filesystem device.

## Key Behavior
- `devread()` performs `pread()` at `xf->offset + addr * xf->sectsize` and returns zero only on full read.
- `devwrite()` refuses writes when the underlying device was opened read-only, then performs `pwrite()` at the same translated offset.
- `deverror()` records `Eio`, closes the device on system-call errors, logs short transfers, and returns failure.

## Interfaces And Dependencies
- Uses `Xfs` from `dat.h` and `chat()` diagnostics.
- Called by the `iotrack` sector cache for actual media I/O.

## Notes
The `xf->offset` field lets `dossrv` mount a FAT filesystem embedded at a byte offset inside another file/device.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/dossrv/devio.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/dossrv/dosfs.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/dossrv/dosfs.c

## Purpose
Implements the 9P request handlers for `dossrv`, translating Plan 9 file operations into FAT directory and file mutations.

## Key Behavior
- Handles `Tversion`, `Tauth`, `Tflush`, `Tattach`, `Twalk`, `Topen`, `Tcreate`, `Tread`, `Twrite`, `Tclunk`, `Tremove`, `Tstat`, and `Twstat`.
- `rattach()` creates/cleans a root fid, opens or references an `Xfs`, parses the FAT format with `dosfs()`, and initializes a synthetic root qid.
- `rwalk()` clones when needed, supports `.`, `..` via `walkup()`, normalizes names, searches directories including long names, and maps DOS directory attributes to qid type bits.
- `ropen()` enforces open-mode permissions, read-only DOS attributes, ORCLOSE parent checks, and truncation requests.
- `rcreate()` validates parent directory writability, classifies/generates 8.3 aliases for long names, allocates an initial cluster for directories, writes DOS entries, and creates `.`/`..` records.
- `rread()` delegates to `readdir()` or `readfile()` after checking read-open state.
- `rwrite()` delegates to `writefile()` after checking write-open state.
- `rremove()` rejects root, read-only, or non-empty-directory removal, truncates file clusters, marks short and preceding long-name entries deleted, updates parent time, and syncs.
- `rstat()` converts a DOS entry and any preceding long filename slots into a Plan 9 `Dir`.
- `rwstat()` supports truncate, mtime/mode changes, DSYSTEM/contiguous mapping through `DMEXCL`/`DMAPPEND`, and rename through delete/recreate of directory entries.
- Renames preserve invisible creation/access fields and relocate other fids that pointed to the old directory slot.

## Interfaces And Dependencies
- Uses global 9P request/reply buffers from `xfssrv.c`.
- Depends heavily on helper functions in `dossubs.c`, xfile management in `xfile.c`, and sector cache functions from `iotrack.c`.

## Notes
The server maps DOS system files to Plan 9 `DMEXCL`, and contiguous system files to `DMAPPEND`. Write and rename paths are careful to release/reacquire directory sectors to avoid lock loops.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/dossrv/dosfs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/dossrv/dosfs.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/dossrv/dosfs.h

## Purpose
Defines 9P message size limits and shared request/reply buffers for `dossrv`.

## Key Contents
- `Maxfdata = IOUNIT`
- `Maxiosize = IOHDRSZ + Maxfdata`
- Declares global `Fcall *req`, `Fcall *rep`, reply data buffer, and stat buffer.

## Notes
This header centralizes the server’s maximum 9P payload sizing for both the main loop and request handlers.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/dossrv/dosfs.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/dossrv/dossubs.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/dossrv/dossubs.c

## Purpose
Contains most FAT filesystem logic for `dossrv`: format detection, BPB parsing, cluster-chain management, directory traversal, long-name handling, file I/O, allocation, truncation, and metadata conversion.

## Key Behavior
- `isdosfs()` recognizes FAT boot-sector jump signatures, including dynamic disk manager cases.
- `dosfs()` reads the boot sector, validates sector geometry, detects FAT12/16/32, populates `Dosbpb`, handles FAT32 active-FAT mirroring flags, reads FAT32 info sector free-space hints, and computes root/data/FAT geometry.
- `rootfile()`, `getfile()`, and `putfile()` manage the synthetic root and held sector for the current DOS directory entry.
- `fileclust()` walks or extends a file’s cluster chain, using contiguous allocation for DOS system files.
- `fileaddr()` translates a file-relative sector number to an absolute filesystem sector, with special handling for FAT12/16 fixed root directories and FAT32 root cluster.
- Name helpers classify Plan 9 names as invalid, valid 8.3, lower-case 8.3, or long; generate `~N` aliases; normalize optional colon/space translation; and validate Plan 9 path elements.
- `searchdir()` scans a directory for a name or for free slots, assembling long filename sequences, checking alias checksums, and reserving enough entries for long names across sector boundaries.
- `readdir()` emits Plan 9 stat records while skipping deleted, volume-label, and `.`/`..` entries and preferring valid long names over short aliases.
- `walkup()` reconstructs a parent directory pointer by using `.`/`..` entries and scanning the grandparent directory for the parent’s start cluster.
- `readfile()` and `writefile()` perform sector-by-sector file data access, allocating clusters on writes and updating file length/time.
- `truncfile()` frees cluster chains beyond the requested length and updates file length/start state.
- `getdir()` and `putdir()` translate DOS attributes, qids, length, and timestamps to/from Plan 9 `Dir` fields.
- Long filename helpers decode and encode UTF-16LE directory slots, maintain checksum/order validation, and support names up to `DOSNAMELEN`.
- FAT helpers `getfat()` and `putfat()` read/write 12-, 16-, and FAT32 28-bit entries across sector boundaries and across mirrored FAT copies; `putfat()` also updates FAT32 info-sector counters when present.
- Allocation helpers `falloc()`, `ffree()`, `cfalloc()`, `iscontig()`, and `makecontig()` find free clusters, zero new clusters, and relocate files to make system files contiguous with spare growth space.
- Time helpers convert between DOS date/time fields and Plan 9 seconds using local timezone rules.
- Debug dump functions print boot sectors, FAT32 info/backup sectors, and directory entries when `chatty` is enabled.

## Interfaces And Dependencies
- Called from `dosfs.c`, `xfile.c`, and other dossrv support modules through prototypes in `fns.h`.
- Uses sector cache APIs from `iotrack.c` and raw device I/O from `devio.c`.
- Relies on `Dosbpb`, `Dosptr`, `Xfs`, and `Xfile` definitions from `dat.h`.

## Notes
This file is the behavioral core of FAT support. Its riskiest paths are metadata mutation paths that span multiple structures: long-name creation/removal, rename, FAT mirroring, FAT12 boundary writes, and contiguous-file relocation.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/dossrv/dossubs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/dossrv/errstr.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/dossrv/errstr.h

## Purpose
Defines the internal error-code to string mapping for `dossrv`.

## Key Contents
- Initializes `errmsg[ESIZE]` with user-facing messages for format errors, I/O errors, authentication, memory, missing files, permission, missing filesystem, bad fcall/stat/version, long names, contiguous-space failures, and system-call errors.

## Interfaces And Dependencies
- Included by `xfssrv.c`, where `xerrstr()` maps `errno` values to 9P `Rerror` strings.

## Notes
The array is defined in the header rather than declared extern, so it is intended to be included by exactly one compilation unit.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/dossrv/errstr.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/dossrv/fns.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/dossrv/fns.h

## Purpose
Shared function prototype header for `dossrv`.

## Key Contents
- Declares FAT parsing/debug helpers, cluster allocation/freeing, FAT read/write, directory search/name conversion, long-name handling, file read/write/truncate, contiguous-file support, time conversion, root/walk helpers, xfile/xfs management, sector/device I/O, 9P request handlers, locking, error/logging, and sync/cache functions.
- Includes `#pragma varargck` annotations for `chat()` and `panic()`.

## Notes
This header exposes almost the entire program as cross-file functions, matching the C style of the rest of the server.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/dossrv/fns.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/dossrv/iotrack.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/dossrv/iotrack.c

## Purpose
Implements a track-oriented sector cache for `dossrv`.

## Key Behavior
- Maintains 80 `Iotrack` buffers indexed by a 31-bucket hash table and a global LRU list.
- Each track holds `xf->sect2trk` sectors plus lazily-created `Iosect` wrappers for individually locked sectors.
- `getsect()` returns a read-populated sector; `getosect()` returns an output sector that can avoid reading when a full sector will be overwritten.
- `getiotrack()` finds or recycles an unreferenced track, flushing modified tracks before reuse and purging stale per-sector wrappers.
- `tread()` reads a whole track when no sector wrappers exist, or reads only missing sectors when some wrappers already exist.
- `twrite()` writes the full track, first filling missing stale sectors if necessary.
- `putsect()` merges sector flags into the parent track, handles immediate-write requests, decrements refs, and unlocks.
- `purgebuf()` flushes/purges all tracks belonging to an `Xfs`; `sync()` flushes all modified tracks.
- `iotrack_init()` initializes hash heads, LRU list, and empty track buffers.

## Interfaces And Dependencies
- Uses `devread()`/`devwrite()` for media I/O and `MLock` from `lock.c`.
- Sector and track structures are declared in `iotrack.h`.

## Notes
This cache is central to mutation correctness because FAT metadata operations often hold and modify sector buffers across helper calls. The simple locks are cooperative and detect misuse rather than blocking.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/dossrv/iotrack.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/dossrv/iotrack.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/dossrv/iotrack.h

## Purpose
Defines lock, sector-cache, and track-cache structures for `dossrv`.

## Key Contents
- Buffer flags: `BSTALE`, `BMOD`, and `BIMM`.
- `MLock` is a simple integer lock used by the server’s single-process/cooperative paths.
- `Iosect` stores next pointer, flags, lock, sector buffer pointer, and owning `Iotrack`.
- `Iotrack` stores hash/LRU links, lock, flags, refcount, owning `Xfs`, track address, and sector-wrapper table/data pointer.

## Notes
The cache treats a track as the I/O unit but exposes sector-sized locked views to FAT code.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/dossrv/iotrack.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/dossrv/lock.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/dossrv/lock.c

## Purpose
Implements the simple `MLock` primitive used by `dossrv`.

## Key Behavior
- `mlock()` asserts the lock is initialized and not already held, then marks it held.
- `unmlock()` asserts the lock is initialized and held, then releases it.
- `canmlock()` tries to acquire without blocking and returns zero if already held.

## Interfaces And Dependencies
- Uses `panic()` for all lock misuse.
- Operates on `MLock` from `iotrack.h`.

## Notes
This is not a blocking kernel-style lock; it is an internal invariant checker and mutual-exclusion marker for the server’s control flow.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/dossrv/lock.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/dossrv/xfile.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/dossrv/xfile.c

## Purpose
Manages `Xfs` filesystem attachments and `Xfile` fid records for `dossrv`.

## Key Behavior
- `getxfs()` opens the requested device/file, optionally parses a `name:offset` suffix for embedded FAT filesystems, falls back to read-only open when write open fails, and reuses an existing live `Xfs` by qid/name/offset.
- Maintains reference counts for attached filesystems and frees device name, `Dosbpb`, cached buffers, and fd when the last reference drops.
- `xfile()` manages fid lookup, allocation, cleaning, and clunking through a 127-bucket hash table plus freelist.
- `clean()` releases any held `Dosptr` and decrements the referenced `Xfs`.
- `dosptrreloc()` updates other fids pointing at a DOS directory entry when a rename/move changes its sector/offset, preserving qid consistency.

## Interfaces And Dependencies
- Uses `deffile`, `readonly`, `errno`, and `chat()` globals.
- Works with `Dosptr`, `Xfs`, and `Xfile` from `dat.h`, and cache cleanup from `iotrack.c`.

## Notes
The `name:offset` handling mutates the input name string at the colon and assumes 512-byte units for the offset suffix.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/dossrv/xfile.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/dossrv/xfssrv.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/dossrv/xfssrv.c

## Purpose
Main server loop and process setup for `dossrv`.

## Key Behavior
- Parses options: `-:` to translate colons/spaces, `-r` read-only, `-v` verbose, `-f devicefile` default filesystem, `-s` stdio mode, and `-p` abort-on-panic.
- Allocates global request/reply `Fcall` buffers and initializes the sector cache.
- In service mode, creates `/srv/dos` or `/srv/<name>`, writes a pipe fd to it, dupes the other pipe end onto stdin/stdout, and forks a detached server process.
- `io()` reads 9P messages, decodes them, dispatches through the `fcalls` table, converts internal `errno` into `Rerror`, encodes replies, and writes them back.
- Installs `fcallfmt` for verbose tracing.
- `xerrstr()` maps internal error codes to strings, using the process errstr for `Eerrstr`.
- `eqqid()` compares Plan 9 qids.

## Interfaces And Dependencies
- Includes `errstr.h` to define the error string table.
- Dispatches handlers implemented in `dosfs.c` and uses global buffers declared in `dosfs.h`.

## Notes
The process model is a classic Plan 9 service-file server: parent exits after forking, child owns the 9P loop. Stdio mode lets it be mounted or driven by another process without creating `/srv`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/dossrv/xfssrv.c -->