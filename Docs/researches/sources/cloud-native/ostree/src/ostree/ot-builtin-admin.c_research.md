<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/ostree/ot-builtin-admin.c -->
# sources/cloud-native/ostree/src/ostree/ot-builtin-admin.c

## Purpose
Implements the top-level `ostree admin` dispatcher and registers admin subcommands.

## Important APIs and Types
Static `admin_subcommands[]` maps names such as `cleanup`, `deploy`, `status`, `switch`, `upgrade`, `unlock`, `pin`, `kargs`, and hidden service commands to their handlers and flags. `ostree_admin_option_context_new_with_commands` creates help text, and `ostree_builtin_admin` dispatches.

## Control Flow
The dispatcher strips the first non-option command from argv, looks it up, prints generated help with missing/unknown errors when needed, sets the process program name to include the subcommand, creates a sub-invocation, and calls the handler. Some commands are conditionally included for soft reboot support.

## State and Persistence
This file mutates only process argv layout and program name. Persistent sysroot changes are performed by subcommands.

## Dependencies and Integration Points
Uses `OstreeCommand`, admin builtins, generic builtins, and admin option parsing. It is registered as top-level `admin` in `main.c`.

## Risks
Command flags determine repository/sysroot parsing behavior and must match handler expectations. Hidden commands are service-facing and should remain available to units even if omitted from help.

## Test Signals
CLI tests for help, missing/unknown subcommand errors, option passthrough, hidden command invocation, command flags, and feature-conditional entries are important.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/ostree/ot-builtin-admin.c -->
