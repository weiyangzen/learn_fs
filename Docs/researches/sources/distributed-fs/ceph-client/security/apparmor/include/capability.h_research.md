# sources/distributed-fs/ceph-client/security/apparmor/include/capability.h

## Purpose
This header defines AppArmor's capability rule representation and public capability mediation API.

## Important APIs and types
`struct aa_caps` stores allow, audit, denied, quiet, kill, and extended capability bitsets. `aa_sfs_entry_caps` exposes feature metadata. `aa_profile_capget` computes a profile's visible capabilities, and `aa_capable` enforces a capability request against a label.

## Control flow and integration
Policy unpack fills `aa_caps` or DFA policydb structures; LSM capability hooks call `aa_capable`; apparmorfs feature reporting references `aa_sfs_entry_caps`.

## State and persistence
Capability policy is stored in per-ruleset `aa_caps`. `aa_free_cap_rules` is currently a no-op because the structure owns no dynamic allocations.

## Dependencies
It depends on Linux capability/sched types, apparmorfs entries, and AppArmor labels/profiles.

## Risks
The header guard end comment has a typo but the macro itself is functional. Any future dynamic fields added to `aa_caps` must update `aa_free_cap_rules`.

## Test signals
Compile capability mediation with policy load/unload cycles and verify no dynamic cleanup is required. Test feature reporting for extended capability support.
