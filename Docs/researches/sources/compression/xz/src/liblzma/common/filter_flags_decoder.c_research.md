<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/src/liblzma/common/filter_flags_decoder.c -->
# sources/compression/xz/src/liblzma/common/filter_flags_decoder.c

Purpose: Decodes an on-wire `.xz` Filter Flags field into an `lzma_filter` with allocated filter-specific options.

Important API: `lzma_filter_flags_decode(lzma_filter *filter, const lzma_allocator *allocator, const uint8_t *in, size_t *in_pos, size_t in_size)`.

Control flow: Initializes `filter->options` to NULL for safe cleanup, decodes Filter ID as VLI, rejects reserved IDs, decodes properties size as VLI, checks that enough input remains, and delegates option decoding to `lzma_properties_decode()`. It advances `*in_pos` past the property bytes even if the property decoder returns an error from filter-specific validation.

State/dependencies: Stateless beyond `filter` output. Depends on VLI decoding and decoder property tables in `filter_decoder.c`.

Risks/tests: Important malformed cases are reserved IDs, truncated VLI, properties size larger than remaining input, unsupported filter ID, and properties that allocate then fail. Tests should assert `filter->options` remains safe to free.
<!-- END_FILE_RESEARCH: sources/compression/xz/src/liblzma/common/filter_flags_decoder.c -->
