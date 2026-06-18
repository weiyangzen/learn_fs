# sources/cloud-native/overlayfs-tools/sh.c

Purpose: generates safe shell scripts for the `overlay` utility actions.

Important APIs/types/functions: globals `vars` and `var_names`; `create_shell_script`, `quote`, `substitue`, and `command`.

Control flow: `create_shell_script` creates a 0700 temporary `.sh`, writes a bash header, exports quoted path variables, and optionally creates backup lower/upper trees when `LOWERNEW` or `UPPERNEW` are set. `quote` emits single-quoted shell strings with embedded quote escaping. `command` substitutes `%L`, `%U`, `%M`, `%N`-style variable prefixes into shell-safe references and appends a command line.

State and persistence: creates executable script files and, when run, the script may copy or mutate layer directories. The C code only writes scripts.

Dependencies/integration: called from `main.c` and `logic.c` callbacks to materialize vacuum/merge/deref operations.

Risks: function name `substitue` is misspelled but internal. Prefix substitution fails if a path does not start with the expected variable value. Backup copy commands in generated scripts are destructive to pre-existing `LOWERNEW`/`UPPERNEW` targets.

Test signals: tests should inspect generated scripts for quoting, prefix substitution, backup handling, and execution on paths containing quotes/spaces.
