# sources/distributed-fs/ceph-client/security/apparmor/include/cred.h

## Purpose
`cred.h` defines helpers for reading, setting, and safely refreshing the AppArmor label stored in Linux credentials, plus a helper for deriving the current AppArmor namespace.

## Important APIs and functions
- `cred_label` and `set_cred_label` access the LSM credential blob.
- `aa_get_newest_cred_label` and `_condref` return current label versions, respecting stale replacements.
- `aa_current_raw_label`, `aa_get_current_label`, `begin_current_label_crit_section`, and related end helpers manage current-task label references.
- `aa_get_current_ns` returns a refcounted namespace for the current label.

## Control flow
The fast critical-section helpers avoid taking references when the cred label is not stale and the current cred cannot change during the section. `begin_current_label_crit_section` may sleep and updates current credentials to the newest label if the old label is stale.

## State and persistence
The state is the AppArmor label pointer in the credential security blob. Refreshing stale labels can replace current task credentials. Namespace references are derived from label components.

## Dependencies
It depends on Linux credentials/scheduler, AppArmor label versioning, policy namespace refs, and task context/blob offsets.

## Risks
Using the sleepable `begin_current_label_crit_section` inside locks is unsafe; the header provides non-sleeping variants for locked contexts. Mispaired put/end calls can leak or underflow label refs. Direct `set_cred_label` transfers ownership expectations to credential lifetime management.

## Test signals
Profile replacement tests should show stale labels update correctly. Lockdep/RCU tests should cover locked critical-section helpers. Credential transition tests should verify label refs are balanced.
