# sources/distributed-fs/ceph-client/security/apparmor/include/policy_compat.h

## Purpose
`policy_compat.h` declares compatibility helpers for mapping older AppArmor policy ABI versions into current internal policy formats.

## Important APIs and symbols
It defines `K_ABI_MASK`, `FORCE_COMPLAIN_FLAG`, version comparison macros, version constants `v5` through `v9`, and declarations for `aa_compat_map_xmatch`, `aa_compat_map_policy`, and `aa_compat_map_file`.

## Control flow and integration
Policy unpack/load code calls these mapping helpers after reading older policy blobs. Version comments document semantic changes: v6 per-entry policydb mediation checks, v8 full network masking, and v9 xbits as policydb permission bits.

## State and persistence
No state is defined here. The helpers mutate loaded policydb structures so they can be mediated by the current runtime.

## Dependencies
It depends on `policy.h` and therefore the main policydb/profile structures.

## Risks
ABI mapping errors can silently grant or deny access differently from older policy semantics. Version masks must preserve non-version flags such as force-complain.

## Test signals
Load v5, v6, v7, v8, and v9 policy fixtures and compare expected permission decisions, especially network masks, file xmatch, and force-complain behavior.
