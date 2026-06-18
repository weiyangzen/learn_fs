# sources/distributed-fs/openafs/src/vol/vol-info.c

## Purpose

`vol-info.c` implements reusable volume inspection and scanning logic for OpenAFS volume utility commands. It can dump volume headers, inspect special files, scan vnode index files, print selected vnode fields as tabular columns, find paths, classify symlinks as mount points, scan ACLs, save inode contents, and accumulate size totals.

## Important APIs, Types, and Functions

Public functions declared in `vol-info.h` include `volinfo_Init`, `volinfo_Options`, `volinfo_AddOutputColumn`, `volinfo_ScanPartitions`, `volinfo_AddVnodeHandler`, and vnode handlers such as `volinfo_PrintVnode`, `volinfo_PrintVnodeDetails`, `volinfo_ScanAcl`, `volinfo_SaveInode`, and `volinfo_AddVnodeToSizeTotals`.

Internally, `struct VnodeDetails` packages a volume, vnode class, disk vnode pointer, vnode number, index offset, optional path, and union payload for mount/symlink/ACL output. `ColumnName` maps the `VOLSCAN_COLUMNS` macro list to numeric column ids. `VnodeScanLists` stores per-class callback lists.

Major helpers include `ReadHdr1`, `AttachVolume`, `DetachVolume`, `volinfo_ScanPartitions`, `HandleAllPart`, `HandlePart`, `HandleVolume`, `HandleHeaderFiles`, `HandleSpecialFile`, `HandleVnodes`, `LookupPath`, `ReadSymlinkTarget`, `PrintColumns`, and size-total print helpers.

## Control Flow

`volinfo_Init` enforces root on non-Windows, initializes directory handling, initializes empty vnode cache class info, and initializes scan callback lists. `volinfo_Options` creates defaults: dump info enabled, hostname set, space column delimiter, and directory magic checks enabled. Callers add output columns and vnode handlers, then call `volinfo_ScanPartitions`.

`volinfo_ScanPartitions` optionally initializes FSSYNC checkout, attaches partitions, resolves partition names or current partition, prints headings, and scans either all partitions, one partition, or one volume. `HandlePart` walks partition directory entries ending in `VHDREXT`. `HandleVolume` reads and validates the volume header file, optionally inspects special inodes, attaches a simplified `Volume` object from inode handles and disk data, prints header information, scans large and small vnode indexes if handlers are registered, prints size totals, and detaches.

`HandleVnodes` opens the class index, computes vnode count from index file size minus the header record, skips the header, reads disk vnode records, applies mode masks, fills `VnodeDetails`, and invokes every registered handler. Handlers print raw vnode lines, output structured columns, save inode data, scan ACLs, or accumulate sizes.

Path lookup uses the large vnode index and `afs_dir_InverseLookup` to climb parent directories from a child fid back to root. Symlink handling reads the target inode and recognizes AFS mount points when contents begin with `#` or `%` and end in `.`.

## State, Persistence, and Concurrency

Most operations are read-only inspections of volume headers, special inodes, vnode index files, and data inodes. Mutating behavior exists in `ReadHdr1` when `opt->fixHeader` repairs bad magic/version fields, and in `volinfo_SaveInode` when inode contents are copied to `TmpInode.*` files in the current directory. FSSYNC checkout can request fileserver coordination before reading volumes. Global state includes selected columns, callback queues, `DirIndexFd`, size totals, and initialization state, so this module is not designed for independent concurrent scans in the same process.

## Dependencies and Integration Points

The file depends on command/dir/ACL/prs headers, vnode and volume structures, partition attach, salvage directory helpers, daemon/FSSYNC inline protocols, inode handles, namei support, and OpenAFS stream wrappers. It provides shared implementation for utilities that need volume/vnode inspection without fully attaching through the fileserver path.

## Risks and Test Signals

Risks include stale global state across scans, path lookup failures on corrupt parent chains, static buffers in date/path/symlink functions, unchecked callback allocation in `volinfo_AddVnodeHandler`, root-only behavior, and accidental mutation via `fixHeader` or inode saving. Tests should cover scanning all/one partition/one volume, FSSYNC denial, bad header magic/version with and without repair, volume type filters, mode masks, symlink and mount parsing, ACL positive/negative entries, path reconstruction, namei output, size totals, and output column formatting with custom delimiters.
