# sources/distributed-fs/eos/unit_tests/mgm/AccessTests.cc

## Purpose
Tests MGM access-control primitives: stall-rule state, POSIX mode checks, ACL overrides, prepare permissions, deletion/rename permissions, sticky-bit behavior, and access rule key normalization.

## Important APIs, types, and functions
The file exercises `mgm::Access::SetStallRule`, `AccessChecker::checkContainer`, `AccessChecker::checkFile`, `mgm::Acl`, `ProcessRuleKey`, Quark namespace metadata stand-ins, and `VirtualIdentity`. Helpers create fake containers/files with uid/gid/mode and identities.

## Control flow
Tests construct metadata and identities, then assert allow/deny outcomes for user/group/other permission bits, ACL user/group entries, prepare flag `P_OK`, deletion flag `D_OK`, and sticky directory semantics. Rename/delete tests combine container and file checks to model operation-level authorization.

## State and persistence
`Access_SetRule` mutates static global stall maps and restores previous state. Other tests use transient metadata objects and ACL strings. No persistent namespace state is written.

## Dependencies and integration points
Uses Google Test, MGM access/ACL/admin command code, `AccessChecker`, common identity definitions, QuarkDB metadata classes, and mapping fixture setup.

## Risks and test signals
This file is a strong behavioral oracle for authorization edge cases. Risks include global stall state leakage across tests, ACL identity-context subtleties, sticky-bit owner rules, and default file mode interpretation. Missing signals include root/admin bypass behavior and multiple supplementary groups beyond simple allowed-gid cases.
