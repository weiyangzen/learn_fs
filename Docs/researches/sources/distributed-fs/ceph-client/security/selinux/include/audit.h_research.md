## sources/distributed-fs/ceph-client/security/selinux/include/audit.h

### Purpose
`audit.h` declares SELinux support routines for Linux audit LSM rules. These routines let audit rules parse SELinux context fields, match task/object LSM properties, free rule-private memory, and update audit rule caches when AVC policy state changes.

### Important APIs, types, and functions
The interface consists of `selinux_audit_rule_avc_callback(u32 event)`, `selinux_audit_rule_init(u32 field, u32 op, char *rulestr, void **rule, gfp_t gfp)`, `selinux_audit_rule_free(void *rule)`, `selinux_audit_rule_match(struct lsm_prop *prop, u32 field, u32 op, void *rule)`, and `selinux_audit_rule_known(struct audit_krule *rule)`.

### Control flow
Audit setup code calls `*_init` to allocate and translate a textual SELinux rule target. Runtime audit matching passes an `lsm_prop` to `*_match`, while rule teardown calls `*_free`. AVC reset events call the callback to invalidate or refresh rule state after policy changes.

### State and persistence
The header owns no state, but documents that rule structures are allocated internally and must be released by the caller. Rule validity depends on the loaded SELinux policy and therefore on AVC reset handling.

### Dependencies and integration points
It includes kernel audit and type headers and is wired into `hooks.c` under `CONFIG_AUDIT` via audit hook registrations and AVC callback registration.

### Risks
Incorrect lifetime handling can leak rule memory or leave stale SIDs after policy reload. Match semantics must remain synchronized with `struct lsm_prop` and audit field/operator definitions.

### Test signals
Build with `CONFIG_AUDIT`; add audit rules using SELinux subject/object fields; reload policy and verify rules still match or are invalidated correctly.
