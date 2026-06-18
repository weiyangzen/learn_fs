# sources/distributed-fs/lizardfs/src/nfs-ganesha/mds_handle.c

## Purpose
Implements pNFS object-handle layout operations for LizardFS FSAL metadata-server mode.

## Important APIs, Types, And Functions
Provides `lzfs_fsal_layoutget`, `lzfs_fsal_layoutreturn`, `lzfs_fsal_layoutcommit`, and `lzfs_fsal_handle_ops_pnfs` to install those operations.

## Control Flow
`layoutget` validates NFSv4.1 file layout, builds a pNFS device id from export id and inode, writes a DS wire handle containing the inode, uses `MFSCHUNKSIZE` as layout utility/stripe unit, encodes a file layout via `FSAL_encode_file_layout`, and marks the layout as last segment and return-on-close. `layoutreturn` validates layout type and otherwise succeeds. `layoutcommit` optionally updates file size and mtime based on layout commit arguments by fetching current attrs and sending a LizardFS setattr.

## State And Persistence Behavior
Layoutget itself does not persist state; it returns layout metadata to clients. Layoutcommit can persist size/mtime changes through `liz_cred_setattr`.

## Dependencies And Integration Points
Depends on Ganesha pNFS helpers, `context_wrap`, `lzfs_internal`, and `MFSCommunication.h`. Works with `mds_export.c` deviceinfo and `ds.c` DS handles.

## Risks And Edge Cases
`layoutcommit` has a FIXME questioning whether the operation makes sense. It assigns `attr.st_mtim.tv_sec = arg->new_time.nseconds` instead of `tv_nsec`, likely corrupting mtime nanoseconds. It calls `setattr` even with mask 0, which may be harmless but unnecessary. Layoutget grants one whole-file segment and assumes DS can serve chunks according to the encoded device info.

## Test Signals
pNFS layoutget/layoutcommit integration tests should validate encoded handles, device ids, file-size extension, mtime update, and unsupported layout handling.
