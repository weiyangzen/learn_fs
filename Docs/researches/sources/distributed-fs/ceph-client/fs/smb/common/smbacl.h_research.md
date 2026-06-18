# sources/distributed-fs/ceph-client/fs/smb/common/smbacl.h

Purpose: defines shared SMB/CIFS security descriptor, SID, ACL, and ACE wire structures plus constants for ACE types and inheritance/audit flags. It is used by SMB client and server code that translates between Windows security descriptors and Linux ownership/mode/ACL state.

Important APIs/types/functions: constants include `NUM_AUTHS`, `SID_MAX_SUB_AUTHORITIES`, many MS-DTYP ACE type values, ACE flags such as `OBJECT_INHERIT_ACE` and `INHERITED_ACE`, SID string sizing macros, and SID role identifiers such as `SIDOWNER`, `SIDGROUP`, `SIDUNIX_USER`, and `SIDNFS_MODE`. The key packed wire structs are `struct smb_ntsd` for a self-relative NT security descriptor, `struct smb_sid`, `struct smb_acl`, and `struct smb_ace`.

Control flow: there is no executable flow. Consumers parse a security descriptor by reading `struct smb_ntsd`, using the owner/group/SACL/DACL offsets to locate `struct smb_sid` and `struct smb_acl`, and then iterating `struct smb_ace` entries according to the ACL header's `num_aces` and each ACE's `size`.

State and persistence behavior: the header defines transient wire formats. Security information may persist later as Linux ACLs, modes, xattrs, or filesystem metadata, but this file itself owns no state. The packed layout and little-endian fields are the persistence-sensitive pieces.

Dependencies and integration points: integrates with KSMBD ACL handling, CIFS ACL handling, SMB xattr storage for NT security descriptors, and ID/SID mapping code. It depends on Linux fixed-width and endian integer types and the protocol guarantee that SID subauthorities are bounded by `SID_MAX_SUB_AUTHORITIES`.

Risks: the variable-length `sub_auth[num_subauth]` and ACE `size` fields require strict bounds checks in consumers; trusting the packed struct size alone can overread malformed client data. SID string sizing must stay aligned with conversion helpers to avoid truncation. Adding unsupported ACE types without explicit handling can accidentally grant or drop access.

Test signals: exercise parsing and encoding of owner/group SIDs, DACLs with allow/deny entries, inherited ACE flags, oversized or malformed SID subauthority counts, ACLs with unknown ACE types, and round trips through SMB create/get-security/set-security paths with xattr-backed ACL storage.
