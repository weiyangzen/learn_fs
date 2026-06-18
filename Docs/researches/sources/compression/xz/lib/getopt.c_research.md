<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/lib/getopt.c -->
# sources/compression/xz/lib/getopt.c

Purpose: gnulib/GNU implementation of short and long option scanning, including global and reentrant parser entry points.

Important APIs/types/functions: globals `optarg`, `optind`, `opterr`, `optopt`; static `getopt_data`; helpers `exchange`, `process_long_option`, `_getopt_initialize`; public/internal functions `_getopt_internal_r`, `_getopt_internal`, and `getopt`.

Control flow: initialization selects ordering mode from optstring, `POSIXLY_CORRECT`, and caller flags. `_getopt_internal_r` permutes non-options if needed, handles `--`, dispatches long options, processes short option clusters, handles `-W;` long-option forwarding, and returns option codes or errors.

State and persistence: global parser state persists across calls; reentrant state lives in caller-provided `_getopt_data`. It mutates `argv` during permutation.

Dependencies and integration: used when platform getopt is missing or insufficient. Standalone mode disables NLS and alloca, and maps locking to no-ops when unavailable.

Risks: global parser is not thread-safe. Argument permutation requires writable `argv`. Ambiguous long-option tracking may allocate memory; failure degrades diagnostics. Error messages are intentionally untranslated in XZ's standalone build.

Test signals: built-in `-DTEST` harness plus xz CLI parsing tests for permutation, POSIX ordering, long abbreviations, missing args, optional args, and invalid options.
<!-- END_FILE_RESEARCH: sources/compression/xz/lib/getopt.c -->
