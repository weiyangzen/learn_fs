# sources/distributed-fs/openafs/src/WINNT/afsd/fs_acl.c

## Purpose

`fs_acl.c` implements the ACL parser, serializer, mutator, cleanup, and validation helpers used by the `fs` command. It supports both traditional AFS ACL text and DFS ACL variants, including positive and negative lists, relative add/remove semantics, and numeric-name pruning through the protection server.

## Important APIs, Types, and Functions

Memory management is handled by `ZapAcl()` and `ZapList()`. `ParseAcl()` converts cache-manager ACL text into `struct Acl`; `EmptyAcl()` creates an empty ACL while preserving DFS metadata if present; `AclToString()` serializes an ACL into the wire/text form accepted by `VIOCSETAL`. `FindList()` locates entries case-insensitively. `ChangeList()` adds, replaces, relative-adds, relative-removes, denies, or destroys rights. `PruneList()` removes zero or `-1` entries. `CleanAcl()` removes bad numeric usernames for AFS ACLs, using `BadName()` and PRDB lookups.

## Control Flow

Parsing reads the plus count and optional `dfs:<type> <cell>` tag, skips to the minus count, then allocates plus and minus entries from successive lines. On partial parse failure it frees any entries already allocated. Mutation first searches the selected list; existing entries are updated according to `rtype`, then pruned. New entries are inserted at list head unless the operation is a relative delete of a non-existing entry. Serialization writes counts and optional DFS metadata, then appends plus and minus entries as `name rights` lines.

## State and Persistence Behavior

The module owns heap-allocated `Acl` and `AclEntry` objects during command execution. It has no durable storage by itself; persistence happens when `fs.c` sends serialized ACL text back to the cache manager. `AclToString()` uses a static `AFS_PIOCTL_MAXSIZE` buffer, so callers must consume or copy it before the next serialization call.

## Dependencies and Integration Points

It depends on AFS constants and rights bits, Windows string-safety APIs, `afs/ptuser.h` and `afs/ptserver.h` for name validation, `cm_GetConfigDir()` for PRDB configuration, and `fs_acl.h` for structure definitions. Its primary consumer is `fs.c` ACL subcommands.

## Risks and Edge Cases

ACL text is trusted only after bounded string length checks, but the code still exits the process on string-copy failures. `AclToString()` can overflow logically if too many entries fit in memory but not in one pioctl buffer; it exits on `StringCbCat()` failure. `BadName()` has an uninitialized `code` path when no cell name is provided, which can make numeric-name validation undefined. DFS cleanup is intentionally skipped, and DFS invalid combinations are mostly discovered only when the cache manager/fileserver rejects the stored ACL.

## Test Signals

Tests should cover empty input, malformed counts, truncated plus/minus lists, AFS and DFS ACL parse/serialize round trips, `read`/`write`/`all`/`none`/`null` conversions via `fs.c`, relative add/remove pruning, negative rights, duplicate names with case differences, large ACLs near `AFS_PIOCTL_MAXSIZE`, numeric-name cleanup with valid and anonymous PRDB results, and parse-failure memory cleanup.
