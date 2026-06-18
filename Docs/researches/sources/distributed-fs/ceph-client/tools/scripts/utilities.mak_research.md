# sources/distributed-fs/ceph-client/tools/scripts/utilities.mak

Purpose: GNU make utility library for string/newline escaping, shell quoting, executable discovery, and three-component version comparison.

Important APIs, types, and functions: defines the `newline` variable, `nl-escape`, `escape-nl`, `unescape-nl`, `shell-escape-nl`, `shell-unescape-nl`, `escape-for-shell-sq`, `shell-sq`, `shell-wordify`, `_sw-esc-nl`, `is-absolute`, `lookup`, `is-executable`, `get-executable`, `get-executable-or-default`, `_ge_attempt`, `_gea_err`, `version-ge3`, and `version-lt3`.

Control flow: these are make-expanded functions. Newline utilities replace embedded newlines with a sentinel before passing through contexts such as `$(shell ...)` that collapse output newlines, then restore them later. Shell quoting helpers produce single-quoted shell words or command substitutions for multi-line text. Executable helpers decide whether a path is absolute, use `command -v` through `sh -c` for relative names, validate executable files, and emit make errors for missing required tools. Version helpers encode `major.minor.patch` triples into comparable integers with awk.

State and persistence: no persistent state beyond make variables and function expansions. The default newline sentinel is a long unusual string intended to avoid collisions.

Dependencies and integration points: depends on GNU make features, POSIX shell, `awk`, `grep`, `test`, and `command -v`. It is meant to be included by other kernel tools makefiles.

Risks: quoting helpers are sensitive to shell quoting and sentinel collisions. Some functions use helper macros without explicitly passing arguments in the local call sites, relying on make's expansion context; changes can easily break them. Version comparison assumes exactly three numeric components. The comments note bash brace-expansion pitfalls around awk.

Test signals: makefile users can validate by round-tripping multi-line variables, resolving absolute and PATH executables, and comparing known version triples such as 2.6.4 >= 2.6.2.
