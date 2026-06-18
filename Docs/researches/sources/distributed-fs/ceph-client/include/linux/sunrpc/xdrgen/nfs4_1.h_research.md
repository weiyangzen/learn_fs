# sources/distributed-fs/ceph-client/include/linux/sunrpc/xdrgen/nfs4_1.h

Purpose: generated XDR type and size definitions for selected NFSv4.1 protocol extensions, including delegation-time attributes, OPEN argument metadata, and POSIX ACL extension attributes.

Important APIs and types: defines aliases `int64_t`, `uint32_t`, `bitmap4`, UTF-8 string aliases, `struct nfstime4`, `fattr4_offline`, and `struct open_arguments4`. Enums define OPEN share access/deny/want, open claim, create mode, delegation types, ACL model/scope, and POSIX ACE tags. `struct posixace4` holds tag, permissions, and `who`; default/access ACL arrays hold `posixace4` elements. Attribute numbers include `FATTR4_OFFLINE`, `FATTR4_TIME_DELEG_ACCESS`, `FATTR4_TIME_DELEG_MODIFY`, `FATTR4_OPEN_ARGUMENTS`, and POSIX ACL attributes. Size macros compute XDR word counts for each generated type.

Control flow: generated encoder/decoder code and NFS protocol code include this header to allocate structs, validate enum values, and size XDR buffers for these attributes.

State and persistence: no runtime state; structures represent decoded or to-be-encoded protocol payloads.

Dependencies and integration points: depends on `_defs.h` and kernel types. It is generated from `Documentation/sunrpc/xdr/nfs4_1.x`, so manual edits would be overwritten.

Risks and test signals: risks include generated file/spec drift, incorrect array maximum assumptions, enum value mismatch with NFS protocol, and stale size macros. Test with xdrgen regeneration, NFSv4.1 OPEN/delegation/POSIX ACL vectors, and interoperability with NFS servers/clients advertising these attributes.
