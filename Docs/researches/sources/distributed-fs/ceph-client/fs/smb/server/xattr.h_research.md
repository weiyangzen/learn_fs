## sources/distributed-fs/ceph-client/fs/smb/server/xattr.h

Purpose: defines ksmbd/Samba-compatible xattr metadata layouts and names used to persist Windows filesystem semantics on POSIX filesystems.

Important APIs and types: defines DOS attribute validity flags and `struct xattr_dos_attrib`, POSIX ACL hash tags and permission bits, `struct xattr_acl_entry`, flexible `struct xattr_smb_acl`, NTACL hash constants, `struct xattr_ntacl`, and xattr names/prefixes for DOS attributes (`user.DOSATTRIB`), alternate streams (`user.DosStream.`), and security descriptors (`security.NTACL`).

Control flow: no active control flow. `vfs.c` encodes/decodes these structures through NDR helpers when storing DOS attributes, stream data, and NTACLs.

State and persistence behavior: the structures describe persistent xattr payloads. DOS attributes store Windows attribute bits, EA size, size/allocation, creation/change/initial times. NTACL xattrs store the security descriptor plus hashes of the descriptor and POSIX ACL state to detect drift. Stream prefixes map SMB alternate data streams to user xattrs.

Dependencies and integration points: used by VFS xattr helpers, SMB2 query/set info, ACL conversion, NDR encode/decode, Samba interoperability, and stream read/write/delete paths.

Risks: layout compatibility with Samba is explicitly required; field changes or name changes can make existing metadata unreadable. `XATTR_SD_HASH_SIZE` is 64 although the hash type is SHA-256, so encode/decode code must remain consistent. Stream xattrs are constrained by filesystem xattr size and namespace support.

Test signals: Samba interoperability for DOSATTRIB and NTACL, DOS attribute round trip, NTACL hash validation after POSIX ACL changes, alternate stream name construction, xattr namespace availability, and big-endian/little-endian NDR compatibility.
