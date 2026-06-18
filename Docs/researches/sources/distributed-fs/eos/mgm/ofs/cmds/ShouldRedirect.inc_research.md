## sources/distributed-fs/eos/mgm/ofs/cmds/ShouldRedirect.inc

Purpose: decides whether a request should be redirected to another MGM endpoint based on configured access redirection rules and the request access mode.

Important APIs and types: `XrdMgmOfs::ShouldRedirect`, `Access::gAccessMutex`, `Access::gRedirectionRules`, access-mode macros such as `IS_ACCESSMODE_R`, `IS_ACCESSMODE_W`, `IS_ACCESSMODE_R_MASTER`, `VirtualIdentity`, and `MgmStats`.

Control flow: localhost and root are exempt when this MGM is master or the request is read-only. With redirection rules present, the function checks global `*`, write `w:*`, read `r:*`, and read-master fallback to `w:*` in precedence order. It tokenizes the selected `host[:port[:delay_ms]]` value, applies default port `1094` for host-only rules, optionally sleeps for a configured delay, records stats by rule type, sets `collapse=true`, and returns true. If no matching rule exists it returns false.

State and persistence behavior: no persistent state changes. It reads global redirection config under the access mutex and records stats counters. The optional delay intentionally blocks the request thread before returning redirect.

Dependencies and integration points: invoked through `MAYREDIRECT` macros in command handlers. Depends on administrator-managed `Access` static state and XRootD redirect response construction by the caller.

Risks: malformed token lists larger than three are silently ignored after setting `collapse=true` and returning true, potentially leaving host/port unchanged. Port parsing uses `strtol` without range validation. Delay is performed while holding the access read lock, which can block config writers and other readers depending on RW lock implementation.

Test signals: localhost/root exemptions, global/read/write/read-master rule selection, host-only default port, host/port parsing, delay handling, empty/malformed rule token behavior, stats counter names, and `collapse` output state.
