<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/ostree/ot-admin-kargs-builtin-edit-in-place.c -->
# sources/cloud-native/ostree/src/ostree/ot-admin-kargs-builtin-edit-in-place.c

## Purpose
Implements hidden `ostree admin kargs edit-in-place`, updating kernel arguments across all deployments without creating new deployments.

## Important APIs and Types
Exports `ot_admin_kargs_builtin_edit_in_place`. Option `--append-if-missing` supplies kernel args to add only when absent.

## Control Flow
The command parses superuser context, requires at least one deployment, iterates every deployment, builds `OstreeKernelArgs` from current bootconfig options, applies each append-if-missing argument, converts the result to a string, and calls `ostree_sysroot_deployment_set_kargs_in_place`.

## State and Persistence
Mutates bootconfig options in place for all deployments in the sysroot.

## Dependencies and Integration Points
Uses sysroot deployment APIs, bootconfig parser, kernel arg helpers, and the kargs dispatcher.

## Risks
This command changes every deployment and is hidden, so it is likely intended for controlled automation. In-place mutation bypasses deploy-based rollback semantics.

## Test Signals
Tests should cover multiple deployments, idempotent append-if-missing, no deployment error, and status/bootloader visibility of changed kargs.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/ostree/ot-admin-kargs-builtin-edit-in-place.c -->
