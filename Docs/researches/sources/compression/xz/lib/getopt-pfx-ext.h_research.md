<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/lib/getopt-pfx-ext.h -->
# sources/compression/xz/lib/getopt-pfx-ext.h

Purpose: wrapper that optionally prefixes GNU long-option getopt extension symbols.

Important APIs/types/functions: remaps `getopt_long`, `getopt_long_only`, `option`, and `_getopt_internal`; sets `__getopt_argv_const` based on prefixed or compatibility mode.

Control flow: if prefixing is active, build prefixed identifiers, clear extension include guard, then include `getopt-ext.h`.

State and persistence: compile-time renaming only.

Dependencies and integration: pairs with `getopt-pfx-core.h` inside generated `getopt.h`.

Risks: compatibility prototypes intentionally differ when not prefixed. Include guard resets are delicate but needed for system-header collisions.

Test signals: compile prefixed getopt_long users and check symbols with `nm`; verify non-prefixed mode matches expected GNU prototypes.
<!-- END_FILE_RESEARCH: sources/compression/xz/lib/getopt-pfx-ext.h -->
