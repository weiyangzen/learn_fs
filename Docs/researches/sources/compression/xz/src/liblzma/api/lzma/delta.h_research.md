# sources/compression/xz/src/liblzma/api/lzma/delta.h

Purpose: declares the Delta filter ID and option structure for byte-wise delta preprocessing.

Important APIs/types/functions: defines `LZMA_FILTER_DELTA`, enum `lzma_delta_type` with `LZMA_DELTA_TYPE_BYTE`, and `lzma_options_delta` containing `type`, `dist`, min/max distance macros, reserved integers, and reserved pointers.

Control flow: applications place a Delta filter in a `lzma_filter` chain, usually before LZMA2. Encoding stores byte differences at distance `dist`; decoding reverses that transformation. The header itself only provides configuration.

State and persistence: filter state is held in the coder implementation, not in the header. `lzma_options_delta` is caller-owned and ABI-reserved for future extensions.

Dependencies/integration: included by `lzma.h`; xz option parsing maps `--delta` to this filter; `filter.h` property/flag APIs encode/decode its options.

Risks: only byte-wise delta is supported; `type` must stay `LZMA_DELTA_TYPE_BYTE` and `dist` must be 1-256. Wrong distance can make decompression reversible but reduce compression effectiveness or fail options validation.

Test signals: `tests/test_filter_flags.c`, filter string tests, raw/stream filter-chain round trips, and xz CLI `--delta` option tests.
