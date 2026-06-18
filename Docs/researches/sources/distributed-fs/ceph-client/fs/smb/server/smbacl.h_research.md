## sources/distributed-fs/ceph-client/fs/smb/server/smbacl.h

Purpose: defines ksmbd's security descriptor control flags, ACL conversion state, and the public API for Windows security descriptor parsing/building, DACL inheritance, and ACL permission checks.

Important APIs and types: defines descriptor revision/control flags such as `DACL_PRESENT`, `DACL_PROTECTED`, `DACL_AUTO_INHERITED`, and `SELF_RELATIVE`; `struct smb_fattr` for uid/gid/mode/access/POSIX ACL conversion output; `struct posix_ace_state`, `struct posix_user_ace_state`, `struct posix_ace_state_array`, and `struct posix_acl_state`; and declarations for SID comparison/mapping, descriptor conversion, inheritance, permission checks, and `set_info_sec`. Inline helpers translate POSIX ACL uid/gid entries through mount idmaps into init-namespace ids visible to ksmbd.

Control flow: callers allocate/populate `smb_fattr`, pass wire descriptors to `parse_sec_desc` for VFS changes, call `build_sec_desc` when returning security descriptors, and use `smb_check_perm_dacl` during open/access evaluation. The inline id translation helpers are used while emitting ACEs from POSIX ACL entries.

State and persistence behavior: the header only declares in-memory conversion state. Persistent ACL state is applied by implementation functions to inode metadata, POSIX ACL xattrs, and ksmbd NTACL xattrs.

Dependencies and integration points: includes common SMB ACL wire structures, VFS/namei/POSIX ACL/mount-idmap headers, and tree-connect management types. It bridges SMB2 security-information handling with Linux VFS permissions and share configuration.

Risks: conversion state owns POSIX ACL references that must be released by callers. The idmapped-mount translation helpers rely on `init_user_ns` as the ksmbd userspace id view; incorrect use would emit wrong SIDs for idmapped exports. Control flag values must remain protocol-accurate because they are stored and sent on the wire.

Test signals: compile with and without `CONFIG_FS_POSIX_ACL`, idmapped mount ACL round trips, descriptor build/query/set paths for owner/group/DACL combinations, and leak checks for `smb_fattr.cf_acls/cf_dacls` ownership.
