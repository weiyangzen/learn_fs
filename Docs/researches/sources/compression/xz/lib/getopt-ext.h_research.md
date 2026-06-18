<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/lib/getopt-ext.h -->
# sources/compression/xz/lib/getopt-ext.h

Purpose: public declarations for GNU long-option extensions.

Important APIs/types/functions: defines `struct option`, `no_argument`, `required_argument`, `optional_argument`, `getopt_long`, and `getopt_long_only`.

Control flow: header-only; callers pass a null-terminated long-option table and optional returned index.

State and persistence: uses the same global getopt state as core parsing.

Dependencies and integration: included through `getopt-pfx-ext.h` and `getopt.h`; backs xz's long CLI options.

Risks: `has_arg` remains `int` for compatibility. Long-only behavior can be surprising when single-dash options overlap with short options.

Test signals: parse exact, abbreviated, ambiguous, flag-setting, required-argument, optional-argument, and long-only options.
<!-- END_FILE_RESEARCH: sources/compression/xz/lib/getopt-ext.h -->
