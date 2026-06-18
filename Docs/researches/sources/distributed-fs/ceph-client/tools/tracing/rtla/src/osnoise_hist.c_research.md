# sources/distributed-fs/ceph-client/tools/tracing/rtla/src/osnoise_hist.c

## Purpose
`osnoise_hist.c` implements `rtla osnoise hist`, a per-CPU histogram mode for OS noise samples. It configures tracefs hist triggers on `osnoise:sample_threshold`, reads the generated histogram, stores per-CPU buckets and summaries, and prints a tabular histogram.

## Important APIs, Types, and Functions
`struct osnoise_hist_cpu` stores bucket samples plus count/min/sum/max. `struct osnoise_hist_data` owns a tracefs histogram handle, per-CPU hist arrays, bucket size, and number of entries. Important functions include `osnoise_alloc_histogram()`, `osnoise_init_trace_hist()`, `osnoise_read_trace_hist()`, `osnoise_print_stats()`, `osnoise_hist_parse_args()`, `osnoise_hist_enable()`, and `osnoise_hist_main_loop()`. The file exports `struct tool_ops osnoise_hist_ops`.

## Control Flow
The parser initializes defaults of microsecond output, bucket size 1, and 256 entries, then handles osnoise runtime/period/threshold/stop options, trace actions, event filters/triggers, histogram formatting flags, warmup, buffer size, and action hooks. Enable creates the tracefs histogram before calling `osnoise_enable()`. The main loop delegates to `hist_main_loop()` and then pauses/reads the tracefs hist file. Printing emits optional headers, bucket rows, overflow counts, and summary lines.

## State and Persistence
Tracefs hist triggers are installed in the tool trace instance and destroyed by `osnoise_destroy_trace_hist()` through mode cleanup. Per-CPU samples live in heap arrays. Trace-output actions can persist trace files.

## Dependencies and Integration Points
The module depends on tracefs histogram APIs, osnoise trace events, `common_parse_options()`, `actions_parse()`, and `osnoise_apply_config()`.

## Risks and Edge Cases
Parsing the hist text uses string searches for `duration: ~`, `cpu:`, and `hitcount:`; format changes in tracefs hist output can break collection. `osnoise_destroy_trace_hist()` assumes a valid hist pointer when called on error. `--no-index` is rejected unless `--with-zeros` is set because sparse output would be ambiguous. Histogram memory scales with `nr_cpus * (entries + 1)`.

## Test Signals
Test with varying bucket/entry sizes, no samples, overflow samples, monitored CPU subsets, no-header/no-summary/no-index combinations, trace actions, threshold stops, and missing `osnoise:sample_threshold` support.
