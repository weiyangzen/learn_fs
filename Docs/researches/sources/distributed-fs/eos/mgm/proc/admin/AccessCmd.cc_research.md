# Research: sources/distributed-fs/eos/mgm/proc/admin/AccessCmd.cc

## Purpose

`AccessCmd.cc` implements the protobuf access-control command. It is the newer replacement for legacy `ProcCommand::Access()`, providing structured `ls`, `set`, `rm`, `ban`, `unban`, `allow`, `unallow`, and `stallhosts` subcommands over `AccessProto`.

## Important APIs, Types, and Functions

- `ProcessRuleKey()` normalizes `threads:<target>` keys, converting username targets to uid strings while allowing `max` and `*`.
- `AccessCmd::ProcessRequest()` enforces access-admin privileges and dispatches by `AccessProto::subcmd_case()`.
- `LsSubcmd()` emits banned/allowed users/groups/hosts/domains/tokens, redirect rules, stall rules/comments, stall-host whitelist, and no-stall blacklist.
- `SetSubcmd()` sets redirect, stall, rate, or thread-limit rules.
- `RmSubcmd()` removes redirect, stall, rate, or thread-limit rules and cleans comments.
- `BanSubcmd()`, `UnbanSubcmd()`, `AllowSubcmd()`, and `UnallowSubcmd()` mutate corresponding sets.
- `StallhostsSubcmd()` manages mutually exclusive stall and no-stall host-pattern sets.
- `aux()` persists config and writes common success/error messages after set mutations.

## Control Flow

`ProcessRequest()` first allows only root, admin uid, admin gid, or sudoer identities. It then switches on the structured subcommand. Read-only listing takes a read lock and iterates every access-control collection. Mutating commands take a write lock, validate enum/input fields, mutate `Access` globals, release the write lock, then call `StoreAccessConfig()` through `aux()` or an inline read-lock block.

`SetSubcmd()` validates redirect keys against global/read/write/network-error keys. Stall and limit rules must parse as integer targets; zero is allowed only for `rate:` limits. For `rate:user:`, `rate:group:`, and `threads:` keys it stores the normalized `ProcessRuleKey()` output. Otherwise it stores global or key-suffixed rules like `r:*`.

`RmSubcmd()` mirrors `set` and removes both normalized and original `threads:` keys to cover an old bug. Ban/allow operations convert users/groups through `Mapping` before inserting uid/gid sets, while hosts/domains/tokens are strings. Unban/unallow verify membership before erasing.

## State and Persistence Behavior

State is stored in `Access` static sets/maps guarded by `Access::gAccessMutex`. Mutations are intended to persist through `Access::StoreAccessConfig()` after releasing the write lock and reacquiring a read lock. Rule comments are stored in `Access::gStallComment` using the request comment from `mReqProto.comment()`.

Token allow/ban sets and stall/no-stall host sets are covered in this protobuf path. Thread-limit normalization persists uid-based keys when possible and erases old username keys on removal.

## Dependencies and Integration Points

The file depends on `AccessCmd.hh`, `ProcInterface` for proc context, `XrdMgmOfs` for stats, `mgm/access/Access`, `MgmStats`, `Mapping`, `StringUtils::trim`, and common constants. It is constructed by `ProcInterface` for `RequestProto::kAccess`, which is centrally admin-gated before handler construction.

## Risks and Edge Cases

- `LsSubcmd()` appears to invert `id2name()` naming: when `id2name()` is true it prints `UidAsString()`/`GidAsString()`, otherwise it tries name lookup. Tests should lock in intended CLI semantics.
- Some `StallhostsSubcmd()` paths call `aux()` even after setting an error return, and the `NOSTALL` `ADD` branch calls `aux()` unconditionally after release; this can persist and report success wording alongside an error state if not carefully interpreted.
- `RmSubcmd()` accepts any non-empty stall key in the existence check, then erases computed variants; removing a non-existent arbitrary key can still persist and report success.
- The command has a defense-in-depth admin check, but central `ProcInterface` also gates `kAccess`; both predicates should remain consistent.
- Persistence failures after in-memory mutation leave changed runtime state even if config storage failed.

## Test Signals

Tests should cover all enum variants, privilege refusal, monitoring versus normal listing, id/name output, token allow/ban, `threads:<username>` conversion and malformed usernames, set/rm redirect keys, rate limit zero/nonzero rules, stall comments, stale username thread-key cleanup, stall/no-stall mutual exclusion, and `StoreAccessConfig()` failure handling. Cross-tests with legacy `Access.cc` should cover expected compatibility and known differences.
