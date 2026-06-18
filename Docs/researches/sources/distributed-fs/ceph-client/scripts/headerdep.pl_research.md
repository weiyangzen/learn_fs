# sources/distributed-fs/ceph-client/scripts/headerdep.pl

## Purpose
Builds a header include dependency graph and either reports recursive include cycles or emits GraphViz DOT output.

## APIs, Control Flow, and State
Options include `--all`, `--graph`, `-I`, help, and version. `strip()` normalizes input paths relative to include roots, `search()` resolves headers in include directories, and `parse_all()` recursively reads `#include <...>` directives into `%deps` keyed by normalized header names. `detect_cycles()` walks dependency chains from requested headers and calls `print_cycle()` for the first or all detected cycles. `graph()` prints vertices and edges with sanitized node names from `mangle()`.

## Dependencies and Integration
It depends on Perl `Getopt::Long`, readable include trees, and optional GraphViz downstream. It is a developer diagnostic utility and stores graph state only in memory.

## Risks and Test Signals
It only parses angle-bracket includes and ignores preprocessor conditionals, quoted includes, macro includes, and generated headers not present on disk. Test signals include cycle warnings with line numbers, `--all` reporting multiple cycles, DOT accepted by `dot`, and include-root normalization for `-I`.
