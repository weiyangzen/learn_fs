# sources/cloud-native/overlayfs-tools/sh.h

Purpose: declares shell-generation state and APIs for overlayfs-tools.

Important APIs/types/functions: enum indexes `LOWERDIR`, `UPPERDIR`, `MOUNTDIR`, `LOWERNEW`, `UPPERNEW`, `NUM_VARS`; extern `var_names` and `vars`; `create_shell_script`; `command`.

Control flow: callers populate `vars`, create a script, then emit formatted commands with path substitutions.

State and persistence: global `vars` controls all script substitution.

Dependencies/integration: used by CLI option parsing and action callbacks.

Risks: global mutable path state is not reentrant. The `command` format language is tiny and has no validation beyond substitution failure.

Test signals: generated script fixture tests.
