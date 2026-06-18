<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/lockdown/lockdown.c -->
# sources/distributed-fs/ceph-client/security/lockdown/lockdown.c

## Purpose

`lockdown.c` implements the Lockdown LSM policy state and control interface. It exposes a `locked_down` hook that denies operations at or below the active lockdown level and a securityfs file for querying or raising the level.

## Important APIs, Types, and Functions

- `kernel_locked_down` stores the current `enum lockdown_reason` threshold.
- `lock_kernel_down()` raises the lockdown level and logs the source.
- `lockdown_param()` parses early `lockdown=integrity` or `lockdown=confidentiality`.
- `lockdown_is_locked_down()` is the LSM hook used by other kernel code through `security_locked_down()`.
- `lockdown_read()` and `lockdown_write()` implement `/sys/kernel/security/lockdown`.
- `lockdown_lsm_init()` applies forced Kconfig defaults and registers the hook.
- `lockdown_secfs_init()` creates the securityfs file.

## Control Flow

Early parameter parsing can raise the level before normal initialization. During LSM init, forced Kconfig modes may raise it again and the `locked_down` hook is registered. Every later lockdown check passes a reason; invalid reasons at or above `LOCKDOWN_CONFIDENTIALITY_MAX` warn and fail closed. If the current level is at least the requested reason, a rate-limited notice names the current command and reason, then returns `-EPERM`.

The securityfs read path prints available levels with the current one in brackets. The write path copies a userspace string, strips a trailing newline, compares it to known level labels, and calls `lock_kernel_down("securityfs", level)`. Attempts to set the current or lower level fail because lockdown is monotonic.

## State and Persistence Behavior

`kernel_locked_down` is global runtime state. It only increases from `LOCKDOWN_NONE` toward integrity or confidentiality maximums and has no lowering path. Securityfs provides persistence only for the running kernel; boot defaults and command-line parameters decide initial state on reboot.

## Dependencies and Integration Points

The file depends on the LSM hook framework, `lockdown_reasons[]`, early parameter infrastructure, securityfs, and UAPI LSM IDs. It is used indirectly by kernel subsystems that call `security_locked_down()` for module loading, kernel memory access, debug interfaces, and confidentiality-sensitive reads.

## Risks and Edge Cases

Reason ordering is security-critical: the numeric lockdown reasons must align with integrity and confidentiality thresholds. `lock_kernel_down()` returns `-EPERM` for already-equal or lower requests, so userspace writes are intentionally not idempotent. If securityfs creation fails, the hook still enforces but runtime visibility/control is reduced.

## Test Signals

Tests should cover boot `lockdown=` parsing, forced Kconfig modes, reading active securityfs state, raising from none to integrity and confidentiality, refusal to lower or repeat levels, invalid strings, invalid hook reasons, and representative `security_locked_down()` callers returning `-EPERM` with rate-limited notices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/lockdown/lockdown.c -->
