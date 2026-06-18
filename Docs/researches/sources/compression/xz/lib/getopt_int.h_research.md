<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/lib/getopt_int.h -->
# sources/compression/xz/lib/getopt_int.h

Purpose: internal declarations and state structure for the gnulib getopt implementation.

Important APIs/types/functions: `enum __ord`, `struct _getopt_data`, `_GETOPT_DATA_INITIALIZER`, `_getopt_internal`, `_getopt_internal_r`, `_getopt_long_r`, and `_getopt_long_only_r`.

Control flow: no runtime logic; defines how parser state tracks current scan pointer, ordering mode, skipped non-option ranges, and standard getopt globals.

State and persistence: describes both global-copy and reentrant state layouts.

Dependencies and integration: included by `getopt.c` and `getopt1.c`.

Risks: layout changes affect both source files and any internal reentrant consumers. Initialization requires `optind=1`, `opterr=1`, and cleared internal initialized flag.

Test signals: reentrant parser tests should run two argument vectors independently and confirm no cross-state leakage.
<!-- END_FILE_RESEARCH: sources/compression/xz/lib/getopt_int.h -->
