# sources/distributed-fs/eos/mgm/acl/Acl.hh

Purpose: declares `eos::mgm::Acl`, a compact interpreter for EOS ACL strings stored in metadata xattrs or carried by tokens. The class exposes permission booleans used by authorization code.

Important APIs and types: four regex constants describe generic/numeric user and system ACL syntax. Static helpers `IsValid` and `ConvertIds` validate and normalize ACL strings. Constructors accept explicit sys/user ACLs, xattr maps, or a path plus error object. `SetFromAttrMap` and `Set` recompute state. Inline getters expose all permission flags, original/effective ACL strings, and whether user ACLs were evaluated. `TokenAcl` extracts token permissions. `AllowXAttrUpdate` authorizes ACL/sys xattr updates.

Control flow: callers construct an `Acl` near the access decision, then inspect getters. `SetFromAttrMap` is the preferred path when metadata xattrs are already available and avoids another namespace lookup.

State and persistence: instance state is a set of booleans and cached ACL strings; no persistence is performed by the header. Xattrs and tokens are the durable sources.

Dependencies and integration points: includes namespace macros, identity mapping, container/file metadata interfaces, and `XrdOucErrInfo` forward declaration. Used by `AccessChecker` and `FuseServer::Server`.

Risks: many permissions are represented as independent booleans, so new rights require updates in constructors, parser, getters, debug output, validators, and consumers. Inline `TokenAcl` declaration hides a nontrivial implementation in the `.cc`. The public API exposes both positive and negative flags, and consumers must apply denial precedence consistently.

Test signals: compile tests should ensure all regex constants remain valid POSIX extended regexes; behavior tests should instantiate from xattr maps and confirm getters used by `Server`/`AccessChecker` reflect expected effective rights.
