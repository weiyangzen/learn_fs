<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/lockdown/Kconfig -->
# sources/distributed-fs/ceph-client/security/lockdown/Kconfig

## Purpose

`lockdown/Kconfig` defines the kernel Lockdown LSM options, including whether lockdown support is built, whether it initializes early, and the default lockdown level.

## Important APIs, Types, and Functions

- `SECURITY_LOCKDOWN_LSM` builds the lockdown LSM and selects module signature support when modules are enabled.
- `SECURITY_LOCKDOWN_LSM_EARLY` places lockdown in the early LSM init path so early boot parameters can be restricted.
- `LOCK_DOWN_KERNEL_FORCE_NONE`, `LOCK_DOWN_KERNEL_FORCE_INTEGRITY`, and `LOCK_DOWN_KERNEL_FORCE_CONFIDENTIALITY` choose the default lockdown mode.

## Control Flow

Kconfig determines whether `lockdown.o` is built, whether it uses `DEFINE_EARLY_LSM` or `DEFINE_LSM`, and which forced mode the init function applies before registering hooks.

## State and Persistence Behavior

The selected default mode seeds the runtime `kernel_locked_down` level in `lockdown.c`. Runtime lockdown is monotonic; it can be raised but not lowered.

## Dependencies and Integration Points

The options depend on the generic security framework and integrate with module signature requirements, early LSM ordering, command-line parsing, and the securityfs lockdown control.

## Risks and Edge Cases

Late initialization may miss checks needed during early boot. Forced integrity or confidentiality can block debugging, kexec, kernel memory access, or other administrative workflows depending on hooks elsewhere in the kernel.

## Test Signals

Build and boot tests should verify each default mode, early versus normal LSM registration, command-line `lockdown=` handling, and visibility through `/sys/kernel/security/lockdown`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/lockdown/Kconfig -->
