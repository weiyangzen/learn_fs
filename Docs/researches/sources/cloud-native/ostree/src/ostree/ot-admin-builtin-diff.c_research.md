<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/ostree/ot-admin-builtin-diff.c -->
# sources/cloud-native/ostree/src/ostree/ot-admin-builtin-diff.c

## Purpose
Implements `ostree admin config-diff`, comparing a deployment's mutable `/etc` against the default `/usr/etc`.

## Important APIs and Types
Exports `ot_admin_builtin_diff`. It accepts `--os` to target a stateroot and uses `ostree_diff_dirs` and `ostree_diff_print`.

## Control Flow
The command parses admin context, requires either a booted deployment or explicit OS name, selects the merge or booted deployment, resolves deployment directory paths for `usr/etc` and `etc`, computes modified/removed/added lists ignoring xattrs, and prints the diff.

## State and Persistence
No persistent state is changed; it reads deployment filesystem state.

## Dependencies and Integration Points
Uses admin sysroot loading, `OstreeDeployment`, GFile path resolution, and OSTree diff APIs.

## Risks
The diff intentionally ignores xattrs, so SELinux or capability changes are not reported. With `--os`, absence of a merge deployment is a hard not-found error.

## Test Signals
Tests should create deployment etc changes and verify added, removed, modified output, booted-vs-os selection, and xattr-ignore behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/ostree/ot-admin-builtin-diff.c -->
