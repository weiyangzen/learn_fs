<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/lib/getopt1.c -->
# sources/compression/xz/lib/getopt1.c

Purpose: implements GNU `getopt_long` and `getopt_long_only` entry points plus reentrant variants.

Important APIs/types/functions: `getopt_long`, `_getopt_long_r`, `getopt_long_only`, `_getopt_long_only_r`, all delegating to `_getopt_internal` or `_getopt_internal_r`.

Control flow: long mode passes `long_only=0`; long-only mode passes `long_only=1`. Reentrant variants accept caller-owned `_getopt_data`.

State and persistence: public functions share global getopt state; `_r` variants use supplied state.

Dependencies and integration: included in `libgnu.a` when replacement long-option parsing is needed.

Risks: same argv mutation and global-state caveats as `getopt.c`. The test harness is compile-time only.

Test signals: compile with `-DTEST` and run sample long options; xz long-option parsing provides integration coverage.
<!-- END_FILE_RESEARCH: sources/compression/xz/lib/getopt1.c -->
