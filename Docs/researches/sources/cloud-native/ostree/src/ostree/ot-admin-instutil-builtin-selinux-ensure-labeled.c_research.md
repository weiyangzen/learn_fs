<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/ostree/ot-admin-instutil-builtin-selinux-ensure-labeled.c -->
# sources/cloud-native/ostree/src/ostree/ot-admin-instutil-builtin-selinux-ensure-labeled.c

## Purpose
Implements `ostree admin instutil selinux-ensure-labeled`, recursively applying SELinux labels to all or part of the first deployment when a policy is present.

## Important APIs and Types
Helpers include `ptrarray_path_join`, `relabel_one_path`, `relabel_recursively`, and `selinux_relabel_dir`. The exported command is `ot_admin_instutil_builtin_selinux_ensure_labeled`.

## Control Flow
After superuser/unlocked parsing, the command selects the first deployment, derives the deployment path, accepts optional subpath and prefix, creates an `OstreeSePolicy`, and if a policy name exists, recursively enumerates files and calls `ostree_sepolicy_restorecon` with allow-nolabel and keep-existing flags. Paths are tracked as an array to produce SELinux relative paths.

## State and Persistence
Mutates SELinux xattrs/labels on deployment files when policy rules assign a label. It prints label changes.

## Dependencies and Integration Points
Depends on GFile enumeration, `OstreeSePolicy`, deployment directories, and SELinux feature availability. Registered only when SELinux support is compiled.

## Risks
The optional-argument handling checks `argc >= 2` but then reads `argv[2]`, so callers should provide both subpath and prefix. Recursive relabeling can be expensive and error-prone on large trees. KEEP_EXISTING changes semantics versus force relabeling.

## Test Signals
SELinux-enabled tests should cover no deployment, no policy, full deployment relabel, subpath/prefix relabel, missing prefix argument, recursive traversal, and unchanged existing labels.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/ostree/ot-admin-instutil-builtin-selinux-ensure-labeled.c -->
