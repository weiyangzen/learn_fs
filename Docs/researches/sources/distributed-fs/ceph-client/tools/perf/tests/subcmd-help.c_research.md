## sources/distributed-fs/ceph-client/tools/perf/tests/subcmd-help.c

Purpose: unit tests for libsubcmd command-name list helpers.
Important functions: `test__load_cmdnames`, `test__uniq_cmdnames`, `test__exclude_cmdnames`, and `test__exclude_cmdnames_no_overlap`.
Control flow: creates `struct cmdnames` lists, adds names, checks lookup case-sensitivity, removes adjacent duplicates via `uniq`, and excludes overlapping names between lists.
State and persistence: heap allocations inside cmdname helpers are released with `clean_cmdnames`.
Dependencies and integration: `<subcmd/help.h>` APIs `add_cmdname`, `is_in_cmdlist`, `uniq`, `exclude_cmds`, and `clean_cmdnames`.
Risks: `uniq` assumes sorted input; tests use already-adjacent duplicates and do not cover unsorted behavior.
Test signals: suite `libsubcmd help tests` contains four test cases with count and membership assertions.
