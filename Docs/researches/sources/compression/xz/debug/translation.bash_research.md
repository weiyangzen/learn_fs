<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/debug/translation.bash -->
# sources/compression/xz/debug/translation.bash

Purpose: helper script for translators to view representative translated `xz` output.

Important APIs/types/functions: resolves an `xz` executable, prints version/source/locale, switches to `tests/files`, puts xz in `PATH`, then evaluates a fixed list of commands covering errors, memory-limit output, help, filters help, verbose mode, and list tables.

Control flow: starts with `set -e` for setup validation, accepts optional executable path, locates top source directory relative to the script, then switches to `set +e` because many test commands intentionally fail.

State and persistence: no persistent repo state; only stdout/stderr diagnostics.

Dependencies and integration: depends on bash, built `xz`, `locale`, optional git, and sample test files. Integrates with translation QA rather than automated tests.

Risks: uses `eval` over hard-coded command strings; safe in current form but fragile if user-provided commands were ever added. Requires being run from a source tree with `tests/files`.

Test signals: translators inspect output manually, often with `less -S`; missing/misaligned translations or malformed tables are the main signal.
<!-- END_FILE_RESEARCH: sources/compression/xz/debug/translation.bash -->
