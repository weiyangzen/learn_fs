# sources/distributed-fs/ceph-client/security/apparmor/secid.c

Purpose: maps AppArmor labels to numeric secids and converts secids/LSM properties to printable security contexts.

Important APIs, types, and functions: global state is `aa_secids` xarray and `apparmor_display_secid_mode`. Public functions include `aa_secid_to_label()`, `apparmor_secid_to_secctx()`, `apparmor_lsmprop_to_secctx()`, `apparmor_secctx_to_secid()`, `apparmor_release_secctx()`, `aa_alloc_secid()`, and `aa_free_secid()`. Internal `apparmor_label_to_secctx()` formats labels from `root_ns`.

Control flow: secid allocation locks the xarray with IRQ-save, allocates an ID from `AA_FIRST_SECID` upward, stores the label pointer, and writes `label->secid`. Conversion from secctx parses a label string relative to root unconfined label and returns its secid. Release frees only AppArmor-owned contexts.

State and persistence: secids are in-memory xarray entries and intentionally do not pin labels; label replacement/freeing must keep mappings coherent. Context conversion allocates strings for callers.

Dependencies and integration: used by LSM secctx hooks, audit/netlabel-facing code, label parsing/rendering, root namespace state, and LSM context IDs.

Risks and test signals: because secids do not hold label refs, stale mapping prevention depends on label lifecycle code outside this file. Test signals include secid allocation/free reuse, invalid label parse errors, display mode inclusion, and release behavior for non-AppArmor contexts.
