<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/ostree/ot-admin-builtins.h -->
# sources/cloud-native/ostree/src/ostree/ot-admin-builtins.h

## Purpose
Declares the function prototypes for `ostree admin` built-in command handlers.

## Important APIs and Types
Defines `BUILTINPROTO` to declare handlers with the standard `(argc, argv, invocation, cancellable, error)` signature. It declares cleanup, config diff, deploy, finalize, boot-complete, soft-reboot commands, unlock, status, origin, upgrade, kargs, state-overlay, and more. `switch` is declared manually because it is a C keyword.

## Control Flow
No runtime control flow exists. The declarations let command tables reference handlers consistently.

## State and Persistence
No state is stored. Each declared handler may mutate sysroot state.

## Dependencies and Integration Points
Includes `ot-main.h` for `OstreeCommandInvocation` and command types. Consumed by `ot-builtin-admin.c` and individual admin source files.

## Risks
Prototype drift breaks command registration at compile time. Conditional implementations must remain aligned with command table feature guards.

## Test Signals
Full compilation with all feature combinations and command-table link checks are the primary signals.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/ostree/ot-admin-builtins.h -->
