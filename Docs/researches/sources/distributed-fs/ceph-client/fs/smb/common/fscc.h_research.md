# sources/distributed-fs/ceph-client/fs/smb/common/fscc.h

Read coverage: full file.

## Purpose
`fscc.h` defines common MS-FSCC wire structures and constants used by SMB client and server code for file system control payloads, reparse points, file information classes, filesystem information classes, directory entries, file attributes, notify records, and POSIX filesystem extension data.

## Important APIs, types, and functions
Key structure groups include reparse buffers (`reparse_data_buffer`, GUID, mount point, symlink, NFS, WSL symlink), clone/zero/integrity/ioctl payloads (`duplicate_extents_to_file`, `duplicate_extents_to_file_ex`, integrity request/response structs, `file_zero_data_information`), file info records (`smb2_file_all_info`, `FILE_BASIC_INFO`, directory info structs, eof/internal/link/network-open/rename info), filesystem info records (`FILE_SYSTEM_ATTRIBUTE_INFO`, `smb2_fs_control_info`, `smb2_fs_full_size_info`, `smb3_fs_ss_info`, `FILE_SYSTEM_SIZE_INFO`, `filesystem_vol_info`, `FILE_SYSTEM_DEVICE_INFO`, `FILE_SYSTEM_POSIX_INFO`), and notify payload `file_notify_information`.

Constants define FS information classes, file system capability bits, file attribute bits plus little-endian forms, notify action values, sector-size flags, NFS special file tags, duplicate-extents flags, and POSIX extension identifiers.

## Control flow
There is no executable control flow. The header defines packed layouts used by request construction and response parsing. Flexible arrays and static assertions ensure variable-length file names begin immediately after packed header groups for rename/link structures.

## State and persistence behavior
No runtime state is stored. The file describes persistent network protocol layouts; field order, packing, endian annotations, and constants must remain stable to interoperate with SMB peers.

## Dependencies and integration points
The header depends on Linux fixed-width and endian types and is included by SMB2 create/query/set/ioctl, reparse point, copy offload, directory enumeration, statfs, attribute, notify, and POSIX extension code. `xattr.c` indirectly relies on security-info constants shared with SMB2 query/set info paths.

## Risks and test signals
Layout drift is the main risk. Missing `__packed`, wrong endian type, or moving a field outside a `__struct_group` would corrupt wire compatibility. Tests should use compile-time offset/size checks where possible, packet decode tests for directory/query info responses, symlink/reparse round trips, clone/zero/integrity ioctl coverage, statfs/FS attribute queries, notify response parsing, and POSIX extension negotiation/query tests.
