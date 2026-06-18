# sources/distributed-fs/ceph-client/fs/smb/client/xattr.c

Read coverage: full file.

## Purpose
`xattr.c` connects Linux VFS extended attribute operations to SMB extended attributes, DOS attribute pseudo-xattrs, creation-time pseudo-xattrs, and CIFS/SMB3 security descriptor xattrs. It exposes both legacy `system.cifs_*` names and newer `system.smb3_*` aliases.

## Important APIs, types, and functions
The VFS-facing API is `const struct xattr_handler * const cifs_xattr_handlers[]`, which contains user, OS/2, ACL, NTSD, SACL, owner, and full descriptor handlers. Core handlers are `cifs_xattr_get`, `cifs_xattr_set`, and `cifs_listxattr`. Pseudo-xattr helpers are `cifs_attrib_get`, `cifs_attrib_set`, `cifs_creation_time_get`, and `cifs_creation_time_set`.

Handler flags distinguish user EAs from `XATTR_CIFS_ACL`, `XATTR_CIFS_NTSD_SACL`, `XATTR_CIFS_NTSD_OWNER`, `XATTR_CIFS_NTSD`, and `XATTR_CIFS_NTSD_FULL`. Security descriptor requests map to SMB security-info bits such as `OWNER_SECINFO`, `GROUP_SECINFO`, `DACL_SECINFO`, and `SACL_SECINFO`, or CIFS ACL set flags.

## Control flow
Set operations acquire a tcon link, allocate a path buffer, build a full path from the dentry, reject oversized EA values, then dispatch by handler flag. User xattrs named `cifs.dosattrib` or `smb3.dosattrib` call `set_file_info` with `FILE_BASIC_INFO.Attributes`; creation-time names call `set_file_info` with `CreationTime`; other user EAs call dialect `set_EA` unless mounted with `NO_XATTR`. Security descriptor writes copy the user-supplied blob into kernel memory and call `set_acl` with the selected descriptor parts.

Get operations follow the same tcon/path setup. DOS attribute and creation-time reads revalidate inode attributes and copy cached `CIFS_I(inode)` fields. User EAs call `query_all_EAs`. Security descriptor reads call `get_acl` with the requested info bits and copy the returned descriptor if the caller buffer is large enough. `cifs_listxattr` lists server EAs unless xattrs are disabled or the share is forced down.

## State and persistence behavior
Successful DOS attribute and creation-time writes update cached inode fields and invalidate `CIFS_I(inode)->time` to force revalidation. User EA and ACL writes persist remotely through SMB server operations. Local state includes XID allocation/freeing, tcon link references, temporary path pages, and allocated ACL buffers.

## Dependencies and integration points
The file depends on VFS xattr handlers, CIFS mount flags, dentry path construction, server operation vectors (`set_file_info`, `set_EA`, `query_all_EAs`, `get_acl`, `set_acl`), security descriptor definitions, and CIFS inode private state.

## Risks and test signals
The security descriptor get path stores `-ERANGE` in an unsigned `u32 acllen` before assigning to `rc`, which deserves attention for signedness behavior. SACL access may require privileges on the server. Pseudo-xattrs bypass `NO_XATTR`, while ordinary user EAs honor it. Test signals should cover get/set/list with `user.*`, `os2.*`, DOS attributes, creation time, legacy and SMB3 ACL aliases, SACL/owner/full descriptor variants, small caller buffers, disabled xattrs, forced shutdown, and servers without EA/ACL operation support.
