<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/safesetid/lsm.c -->
# sources/distributed-fs/ceph-client/security/safesetid/lsm.c

## Purpose

`safesetid/lsm.c` implements SafeSetID enforcement. It restricts setuid/setgid/setgroups transitions for source IDs covered by policy and blocks non-setid uses of `CAP_SETUID` or `CAP_SETGID` for those constrained IDs.

## Important APIs, Types, and Functions

- `safesetid_initialized` gates later securityfs setup.
- `safesetid_setuid_rules` and `safesetid_setgid_rules` are RCU-protected active rulesets.
- `_setid_policy_lookup()` checks a supplied ruleset for default, constrained, or explicitly allowed source-to-destination transitions.
- `setid_policy_lookup()` selects the active UID or GID ruleset under RCU.
- `safesetid_security_capable()` constrains `CAP_SETUID`/`CAP_SETGID` uses outside setid syscall paths.
- `id_permitted_for_cred()` validates a candidate new UID/GID against old credentials and policy.
- `safesetid_task_fix_setuid()`, `safesetid_task_fix_setgid()`, and `safesetid_task_fix_setgroups()` enforce transitions after normal credential calculations.
- `safesetid_security_init()` registers hooks and schedules securityfs init.

## Control Flow

Policy lookup hashes by source ID. If a source has no rule, the result is `SIDPOL_DEFAULT`. If at least one rule for the source exists but no destination matches, the source is `SIDPOL_CONSTRAINED`. A matching destination is `SIDPOL_ALLOWED`. Capability checks ignore unrelated capabilities and allow `CAP_OPT_INSETID` paths to proceed to the later transition hooks. For other `CAP_SETUID` or `CAP_SETGID` uses, a constrained source ID is denied so it cannot use those capabilities for user namespace mappings or other auxiliary operations.

The setuid/setgid hooks first skip enforcement when the old real ID has no policy. Otherwise every new real, effective, saved, and filesystem ID must either already be present in the old credentials or be allowed by policy. Setgroups similarly validates every new supplementary group. On denial, the hook sends `SIGKILL` to the current process and returns `-EACCES`.

## State and Persistence Behavior

Active UID/GID policies persist in global RCU pointers populated by `securityfs.c`. `safesetid_initialized` is `__initdata` and only coordinates init sequencing. Rulesets are immutable after publication from the enforcement side; updates replace the entire pointer and old rules are freed after an RCU grace period.

## Dependencies and Integration Points

The file depends on LSM hooks for `task_fix_setuid`, `task_fix_setgid`, `task_fix_setgroups`, and `capable`; Linux credential and group-info structures; RCU; capability options; and policy types from `lsm.h`. It integrates with the securityfs policy writer through shared globals and `_setid_policy_lookup()`.

## Risks and Edge Cases

`id_permitted_for_cred()` uses the old real UID as the UID policy source; for GID checks the intended source is the old real GID, and any mismatch here would be security-sensitive. Killing on denied transitions prevents partially privileged processes from continuing after failing to drop privileges, but it is operationally harsh. Policy lookup mutates `pol->type` in `setid_policy_lookup()`, so ruleset type correctness relies on matching pointer selection.

## Test Signals

Tests should cover unconstrained default behavior, allowed and denied UID/GID transitions, transitions to IDs already in old credentials, fsuid/fsgid coverage, setgroups validation, denial-triggered `SIGKILL`, constrained `CAP_SETUID`/`CAP_SETGID` denial for user namespace mapping, `CAP_OPT_INSETID` pass-through, concurrent policy replacement under RCU, and warnings for blocked transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/safesetid/lsm.c -->
