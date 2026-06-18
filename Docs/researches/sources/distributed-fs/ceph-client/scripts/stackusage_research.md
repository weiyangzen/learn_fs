# sources/distributed-fs/ceph-client/scripts/stackusage

Purpose: `stackusage` runs `make` with GCC/Clang stack-usage generation enabled and aggregates newly created `.su` files into a sorted report.

Important APIs, types, and functions: it parses `-o outfile` and `-h`, records the current epoch time, defaults `outfile` to a temporary file, invokes `KCFLAGS="${KCFLAGS} -fstack-usage" make "$@"`, then finds `.su` files newer than the start time. A Perl one-liner prepends directory names, removes column numbers, tab-separates fields, and the result is sorted by stack size descending.

Control flow: option parsing stops at first non-option make argument. Build happens before report collection. The output path is printed at the end.

State and persistence: it creates compiler `.su` files through the build and writes the aggregated report.

Dependencies and integration points: depends on a compiler supporting `-fstack-usage`, make/Kbuild, `find`, `xargs`, Perl `File::Basename`, `sort`, and `mktemp`.

Risks: filenames with unusual whitespace may be fragile through `xargs` and Perl field parsing. Only files newer than script start are included, so clock issues or preexisting outputs may affect reports.

Test signals: run on a small build target, verify `.su` records are normalized and sorted, then compare two outputs with `stackdelta`.
