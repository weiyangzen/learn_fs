<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/safesetid/securityfs.c -->
# sources/distributed-fs/ceph-client/security/safesetid/securityfs.c

## Purpose

`safesetid/securityfs.c` implements the SafeSetID policy management interface under securityfs. It parses complete UID/GID allowlist replacements, validates and repairs unsafe transitive gaps, publishes new rulesets atomically under RCU, and serves the stored policy text back to readers.

## Important APIs, Types, and Functions

- `parse_policy_line()` parses one `<ID>:<ID>` line into a typed `setid_rule` using the writer file credential's user namespace.
- `insert_rule()` inserts a rule into the UID or GID hash table.
- `verify_ruleset()` detects destinations that would be unconstrained if reached and inserts self-rules to constrain them, returning `-EINVAL` for bogus-but-fixed policies.
- `handle_policy_update()` parses, validates, and publishes a full policy replacement.
- `safesetid_uid_file_write()` and `safesetid_gid_file_write()` enforce `CAP_MAC_ADMIN`, offset zero, and call the common update helper.
- `safesetid_file_read()` returns the current stored policy string under the relevant update mutex.
- `safesetid_init_securityfs()` creates `/sys/kernel/security/safesetid/uid_allowlist_policy` and `gid_allowlist_policy`.

## Control Flow

Policy writes must start at offset zero and come from a file credential capable of `CAP_MAC_ADMIN` in `init_user_ns`. The update helper allocates a fresh ruleset, duplicates the userspace buffer for parsing and for later readback, then requires every policy line to end with `\n`. Each line is split on `:`, parsed as u32, mapped with `make_kuid()` or `make_kgid()` in the writer's namespace, validated, checked for duplicates through `_setid_policy_lookup()`, and inserted.

After parsing, `verify_ruleset()` walks all rules and checks whether each destination ID is itself constrained. If not, it warns and inserts a self-transition rule so a process that transitions into that ID cannot later escape policy. Non-allocation verification errors are allowed to fall through after this fix-up, preserving the policy with added constraints. Publication uses the UID or GID update mutex and `rcu_replace_pointer()`, then releases the old ruleset after an RCU grace period.

Reads take the same update mutex, dereference the ruleset with lockdep protection, and copy the stored original policy string with `simple_read_from_buffer()`. Securityfs initialization is skipped if the LSM hook init did not set `safesetid_initialized`.

## State and Persistence Behavior

There are separate UID and GID update mutexes. Published rulesets persist until the next full replacement or shutdown. Old rulesets are freed asynchronously by `call_rcu()`, including all hash entries and stored policy text. The securityfs files expose the original submitted text, not necessarily the self-rules inserted during verification.

## Dependencies and Integration Points

This file depends on securityfs, credentials, namespace-aware UID/GID mapping, `CAP_MAC_ADMIN`, RCU, hash tables, and the enforcement-side globals and lookup helper in `lsm.c`. It is initialized through SafeSetID's `initcall_fs` hook.

## Risks and Edge Cases

The parser requires a trailing newline on the final line; missing it rejects the whole update. Failed updates release the fresh ruleset and leave the old active policy untouched. Returning `len` after a policy that `verify_ruleset()` judged insecure but fixed may surprise userspace because warnings are the only signal of the inserted self-rules. Readback omits fix-up rules because it uses the original policy string.

## Test Signals

Tests should cover permission denial without `CAP_MAC_ADMIN`, nonzero offset writes, malformed lines, missing newline, invalid namespace IDs, duplicate entries, valid UID and GID replacement, concurrent readers during replacement, RCU freeing under stress, transitive-unconstrained warnings and self-rule behavior, readback contents, and securityfs creation failure cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/safesetid/securityfs.c -->
