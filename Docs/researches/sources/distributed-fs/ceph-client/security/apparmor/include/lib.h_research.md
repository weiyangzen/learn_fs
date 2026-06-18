# sources/distributed-fs/ceph-client/security/apparmor/include/lib.h

## Purpose
`lib.h` gathers shared AppArmor utilities: debug/assert macros, namespace visibility aliases, LSM blob offsets, common refcount type, string tables/counting, policy-list helpers, DFA null transition helper, path mediation predicate, and label-build macros for domain transitions.

## Important APIs and types
Debug constants and macros include `DEBUG_*`, `AA_DEBUG`, `AA_WARN`, `AA_BUG`, and `AA_ERROR`. `struct aa_common_ref` tags refcounted objects embedded in apparmorfs inodes. `struct aa_str_table` and `aa_str_table_ent` store transition/tag strings. `struct aa_policy` is the common name/list/profile-child base for namespaces and profiles. `fn_label_build` and `fn_label_build_in_scope` construct transition labels across stacked profile labels.

## Control flow and integration
`AA_BUG` becomes a runtime WARN when debug asserts are enabled and compile/no_printk validation otherwise. `aa_dfa_null_transition` provides the standard NUL separator step used by link, domain, and network pair matching. `fn_label_build` invokes a transition callback for each profile in a stacked label, flattens/uniques resulting profile vectors, and returns a merged label.

## State and persistence
The header declares global `apparmor_initialized`, `apparmor_blob_sizes`, and `stacksplitdfa`. Counted strings and string tables are refcounted in-memory policy state.

## Dependencies
It depends on slab, fs, LSM hooks, match DFA declarations, labels/profiles through macro call sites, and policy namespace visibility functions.

## Risks
Macro-heavy label building can obscure error paths and cleanup responsibilities. Debug behavior changes significantly with `CONFIG_SECURITY_APPARMOR_DEBUG_ASSERTS`. `path_mediated_fs` excludes `SB_NOUSER` filesystems from path mediation, so filesystem flags directly affect security coverage.

## Test signals
Compile with debug asserts on/off. Exercise stacked-label transitions that produce multiple intermediate labels and allocation failures. Validate string table resizing/destruction and policy lookup under RCU.
