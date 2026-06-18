<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/lib/getopt-pfx-core.h -->
# sources/compression/xz/lib/getopt-pfx-core.h

Purpose: wrapper that optionally prefixes core getopt symbols to avoid collisions with system getopt.

Important APIs/types/functions: `__GETOPT_PREFIX`, `__GETOPT_ID`, and macro remapping for `getopt`, `optarg`, `opterr`, `optind`, and `optopt`.

Control flow: if a prefix is configured, undefine public names, define prefixed aliases, apply a macOS workaround, clear `_GETOPT_CORE_H`, then include `getopt-core.h`.

State and persistence: compile-time symbol renaming only.

Dependencies and integration: used by generated `getopt.h` for standalone applications embedding gnulib getopt.

Risks: relies on include guard manipulation and platform-specific system header behavior. Misordered includes can still expose unprefixed declarations.

Test signals: compile a program defining `__GETOPT_PREFIX` alongside system `<unistd.h>` and verify only prefixed symbols are exported.
<!-- END_FILE_RESEARCH: sources/compression/xz/lib/getopt-pfx-core.h -->
