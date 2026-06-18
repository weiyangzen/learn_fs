# sources/distributed-fs/eos/mgm/utils/AttrHelper.cc

## Purpose
Implements small attribute-policy helpers used by MGM write paths for owner impersonation, atomic uploads, versioning, and xattr retrieval.

## Important APIs, types, and functions
`checkDirOwner()` evaluates `sys.auth.owner`, including sticky `*` and protocol-qualified identity keys. `checkAtomicUpload()` evaluates `sys.forced.atomic`, `user.forced.atomic`, then CGI fallback. `getVersioning()` evaluates CGI first, then system and user versioning attributes. `getValue()` returns string xattr values by key.

## Control flow
Directory-owner checks build an owner key from `vid.prot` plus either DN for GSI or `uid_string` for other protocols. Comma padding anchors list matching to avoid prefix collisions. On a non-sticky match, the virtual identity is rewritten to the directory uid/gid. Atomic and versioning helpers parse numeric strings with configured precedence.

## State and persistence behavior
No state is persisted. The only mutation is to the caller-provided `VirtualIdentity` and `sticky_owner` output flag.

## Dependencies and integration points
Uses MGM constants such as `SYS_OWNER_AUTH`, `SYS_FORCED_ATOMIC`, `USER_FORCED_ATOMIC`, `SYS_VERSIONING`, and `USER_VERSIONING`; `StringToNumeric`; and EOS logging. It is consumed by request paths evaluating inherited directory xattrs.

## Risks and test signals
`checkAtomicUpload()` treats the mere presence of `atomic_cgi` as true, regardless of its value. Numeric parse failures leave defaults. Sticky owner does not rewrite the VID by design. Tests should cover anchored owner matching, GSI DN versus uid string keys, sticky behavior, parse failures, precedence order, and CGI values like `"0"`.
