<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/safesetid/lsm.h -->
# sources/distributed-fs/ceph-client/security/safesetid/lsm.h

## Purpose

`safesetid/lsm.h` defines SafeSetID's internal policy model shared by enforcement and securityfs code.

## Important APIs, Types, and Functions

- `enum sid_policy_type` represents default, constrained, and allowed decisions.
- `kid_t` wraps `kuid_t` or `kgid_t` in one union.
- `enum setid_type` distinguishes UID and GID policies.
- `struct setid_rule` stores one source-to-destination allow rule in a hash bucket.
- `SETID_HASH_BITS` sets the policy hash table to 256 buckets.
- `INVALID_ID` provides an invalid `kid_t` sentinel.
- `struct setid_ruleset` stores the hash table, original policy string, RCU head, and UID/GID type.
- `_setid_policy_lookup()`, active ruleset globals, and `safesetid_init_securityfs()` are declared for cross-file use.

## Control Flow

The header has no runtime flow, but it defines how callers interact: securityfs builds a complete `setid_ruleset`, enforcement looks up decisions, and old rulesets are retired through RCU.

## State and Persistence Behavior

The active ruleset pointers declared here are global and RCU-protected. Each ruleset retains the original policy string so securityfs reads can return the configured allowlist exactly as written.

## Dependencies and Integration Points

It depends on kernel UID/GID types and hash-table support. It is included by both `lsm.c` and `securityfs.c`, making it the contract between policy parsing and policy enforcement.

## Risks and Edge Cases

The `kid_t` union and `INVALID_ID` require callers to respect the accompanying `setid_type`; mixing UID and GID interpretations can produce invalid comparisons. Hashing by numeric kernel ID value assumes IDs are already mapped and valid in the relevant user namespace.

## Test Signals

Build coverage plus policy lookup tests for default, constrained, allowed, duplicate, invalid ID, UID, and GID cases validate the definitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/safesetid/lsm.h -->
