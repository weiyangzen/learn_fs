# Research: sources/distributed-fs/eos/mgm/proc/admin/Access.cc

## Purpose

`Access.cc` implements the legacy CGI `/proc/admin access` command through `ProcCommand::Access()`. It manages access-control allow/ban lists, global redirection rules, stall/rate rules, and listing output by mutating or reading static state in `mgm/access/Access`.

## Important APIs, Types, and Functions

- `ProcCommand::Access()` is the only function in this file.
- Input CGI keys include `mgm.access.user`, `group`, `host`, `domain`, `option`, `redirect`, `stall`, and `type`.
- `mSubCmd` selects `ban`, `unban`, `allow`, `unallow`, `set`, `rm`, or `ls`.
- Shared state includes `Access::gBannedUsers`, `gBannedGroups`, `gBannedHosts`, `gBannedDomains`, allowed equivalents, `gRedirectionRules`, `gStallRules`, and `gStallComment`.
- Persistence is through `Access::StoreAccessConfig()`.

## Control Flow

The function parses CGI fields into local strings, derives `monitoring` from option `m`, and disables id-to-name translation when option `n` is present. For `ban` and `allow`, it converts usernames/groups to uid/gid and inserts entries into the appropriate sets; hosts and domains are inserted directly. For `unban` and `unallow`, it validates membership before erasing. Each mutation is protected by `Access::gAccessMutex` and immediately calls `StoreAccessConfig()`.

The `set` branch handles either redirection or stall/rate rules. Redirection supports global `*` plus `r`, `w`, `ENONET`, `ENOENT`, and `ENETUNREACH` keys. Stall supports those keys and `rate:user:`/`rate:group:` rules, validates the integer threshold, stores optional comments from `mComment`, and persists. The `rm` branch removes corresponding redirect or stall rules.

The `ls` branch takes a read lock and emits all non-empty lists. Output can be human-oriented with section headers and counters or monitoring-oriented with `key=value` lines. Numeric uid/gid or name translation is controlled by `translate`.

## State and Persistence Behavior

All meaningful state lives in `Access` static containers and is guarded by `Access::gAccessMutex`. Mutations call `Access::StoreAccessConfig()` while still under the write lock in this legacy implementation. The command writes result state into the `ProcCommand` fields `stdOut`, `stdErr`, and `retc`.

The file does not include token allow/ban handling or thread-limit key normalization present in the newer protobuf `AccessCmd` path.

## Dependencies and Integration Points

The implementation depends on `XrdOucEnv`, `XrdMgmOfs` for stats, `mgm/access/Access.hh` for global access state, `MgmStats`, and `Mapping` helpers for username/group conversion. It integrates with the legacy `ProcCommand` dispatcher and the stored access configuration consumed by runtime access checks elsewhere in MGM.

## Risks and Edge Cases

- `set` uses `atoi()` for stall/rate parsing, so malformed numeric strings can become zero; the protobuf path uses `std::stoi()` and is stricter.
- Every individual user/group/host/domain operation persists immediately, so a command with multiple fields can partly succeed before a later field fails.
- Rate rules are accepted only for `rate:user:` and `rate:group:`; old string handling does not normalize usernames to uid and may leave stale rule variants.
- Listing typo `"Allowd Users"` is client-visible legacy output.
- Holding the write lock while calling `StoreAccessConfig()` may increase contention or risk lock-order issues depending on storage internals.

## Test Signals

Regression tests should cover each subcommand with user/group/host/domain, missing users/groups, duplicate removals, redirect/stall/rate set and remove, monitoring output, numeric output option `n`, persistence failure handling, and compatibility with existing config files. Cross-plane tests should compare legacy behavior with `AccessCmd` for equivalent operations and document intentional differences.
