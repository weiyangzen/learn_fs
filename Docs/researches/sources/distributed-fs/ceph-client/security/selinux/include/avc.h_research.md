## sources/distributed-fs/ceph-client/security/selinux/include/avc.h

### Purpose
`avc.h` defines the object-manager-facing Access Vector Cache interface. It is the main boundary between SELinux hook implementations and cached security-server decisions, including audit calculation and callback registration.

### Important APIs, types, and functions
Important declarations include `avc_init`, `avc_has_perm_noaudit`, `avc_has_perm`, `avc_has_extended_perms`, `avc_policy_seqno`, `avc_add_callback`, AVC stats helpers, and cache threshold helpers. `struct avc_cache_stats` tracks cache counters. `struct selinux_audit_data` records source SID, target SID, class, requested/audited/denied masks, and result. Inline `avc_audit_required()` computes whether an access decision requires audit; inline `avc_audit()` invokes `slow_avc_audit()` when needed.

### Control flow
Hook code usually calls `avc_has_perm()` for check plus audit or `avc_has_perm_noaudit()` when checks must happen under locks, followed by `avc_audit()` after locks are released. `avc_audit_required()` suppresses audit for `AVD_FLAGS_NEVERAUDIT`, distinguishes denial audit from allow audit, and honors dontaudit-style `auditdeny` filtering.

### State and persistence
The header declares interfaces to global AVC cache state, policy sequence numbers, callback lists, and optional per-CPU stats. It stores no state directly.

### Dependencies and integration points
It depends on generated Flask class and permission headers, SELinux security server types, Linux audit/LSM audit structures, and is included by `hooks.c`, `objsec.h`, NetLabel interfaces, and AVC implementation files.

### Risks
Audit logic is subtle: `auditdeny` filtering is intentionally not a direct denied-permission mask. Callers that skip post-check auditing or pass incomplete audit data can lose important diagnostics. Policy sequence number users must revalidate cached decisions.

### Test signals
Test AVC allow/deny, permissive domain behavior, dontaudit/noaudit cases, extended ioctl/netlink permissions, policy reload sequence changes, cache stats, and callback execution.
