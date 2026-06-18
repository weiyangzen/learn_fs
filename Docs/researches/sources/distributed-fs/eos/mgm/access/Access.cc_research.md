# sources/distributed-fs/eos/mgm/access/Access.cc

Purpose: implements global MGM admission-control configuration: banned and allowed users/groups/hosts/domains/tokens, stall rules, redirection rules, stall host filters, find limits, and thread limits. These rules are read by higher-level MGM request handling such as stall and redirect decisions.

Important APIs and functions: static storage is defined for all sets/maps declared in `Access.hh`, protected by `gAccessMutex`. `Reset` clears in-memory rules; `EnforceConfig` loads serialized global config from `FsView::gFsView`; `StoreAccessConfig` serializes current rules back; `GetFindLimits` derives rate limits from `rate:*` stall rules; `SetStallRule`, `RemoveStallRule`, `SetSlaveToMasterRules`, and `SetMasterToSlaveRules` mutate stall/redirection state; `ThreadLimit` resolves per-user and global thread caps; `CanStall` applies regex-based host allow/deny lists.

Control flow: config loading tokenizes colon-separated lists for identities/hosts and comma/tilde-separated entries for stall/redirection rules. Applying redirect/stall can be disabled while still keeping rate/thread rules. Store reverses the process and escapes commas/tildes in stall comments with sentinel strings.

State and persistence: in-memory static sets/maps are authoritative during runtime; persistence is the MGM global configuration store through `FsView::gFsView.GetGlobalConfig` and `SetGlobalConfig`. Atomic booleans cache the presence of global/read/write/user-group stall rules for fast checks.

Dependencies and integration points: depends on `FsView`, `StringConversion`, POSIX regex, and `Mapping` for UID/GID string conversion. Failover hooks adjust access rules when transitioning between master and slave roles.

Risks: serialization is hand-rolled and delimiter-based; malformed values are mostly ignored or parsed as zero by `atoi`. `StoreAccessConfig` appears to append banned domains into `hostval` rather than `domainval`, which could drop or misstore domain bans. `SetStallRule` sets `gStallGlobal` from the supplied `mIsGlobal` without recomputing read/write/user-group flags. `CanStall` assumes the caller already holds the read lock, so misuse can race with config updates.

Test signals: tests should round-trip every global config key, especially domains/tokens/comments with escaped delimiters; verify master/slave transition side effects; check per-user/group/wildcard find limits; exercise `CanStall` whitelist and blacklist regex behavior; and confirm thread limits under explicit and default rules.
