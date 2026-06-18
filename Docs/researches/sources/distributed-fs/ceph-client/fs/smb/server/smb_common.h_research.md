## sources/distributed-fs/ceph-client/fs/smb/server/smb_common.h

Purpose: declares common SMB server constants, wire helper structs, protocol-version operation tables, and cross-module helpers shared by ksmbd negotiation, command dispatch, VFS access checks, and directory response formatting.

Important APIs and types: defines protocol indexes (`SMB1_PROT` through `SMB311_PROT`, `BAD_PROT`), open disposition response constants, generic/read/write/execute/all access bit expansions, SMB1 negotiate flags, `struct smb_negotiate_rsp`, `struct fs_extended_info`, `struct object_id_info`, directory info wire structs, `struct smb_version_ops`, and `struct smb_version_cmds`. It declares negotiation, dialect lookup, message validation, short-name, share-mode, credential override, server-side-copy limit, and generic access mapping functions. `smb_get_msg` strips the four-byte RFC1002 header.

Control flow: the header has no active control flow, but `smb_version_ops` is the dispatch contract installed on `struct ksmbd_conn`; command processing calls its callbacks for command id extraction, response allocation/header initialization, session/tcon lookup, signing, encryption, and transform handling. Access-mask macros are consumed before permission and share-mode checks.

State and persistence behavior: all state named here is runtime state owned by connections, sessions, work items, files, or VFS objects. The packed structs describe wire or metadata layouts but are not themselves persistent storage in this header.

Dependencies and integration points: includes ksmbd global headers plus SMB1, SMB2, and FSCC protocol definitions. It is central to `smb_common.c`, SMB2 PDU handling, directory enumeration, VFS file open checks, signing/encryption setup, and server-side copy FSCTL handling.

Risks: packed wire structs and endian-tagged access masks must stay aligned with protocol definitions. The ops table contains security-critical hooks; a partially initialized connection could skip signing, session validation, or encryption. `smb_get_msg` assumes a valid RFC1002-prefixed buffer, so callers must validate buffer length separately.

Test signals: build coverage across SMB1-disabled and enabled configurations, protocol negotiation for every dialect constant, response header initialization, access-mask mapping against Windows generic rights, and command dispatch paths that exercise every non-NULL `smb_version_ops` callback.
