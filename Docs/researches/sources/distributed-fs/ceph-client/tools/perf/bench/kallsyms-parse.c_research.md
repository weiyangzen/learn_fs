# Research: sources/distributed-fs/ceph-client/tools/perf/bench/kallsyms-parse.c

Purpose: benchmarks parsing `/proc/kallsyms` through perf's kallsyms parser.

Important APIs/types/functions: `bench_kallsyms_parse()` parses options and loops. `do_kallsyms_parse()` invokes `kallsyms__parse()` with a no-op callback and measures elapsed time.

Control flow: for each iteration, open/parse kallsyms, time the parse, update stats, and print average/stddev at the end.

State and persistence: only runtime stats; no persistent output. Reads `/proc/kallsyms`.

Dependencies and integration: depends on perf kallsyms parser, stats, parse-options, and access to kernel symbol file.

Risks: restricted kallsyms, kernel symbol count, and I/O cache state heavily affect results. A no-op callback measures parser overhead but not downstream symbol processing.

Test signals: normal and restricted `/proc/kallsyms`, repeated iterations, cold vs warm cache, and parser error handling.
