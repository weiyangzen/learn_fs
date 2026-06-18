## sources/distributed-fs/eos/mgm/ofs/cmds/ShouldRoute.inc

Purpose: delegates path-based request routing decisions to the MGM routing subsystem, supporting reroute and stall responses.

Important APIs and types: `XrdMgmOfs::ShouldRoute`, `PathRouting::Reroute`, `PathRouting::Status::{REROUTE,STALL}`, `VirtualIdentity`, and `MgmStats`.

Control flow: root and localhost clients are never routed. If `mRouting` is null, which can happen during shutdown, the request is not routed. Otherwise `mRouting->Reroute()` receives path, opaque info, identity, and output host/port/stat string. `REROUTE` records the returned stat counter and returns true; `STALL` sets `stall_timeout=5` seconds and returns true; all other statuses return false.

State and persistence behavior: no persistence. It reads routing configuration through `mRouting` and increments stats when reroute occurs.

Dependencies and integration points: used by MGM request front-door logic around path routing. Caller must interpret true plus host/port as reroute or true plus `stall_timeout` as stall. It is separate from static access redirection rules in `ShouldRedirect.inc`.

Risks: a `STALL` result returns true without setting host/port, so callers must branch on `stall_timeout`. Stall duration is hardcoded to 5 seconds. Routing is disabled for privileged/local identities even if rules would otherwise match.

Test signals: root/localhost bypass, null-routing bypass during shutdown, reroute host/port propagation and stat increment, stall timeout behavior, and no-route fallback.
