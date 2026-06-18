# sources/distributed-fs/eos/mgm/auth/AccessChecker.cc

Purpose: implements stateless metadata access decisions for containers, files, and public anonymous paths. It combines POSIX mode checks with `Acl` flags and special EOS identity rules.

Important APIs and functions: `checkContainer(IContainerMD*, XAttrMap, mode, vid)` builds an `Acl` and delegates to `checkContainer(IContainerMD*, Acl, mode, vid)`. The main container check handles root, daemon read/browse, immutable ACLs, prepare permission, sticky-bit delete rules, POSIX access, and ACL recovery/denial. `checkFile` enforces sticky parent deletion and file execute/browse bits. `checkPublicAccess` gates anonymous/public access based on `eosnobody`, protocol `sss`, squash files, and configured public access depth.

Control flow: container access first applies early allow/deny rules, then performs a POSIX access check unless token identity is present. If POSIX fails and ACLs exist, it tests requested write/read/execute bits against positive and negative ACL flags. File checks are intentionally narrower and currently only inspect execute permission except deletion.

State and persistence: no mutable state or persistence. It reads metadata fields, xattr-derived ACLs, and global mapping/public-access configuration.

Dependencies and integration points: depends on `Acl`, `common/Definitions.hh` permission bits such as `P_OK` and `D_OK`, `IFileMD`, `IContainerMD`, `common::Path`, and `Mapping`. It provides a lower-level authorization utility used by MGM code paths outside direct FUSE capability issuance.

Risks: token identities bypass POSIX checks and rely entirely on ACL evaluation; consumers must pass a token-derived ACL scope correctly. File access does not evaluate file ACLs, only mode bits for browse and parent container checks elsewhere. Sticky-bit delete logic is split between container and file checks, so both must be called for complete semantics.

Test signals: tests should cover root/daemon shortcuts, immutable ACL write denial, prepare permission, sticky directory delete for owner/non-owner, ACL positive recovery after POSIX denial, explicit ACL denials overriding mode bits, token behavior, file execute bit matrix, eosnobody squash access, and public access depth.
