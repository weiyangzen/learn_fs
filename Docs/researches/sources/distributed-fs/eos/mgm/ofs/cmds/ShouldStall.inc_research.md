## sources/distributed-fs/eos/mgm/ofs/cmds/ShouldStall.inc

Purpose: enforces request stalls or delays for banned identities, global/read/write stall rules, per-user/per-group rate rules, and thread-pool saturation.

Important APIs and types: `XrdMgmOfs::ShouldStall`, `Access::gBannedUsers`, `gBannedGroups`, `gBannedHosts`, `gBannedDomains`, `gBannedTokens`, `gStallRules`, `gStallComment`, `gStallGlobal`, `gStallRead`, `gStallWrite`, `gStallUserGroup`, `MgmStats`, `mTracker.ShouldStall`, and `VirtualIdentity`.

Control flow: initially stalling is enabled, then disabled for booted FST daemon SSS clients and for HTTPS unless `EOS_MGM_ALLOW_HTTP_STALL` is set. Under `Access::gAccessMutex`, non-root users above uid 3 and non-stat/non-no-stall-app requests first check per-uid thread saturation, then banned user/group/host/domain/token lists, then global/read/write stall rules, then user/group rate rules. Rate rules match exact and wildcard user/group prefixes and optionally fine-grained Eosxd command names. If a hard stall applies, it adds a random 0-5 second offset unless the stall is rate-limit delay mode, builds a user message, records stats, and returns true. If a rate limit has a finite cutoff but is not a hard saturation, it releases the access lock, sleeps for a computed millisecond delay capped at 40s, records delay stats, and returns false.

State and persistence behavior: no persistent mutation. It reads access policy state, MgmStats moving averages, environment variables, and thread tracker state. It records stall/delay counters and may sleep the current request thread.

Dependencies and integration points: called by `MAYSTALL` macros in most MGM operations. FUSE clients receive immediate true/error-style responses for banned user/group cases instead of long stalls. Localhost root/admin can still be affected by global boot/write stall semantics.

Risks: sleeping request threads can affect thread-pool pressure; the code caps delay but hard stalls may still be long. Several branches depend on string prefixes such as `fuse` and `Eosxd`. The read lock is manually released before delay sleep, so changes after rule evaluation do not cancel the delay. The stat command and a configured FUSE no-stall app bypass many user-level rules.

Test signals: FST daemon bypass, HTTPS bypass and environment override, banned user/group/host/domain/token, FUSE banned behavior, global/read/write stalls, user/group exact and wildcard rate rules, Eosxd command-specific matching, saturated thread stalls with random offset, delay-mode cap at 40s, and localhost/root global stall behavior.
