# sources/distributed-fs/ceph-client/security/apparmor/domain.c

## Purpose
`domain.c` implements AppArmor profile attachment and domain transitions: exec transitions, x-table lookups, unconfined attachment, xattr-conditioned attachments, `change_hat`, `change_profile`, `change_onexec`, stacking, ptrace/no_new_privs restrictions, and learning-profile creation in complain mode.

## Important APIs and functions
- Public entry points: `apparmor_bprm_creds_for_exec`, `aa_change_hat`, `aa_change_profile`, and `x_table_lookup`.
- Transition helpers: `profile_transition`, `x_to_label`, `find_attach`, `aa_xattrs_match`, `profile_onexec`, and `handle_onexec`.
- Label matching helpers: `label_compound_match`, `label_components_match`, `label_match`, and `change_profile_perms`.
- Hat helpers: `change_hat` and `build_change_hat`.
- Safety checks: `may_change_ptraced_domain`, no_new_privs subset checks, and secureexec/personality handling.

## Control flow
Exec starts in `apparmor_bprm_creds_for_exec`. It captures the current/newest label, records the label under which no_new_privs began, builds path conditions from executable inode owner/mode, and either processes a pending onexec transition or computes a profile transition for each component of a stacked label. `profile_transition` resolves the executable path, matches file permissions, decodes the exec transition index, finds/creates the target label, audits, and sets secureexec for safe transitions.

Attachment search prefers exact or most-specific xmatch path matches, then considers xattrs; equal specificity and equal xattr count are conflicts. `aa_change_hat` selects hats across the current namespace, supports token-based restore, and kills on brute-force token mismatch. `aa_change_profile` parses target labels, checks change permissions, optionally stores an onexec target, or immediately replaces/merges the current label.

## State and persistence
The file mutates task AppArmor context fields: current credential label, previous hat label, onexec target, change_hat token, and no_new_privs baseline label. It also creates null learning profiles in complain mode and uses policy namespace/profile lists. Exec transition results persist in the new credentials.

## Dependencies and integration
It depends on Linux binprm, ptrace, xattrs, credentials, path naming, labels, file permissions, policy namespaces, audit, task context, and IPC ptrace mediation. It is tightly integrated with policy unpack encoding through `xindex` flags and transition tables.

## Risks
This is a high-risk security boundary. Path lookup failures, xattr matching, conflict fallbacks, and unconfined attachment rules determine whether tasks become confined, remain in-profile, or become unconfined. no_new_privs subset checks must be correct for stacked labels. Ptrace restrictions must use the right tracer credentials and target label. Complain-mode null profile creation changes runtime policy shape and must not leak into enforce behavior.

## Test signals
Test exec transitions for ix/px/cx/nx/ux-style cases, named transition tables, child transitions, stacking targets, missing targets, conflict fallback, and xattr-conditioned attachment. Exercise no_new_privs, ptraced exec, secureexec, personality clearing, change_hat enter/restore/token mismatch, change_profile immediate/onexec/test modes, and unprivileged unconfined stacking restrictions. Audit output should explain fallback/conflict/missing-profile causes.
