<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/ostree/ot-admin-builtin-upgrade.c -->
# sources/cloud-native/ostree/src/ostree/ot-admin-builtin-upgrade.c

## Purpose
Implements `ostree admin upgrade`, pulling from the current origin and deploying a new tree when available.

## Important APIs and Types
Exports `ot_admin_builtin_upgrade`. Options include `--reboot`, `--kexec`, `--allow-downgrade`, `--override-commit`, `--pull-only`, `--deploy-only`, `--stage`, and `--os`. It uses `OstreeSysrootUpgrader`, pull flags, progress reporting, origin mutation, and optional reboot exec.

## Control Flow
The command validates incompatible options, constructs upgrader flags for staging/kexec, creates an upgrader for the selected OS, duplicates and sanitizes origin transient state, applies override commit if provided, configures pull flags including synthetic deploy-only and allow older, runs pull with console progress, cleans up on failed pull-only, deploys unless pull-only, prints no-update status if unchanged, and reboots if requested.

## State and Persistence
Pulling mutates repository objects and refs. Deploying mutates sysroot deployment state. Override commit is applied to the upgrader origin for this operation. Optional cleanup runs after failed pull-only. Optional reboot replaces the process.

## Dependencies and Integration Points
Uses sysroot upgrader APIs, repo pull progress callbacks, console locking, origin keyfiles, and shared reboot helper.

## Risks
Pull-only and deploy-only modes alter normal sequencing and must not be combined. Allow-downgrade intentionally accepts older commits. Override commit affects pull/deploy selection and must not persist unintended transient state. Progress handling is TTY-dependent.

## Test Signals
Tests should cover no update, successful pull/deploy, staged upgrade, kexec flag, pull-only cleanup on failure, deploy-only synthetic mode, allow-downgrade, override commit, option conflicts, and reboot exec path.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/ostree/ot-admin-builtin-upgrade.c -->
