# sources/distributed-fs/ceph-client/scripts/basic/fixdep.c

## Purpose
`fixdep.c` is a host build tool that transforms compiler dependency files into kbuild `.cmd` snippets. It replaces broad dependencies on generated config headers with fine-grained dependencies on individual `include/config/<SYMBOL>` files.

## APIs, Types, And Functions
It uses `struct item` hash tables to de-duplicate files and config symbols. Key functions are `parse_dep_file()`, `parse_config_file()`, `use_config()`, `read_file()`, `is_ignored_file()`, `is_no_parse_file()`, and `in_hashtable()`.

## Control Flow
`main()` expects `<depfile> <target> <cmdline>`, prints `savedcmd_<target>`, reads the depfile, and parses make dependency syntax. The parser skips comments, whitespace, continuation backslashes, targets, and ignored `autoconf.h`. It records the first source file, prints normal dependencies, reads parseable dependency files, scans for standalone `CONFIG_` tokens, normalizes `_MODULE`, and emits wildcard config dependencies plus final make rules.

## State And Persistence
State is process-local hash tables and read buffers. Persistence is stdout redirected by kbuild into `.cmd` files. No source files are modified.

## Dependencies And Integration Points
It depends on POSIX file APIs and `xalloc.h`. It integrates with compiler `-MD` depfiles, kbuild command-line change tracking, module version tooling that parses `source_*`/`deps_*`, Rust dep-info comments, and kconfig’s `include/config/` file tree.

## Risks And Test Signals
Risks include make-syntax edge cases, escaped path handling, false-positive `CONFIG_` mentions, and failure to write full output. Test signals are minimal rebuilds after config changes, valid `.cmd` files, ignored binary Rust artifacts, and parse errors on malformed depfiles.
