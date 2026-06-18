# sources/distributed-fs/ceph-client/security/apparmor/include/label.h

## Purpose
`label.h` defines AppArmor labels: refcounted, RCU-aware sets of one or more profiles that represent confinement. It also defines label sets, proxies for replacement, iteration macros, merge/subset helpers, printing/parsing APIs, and refcount helpers.

## Important APIs and types
Core types are `struct aa_labelset`, `struct aa_proxy`, `struct label_it`, and `struct aa_label`. Label flags include unconfined, null, immutable, in-tree, profile, explicit, stale, renamed, and revoked. Iteration macros cover all profiles, confined profiles, profiles in a namespace, merge differences, and set differences. Public functions cover allocation, insertion/replacement, subset checks, merge, name update, printing, parsing, and profile-label matching.

## Control flow and integration
Most mediation code iterates labels with `fn_for_each_confined` or namespace-scoped variants. Policy replacement marks labels stale and redirects proxies so callers can obtain newest labels. Stacked labels are parsed and split using `stacksplitdfa`.

## State and persistence
Labels are long-lived kernel objects with krefs, RCU cleanup, rbtree membership in namespace label sets, proxy pointers, secids, cached names, mediation bitmasks, and variable profile vectors. Proxies preserve stable object identity across replacement.

## Dependencies
It depends on atomic/kref/RCU/rbtree/audit primitives, AppArmor class constants, and lib helpers. It is foundational for credentials, policy, file, socket, audit, and domain code.

## Risks
Label lifetime and replacement are high risk: stale/proxy handling must avoid use-after-free, refcount leaks, and stale security decisions. Iteration macros hide control flow and rely on labels being NUL-terminated by profile vectors. The `mediates` bitmask only supports class IDs up to 63.

## Test signals
Stress profile replacement/removal while files and sockets hold labels. Test stacked-label parsing, merge/subset operations, namespace-scoped iteration, RCU label acquisition, and audit/seq printing for hidden or subnamespace labels.
