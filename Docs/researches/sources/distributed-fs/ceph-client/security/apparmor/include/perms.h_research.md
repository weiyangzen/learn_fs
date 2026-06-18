# sources/distributed-fs/ceph-client/security/apparmor/include/perms.h

## Purpose
`perms.h` defines AppArmor's common permission bit layout, `aa_perms` structure, permission accumulation semantics, cross-check macros, and permission/audit helper prototypes.

## Important APIs and types
It maps read/write/exec/append to VFS bits and defines AppArmor-specific create/delete/open/rename/setattr/getattr/cred/chmod/chown/chgrp/lock/mmap/mprotect/link/snapshot/stack/onexec/change_profile/changehat bits. `struct aa_perms` contains allow, deny, subtree, cond, kill, complain, prompt, audit, quiet, hide, xindex, tag, and label fields. `aa_perms_accum` and `aa_perms_accum_raw` combine permissions across stacked labels. `aa_check_perms` applies decisions and auditing.

## Control flow and integration
Policydb accept entries are converted into `aa_perms`, mode-adjusted, accumulated across profiles, and checked against requested masks. Cross-check macros validate bidirectional or namespace/profile pair permissions, used notably for AF_UNIX peer checks.

## State and persistence
Permission sets are loaded policy state and transient decision state. `nullperms`, `allperms`, and `default_perms` provide standard defaults.

## Dependencies
It depends on Linux fs permission bits and AppArmor labels/audit structures.

## Risks
Permission bit overlays such as `AA_LINK_SUBSET` over `AA_MAY_LOCK` require context-specific interpretation. Accumulation rules are security critical for stacked labels. `AA_MAY_DELEGATE` appears as an empty macro marker, so callers must not treat it as a usable bit.

## Test signals
Unit tests should cover permission accumulation, deny overriding allow, audit/quiet/kill/complain interactions, link subset overlay behavior, xcheck macros, and string/audit formatting.
