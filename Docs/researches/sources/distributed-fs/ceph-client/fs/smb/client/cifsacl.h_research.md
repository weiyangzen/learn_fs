# sources/distributed-fs/ceph-client/fs/smb/client/cifsacl.h

Purpose: defines CIFS ACL constants and packed SMB3 security descriptor structures used by ACL parsing and synthesis. It bridges common SMB ACL wire definitions with client-local mode masks and special SID helper layouts.

Important APIs and types: defines permission masks `READ_BIT`, `WRITE_BIT`, `EXEC_BIT`, `ACL_OWNER_MASK`, `ACL_GROUP_MASK`, `ACL_EVERYONE_MASK`, `UBITSHIFT`, `GBITSHIFT`, `DEFAULT_SEC_DESC_LEN`, `MIN_SID_LEN`, and `MIN_SEC_DESC_LEN`. It declares packed wire-compatible `struct smb3_sd`, `struct smb3_acl`, `struct owner_sid`, and `struct owner_group_sids`, plus ACL control flags such as `ACL_CONTROL_SR`, `ACL_CONTROL_DP`, and ACL revision constants.

Control flow: this header has no executable flow. It is included by `cifsacl.c` and globally through `cifsglob.h`, so its constants guide DACL building, chmod mode mapping, SMB3 security descriptor parsing, and special S-1-5-88 owner/group persistence.

State and persistence behavior: the packed structs describe persistent on-the-wire or server-stored data, especially self-relative SMB3 security descriptors and special NFS-style owner/group SIDs. The macros set local buffer sizing assumptions for constructing security descriptors in memory before sending them to the server.

Dependencies and integration points: includes `../common/smbacl.h` for shared `smb_ntsd`, `smb_acl`, `smb_ace`, and `smb_sid` definitions. It is consumed by ACL code, SMB2/SMB3 create/query/set-info paths, and the broader CIFS global declarations that need ACL type names.

Risks: these packed structures must stay aligned with MS-DTYP/MS-SMB2 field order and endianness. `DEFAULT_SEC_DESC_LEN` is only a conservative construction size for common owner/group/world descriptors; callers that add inherited or special ACEs must size larger. Changing mask constants would alter chmod/chown semantic translation across the client.

Test signals: compile-time packed layout checks if added, ACL round trips against Windows/Samba security descriptors, chmod/chown buffer sizing with four or more ACEs, special owner/group SID persistence, and static analysis for endian annotations on the SMB3 descriptor fields.
