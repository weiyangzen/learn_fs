# Group Research: group_1659_reactos_sources_windows_reactos_drivers_filesystems_btrfs_fileinfo__be2b7d69f192

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/btrfs/fileinfo.c -->
# File Research: sources/windows/reactos/drivers/filesystems/btrfs/fileinfo.c

## Scope

This report covers the complete `fileinfo.c` file in the ReactOS-imported WinBtrfs filesystem driver. The file implements Windows file information, extended attribute, rename, link, disposition, size, stream, and stat query/set behavior for Btrfs FCBs and file references. It is a major metadata mutation module: beyond `IRP_MJ_QUERY_INFORMATION` and `IRP_MJ_SET_INFORMATION`, it owns alternate data stream rename/conversion logic, hardlink creation and enumeration, cross-subvolume move emulation, directory child hash maintenance, EA storage, LX metadata EAs, and notification emission for these operations.

## Primary Responsibilities

- Provides compatibility definitions for Windows 10 file information classes and structures when building with MinGW or ReactOS headers.
- Implements `drv_set_information()` for allocation, basic attributes/times, disposition/delete-on-close, EOF/valid-data-length, file position, rename, hardlink, and selected extended Windows information classes.
- Implements `drv_query_information()` and `query_info()` for basic, standard, internal, EA, name, stream, network-open, compression, hardlink, ID, stat, LX stat, and case-sensitive information classes.
- Implements `drv_query_ea()` and `drv_set_ea()` for NT extended attributes stored in the driver xattr buffer, including special handling for LXSS UID/GID/mode metadata.
- Maintains directory child ordered/hash lists through `insert_dir_child_into_hash_lists()` and `remove_dir_child_from_hash_lists()`.
- Handles file and stream rename transformations, including stream-to-file and file-to-stream conversion where Win32 stream names are represented as Btrfs xattrs.
- Handles cross-subvolume moves by duplicating FCB/file-reference state, assigning new inode numbers, updating extent references, and leaving deleted dummy records behind for flush/rollback consistency.

## Set Information Dispatch

`drv_set_information()` validates the target device, mount state, readonly volume state, FCB/CCB presence, and readonly subvolume restrictions before dispatching by `FileInformationClass`. It enters the filesystem, establishes top-level IRP state, checks oplocks, sets `IoStatus.Information` to zero, and completes the IRP before returning.

Supported set paths include allocation/EOF changes, basic attributes, disposition, hardlink creation, rename, position, valid data length, and selected non-ReactOS extended information classes such as case-sensitive directory information.

## Rename, Streams, And Links

`set_rename_information()` is the central rename path. It normalizes the target component, validates the name, resolves the destination parent, enforces access and replacement rules, applies POSIX/readonly handling, deletes overwritten targets with rollback support, then mutates file references, directory child lists, hardlink side records, parent sizes, timestamps, and notifications.

Alternate data streams are represented as xattrs with a `user.` prefix and directory-child entries with index `0`. The file handles ADS-to-ADS renames, stream-to-file conversion, and file-to-stream conversion, including dummy deleted FCBs so flush can remove old on-disk xattr/file metadata.

`set_link_information()` creates hardlinks for regular non-ADS files, rejects directories/streams and cross-subvolume links, enforces link-count limits, handles replacement, creates a new fileref and directory child, updates hardlink records and `st_nlink`, and sends notifications.

## Query And EA Behavior

`query_info()` serves `IRP_MJ_QUERY_INFORMATION`, filling Windows structures from Btrfs inode, fileref, stream, xattr, and reparse metadata. Helpers cover basic, standard, network-open, internal ID, EA size, file name, streams, compression, hardlinks, file IDs, Windows stat, LX stat, and case-sensitive information.

`fileref_get_filename()` constructs paths by walking parent filerefs, using `\` for normal components and `:` for ADS components, with truncation reporting via `STATUS_BUFFER_OVERFLOW`.

`drv_query_ea()` returns stored `FILE_FULL_EA_INFORMATION` records with name-list, index, restart, and single-entry scan modes. `drv_set_ea()` validates and merges EA buffers, removes zero-length values, repacks the EA xattr buffer, and consumes special LXSS UID/GID/mode EAs into inode metadata instead of persisting them as ordinary EAs.

## Locking And Dirty State

Metadata mutations use `Vcb->tree_lock`, `Vcb->fileref_lock`, per-FCB `Header.Resource`, per-directory `dir_children_lock`, and sometimes the global FCB lock. Many operations initialize rollback lists and call `clear_rollback()` on success or `do_rollback()` on failure. Dirty FCBs and filerefs are marked so later flush writes inode items, xattrs, directory items, extents, hardlink state, and deleted dummy records.

## Important Invariants And Risks

- ADS data must fit within the computed xattr capacity from Btrfs node size.
- File/stream conversion paths transfer pointer ownership across FCBs and filerefs; correctness depends on nulling moved fields and preserving dummy deleted objects.
- Cross-subvolume moves create new inodes and update extent references, so missed metadata updates can corrupt references or leak extents.
- Directory `st_size` is manually adjusted from UTF-8 name lengths in rename/link paths.
- Hardlink side lists must stay synchronized with directory child moves, replacements, and link creation.
- `fileref_get_filename()` has a FIXME about needing a fileref filepart lock, making concurrent rename/name-query behavior a known synchronization concern.
- ReactOS builds exclude several Windows 10 information classes and case-sensitive set/query paths guarded by `#ifndef __REACTOS__`.

<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/btrfs/fileinfo.c -->