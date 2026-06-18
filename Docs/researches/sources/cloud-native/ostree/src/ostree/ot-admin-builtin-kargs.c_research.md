<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/ostree/ot-admin-builtin-kargs.c -->
# sources/cloud-native/ostree/src/ostree/ot-admin-builtin-kargs.c

## Purpose
Implements the `ostree admin kargs` dispatcher for kernel-argument subcommands.

## Important APIs and Types
Registers hidden `edit-in-place` through `admin_kargs_subcommands[]` and exports `ot_admin_builtin_kargs`.

## Control Flow
Mirrors the instutil dispatcher: extracts the first non-option subcommand, searches the table, generates help/errors for missing or unknown commands, sets program name, and calls the selected subcommand.

## State and Persistence
This file only mutates argv layout and process prgname. Deployment bootconfig mutations are performed by the selected kargs subcommand.

## Dependencies and Integration Points
Depends on `ot-admin-kargs-builtins.h`, admin option parsing, and the `OstreeCommand` dispatch model. Registered under `ostree admin kargs`.

## Risks
The only current subcommand is hidden, so user-facing help may be sparse. Option forwarding and `--` handling must remain consistent with other dispatchers.

## Test Signals
Dispatcher tests for missing command, unknown command, hidden command invocation, and option passthrough are useful.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/ostree/ot-admin-builtin-kargs.c -->
