# sources/distributed-fs/eos/mgm/acl/Acl.cc

Purpose: implements ACL parsing and permission-flag calculation for EOS MGM metadata. It converts `sys.acl`, `user.acl`, and token ACL strings into booleans consumed by FUSE capability issuance, namespace access checks, xattr authorization, quota/workflow permissions, and token issuance.

Important APIs and functions: constructors build ACLs from explicit strings, xattr maps, or a path lookup. `SetFromAttrMap` selects directory/file user ACLs based on `sys.eval.useracl`, merges file `sys.acl` into directory `sys.acl`, and obtains token ACLs. `Set` parses rules and computes flags like read/write/write-once/update/browse/delete/chmod/chown/quota/archive/prepare/token/sys-acl/xattr. `IsValid` validates ACL syntax with POSIX regexes. `ConvertIds` converts `u:`/`g:` rules between names and numeric IDs. `TokenAcl` derives a rule from `VirtualIdentity::token`. `AllowXAttrUpdate` checks whether a sys xattr can be modified.

Control flow: parsing splits ACLs by comma, resolves primary or secondary groups, builds match tags for UID/GID/name/egroup/key/everyone, and scans each permission character. Denials and reallows are tracked in arrays and reconciled after all matching rules so `+d` and `+u` can re-enable specific system ACL denials. Token ACLs replace normal ACLs entirely.

State and persistence: `Acl` instances are transient and store only computed booleans plus remembered ACL strings and user-ACL evaluation flags. Persistent ACL data lives in file/container xattrs and in tokens.

Dependencies and integration points: depends on `Mapping`, `StringConversion`, `Egroup`, global `gOFS`, `_attr_ls`, namespace xattr maps, and token objects on `VirtualIdentity`. `Server.cc` and `AccessChecker.cc` consume the computed booleans.

Risks: token path handling is counterintuitive: `TokenAcl` returns a permission rule when `ValidatePath(vid.scope)` is false and returns a restrictive root rule when true; this depends on the token API's return convention and deserves regression coverage. `Set` loops across secondary groups and can repeatedly apply user-specific rules for each group, so denial/reallow ordering is subtle. `mCanChown` is set true even under deny for `c`, matching the comment but surprising. Regex validation and parser behavior must stay aligned, including `wo`, `!`, and `+` combinations.

Test signals: tests should cover numeric/name ACL validation, conversion failures, secondary group matching, egroup matching, `z:` everyone rules, key rules, deny/reallow precedence, immutable `i`, write-once `wo`, sys-only permissions `A/X/p/t/q`, token ACL replacement and scope failures, file-level user ACL evaluation, and `AllowXAttrUpdate` for `sys.acl` versus other `sys.*`.
