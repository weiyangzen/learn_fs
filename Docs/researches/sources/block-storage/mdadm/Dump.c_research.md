# File Research: sources/block-storage/mdadm/Dump.c

## Purpose
`Dump.c` implements metadata dump and restore support for mdadm. It copies RAID metadata between real devices and same-sized dump files, using metadata-handler callbacks.

## Major Entry Points
- `Dump_metadata(char *dev, char *dir, struct context *c, struct supertype *st)`
- `Restore_metadata(char *dev, char *dir, struct context *c, struct supertype *st, int only)`

## Dump Behavior
`Dump_metadata()` requires an existing output directory, opens the source device read-only, obtains its size, guesses metadata type if not supplied, loads the superblock with hardware compatibility ignored, and requires the supertype to provide `copy_metadata`.

It creates a new file in the target directory named after the source device basename, truncates it to the same size as the source device, and asks the metadata handler to copy metadata into it. If the source is a block device, it scans `/dev/disk/by-id` for names pointing to the same `st_rdev` and creates hardlinks in the dump directory for those identifiers.

## Restore Behavior
`Restore_metadata()` opens the target device read-write, checks its size, then chooses a source file. If the restore path is a directory, it prefers a file whose name also maps through `/dev/disk/by-id` to the target block device; it rejects ambiguous matches with different inodes. If no by-id match exists, it falls back to the target device basename. If the restore path is a file, that is allowed only when `only` indicates a single target device.

The restore file must be exactly the same size as the target device. The function guesses and loads metadata from the file, requires `copy_metadata`, then copies metadata from file to device.

## Dependencies and Integration Points
Both paths use mdadm device open helpers, metadata supertype probing/loading, the `copy_metadata` callback, size probing, and `/dev/disk/by-id` stable-name matching.

## Safety and Risk Notes
The same-size check protects against restoring dumps to mismatched devices. A bug-like condition appears in `Restore_metadata()`: `if (!fl)` treats file descriptor `0` as failure but misses `-1`; the usual check should be `fl < 0`. In normal CLI execution fd 0 is often already open, but this is still a fragile error check.
