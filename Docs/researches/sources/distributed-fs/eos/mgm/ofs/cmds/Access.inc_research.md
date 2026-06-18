# Research: sources/distributed-fs/eos/mgm/ofs/cmds/Access.inc

## Purpose

`Access.inc` implements access checking and access-right derivation for EOS MGM paths. It handles the public XRootD `access()` entry point, lower-level `_access()` checks against namespace metadata, ACL/POSIX permission interpretation, token-issuer permission, OC-style access string generation, anonymous/public access restrictions, squashfs special access, and a coarse `GetXrdAccPrivs()` bridge for XRootD authorization.

## Important APIs, Types, and Functions

- `XrdMgmOfs::access()` performs namespace mapping, external authorization, identity mapping, token/access-mode guards, stall/redirect handling, and delegates to `_access()`.
- `XrdMgmOfs::_access()` checks file or directory existence, parent-directory fallback for files and non-existing entries, `sys.owner.auth`, `Acl`, `AccessChecker::checkContainer()`, `AccessChecker::checkFile()`, token-issuer permission via `T_OK`, root/daemon override, and public access restrictions.
- `XrdMgmOfs::acc_access()` returns an OC permission string such as `R`, `WCKNV`, and `D` based on POSIX bits plus ACLs.
- `is_squashfs_access()` and `allow_public_access()` implement `eosnobody`/squashfs and anonymous-depth restrictions.
- `GetXrdAccPrivs()` performs basic mapping and currently returns `XrdAccPriv_All` after coarse checks.

## Control Flow

The high-level entry point maps `inpath` through `NAMESPACEMAP`, checks illegal names and external authorization, maps the client to `VirtualIdentity`, enforces global access restrictions, and invokes `_access`. `_access` first prefetches the requested item, tries file and container lookups, and if it is a file or non-existing child, switches the authorization object to the parent directory while optionally carrying file xattrs into the ACL.

The main permission path evaluates `sys.owner.auth` before ACL/POSIX checks, constructs `Acl`, locks the container to read mode and ownership, rejects token issuance for non-owners unless ACL allows it, then checks container and file permission. Deletion has a special path where `!d` can be overridden for a file owner. If metadata is missing, it returns `ENOENT`; if the directory exists but permission fails, it returns `EACCES`.

`acc_access()` uses similar metadata discovery but computes boolean capabilities for read, write/create, execute/browse, and delete, merging secondary groups when configured and applying ACL mutable/delete/write-once semantics.

## State and Persistence Behavior

The file does not modify namespace metadata. It reads file/container attributes, ownership, mode bits, secondary-group mappings, public-access config, and static cached `eosnobody` uid. It increments `MgmStats` counters for identity mapping, access, and redirect decisions. Permission decisions are transient, but they are consumed by mutating operations throughout OFS.

## Dependencies and Integration Points

Dependencies include `Mapping::IdMap`, `Acl`, `AccessChecker`, `eos::Prefetcher`, `eosView`, namespace metadata locks, `XrdMgmOfsSecurity.hh` macros, token-scope/access-mode macros, public access mapping, and XRootD `XrdAccPrivs`. It is a core integration point for mkdir, symlink, find, FUSE/FSctl paths, token issuance, and any command that calls `_access()`.

## Risks and Edge Cases

- File permission checks use parent directory ACLs plus file attributes. Ordering around `sys.owner.auth` is security-sensitive and intentionally mirrors open/mkdir behavior.
- `_access` allows root all access and daemon read-only access; regression here would affect internal services.
- `F_OK` succeeds if the directory metadata object exists, even when `permok` is false.
- Public access restrictions are checked only in some terminal paths; callers relying on `_access` need to understand when anonymous depth limits apply.
- `GetXrdAccPrivs()` currently returns all privileges after basic checks, so it should not be mistaken for a fine-grained authorization decision.

## Test Signals

Tests should cover file versus directory checks, missing child parent checks, ACL read/write/write-once/browse/delete/chmod/token combinations, `sys.owner.auth` keyed and sticky cases, file-owner delete despite `!d`, root and daemon behavior, anonymous public-depth denial, `eosnobody` squashfs allow/deny, secondary groups, token identity, and OC permission string output.
