<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/ostree/main.c -->
# sources/cloud-native/ostree/src/ostree/main.c

## Purpose
Defines the main entry point for the `ostree` command-line tool and registers the top-level built-in command table.

## Important APIs and Types
The static `commands[]` array maps command names to `OstreeCommand` entries, flags, function pointers, and descriptions. `main` calls `ostree_command_lookup_external`, `ostree_command_exec_external`, or `ostree_main`.

## Control Flow
Startup asserts an argv is present, checks whether the requested command should dispatch to an external executable, and otherwise invokes the internal command dispatcher with the built-in table.

## State and Persistence
No persistent state is modified directly. The selected built-in may open repositories, mutate sysroots, or access remotes.

## Dependencies and Integration Points
Includes `ot-builtins.h` and integrates all top-level OSTree CLI commands including `admin`, `checkout`, `pull`, `remote`, `summary`, and more. Conditional compilation hides GPG and network pull commands when features are disabled.

## Risks
Command table flags determine whether repository context is required and must match each command's parser. External command lookup changes `argv[0]` before exec, so compatibility depends on `ot-main` behavior.

## Test Signals
CLI smoke tests for command discovery, help output, external command dispatch, feature-conditional commands, and no-repo commands are appropriate.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/ostree/main.c -->
