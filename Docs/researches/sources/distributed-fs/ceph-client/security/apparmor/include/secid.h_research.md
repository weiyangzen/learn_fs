# sources/distributed-fs/ceph-client/security/apparmor/include/secid.h

Purpose: declares AppArmor security identifier allocation and conversion between numeric secids, labels, and LSM security contexts.

Important APIs/constants: `AA_SECID_INVALID` is never allocated, `AA_SECID_WILDCARD` matches any secid for secmark policy, and `apparmor_display_secid_mode` controls whether mode is included in rendered secctx. The public functions are `aa_secid_to_label()`, `apparmor_secid_to_secctx()`, `apparmor_lsmprop_to_secctx()`, `apparmor_secctx_to_secid()`, `apparmor_release_secctx()`, `aa_alloc_secid()`, and `aa_free_secid()`.

Control flow: labels receive secids during label initialization; network secmark and LSM secctx hooks convert between secids and AppArmor label names. Release frees allocated security context memory through the LSM context wrapper.

State and persistence: secids pin labels while active; freeing a label releases its secid. The wildcard value is policy semantics, not an allocated object.

Dependencies and integration: integrates with label lifecycle, socket/secmark checks, audit, LSM hooks, and sysctl control in `lsm.c`. Risks include stale secid-to-label references after label replacement and ambiguous string-to-secid parsing. Test with label replacement, secmark wildcard rules, getpeersec/secctx hooks, display-mode toggles, and invalid secctx inputs.
