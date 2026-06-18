<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/ostree/ot-admin-builtin-set-origin.c -->
# sources/cloud-native/ostree/src/ostree/ot-admin-builtin-set-origin.c

## Purpose
Implements `ostree admin set-origin`, configuring a remote and writing a new origin refspec for a deployment.

## Important APIs and Types
Exports `ot_admin_builtin_set_origin`. Options include `--set KEY=VALUE` for remote options and `--index` to target a non-booted deployment. It uses `ostree_repo_remote_change`, `ostree_parse_refspec`, `ostree_sysroot_origin_new_from_refspec`, and `ostree_sysroot_write_origin_file`.

## Control Flow
The command parses superuser context, requires remote and URL, opens the sysroot repo, selects the booted deployment or indexed deployment, converts `--set` pairs into an `a{sv}` remote-options variant, adds the remote if needed, derives the branch from an explicit argument or old origin, builds a new refspec, and writes the deployment origin file.

## State and Persistence
Mutates repository remote configuration and deployment origin metadata. It does not deploy new content by itself.

## Dependencies and Integration Points
Integrates repo remote management, deployment origin files, and later upgrade/switch behavior that reads origins.

## Risks
If the old origin lacks a refspec and no branch is provided, the command fails. Remote options are accepted as strings only. Changing the origin of a non-booted deployment depends on index stability.

## Test Signals
Tests should cover adding a new remote, updating booted and indexed deployments, branch inheritance, explicit branch override, remote option parsing, missing refspec failure, and later upgrade using the new origin.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/ostree/ot-admin-builtin-set-origin.c -->
