# sources/distributed-fs/ceph-client/security/apparmor/policy_compat.c

Purpose: converts older AppArmor packed policy DFA permission encodings into the current `struct aa_perms` table model used by the policy engine. It supports legacy file permission layouts, generic policydb versions, and xmatch DFAs so older userspace policy compilers can still load policy into newer kernels.

Important APIs, types, and functions: exported entry points are `aa_compat_map_xmatch()`, `aa_compat_map_policy()`, and `aa_compat_map_file()`. They allocate `policy->perms`, set `policy->size`, and rewrite DFA accept tables through `remap_dfa_accept()`. Internal helpers include `dfa_map_xindex()`, `map_old_perms()`, `compute_fperms_*()`, `compute_xmatch_perms()`, `compute_perms_entry()`, `map_other()`, and `map_xbits()`. The code depends on `struct aa_policydb`, `struct aa_dfa`, `struct aa_perms`, `ACCEPT_TABLE()`, `ACCEPT_TABLE2()`, and version predicates such as `VERSION_LE(version, v8)`.

Control flow: each public mapper allocates a permission table from DFA state count, fills it state-by-state from embedded accept bits, then rewrites accept1/accept2 to permission-table indexes. File DFAs get two entries per DFA state for user/other owner-condition variants. Generic policydb mapping treats accept1 as base user permissions and accept2 as extension bits/audit/quiet, with version-specific handling around v8/v9 xbits.

State and persistence: it mutates in-memory policydb state only: `policy->perms`, `policy->size`, and the DFA accept tables. No filesystem state is changed. Allocation uses `kvzalloc_objs()` and failures leave callers with `-ENOMEM`.

Dependencies and integration: called from `policy_unpack.c` when loaded policy lacks an explicit `perms` table. Its output is later verified by `verify_profile()` and consumed by rule lookup paths. It integrates with AppArmor permission constants, xtransition encodings, DFA table layouts, and debug logging.

Risks and test signals: compatibility bit layouts are historical and easy to mis-map; errors can grant, deny, or audit the wrong operation. The owner split and xindex remapping are especially sensitive because accept2 becomes an owner flag for file DFAs. There is no direct KUnit file for this mapper; practical tests are successful loads of legacy v5-v9 policy, accept index verification, and permission behavior regression tests.
