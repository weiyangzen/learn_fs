# sources/distributed-fs/ceph-client/security/apparmor/capability.c

## Purpose
`capability.c` mediates Linux capability checks under AppArmor policy, exposes capability feature metadata, deduplicates noisy capability audit records, and computes the visible capability set for a profile.

## Important APIs and functions
- `aa_sfs_entry_caps` reports capability mask and extended capability support in apparmorfs features.
- `audit_cb` prints `capname` using the generated `capability_names.h` table.
- `audit_caps` handles legacy capability audit mode, quiet/kill bits, complain mode, and one-second per-CPU duplicate suppression.
- `profile_capable` performs the per-profile capability decision using either DFA-based `AA_CLASS_CAP` permissions or legacy `aa_caps` bitsets.
- `aa_capable` iterates confined profiles in a label for LSM capability checks.
- `aa_profile_capget` returns the capability set visible to capability-get style queries.

## Control flow
The public `aa_capable` initializes audit data and checks each confined profile. `profile_capable` first tries the new policydb class path; capabilities are split into 32-bit chunks selected by `cap >> 5`, with the request bit derived from `cap & 0x1f`. If no DFA class mediates capabilities, it falls back to legacy allow/denied/audit/quiet/kill masks.

## State and persistence
The file uses per-CPU `audit_cache` entries keyed by subject cred and capability number with a one-second expiration. It holds a cred reference while cached. Profile capability rules are loaded policy state in `aa_ruleset`.

## Dependencies and integration
It depends on generated capability names, Linux capability constants, timekeeping, AppArmor audit, policydb permissions, profile modes, and label iteration. LSM hooks call `aa_capable` through AppArmor's main LSM integration.

## Risks
Duplicate audit suppression trades visibility for log noise reduction and must correctly release cached credentials. Capability chunk math must match policy compiler encoding. The loop in `aa_profile_capget` is sensitive to `CAP_LAST_CAP` coverage and permission bit shifting, so changes in kernel capability count should be tested.

## Test signals
Test allowed, denied, audited, quiet, kill, and `CAP_OPT_NOAUDIT` cases under both DFA and legacy policy. Verify duplicate audit suppression over repeated checks and expiration after one second. Confirm apparmorfs feature `caps/mask` matches generated capability names.
