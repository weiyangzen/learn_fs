# sources/compression/xz/src/liblzma/api/lzma/filter.h

Purpose: defines common filter-chain representation plus raw coding, filter property, filter flag, and string conversion APIs.

Important APIs/types/functions: defines `LZMA_FILTERS_MAX`, `lzma_filter { lzma_vli id; void *options; }`, support queries, `lzma_filters_copy/free`, raw encoder/decoder memusage and initialization, `lzma_filters_update`, raw buffer encode/decode, property size/encode/decode, filter flag size/encode/decode, and string APIs `lzma_str_to_filters`, `lzma_str_from_filters`, `lzma_str_list_filters` with `LZMA_STR_*` flags.

Control flow: filter chains are arrays terminated by `LZMA_VLI_UNKNOWN`. Callers validate/support-check filters, estimate memory, initialize streamed raw coders or use buffer APIs, and may update filters after supported flush/barrier points. String APIs parse user-facing presets/chains and allocate option structs.

State and persistence: filter options are caller-owned unless allocated by decode/string APIs, then freed with `lzma_filters_free()`. Streamed raw coders keep internal state in `lzma_stream`.

Dependencies/integration: core glue between BCJ, Delta, LZMA1/2, Block, Stream, and CLI options. xz uses this API heavily for command-line filters, memory estimates, and runtime filter updates.

Risks: arrays must have `LZMA_FILTERS_MAX + 1` slots for arbitrary chains. `lzma_filters_copy()` does not free old destination options. Property sizing may succeed even if full encoder initialization would fail. String parsing validates syntax but not every semantic condition unless later coder init checks it.

Test signals: `tests/test_filter_flags.c`, `tests/test_filter_str.c`, CLI option parsing, raw encode/decode round trips, and memory usage checks.
