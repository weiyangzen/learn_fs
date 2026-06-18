# sources/distributed-fs/ceph-client/fs/smb/client/export.c

Purpose: provides the optional `CONFIG_CIFS_NFSD_EXPORT` exportfs operations table for exporting CIFS mounts through NFSD. The implementation is intentionally minimal and documents the constraints around server inode numbers and fsid usage.

Important APIs and functions: defines `cifs_get_parent` and `const struct export_operations cifs_export_ops` when `CONFIG_CIFS_NFSD_EXPORT` is enabled. The table uses `generic_encode_ino32_fh` for file-handle encoding and wires `.get_parent` to `cifs_get_parent`; mandatory decode operations are noted but not implemented in this file.

Control flow: when compiled in, exportfs can call `cifs_get_parent`, but it currently logs the request and returns `-EACCES`. File handle encoding is delegated to the generic 32-bit inode encoder.

State and persistence behavior: no state is stored by this file. Export behavior relies on stable server inode numbers from CIFS mount options; CIFS inode generation numbers are effectively zero.

Dependencies and integration points: depends on Linux exportfs, CIFS globals/debug, and CIFS filesystem declarations. It integrates only when the kernel config enables CIFS NFSD export support and an administrator configures CIFS paths for NFS export.

Risks: parent lookup and file-handle decode are incomplete, so practical NFSD export support is limited. Generic 32-bit inode handles can be insufficient for servers with 64-bit inode numbers. Exporting without `serverino` or a stable fsid can produce unstable or ambiguous NFS file handles.

Test signals: compile with and without `CONFIG_CIFS_NFSD_EXPORT`, verify `cifs_export_ops` linkage, attempted NFSD export returning access failure for parent lookup, and documentation/admin tests requiring `serverino` plus explicit fsid.
