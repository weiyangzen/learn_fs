<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/src/liblzma/common/filter_common.c -->
# sources/compression/xz/src/liblzma/common/filter_common.c

Purpose: Centralizes common filter-chain behavior shared by raw encoder and decoder paths: feature metadata, option copying/freeing, chain validation, chain initialization, and memory usage estimation.

Important APIs and data: The compile-time `features[]` table maps filter IDs to option structure sizes and chain-placement rules (`non_last_ok`, `last_ok`, `changes_size`). Public/internal functions include `lzma_filters_copy()`, `lzma_filters_free()`, `lzma_validate_chain()`, `lzma_raw_coder_init()`, and `lzma_raw_coder_memusage()`.

Control flow: `lzma_filters_copy()` copies to a temporary array first so `real_dest` is unchanged on failure. `lzma_validate_chain()` enforces one to four filters, known IDs, legal non-last/last placement, and at most three size-changing filters. `lzma_raw_coder_init()` uses a caller-provided `coder_find()` table; encoders reverse chain order before calling `lzma_next_filter_init()`, while decoders preserve order. `lzma_raw_coder_memusage()` validates the chain, sums per-filter memory usage, uses 1 KiB for simple filters without a callback, and adds `LZMA_MEMUSAGE_BASE`.

State and persistence: The module owns no persistent global state beyond static feature metadata. It allocates filter option copies on demand and relies on callers to release them with `lzma_filters_free()`.

Dependencies and integration: Included by filter encoder/decoder ID tables, Block Header parsing, stream decoders, and raw APIs. Compile-time `HAVE_ENCODER_*`/`HAVE_DECODER_*` macros determine which filters appear valid.

Risks and tests: Chain validation controls API safety and file-format correctness. Tests should cover unsupported IDs, missing terminators, invalid last filters, too many filters, many size-changing filters, option copy rollback, allocator failures, and encoder order reversal.
<!-- END_FILE_RESEARCH: sources/compression/xz/src/liblzma/common/filter_common.c -->
