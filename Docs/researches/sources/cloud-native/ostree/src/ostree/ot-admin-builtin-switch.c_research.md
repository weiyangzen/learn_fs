<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/ostree/ot-admin-builtin-switch.c -->
# sources/cloud-native/ostree/src/ostree/ot-admin-builtin-switch.c

## Purpose
Implements `ostree admin switch`, changing the tracked origin refspec to a new remote/ref, pulling it, deploying it, and deleting the old ref.

## Important APIs and Types
Exports `ot_admin_builtin_switch`. Options are `--reboot`, `--kexec`, and `--os`. Uses `OstreeSysrootUpgrader`, origin keyfiles, refspec parsing, pull/deploy APIs, repo transactions, and `ot_admin_execve_reboot`.

## Control Flow
The command parses superuser context, creates an upgrader with `IGNORE_UNCONFIGURED` and optional kexec, reads the old origin refspec, parses the requested new refspec or remote-only syntax ending in `:`, builds the final refspec, rejects no-op switches, writes the upgrader origin, pulls allowing older commits, deploys, starts a repo transaction to delete the old remote ref, commits it, and optionally reboots.

## State and Persistence
Mutates deployment origin, downloads content, creates a new deployment, deletes the old repo ref, and may replace the process with `systemctl reboot`.

## Dependencies and Integration Points
Integrates remote/ref tracking with the sysroot upgrader and repo transaction APIs. It shares progress display behavior with upgrade.

## Risks
Deleting the old ref after deploy can surprise users if the old ref is still desired. Remote-only syntax must preserve the old branch correctly. Pull allows older commits intentionally, so downgrade-like switches are possible.

## Test Signals
Tests should cover remote-only switches, full refspec switches, equal-ref rejection, pull/deploy success, old ref deletion transaction, kexec flag propagation, and reboot exec failure.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/ostree/ot-admin-builtin-switch.c -->
