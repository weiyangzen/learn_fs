<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/safesetid/Kconfig -->
# sources/distributed-fs/ceph-client/security/safesetid/Kconfig

## Purpose

`safesetid/Kconfig` defines the SafeSetID LSM option, which restricts UID/GID transitions and related `CAP_SETUID`/`CAP_SETGID` uses according to system-wide allowlists.

## Important APIs, Types, and Functions

- `SECURITY_SAFESETID` builds SafeSetID, depends on `SECURITY`, selects `SECURITYFS`, defaults to `n`, and documents the allowlist-based setid transition model.

## Control Flow

When enabled, Kbuild includes the SafeSetID objects and the LSM registers hooks plus securityfs policy files. When disabled, no SafeSetID runtime policy exists.

## State and Persistence Behavior

The configuration only controls availability. Runtime policies are supplied through securityfs and live in RCU-protected rulesets in `lsm.c` and `securityfs.c`.

## Dependencies and Integration Points

SafeSetID depends on the generic LSM framework and securityfs. It integrates with credential-changing syscalls and capability checks through LSM hooks.

## Risks and Edge Cases

Improperly configured allowlists can prevent privileged processes from dropping privileges, which SafeSetID treats as dangerous enough to kill the process on denied setid transitions. Enabling the option without a policy has no transition constraints.

## Test Signals

Build tests should confirm `SECURITYFS` is selected. Runtime tests should verify securityfs policy files exist only when the LSM initializes and that no policy means default kernel setid behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/safesetid/Kconfig -->
