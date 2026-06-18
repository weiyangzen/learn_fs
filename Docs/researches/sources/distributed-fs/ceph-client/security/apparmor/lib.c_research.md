# sources/distributed-fs/ceph-client/security/apparmor/lib.c

Purpose: provides common AppArmor helpers for debug parsing, string tables, counted strings, policy names, permission printing, and permission/audit mode evaluation.

Important APIs/functions: `aa_parse_debug_params()` and `aa_print_debug_params()` map sysfs debug strings. `aa_resize_str_table()`/`aa_destroy_str_table()` manage unpacked string tables. `skipn_spaces()` and `aa_splitn_fqname()` parse policy namespace/profile names. `aa_info_message()` logs status. `aa_str_alloc()`/`aa_str_kref()` implement counted strings. `aa_perm_mask_to_str()`, `aa_audit_perm_names()`, and `aa_audit_perm_mask()` format permission masks. `aa_apply_modes_to_perms()` applies audit/complain/kill/user modes. `aa_check_perms()` centralizes allow/deny/audit return semantics. `aa_policy_init()`/`aa_policy_destroy()` manage hierarchical policy names.

Control flow: mediation code computes `aa_perms`, applies modes, then calls `aa_check_perms()` to decide error and audit type. Name parsing supports both `:ns:profile` and policy hierarchy forms.

State and persistence: `nullperms`, `allperms`, file permission names, and counted policy strings are shared infrastructure. Dependencies include audit, profile modes, and policy structures.

Risks and test signals: incorrect mode application can silently allow complain-mode denials or suppress audit. Name parsing is security-sensitive for namespace boundaries. Test debug sysfs parsing, permission mask formatting, `hide` returning `-ENOENT`, complain/kill/user modes, and fqname parsing edge cases.
