# sources/distributed-fs/ceph-client/security/apparmor/include/policy.h

## Purpose
`policy.h` defines AppArmor's core policy structures: policy databases, rulesets, attachments, profiles, generic policy data blobs, mode macros, policy management permissions, and profile/policy reference helpers.

## Important APIs and types
Key structures are `aa_policydb`, `aa_data`, `aa_ruleset`, `aa_attachment`, and `aa_profile`. `aa_policydb` wraps DFA, permissions, transition strings, tags, and class start states. `aa_ruleset` combines policy/file policydbs, capabilities, rlimits, and secmarks. `aa_profile` combines policy identity, parent/ns, mode/audit/path flags, attachment data, rawdata/hash/dentries/data, and embedded variable-size label/rules.

Mode macros include `COMPLAIN_MODE`, `USER_MODE`, `KILL_MODE`, `PROFILE_IS_HAT`, and `profile_unconfined`. Public functions cover allocation/free, lookup, profile replacement/removal, learning-profile creation, ruleset allocation, policy management capability checks, and mediation-class computation.

## Control flow and integration
Policy unpack fills these structures. Mediation code retrieves `profile->label.rules[0]`, checks `RULE_MEDIATES` for a class, uses file or policy policydbs for DFA matching, and applies mode/audit behavior. Policy management paths call `aa_replace_profiles` and `aa_remove_profiles`.

## State and persistence
This header defines the in-memory representation of loaded policy. Profiles belong to namespaces, have hierarchy/children, may hold raw policy load data and hashes, expose apparmorfs dentries, and carry label/rules lifetime state.

## Dependencies
It depends on Linux credentials, capabilities, krefs, rhashtable, sockets, AppArmor audit/capability/domain/file/lib/label/net/perms/resource, and apparmorfs dentry indices.

## Risks
Profile structure layout is delicate because `struct aa_label label` is variable-length and last. `aa_get_newest_profile` returns a profile from a label reference and depends on label lifetime rules. Class mediation fallback between NETV9 and NET must match policy ABI. Policy management capability checks are central to load/remove security.

## Test signals
Test policy allocation/free under replacement/removal, profile lookup by namespace/fqname, learning profile creation, rawdata/hash dentries, class mediation bits, v9/v8 network fallback, and policy load/remove permission checks.
