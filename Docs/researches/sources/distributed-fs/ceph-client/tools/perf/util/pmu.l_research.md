# sources/distributed-fs/ceph-client/tools/perf/util/pmu.l

## Purpose
This flex lexer tokenizes PMU sysfs format descriptions, such as `config:0-7` or `config1:1,6-7`, for the parser in `pmu.y`.

## Important APIs, Types, and Functions
It is generated with the `perf_pmu_` prefix, reentrant scanner support, and bison bridge support. The local `value` helper converts decimal text to a numeric `PP_VALUE` token and reports `PP_ERROR` on conversion failure. It also returns tokens for `config`, `-`, `:`, and `,`.

## Control Flow
The scanner matches decimal numbers first, then the literal `config`, punctuation, dots, and newlines. Dots and newlines are ignored. `perf_pmu_wrap` returns 1 to indicate end of input.

## State and Persistence
Scanner state is owned by flex and passed through `yyscan_t`. Parsed numeric values are stored in the bison semantic value for the current scanner.

## Dependencies and Integration Points
It includes `pmu.h` and `pmu-bison.h`, and is called by `__perf_pmu_format__load` in `pmu.c`. The parser ultimately fills a `struct perf_pmu_format`.

## Risks
Only decimal numeric input is accepted by this lexer. It silently ignores dots, which matches expected sysfs grammar but could hide malformed input. Overflow and conversion errors are collapsed into `PP_ERROR`.

## Test Signals
Parser tests should feed valid ranges, single bits, multiple comma-separated terms, malformed numbers, unsupported tokens, and config indexes. Generated scanner build coverage is also required.
